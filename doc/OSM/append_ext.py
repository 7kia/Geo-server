#!/usr/bin/env python
#coding=utf-8

import os
import sys
args = sys.argv
help1="""
	Скрипт для добавление расширения ко всем файлам в каталоге
	Принимает первым параметром имя католога а вторым нужное 
	расширение без точки
"""
print help1

if len(args) < 3:
	print 'Usage: %s <dirname> <extension>' % args[0]
	exit(1)
	
dirname = args[1].strip()
ext = args[2].strip()

files = os.listdir(dirname)
for curr_file in files:
	command = 'mv '+dirname+'/'+curr_file+' '+dirname+'/'+curr_file+'.'+ext
	print command
	os.system(command)