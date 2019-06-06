#!/usr/bin/env python
# coding=utf-8

import sys
import os
import getopt
from pyspatialite import dbapi2 as db

help1 = """
		Скрипт создания базы данных секторов, принадлежащих городам
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
    optlist, args = getopt.getopt(sys.argv[1:], 'vs:d:f:')
    # print optlist
    dirname = filter(lambda item: item[0] == '-d', optlist)[0][1]
    db_file = filter(lambda item: item[0] == '-f', optlist)[0][1]
    scale = int(filter(lambda item: item[0] == '-s', optlist)[0][1])
except:
    print 'Usage %s [-v] -d <dat_files_dir> -s <scale> -f <db_file>' % sys.argv[0]
    exit(1)

if '-v' in map(lambda item: item[0], optlist):
    print help1

conn = db.connect(db_file)
# creating a Cursor
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS citysector(sector INTEGER, city_name, city_lastname)')
cur.execute('CREATE TABLE IF NOT EXISTS scaleparam(scl INTEGER)')
cur.execute('DELETE FROM scaleparam')
cur.execute('INSERT INTO scaleparam (scl) VALUES(' + str(scale) + ')')


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
    for line in lines:
        city_data = line.split('|')
        city_name = city_data[0]
        city_lastname = city_data[1]
        city_geom = city_data[2]
        city_count += 1
        print 'Processing city: %s (%i/%i)' % (city_name, city_count, lines_count)
        '''перебираем сектора'''
        for row in range(0, 180 * scale - 1):
            for col in range(0, 360 * scale - 1):
                lat1 = row / scale - 90
                lat2 = lat1 + 1 / scale
                lng1 = col / scale - 180
                lng2 = lng1 + 1 / scale
                sector_geojson = '{"type":"Polygon", "coordinates": [[[' + str(lng1) + ',' + str(lat1) + '],[' + str(
                    lng2) + ',' + str(lat1) + '],[' + str(lng2) + ',' + str(lat2) + '],[' + str(lng1) + ',' + str(
                    lat2) + '],[' + str(lng1) + ',' + str(lat1) + ']]]}'
                sector = row * 360 * scale + col
                sql = "SELECT Intersects(GeomFromGeoJSON('" + sector_geojson + "'),GeomFromGeoJSON('" + city_geom + "')) as result"
                res = cur.execute(sql)
                for rec in res:
                    sector_in_city = rec[0]
                if sector_in_city == 1:
                    sql = 'INSERT INTO citysector (sector, city_name, city_lastname) VALUES(' + sector + ',"' + city_name + '","' + city_lastname + '")'
                    cur.execute(sql)
    f.close()
cur.close()
conn.close()
