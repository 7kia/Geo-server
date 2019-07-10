#coding=utf-8
from cgi import parse_qs, escape
# importing pyspatialite
from pyspatialite import dbapi2 as db
import time
import os
import math
import json

import sys
abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)
import config

DB_DIR = config.DB_DIR
DB_FILE = 'water.sqlite'

def application(environ, start_response):
    status = '200 OK'
    d = parse_qs(environ['QUERY_STRING'])
    data = d['data'][0].split(',')
    #print data
    lat1 = float(data[0])
    lng1 = float(data[1])
    lat2 = float(data[2])
    lng2 = float(data[3])
    db_file = DB_DIR + DB_FILE
    res = getWidthRiver((lat1,lng1), (lat2,lng2), db_file)
    #print res
    if res != None:
        response = json.dumps({"res":True, "waters":res})   
    else:
        response = json.dumps({"res":False})
    #print response
    response_headers = [('Content-type', 'text/html; charset=utf-8'), ('Access-Control-Allow-Origin', '*')]
    start_response(status, response_headers)
    return [response]




#расчет рстояния между двумя точками на сфере
def widthRiver(lat1, lng1, lat2, lng2) :

    pi = 3.14
    EARTH_RADIUS = 6372795
    rLat1 = lat1 * pi /180
    rLat2 = lat2 * pi /180
    rLng1 = lng1 * pi /180
    rLng2 = lng2 * pi /180

# Cosinus and sinus coordinates
    cLat1 = math.cos(rLat1)
    cLat2 = math.cos(rLat2)
    sLat1 = math.sin(rLat1)
    sLat2 = math.sin(rLat2)
    deltaLng = rLng2 - rLng1
    cDelta = math.cos(deltaLng)
    sDelta = math.sin(deltaLng)

    x = math.sqrt(pow(cLat2 * sDelta, 2) + pow(cLat1 * sLat2 - sLat1 * cLat2 * cDelta,2));
    y = (sLat1 * sLat2 + cLat1 * cLat2 * cDelta);

    width = math.atan(x / y) * EARTH_RADIUS;

    return width


# Код нахождение рек и ширины рек между 2мя юнитами
# Input: Координаты юнитов в виде пары кортежей (lat1,lng1),(lat2,lng2), файл базы данных
# Output: json строка типа: {'id_river': {'id':10222, 'width': 200, 'x_cross1':51.05, 'y_cross1':21.05, 'x_cross2': 52.05, 'y_cross2': 22.05, 'country': 'ukraine', 'geometry': 'geometry JSON string' }, ...} Если река без ширины,
# возвращает -1 в значении ширины
def getWidthRiver(unit1, unit2, db_file):

    #connection db and include extension
    conn = db.connect(db_file)
    sql = conn.cursor()

    # Запрос на поиск пересечения линии между юнитами и рек.
    # Переменная out выходной словарь с данными

    c = sql.execute("SELECT id, name, sub_type, geometry, country, blob FROM water WHERE Crosses(MakeLine(MakePoint(?,?), MakePoint(?,?)), blob)", (unit1[1], unit1[0], unit2[1], unit2[0]))
    out = {}

    # Если тип найденной реки "riverbank", для нее находим ширину реки. Иначе width = -1;
    # В выдачу добавлены точки пересечения прямой между юнитами с рекой, т.е. по сути точки берега реки, через который,
    # проходит бой юнитов.
    water = 0
    for row in c:
        water += 1
        if (row[2] == 'riverbank'):
            sql.execute("SELECT AsGeoJSON(Intersection(MakeLine(MakePoint(?,?), MakePoint(?,?)), ?))", (unit1[1], unit1[0], unit2[1], unit2[0], row[5]))
            points = sql.fetchone()
            jdecode = json.loads(points[0])
            point1, point2 = jdecode['coordinates'][0:2]
            width = widthRiver(point1[1], point1[0], point2[1], point2[0])
            out[row[0]] = {'id': row[0], 'width': width, 'x_cross1': point1[0], 'y_cross1': point1[1], 'x_cross2': point2[0], 'y_cross2': point2[1], 'country': row[4], 'geometry': json.loads(row[3])}
        else:
            out[row[0]] = {'id': row[0], 'width': -1, 'country': row[4], 'geometry': json.loads(row[3])}
    sql.close()
    conn.close()
    #print out
    if water != 0:
        return out
    else:
        return None
#Test
#coordinates = json.dumps([[21.012357,52.499875], [20.919307,52.281555]])
#water?data=21.012357,52.499875,20.919307,52.281555
#a = getWidthRiver(coordinates)
#print (a)