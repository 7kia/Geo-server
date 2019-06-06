#!/usr/bin/env python
#coding=utf-8
# скрипт для разбиения файла OSM (.osm OR .pbf) на меньшие части
# с требуемой глубиной
# при глубине 1 заданная область делится на 9 равных частей 
# при глубине 2 каждая из частей также делится на 9 частей и т.д.

import os
import sys
import getopt

count = 0
depth = 0

help1="""
		Скрипт разбиения OSM или PBF файла нак части с требуемой глубиной
		Принимает имя файла вернюю, нижнюю, левую и правые границы и глубину
		разбиения. при глубине 1 заданная область делится на n**2 равных частей, 
		при глубине 2 каждая из частей также делится на n**2 частей и т.д.
"""

try:
	optlist, args = getopt.getopt(sys.argv[1:],'sf:t:l:b:r:d:n:')
	print optlist
	infile = filter(lambda item: item[0]=='-f',optlist)[0][1]
	top = float(filter(lambda item: item[0]=='-t',optlist)[0][1])
	left = float(filter(lambda item: item[0]=='-l',optlist)[0][1])
	bottom = float(filter(lambda item: item[0]=='-b',optlist)[0][1])
	right = float(filter(lambda item: item[0]=='-r',optlist)[0][1])
	depth = float(filter(lambda item: item[0]=='-d',optlist)[0][1])
	n = int(filter(lambda item: item[0]=='-n',optlist)[0][1])

except:
	print 'Usage %s [-s] -f <osm_file> -t <top> -l <left> -b <bottom> -r <right> -d <depth> -n <n>' % sys.argv[0]
	exit(1)

if '-s' not in map(lambda item: item[0],optlist):
	print help1
				   
				   
#формируем словарь описания области карты
def get_area():
	global depth,top,left,bottom,right,infile
	area = {}
	area['top'] = top
	area['left'] = left
	area['bottom'] = bottom
	area['right'] = right
	area['depth'] = depth
	area['infile'] = infile
	return area

#делим область на n**2 частей и каждую часть еще на n**2 и т.д. 
# пока не достигнем нужной глубины разбиения 
def split_n(area, n):
	print area
	if area['depth'] == 0:
		return
	areas = []
	delta_width = (area['right'] - area['left'])/n
	delta_height = (area['top'] - area['bottom'])/n
	area1 = area.copy()
	for row in range(n):
		for col in range(n):
			areas.append(area.copy())
			areas[len(areas)-1]['left'] = area['left'] + col * delta_width
			areas[len(areas)-1]['top'] = area['top'] - row * delta_height
			areas[len(areas)-1]['bottom'] = area['top'] - (row + 1) * delta_height
			areas[len(areas)-1]['right'] = area['left'] + (col + 1) * delta_width
			areas[len(areas)-1]['depth'] -= 1
	for area_curr in areas:
		osm_cut_area(area_curr)
	for area_curr in areas:	
		split_n(area_curr, n)

#разбиваем OSM файл на множество мелких в соответствии с заданной глубиной
def osm_cut_area(area):
	global count, depth, n
	count += 1
	infile = area['infile']
	top = area['top']
	left = area['left']
	bottom = area['bottom']
	right = area['right']
	
	command = ' '.join(['./osm_cut_box.py', '-f',infile, '-t',str(top), '-l',str(left), '-b',str(bottom), '-r',str(right), '-s'])
	print 'Prosessing %d / %d: %s' % (count, reduce(lambda n1,n2: (n1+n2),map(lambda x: n**(2*x),range(1, int(depth)+1))), command)
	os.system(command)
	#print command
				   
split_n(get_area(), n)
