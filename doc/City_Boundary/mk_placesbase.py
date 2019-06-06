#!/usr/bin/env python
# coding=utf-8

import sys
import os
import getopt
from pyspatialite import dbapi2 as db

help1 = """
		Скрипт создания базы координат населенных пунктов
"""

# print progress
def print_progress(message, count, size, index=None):
    progress = float(count) / size * 100
    if index != None:
        sys.stdout.write("%s: %d%%  (index=%d)  \r" % (message, progress, index))
        sys.stdout.flush()
    else:
        sys.stdout.write("%s: %d%%  \r" % (message, progress))
        sys.stdout.flush()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'vd:f:')
    # print optlist
    dirname = filter(lambda item: item[0] == '-d', optlist)[0][1]
    db_file = filter(lambda item: item[0] == '-f', optlist)[0][1]
except:
    print 'Usage %s [-v] -d <dat_files_dir> -f <db_file>' % sys.argv[0]
    exit(1)

if '-v' in map(lambda item: item[0], optlist):
    print help1

conn = db.connect(db_file)
# creating a Cursor
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS place(id INTEGER PRIMARY KEY AUTOINCREMENT, place_name, place_type, geometry, lat, lng, country )')

'''получаем список файлов с данными'''
dat_files = os.listdir(dirname)
'''перебираем файлы с данными'''
for dat_file in dat_files:
    if dat_file.split('.').pop() != 'sqlite':
        continue
    print "Processing file %s" % (dirname + '/' + dat_file)
    conn2 = db.connect(dirname + '/' + dat_file)
    cur2 = conn2.cursor()
    res = cur2.execute("SELECT name, sub_type, AsGeoJSON(Geometry) as geom, Y(GEOMETRY) as lat, X(Geometry) as lng FROM pt_place WHERE sub_type='town' OR sub_type='city' OR sub_type='village' OR sub_type='hamlet'")
    for row in res:
        place_name = row[0]
        place_type = row[1]
        geometry = row[2]
        lat = row[3]
        lng = row[4]
        country = dat_file.split('-')[0]
        if place_name == None or place_type == None or geometry == None:
            continue
        sql = "INSERT INTO place (place_name, place_type, geometry, lat, lng, country) VALUES('"+place_name+"', '"+place_type+"', '"+geometry+"', "+str(lat)+", "+ str(lng) +", '"+country+"')"
        #print sql
        cur.execute(sql)
    conn.commit()
    cur2.close()
    conn2.close()
cur.close()
conn.close()
