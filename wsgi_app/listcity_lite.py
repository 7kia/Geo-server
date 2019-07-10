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
import json

DB_DIR = config.DB_DIR
PLACES_DB_FILE = 'places.sqlite'
CITY_DB_FILE = 'city.sqlite'
MIN_RAST = 0.05

def application(environ, start_response):
    status = '200 OK'
    db_file = CITY_DB_FILE
    listcity = getListCity(db_file)
    if listcity != None:
        response = json.dumps({'city_list':listcity})
        #response = '{"city_list":[' + ','.join(listcity) + ']}'
        #response = '{"incity":true, "city_name":"' + city[0] + '", "city_lastname":"' + city[1] + '"}'
    else:
        response = '{"city_list":[]}'
    response_headers = [('Content-type', 'text/html; charset=utf-8'), ('Access-Control-Allow-Origin', '*')]
    start_response(status, response_headers)
    return [response]

#определение пересечения точки с полигоном города и возврат в случае пересечения имени города и его полигона
def getListCity(db_file):
    conn = db.connect(DB_DIR + db_file)
    cur = conn.cursor()
    sql = "SELECT id, city_name, city_lastname, country, min_lat, min_lng, max_lat, max_lng FROM city ORDER BY city_name"
    res = cur.execute(sql)
    citylist = []
    for rec in res:
        id = rec[0]
        city_name = rec[1].encode('utf-8')
        city_lastname = rec[2].encode('utf-8')
        city_country = rec[3].encode('utf-8')
        min_lat = rec[4]
        min_lng = rec[5]
        max_lat = rec[6]
        max_lng = rec[7]
        avg_lat = (min_lat + max_lat)/2
        avg_lng = (min_lng + max_lng)/2
        #cityitem = '{"incity":true, "city_name":"' + city_name + '", "city_lastname":"' + city_lastname + '", "city_country":"' + city_country + '", "id":' + str(id)+ ', "avg_lat":'+str(avg_lat)+', "avg_lng":' + str(avg_lng) + "min_lat"+ '}'
        cityitem = {}
        cityitem['incity'] = 'true'
        cityitem['cityname'] = city_name
        cityitem['city_lastname'] = city_lastname
        cityitem['city_country'] = city_country
        cityitem['id'] = id
        cityitem['avg_lat'] = avg_lat
        cityitem['avg_lng'] = avg_lng
        cityitem['min_lat'] = min_lat
        cityitem['min_lng'] = min_lng
        cityitem['max_lat'] = max_lat
        cityitem['max_lng'] = max_lng
        citylist.append(cityitem)
    cur.close()
    conn.close()
    if len(citylist) == 0:
        return None
    else:
        return citylist

#нахождение населенных пунктов центры которых удалены на расстояние не более заданного от заданной точки
#в случае нахождения возврат названия и геометрии ближайшего населенного пункта
def getPlace(point_lat, point_lng):
    conn = db.connect(DB_DIR + PLACES_DB_FILE)
    cur = conn.cursor()
    sql = "SELECT id, place_name, place_type, geometry, lat, lng, country, Distance(GeomFromGeoJSON(geometry), MakePoint("+str(point_lng)+","+str(point_lat)+")) as rast from place where Distance(GeomFromGeoJSON(geometry), MakePoint("+str(point_lng)+","+str(point_lat)+")) < " + str(min_rast)
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