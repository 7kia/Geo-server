#!/usr/bin/env python
#coding=utf-8

help1="""
		Скрипт для пакетного запуска скриптов для создания сетки для ускорения 
		поиска узла а графах, представленных как базы SQLite. Принимает 
		параметром имя каталога и номер режима разбиения в пределах [1-4].
		Номер режима разбиения - целое число m . 2 в степени m 
		обозначает во сколько раз размер ячейки меньше градуса
"""

import os
import sys
import getopt

need_update = False

try:
	optlist, args = getopt.getopt(sys.argv[1:],'sud:m:')
	dirname = filter(lambda item: item[0]=='-d',optlist)[0][1]
	m = int(filter(lambda item: item[0]=='-m',optlist)[0][1])
	if m not in [1,2,3,4]:
		m = 1

except:
	print 'Usage: %s [-s] [-u] -d <dir_name> -m <mode>' % sys.argv[0]
	exit(1)
	
if '-s' not in map(lambda item: item[0],optlist):
	print help1
	
if '-u' in map(lambda item: item[0],optlist):
	need_update = True

count = 0
print 'Processing file in %s...' % dirname
sqlite_files = os.listdir(dirname)
print 'Found '+str(len(sqlite_files))+' files:'

for filename in sqlite_files:
	count += 1
	print 'Processing file %s (%d / %d)' % (filename,count,len(sqlite_files))
	if need_update:
		command = './mkgrid3.py -s -u -f ' + dirname+'/'+filename + ' -m ' + str(m)
		# command_roads = './mkgrid3_roads.py -s -u -f ' + dirname+'/'+filename + ' -m ' + str(m)
	else:
		command = './mkgrid3.py -s -f ' + dirname+'/'+filename + ' -m ' + str(m)
		# command_roads = './mkgrid3_roads.py -s -f ' + dirname+'/'+filename + ' -m ' + str(m)
	os.system(command)
	# os.system(command_roads)
	#print command
	
print 'Done'
