from cgi import escape
from urlparse import parse_qs
# importing pyspatialite
from pyspatialite import dbapi2 as db
import time
import os
import math
import sys
import json

from wsgi_app.databaseFileSearcher import DatabaseFileSearcher
from wsgi_app.roadSearcher import RoadSearcher

abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)
import config

DB_DIR = config.DB_DIR
MIN_SIZE_DEFAULT = 1000


def findNearest(environ):
    begin = time.clock()

    d = parse_qs(environ['QUERY_STRING'])
    data = d['data'][0].split(',')
    # print data
    start_lat = float(data[0])
    start_lng = float(data[1])
    end_lat = float(data[2])
    end_lng = float(data[3])
    filename = data[4]
    scale = int(data[5])
    before_searchBestDbFile = time.clock()
    db_file = DatabaseFileSearcher.search_best_db_file_by_two_points(
        (start_lat, start_lng), (end_lat, end_lng),
        filename
    )
    # print 'using db_file='+db_file
    after_searchBestDbFile = time.clock()
    route = getRoute((start_lat, start_lng), (end_lat, end_lng), db_file, scale)
    after_getRoute = time.clock()

    print 'begin=%f, before_searchBestDbFile=%f, after_searchBestDbFile=%f, after_getRoute=%f' % (begin, before_searchBestDbFile, after_searchBestDbFile, after_getRoute)
    print 'time_for_find_files=%s  time_for_find_route=%f' % (after_searchBestDbFile - before_searchBestDbFile, after_getRoute - after_searchBestDbFile)

    return route


def application(environ, start_response):
    return RoadSearcher.handle_request(environ, start_response, findNearest)


def getRoute(start,end,db_file,scale):
    # creating/connecting the db
    #print 'db_file='+db_file
    print DB_DIR + db_file
    conn = db.connect(DB_DIR + db_file)
    # creating a Cursor
    cur = conn.cursor()
    id_start = getNodeId(cur,start,scale)
    id_end = getNodeId(cur,end,scale)
    sql = 'SELECT AsGeoJSON(geometry) AS geometry FROM rails_net WHERE NodeFrom='+str(id_start)+' AND NodeTo='+str(id_end)+' LIMIT 1'
    try:
        rs = cur.execute(sql)
        for row in rs:
            result = row[0]
        cur.close()
        conn.close()
        return result
    except Exception as exception:
        return json.dumps(str(exception), sort_keys=True, indent=4)

#+'='+DB_DIR+'='+config.HOSTNAME

#calculating sector by coordinates
def latlng2sector(lat,lng,scale):
    row = math.floor(scale*(lat + 90.0))
    col = math.floor(scale*(lng + 180))
    sector = row * 360 * scale + col
    return sector

def getNodeId(cur,point,scale):
    #sql = 'select node_id, MIN(Distance(geometry,MakePoint('+str(start[1])+','+str(start[0])+'))) as rast from roads_nodes'
    sector = latlng2sector(point[0],point[1],scale)
    sql = 'select * from sqlite_master where type = \'table\''
    rs = cur.execute(sql)
    print rs
    print 'sector=%i' % sector
    try:
        sql = 'select node_id, MIN(Pow(('+str(point[1])+'-X(geometry)),2) +Pow(('+str(point[0])+'-Y(geometry)),2)) as rast from rails_nodes where connected=1 and sector='+str(sector)
        rs = cur.execute(sql)
    except:
        print 'Except: without using "connected" '
        try:
            sql = 'select node_id, MIN(Pow(('+str(point[1])+'-X(geometry)),2) +Pow(('+str(point[0])+'-Y(geometry)),2)) as rast from rails_nodes where sector='+str(sector)
            rs = cur.execute(sql)
        except:
            print 'Ecxcept: without using "connected and "sector"'
            sql = 'select node_id, MIN(Pow(('+str(point[1])+'-X(geometry)),2) +Pow(('+str(point[0])+'-Y(geometry)),2)) as rast from rails_nodes'
            rs = cur.execute(sql)
    node_id = 0
    for row in rs:
        node_id = row[0]
    return node_id




def isInside(filename,point1,point2):
    boundary = getBoundaryFromName(filename)
    if isPointInside(boundary, point1) and isPointInside(boundary, point2):
        return True
    return False

def isPointInside(b, point):
    if len(b) == 0:
        return True
    if point[0] <= b['top'] and point[0] >= b['bottom'] and point[1] <= b['right'] and point[1] >= b['left']:
        return True
    return False

def getBoundaryFromName(name):
    boundary = {}
    ls1 = name.split('[')
    if len(ls1) < 2:
        return boundary
    ls = ls1[1].split(']')[0].split(',')
    if len(ls) < 4:
        return boundary
    boundary['top'] = float(ls[0])
    boundary['left'] = float(ls[1])
    boundary['bottom'] = float(ls[2])
    boundary['right'] = float(ls[3])
    return boundary

def getAreaSize(filename):
    boundary = getBoundaryFromName(filename)
    if len(boundary) == 0:
        return MIN_SIZE_DEFAULT
    size = boundary['top'] - boundary['bottom']
    return size
