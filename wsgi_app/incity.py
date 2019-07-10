#coding=utf-8
from cgi import parse_qs, escape
# importing pyspatialite
from pyspatialite import dbapi2 as db
import time
import os
import math

import sys
abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)
import config

DB_DIR = config.DB_DIR
CITY_DB_FILE = 'city.sqlite'
PLACES_DB_FILE = 'places.sqlite'
MIN_RAST = 0.05

def application(environ, start_response):
    status = '200 OK'
    d = parse_qs(environ['QUERY_STRING'])
    data = d['data'][0].split(',')
    #print data
    point_lat = float(data[0])
    point_lng = float(data[1])
    db_file = CITY_DB_FILE
    city = getCity(point_lat, point_lng, db_file)
    #print city
    if city != None:
        response = '{"incity":true, "city_name":"' + city[0] + '", "city_lastname":"' + city[1] + '","city_geometry":' + city[2] + ',"id":'+ str(city[3]) +'}'
        #response = '{"incity":true, "city_name":"' + city[0] + '", "city_lastname":"' + city[1] + '"}'
    else:
        response = '{"incity":false}'
    response_headers = [('Content-type', 'text/html; charset=utf-8'), ('Access-Control-Allow-Origin', '*')]
    start_response(status, response_headers)
    return [response]

#определение пересечения точки с полигоном города и возврат в случае пересечения имени города и его полигона
def getCity(point_lat, point_lng, db_file):
    conn = db.connect(DB_DIR + db_file)
    cur = conn.cursor()
    sql = "SELECT id, geometry, city_name, city_lastname FROM city WHERE min_lng <= " + str(point_lng) + " AND min_lat <= " + str(point_lat) + " AND max_lng  >= " + str(point_lng) + " AND max_lat >= " + str(point_lat)
    id = -1
    res = cur.execute(sql)
    for rec in res:
        id = rec[0]
        city_geometry = rec[1].strip().encode('utf-8')
        city_name = rec[2].encode('utf-8')
        city_lastname = rec[3].encode('utf-8')
        #print 'city_name: '+city_name
        point_geometry = '{"type":"Point","coordinates":[' + str(point_lng) + ',' + str(point_lat) + ']}'
        if id != -1:
            sql = "SELECT Intersects(GeomFromGeoJSON('" + city_geometry + "'),GeomFromGeoJSON('" + point_geometry + "'))"
            res2 = cur.execute(sql)
            in_city = 0
            for rec2 in res2:
                print 'rec=' + str(rec2)
                in_city = rec2[0]
                if in_city == 1:
                    cur.close()
                    conn.close()
                    return (city_name, city_lastname, city_geometry, id)
    cur.close()
    conn.close()
    return None

#нахождение населенных пунктов центры которых удалены на расстояние не более заданного от заданной точки
#в случае нахождения возврат названия и геометрии ближайшего населенного пункта
def getPlace(point_lat, point_lng):
	conn = db.connect(DB_DIR + PLACES_DB_FILE)
	cur = conn.cursor()
	sql = "SELECT id, place_name, place_type, geometry, lat, lng, country, Distance(GeomFromGeoJSON(geometry), MakePoint("+str(point_lng)+","+str(point_lat)+")) as rast from place where Distance(GeomFromGeoJSON(geometry), MakePoint("+str(point_lng)+","+str(point_lat)+")) < " + str(MIN_RAST)
	res = cur.execute(sql)
	places = []
	for rec in res:
		place = {}
		place['id'] = rec[0]
		place['place_name'] = rec[1].encode('utf-8')
		place['place_type'] = rec[2].encode('utf-8')
		place['place_geometry'] = rec[3].encode('utf-8')
		place['rast'] = rec[7]
		places.append(place)
	if len(places) == 0:
		return None
	else:
		places.sort(key = lambda x: x['rast'])
		return (places[0]['place_name'], places[0]['place_type'], places[0]['place_geometry'])