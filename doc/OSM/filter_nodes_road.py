#!/usr/bin/env python
# coding=utf-8

from pyspatialite import dbapi2 as db
#import sqlite3
import sys
import math
import getopt

CONNECTED_COFF = 0.8
output_len = 0;
need_update = False

try:
	optlist, args = getopt.getopt(sys.argv[1:],'suf:')
	db_file = filter(lambda item: item[0]=='-f',optlist)[0][1]
except:
	print 'Usage: %s [-s] [-u] -f <db_filename> ' % sys.argv[0]
	exit(1)
	
help1="""
	Скрипт для проверки связности графа дорожной сети представленного
	как база SQLite. Принимает параметром имя файла базы.  
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

#загрузка дорог
def load_roads(cur):
	sql = 'SELECT id, node_from, node_to FROM roads'
	res = cur.execute(sql)
	roads = []
	for row in res:
		roads.append({'id':row[0], 'node_from':row[1], 'node_to':row[2]})
	return roads

#загрузка путей
def load_paths(cur):
	sql = 'SELECT count(*) FROM roads'
	res = cur.execute(sql)
	for row in res:
		size = row[0]
	sql = 'SELECT id, node_from, node_to FROM roads'
	res = cur.execute(sql)
	paths = {}
	count = 0
	for row in res:
		count = count + 1
		if count % 10000.0 == 0:
			print_progress('',count,size)
			
		if paths.has_key(row[1]):
			paths[row[1]].append(row[2])
		else:
			paths[row[1]] = [row[2]]
		if paths.has_key(row[2]):
			paths[row[2]].append(row[1])
		else:
			paths[row[2]] = [row[1]]
	return paths
	
#загрузка узлов
def load_nodes(cur):
	sql = 'SELECT count(*) FROM roads_nodes'
	res = cur.execute(sql)
	for row in res:
		size = row[0]
	sql = 'SELECT node_id FROM roads_nodes'
	res = cur.execute(sql)
	nodes = []
	count = 0
	for row in res:
		count = count + 1
		if count % 10000.0 == 0:
			print_progress('',count,size)
		nodes.append({'node_id':row[0], 'connected':False, 'visited':False, 'wavelabel': False})
	return nodes
	
#обход графа
def walk_graph(paths, nodes, def_index=None):
	max_len_connected = 0
	best_index = 1
	if def_index == None:
		index_list = range(1,len(nodes)+1)
	else:
		index_list = [def_index]
	for index in index_list:
		oldFront = []
		newFront = []
		connected = []
		for i in range(len(nodes)): 
			nodes[i]['connected'] = False
			nodes[i]['wavelabel'] = False
		start_id = index
		nodes[start_id-1]['wavelabel'] = True
		nodes[start_id-1]['connected'] = True
		connected.append(start_id)
		oldFront.append(start_id)
		while True:
			for curr_id in oldFront:
				for conn_id in paths[curr_id]:
					if nodes[conn_id-1]['wavelabel'] == False:
						nodes[conn_id-1]['wavelabel'] = True
						newFront.append(conn_id)
						connected.append(conn_id)
						nodes[conn_id-1]['connected'] = True
			if len(newFront) == 0:
				if len(connected) >= len(nodes) * CONNECTED_COFF or def_index != None:
					print '    Found connected nodes %d, -  %d%%' % (len(connected), float(len(connected))/len(nodes)*100)
					return
				else:
					if max_len_connected < len(connected):
						max_len_connected = len(connected)
						best_index = index
					break
			oldFront = newFront
			newFront = []
			print_progress('Searching not connected nodes: ',len(connected),len(nodes),index)
	if index == len(nodes):
		walk_graph(paths, nodes, best_index)

def column_exists(cur,table,column):
	sql = "SELECT "+column+" from "+table+" LIMIT 1"
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


#добавление столбца в roads_nodes
def add_column(cur,table,column):
	sql = 'ALTER TABLE '+table+' ADD COLUMN connected INTEGER DEFAULT 1'
	print 'Add column "'+column+'"...'
	try:
		res = cur.execute(sql)
	except:
		print 'column "'+column+'" may be exists, try set it to 1'
		try:
			sql = 'UPDATE '+table+' SET '+column+'=1'
			res = cur.execute(sql)
			print 'Setup done'
		except:
			print 'Error during execution of sql query. Exiting...'
			exit(1)	
	else:
		print 'Done'
		return

#добавление столбца и запись в него данных о связности
def mark_unconnected_nodes(nodes, cur,conn):
	BUFFER_SIZE = 1000
	notconnected = []
	for node in nodes:
		if node['connected'] == False:
			notconnected.append(node['node_id'])
	number_rows = len(notconnected)
	
	try:
		print 'Begin change database...'
		offset = 0
		while offset < number_rows:
			for id in notconnected[offset:offset+BUFFER_SIZE]:
				sql = 'UPDATE roads_nodes SET connected=0 WHERE node_id=' + str(id)
				cur.execute(sql)
			conn.commit()
			offset = offset + BUFFER_SIZE
		print 'Done'
	except:
		print 'Error during execution of sql query. Exiting...'
		return	
		
		
conn, cur = connect_db(db_file)

if not table_exists(cur,'roads'):
	print 'File "%s" is not roads net database' % db_file
	exit(0)


if need_update:
	add_column(cur,'roads_nodes','connected')
else:
	if column_exists(cur,'roads_nodes','connected'):
		print '%s file already processed' % db_file
		exit(0)
	else:
		add_column(cur,'roads_nodes','connected')
	
print 'Load paths...'
paths = load_paths(cur)
print ' Done'
print 'Load nodes...'
nodes = load_nodes(cur)
print ' Done'

print 'paths: %d nodes %d' % (len(paths), len(nodes))
if len(paths) == 0 or len(nodes) == 0:
	print 'Graph is empty. Exiting...'
	exit(1)

walk_graph(paths,nodes)
print '   Done'

#answer = raw_input('Flag unconnected nodes in the database? (y/n)')
#if answer.lower()[0] == 'y':

mark_unconnected_nodes(nodes,cur,conn)
	

