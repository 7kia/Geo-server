#!/usr/bin/python3

__author__ = 'ChuchelovSE'
# Код нахождение рек и ширины рек между 2мя юнитами
# Input: Координаты юнитов в json формате; {{'x_unit1', 'y_unit1'}, {'x_unit2', 'y_unit2'}}
# Output: json строка типа: {'name_river': {'id':10222, 'width': 200, 'x_cross1':51.05, 'y_cross1':21.05, 'x_cross2': 52.05, 'y_cross2': 22.05 }} Если река без ширины,
# возвращает -1 в значении ширины

import sqlite3
import json
import math

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



def getWidthRiver(coordinates):

    coordinatesFromJson = json.loads(coordinates)
    unit1, unit2 = coordinatesFromJson

    #connection db and include extension
    db = sqlite3.connect('poland.sqlite')
    db.enable_load_extension(True)
    db.load_extension("mod_spatialite.so.7.1.0")
    sql = db.cursor()

    # Запрос на поиск пересечения линии между юнитами и рек.
    # Переменная out выходной словарь с данными

    c = sql.execute("SELECT id, name, sub_type, AsGeoJSON(Geometry) FROM ln_waterway WHERE Crosses(MakeLine(MakePoint(?,?), MakePoint(?,?)), Geometry)", (unit1[0], unit1[1], unit2[0], unit2[1]))
    out = {}

    # Если тип найденной реки "riverbank", для нее находим ширину реки. Иначе width = -1;
    # В выдачу добавлены точки пересечения прямой между юнитами с рекой, т.е. по сути точки берега реки, через который,
    # проходит бой юнитов.

    for row in c:
        if (row[2] == 'riverbank'):
            sql.execute("SELECT AsGeoJSON(Intersection(MakeLine(MakePoint(?,?), MakePoint(?,?)), GeomFromGeoJSON(?)))", (unit1[0], unit1[1], unit2[0], unit2[1], row[3]))
            points = sql.fetchone()
            jdecode = json.loads(points[0])
            point1, point2 = jdecode['coordinates']
            width = widthRiver(point1[1], point1[0], point2[1], point2[0])
            out[row[1]] = {'id': row[0],
                           'width': width,
                           'x_cross1': point1[0],
                           'y_cross1': point1[1],
                           'x_cross2': point2[0],
                           'y_cross2': point2[1]
                           }
        else:
            if not row[1] in out:
                out[row[1]] = {'id': row[0],
                               'width': -1}
        jencode = json.dumps(out)

    return jencode

#Test
coordinates = json.dumps([[21.012357,52.499875], [20.919307,52.281555]])
a = getWidthRiver(coordinates)
print (a)