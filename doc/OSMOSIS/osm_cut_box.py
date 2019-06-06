#!/usr/bin/env python
#coding=utf-8

#вырезка чаcти OSM файла, ограниченной полигоном заданном в файле 
# при помощи утилиты osmosis
# формат файла см.http://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format

import os
import sys
import getopt

try:
	optlist, args = getopt.getopt(sys.argv[1:],'sf:t:l:b:r:')
	infile = filter(lambda item: item[0]=='-f',optlist)[0][1]
	top = filter(lambda item: item[0]=='-t',optlist)[0][1]
	left = filter(lambda item: item[0]=='-l',optlist)[0][1]
	bottom = filter(lambda item: item[0]=='-b',optlist)[0][1]
	right = filter(lambda item: item[0]=='-r',optlist)[0][1]
except:
	print 'Usage %s [-s] -f <osm_file> -t <top> -f <left> -b <bottom> -r <right>' % sys.argv[0]
	exit(1)

help1="""
	Скрипт для вырезания части OSM файла, ограниченной максимальными
	и минимальными широтой и долготой. Принимает полное имя файла OSM
	и границы: верхняя левая нижняя и правая в градусах
"""

if '-s' not in map(lambda item: item[0],optlist):
	print help1
	
try:
	fd=open(infile,'r')
except:
	print 'File Not Found: %s' % infile
	exit(1)
else:
	fd.close()
	
outfile = (infile.strip()).split('/')[len((infile.strip()).split('/'))-1] + '[' + ','.join([top,left,bottom,right])+']'
if infile.endswith('.osm'):
	intype = '--read-xml'
	outtype = '--write-xml'
	ext = '.osm'
elif infile.endswith('.pbf'):
	intype = '--read-pbf'
	outtype = '--write-pbf'
	ext = '.pbf'
else:
	print 'no-supported file format'
	exit(1)
command = 'osmosis '+intype+' file='+infile+'  --bounding-box top='+top+' left='+left+' bottom='+bottom+' right='+right+' '+outtype+' file='+outfile+ext 
os.system(command)