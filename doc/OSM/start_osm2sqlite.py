#!/usr/bin/env python
#coding=utf-8

help1="""
		Скрипт для создания баз SQLite3(Spatialite) из всех
		файлов в каталогах /osm и /pbf. Файлы .sqlite будут
		созданы в каталоге /sqlite
"""

import os
import sys

args= sys.argv

if '-s' not in args:
	print help1

count = 0
print 'Processing OSM...'
osm_files = os.listdir('osm')
print 'Found '+str(len(osm_files))+' files:'
for filename in osm_files:
	print filename
for filename in osm_files:
	count += 1
	print 'Processing file %s (%d / %d)' % (filename,count,len(osm_files))
	command = './osm2sqlite.sh ' + filename
	os.system(command)

count = 0
print 'Processing PBF...'
pbf_files = os.listdir('pbf')
print 'Found '+str(len(pbf_files))+' files:'
for filename in pbf_files:
	print filename
for filename in pbf_files:
	count += 1
	print 'Processing file %s (%d / %d)' % (filename,count,len(pbf_files))
	command = './pbf2sqlite.sh ' + filename
	os.system(command)