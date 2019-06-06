#!/usr/bin/env python
# coding=utf-8

from pyspatialite import dbapi2 as db
#import sqlite3
import sys
import math
import getopt

output_len = 0;
need_update = False

try:
	optlist, args = getopt.getopt(sys.argv[1:],'suf:m:')
	db_file = filter(lambda item: item[0]=='-f',optlist)[0][1]
	m = int(filter(lambda item: item[0]=='-m',optlist)[0][1])
	if m in [1,2,3,4]:
		scale = math.pow(2,m)
	else:
		scale = 1
	
except:
	print 'Usage: %s [-s] [-u] -f <db_filename> -m <mode>' % sys.argv[0]
	exit(1)
	
help1="""
	Скрипт для создания сетки для ускорения поиска узла а графе, представленном
	как база SQLite. Принимает параметром имя файла базы и номер режима разбиения.
	Номер режима разбиения - целое число m . 2 в степени m обозначает во сколько 
	раз размер ячейки меньше градуса. m должно быть в пределах [1-4]
"""

if '-s' not in map(lambda item: item[0],optlist):
	print help1

if '-u' in map(lambda item: item[0],optlist):
	need_update = True
	
	
#print progress
def print_progress(message,count,size,index=None):
	progress = float(count)/size*100
	if index != None:
		sys.stdout.write("%s: %d%%  (index=%d)  \r" % (message, progress,index) )
		sys.stdout.flush()
	else:
		sys.stdout.write("%s: %d%%  \r" % (message, progress) )
		sys.stdout.flush()

		
#подключение к БД
def connect_db(db_file):
	#print db_file
	conn = db.connect(db_file)
	# creating a Cursor
	cur = conn.cursor()
	return conn,cur


#загрузка узлов
def load_nodes(cur, currentDb):
	sql = 'SELECT count(*) FROM ' + currentDb
	res = cur.execute(sql)
	for row in res:
		size = row[0]

	nodes = []
	sql = 'select node_id, Y(geometry) as lat, X(geometry) as lng from ' + currentDb
	res = cur.execute(sql)

	count = 0
	for row in res:
		count = count + 1
		if count % 10000.0 == 0:
			print_progress('',count,size)
		nodes.append({'node_id':row[0], 'lat': row[1], 'lng':row[2], 'sector': latlng2sector(row[1],row[2])})
	return nodes


#вычисление сектора по координатам
def latlng2sector(lat,lng):
	global scale
	row = math.floor(scale*(lat + 90.0))
	col = math.floor(scale*(lng + 180))
	sector = row * 360 * scale + col
	return sector

def column_exists(cur,table,column):
	sql = "SELECT " + column + " from " + table + " LIMIT 1"
	has_connected = True
	try:
		res = cur.execute(sql)
	except:
		has_connected = False
	else:
		has_connected = True
	return has_connected

def table_exists(cur,table):
	sql = "SELECT * from "+table+" LIMIT 1"
	table_exists = True
	try:
		res = cur.execute(sql)
	except:
		table_exists = False
	else:
		table_exists = True
	return table_exists


#добавление столбца в таблицу
def add_column(cur, table, column):
	sql = 'ALTER TABLE '+table+' ADD COLUMN ' + column + ' INTEGER DEFAULT 0'
	print 'Add column "'+column+'"...'
	try:
		res = cur.execute(sql)
	except:
		print 'column "'+column+'" may be exists, try set it to 0'
		try:
			sql = 'UPDATE '+table+' SET '+column+'=0'
			res = cur.execute(sql)
			print 'Setup done'
		except:
			print 'Error during execution of sql query. Exiting...'
			exit(1)	
	else:
		print 'Done'
		return

#запись данных значения сектора в таблицу узлов
def store_sector(nodes, cur, conn, currentDb):
	BUFFER_SIZE = 1000
	num_rows = len(nodes)
	try:
		print 'Begin change database...'
		offset = 0
		while offset < num_rows:
			for node in nodes[offset:offset+BUFFER_SIZE]:
				sql = 'UPDATE ' + currentDb + ' SET sector=' + str(node['sector']) + ' WHERE node_id=' + str(node['node_id'])
				cur.execute(sql)
			conn.commit()
			offset = offset + BUFFER_SIZE
			if offset % 10000.0 == 0:
				print_progress('Progress: ', offset, num_rows)
		print 'Done'
	except:
		print 'Error during execution of sql query. Exiting...'
		return
	
#создание индекса
def create_index(cur, table, column):
	sql = 'DROP INDEX IF EXISTS ' + column + '_i'
	print 'Dropping index...'
	try:
		cur.execute(sql)
	except:
		print 'Error during execution of sql query. Exiting...'
		exit(1)
	else:
		print 'Done'
	sql = 'CREATE INDEX IF NOT EXISTS '+column + '_i' +' ON ' + table + '(' + column + ')'
	print 'Create index "'+column+'_i "...'
	try:
		cur.execute(sql)
	except:	
		print 'Error during execution of sql query. Exiting...'
		exit(1)	
	else:
		print 'Done'
		return
		
pathDatabases = ["rails", "roads"]
pathNodeDatabases = ["rails_nodes", "roads_nodes"]

conn, cur = connect_db(db_file)

for currentDb in pathNodeDatabases:
	if not table_exists(cur, currentDb):
		print 'File "%s" is not rails net database' % db_file
		exit(0)

for currentDb in pathNodeDatabases:
	print('===============================================')
	print('Handle \'' + currentDb + '\'')
	print('===============================================')
	if need_update:
		add_column(cur, currentDb, 'sector')
	else:
		if column_exists(cur, currentDb, 'sector'):
			print '%s file already processed' % db_file
			exit(0)
		else:
			add_column(cur, currentDb, 'sector')


	print 'Load nodes...'
	nodes = load_nodes(cur, currentDb)
	print ' Done'

	print 'nodes: %d' % (len(nodes))
	if len(nodes) == 0:
		print 'Graph is empty. Exiting...'
		exit(1)

	if '-s' not in map(lambda item: item[0],optlist):
		answer = raw_input('Save sector numbers to the database? (y/n)')
		if answer.lower()[0] == 'y':
			store_sector(nodes, cur, conn, currentDb)
			create_index(cur, currentDb, 'sector')
		else:
			exit(0)
	else:
		store_sector(nodes, cur, conn, currentDb)
		create_index(cur, currentDb, 'sector')#'roads_nodes'

