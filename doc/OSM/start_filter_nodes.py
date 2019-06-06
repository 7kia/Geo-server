#!/usr/bin/env python
#coding=utf-8

help1="""
		Скрипт для для запуска скриптов проверки связности  
		графа дорожной сети преставленного как база SQLite.
		Принимает имя каталога с файлами баз данных
"""

import os
import sys
import getopt

need_update = False

try:
	optlist, args = getopt.getopt(sys.argv[1:],'sud:')
	dirname = filter(lambda item: item[0]=='-d',optlist)[0][1]
except:
	print ('Usage: %s [-s] [-u] -d <dir_name> ' % sys.argv[0])
	exit(1)
	
if '-s' not in map(lambda item: item[0],optlist):
	print (help1)
	
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
		command = './filter_nodes.py -s -u -f ' + dirname+'/'+filename
		#command_roads = './filter_nodes_road.py -s -u -f ' + dirname+'/'+filename
	else:
		command = './filter_nodes.py -s -f ' + dirname+'/'+filename
		#command_roads = './filter_nodes_road.py -s -f ' + dirname+'/'+filename
	os.system(command)
	#os.system(command_roads)
	#print command
