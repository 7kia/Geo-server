#!/usr/bin/env python
#coding=utf-8

#вырезка чаcти OSM файла, ограниченной полигоном заданном в файле 
# при помощи утилиты osmosis
# формат файла см.http://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format

import os
import sys
import getopt

try:
	optlist, args = getopt.getopt(sys.argv[1:],'sf:p:')
	infile = filter(lambda item: item[0]=='-f',optlist)[0][1]
	polyfile = filter(lambda item: item[0]=='-p',optlist)[0][1]
except:
	print 'Usage %s -[s] -f <osm_file> -p <poligon_file>' % sys.argv[0]
	exit(1)

help1="""
	Скрипт для вырезания части OSM файла, ограниченной полигоном 
	в отдельный OSM файл. Принимает полное имя файла OSM и файл
	содержащий описание полигона. Формат файла описания полигона
	см. http://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format
"""


if '-s' not in map(lambda item: item[0],optlist):
	print help1
	

outfile = 'cutted_'+(infile.strip()).split('/')[len((infile.strip()).split('/'))-1]
try:
	fd=open(infile,'r')
except:
	print 'File Not Found: %s' % infile
	exit(1)
else:
	fd.close()

if infile.strip().endswith('.osm'):
	intype = '--read-xml'
	outtype = '--write-xml'
	ext = '.osm'
elif infile.strip().endswith('.pbf'):
	intype = '--read-pbf'
	outtype = '--write-pbf'
	ext = '.pbf'
else:
	print 'no-supported file format'
	exit(1)
command = 'osmosis '+intype+' file='+infile+' --bounding-polygon file="'+polyfile+'" '+outtype+' file='+outfile+ext
os.system(command)