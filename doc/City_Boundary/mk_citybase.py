#!/usr/bin/env python
# coding=utf-8

import sys
import os
import getopt
from pyspatialite import dbapi2 as db

help1 = """
		Скрипт создания базы данных границ городов
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
cur.execute('CREATE TABLE IF NOT EXISTS city(id INTEGER PRIMARY KEY AUTOINCREMENT, city_name, city_lastname, geometry, min_lng DOUBLE, min_lat DOUBLE, max_lng DOUBLE, max_lat DOUBLE, country)')

'''получаем список файлов с данными'''
dat_files = os.listdir(dirname)
'''перебираем файлы с данными'''
for dat_file in dat_files:
    if dat_file.split('.').pop() != 'dat':
        continue
    try:
        f = open(dirname + '/' + dat_file, 'r')
        print 'Processing file: %s' % dat_file
    except:
        print "Can't open file %s " % dat_file
        exit(1)
    lines = f.readlines()
    lines_count = len(lines)
    '''перебираем строки'''
    city_count = 0
    country = dat_file.split('_')[0]
    for line in lines:
        city_data = line.split('|')
        city_name = city_data[0].replace("'","")
        city_lastname = city_data[1].replace("'","")
        city_geometry = city_data[len(city_data)-1]
        city_count += 1
        print 'Processing city: %s (%i/%i)' % (city_name, city_count, lines_count)
        sql = "SELECT MbrMinX(GeomFromGeoJSON('"+ city_geometry +"')) as min_lng, MbrMinY(GeomFromGeoJSON('"+ city_geometry +"')) as min_lat, MbrMaxX(GeomFromGeoJSON('"+ city_geometry +"')) as max_lng, MbrMaxY(GeomFromGeoJSON('"+ city_geometry +"')) as max_lat"
        res = cur.execute(sql)
        for rec in res:
            min_lng = rec[0]
            min_lat = rec[1]
            max_lng = rec[2]
            max_lat = rec[3]
        sql = "INSERT INTO city (city_name, city_lastname, geometry, min_lng, min_lat, max_lng, max_lat, country) VALUES('"+city_name+"', '"+city_lastname+"', '"+city_geometry+"'," + str(min_lng) + "," + str(min_lat) + "," + str(max_lng) + "," + str(max_lat) + ", '" + country + "')"
        #print sql
        cur.execute(sql)
    conn.commit()
    f.close()
cur.close()
conn.close()
