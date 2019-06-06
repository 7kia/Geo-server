#!/usr/bin/env python
# coding=utf-8

import sys
import os
import getopt
from pyspatialite import dbapi2 as db

help1 = """
        Скрипт создания базы данных рек и каналов
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
    if not name:
        return 'noname'
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
cur.execute('CREATE TABLE IF NOT EXISTS water(id INTEGER PRIMARY KEY AUTOINCREMENT, name, sub_type, geometry, country)')

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
    res = cur2.execute("SELECT name, sub_type, AsGeoJSON(Geometry) AS geometry FROM ln_waterway WHERE Geometry NOT NULL")
    for row in res:
        obj_count += 1        
        name = filterString(row[0])        
        sub_type = row[1]
        geometry = row[2]
        country = dat_file.split('-')[0]
        if len(name) == 0:
            continue        
        
        sql = "INSERT INTO water (name, sub_type, geometry, country) VALUES('"+name+"','"+sub_type+"','"+geometry+"','" + country + "')"
        #print sql
        cur.execute(sql)
    conn.commit()
    res = cur2.execute("SELECT name, sub_type, AsGeoJSON(Geometry) AS geometry FROM pg_waterway WHERE Geometry NOT NULL")
    for row in res:
        obj_count += 1        
        name = filterString(row[0])
        sub_type = row[1]
        geometry = row[2]
        country = dat_file.split('-')[0]
        if len(name) == 0:
            continue
               
        sql = "INSERT INTO water (name, sub_type, geometry, country) VALUES('"+name+"','"+sub_type+"','"+geometry+"','"  + country + "')"
        #print sql
        cur.execute(sql)
    conn.commit()      
    cur2.close()
    conn2.close()
cur.close()
conn.close()
