#!/usr/bin/env python
# coding=utf-8

import sys
import os
import getopt
from pyspatialite import dbapi2 as db

help1 = """
		Скрипт создания базы данных объектов ландшафта
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

def filterString(name):
    if name.isalnum():
        return name
    char_list = []
    for ch in name:
        if ch.isalnum() or ch in [" ", "-"]:
            char_list.append(ch)
    name = "".join(char_list)
    return name


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
cur.execute('CREATE TABLE IF NOT EXISTS object(id INTEGER PRIMARY KEY AUTOINCREMENT, name, sub_type, geometry, min_lng DOUBLE, min_lat DOUBLE, max_lng DOUBLE, max_lat DOUBLE, country)')

'''получаем список файлов с данными'''
dat_files = os.listdir(dirname)
'''перебираем файлы с данными'''
for dat_file in dat_files:
    if dat_file.split('.').pop() != 'sqlite':
        continue
    print "Processing file %s" % (dirname + '/' + dat_file)    
    conn2 = db.connect(dirname + '/' + dat_file)
    cur2 = conn2.cursor()
    obj_count = 0    
    res = cur2.execute("select name, sub_type, AsGeoJSON(Geometry) as geometry from pg_landuse where name not NULL and Geometry not NULL")
    for row in res:
        obj_count += 1        
        name = filterString(row[0])        
        sub_type = row[1]
        geometry = row[2]
        country = dat_file.split('-')[0]
        if len(name) == 0:
            continue
        print 'Processing object: %s (%i)' % (name, obj_count)
        sql = "SELECT MbrMinX(GeomFromGeoJSON('"+ geometry +"')) as min_lng, MbrMinY(GeomFromGeoJSON('"+ geometry +"')) as min_lat, MbrMaxX(GeomFromGeoJSON('"+ geometry +"')) as max_lng, MbrMaxY(GeomFromGeoJSON('"+ geometry +"')) as max_lat"
        res = cur.execute(sql)
        for rec in res:
            min_lng = rec[0]
            min_lat = rec[1]
            max_lng = rec[2]
            max_lat = rec[3]
                
        sql = "INSERT INTO object (name, sub_type, geometry, min_lng, min_lat, max_lng, max_lat, country) VALUES('"+name+"', '"+sub_type+"', '"+geometry+"'," + str(min_lng) + "," + str(min_lat) + "," + str(max_lng) + "," + str(max_lat) + ", '" + country + "')"
        #print sql
        cur.execute(sql)
    conn.commit()
    res = cur2.execute("select name, sub_type, AsGeoJSON(Geometry) as geometry from pg_natural where name not NULL and Geometry not NULL")
    for row in res:
        obj_count += 1        
        name = filterString(row[0])
        sub_type = row[1]
        geometry = row[2]
        country = dat_file.split('-')[0]
        if len(name) == 0:
            continue
        print 'Processing object: %s (%i)' % (name, obj_count)
        sql = "SELECT MbrMinX(GeomFromGeoJSON('"+ geometry +"')) as min_lng, MbrMinY(GeomFromGeoJSON('"+ geometry +"')) as min_lat, MbrMaxX(GeomFromGeoJSON('"+ geometry +"')) as max_lng, MbrMaxY(GeomFromGeoJSON('"+ geometry +"')) as max_lat"
        res = cur.execute(sql)
        for rec in res:
            min_lng = rec[0]
            min_lat = rec[1]
            max_lng = rec[2]
            max_lat = rec[3]
                
        sql = "INSERT INTO object (name, sub_type, geometry, min_lng, min_lat, max_lng, max_lat, country) VALUES('"+name+"', '"+sub_type+"', '"+geometry+"'," + str(min_lng) + "," + str(min_lat) + "," + str(max_lng) + "," + str(max_lat) + ", '" + country + "')"
        #print sql
        cur.execute(sql)
    conn.commit()      
    cur2.close()
    conn2.close()
cur.close()
conn.close()
