I. Извлечение данных о границах городов (На Windows)
1. Скачиваем с сайта http://www.gadm.org/ базу данных нужной страны в формате 
Geopackage(Spatialite). Файл базы представляет собой sqlite базу. Расширение файла .gpkg

2. Скачиваем mod_spatialite:  
http://www.gaia-gis.it/gaia-sins/windows-bin-amd64-test/mod_spatialite-4.4.0-RC0-win-amd64.7z
Распаковываем.

3. Скачиваем spatialite_gui: 
http://www.gaia-gis.it/gaia-sins/windows-bin-amd64-test/spatialite_gui-4.4.0-RC0-win-amd64.7z

4. Запускаем spatialite_gui и открываем скачанную базу(.gpkg файл)
Выполняем запросы, вводя их в соотвествующее окно

Запросы для разных стран будут немного различаться, так как обозначение города
в базах разных стран отличается (поле TYPE_2).
Для составления запросов к базе интересующей страны нужно сначала открыть эту базу
в spatialite_gui в Windows, и посмотреть как обозначаются города, потом по аналогии с нижеприведенными
примерами составить запрос. Данные по городам содержаться в виртуальных таблицах vgpkg_<COUNTRY_ID>_adm2
В некоторых базах крупные города (например в России это Москва и Санкт-Петербург)
вынесены в уровень 1, поэтому нужно делать два запроса. Для доступа к виртуальным таблицам 
Вот примеры для некоторых стран:

RUS(Россия):
create table town2 as select NAME_2, NL_NAME_2, AsGeoJson(geom) from vgpkg_RUS_adm2 where TYPE_2 like '%Gor%' order by NAME_2
create table town1 as select  NAME_1, VARNAME_1, AsGeoJson(geom) as geom from vgpkg_RUS_adm1 where ENGTYPE_1 like '%City%'

DEU(Германия):
create table town2 as select NAME_2, NL_NAME_2, AsGeoJson(geom) from vgpkg_DEU_adm2 where TYPE_2 like '%Stadt%' order by NAME_2

UKR(Украина):
create table town2 as select NAME_2, NL_NAME_2, AsGeoJson(geom) from vgpkg_UKR_adm2 where TYPE_2 like '%Mist%' order by NAME_2
create table town1 as select  NAME_1, VARNAME_1, AsGeoJson(geom) as geom from vgpkg_UKR_adm1 where ENGTYPE_1 like '%City%'

POL(Польша):
create table town2 as select NAME_2, NL_NAME_2, AsGeoJson(geom) from vgpkg_POL_adm2 where ENGTYPE_2 like '%City%' order by NAME_2

Этими запросами мы получаем нужные нам данные из виртуальных таблиц
и создаем из них обычные таблицы.

5. В консоли заходим в каталог с распакованным mod_spatialite 
Запускаем sqlite3. Запустится интерпретатор команд sqlite3. 
Должно появиться приглашение sqlite>
Даем команды (команды начинаются с точки, запросы вводятся без точки и заканчиваются точкой с запятой):
.open <файл_базы> (например RUS_adm.gpkg)
.load mod_spatilaite
.output <файл_для_результатов_запроса>
SQL_запрос; (может быть не один, результаты последующих добавятся в конец файла)
select * from town1; (при необходимости)
select * from town2;
.quit

В файле <файл_для_результатов_запроса> будут построчно для каждого города записаны
его данные, например:
Abakan|Абака́н|{"type":"MultiPolygon","coordinates":[[[[91.45278930664067,53.70172119140624],[91.44386291503916,53.69742965698241],[91.42509460449224,53.6989135742188],[91.43031311035167,53.71451568603515],[91.43953704833984,53.71738052368175],[91.4507827758789,53.71098709106445],[91.45278930664067,53.70172119140624]]]]}
Abdulino|Абду́лино|{"type":"MultiPolygon","coordinates":[[[[53.64326095581054,53.64121627807622],[53.64043807983404,53.63984680175792],[53.63545989990245,53.64115142822276],[53.62926864624034,53.64559173583979],[53.62684249877929,53.65185546875011],[53.62889099121099,53.65377807617198],[53.63702774047856,53.65586471557617],[53.64294815063482,53.65501403808599],[53.64886856079107,53.65415954589854],[53.65367889404302,53.65184402465819],[53.65489196777355,53.64871215820312],[53.65250778198253,53.6447639465332],[53.6485710144043,53.64192962646495],[53.64326095581054,53.64121627807622]]]]}
...

т.е. структура каждой строки следующая:
Английское_имя|Национальное_имя (может отсутствовать)| геометрия границы в формате GeoJSON

Далее эти файлы можно парсить любым удобным способом и создавать на их основе базу данных.
Ниже приводится пример скрипта на Python. Скрипт парсит файлы имеющиеся в указанном входном каталоге,
создает базу данных с одной таблицей 'city', каждая строка таблицы содержит данные по одному городу:
английское имя, национальное имя, геометрию в виде строки GeoJSON, а также максимальные и минимальные
значения широты и долготы.

 

#!/usr/bin/env python
# coding=utf-8

import sys
import os
import getopt
from pyspatialite import dbapi2 as db

help1 = """
		Скрипт создания базы данных границ городов
"""

# print progress
def print_progress(message, count, size, index=None):
    progress = float(count) / size * 100
    if index != None:
        sys.stdout.write("%s: %d%%  (index=%d)  \r" % (message, progress, index))
        sys.stdout.flush()
    else:
        sys.stdout.write("%s: %d%%  \r" % (message, progress))
        sys.stdout.flush()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'vd:f:')
    # print optlist
    dirname = filter(lambda item: item[0] == '-d', optlist)[0][1]
    db_file = filter(lambda item: item[0] == '-f', optlist)[0][1]
except:
    print 'Usage %s [-v] -d <dat_files_dir> -f <db_file>' % sys.argv[0]
    exit(1)

if '-v' in map(lambda item: item[0], optlist):
    print help1

conn = db.connect(db_file)
# creating a Cursor
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS city(id INTEGER PRIMARY KEY AUTOINCREMENT, city_name, city_lastname, geometry, min_lng DOUBLE, min_lat DOUBLE, max_lng DOUBLE, max_lat DOUBLE)')

'''получаем список файлов с данными'''
dat_files = os.listdir(dirname)
'''перебираем файлы с данными'''
for dat_file in dat_files:
    if dat_file.split('.').pop() != 'dat':
        continue
    try:
        f = open(dirname + '/' + dat_file, 'r')
        print 'Processing file: %s' % dat_file
    except:
        print "Can't open file %s " % dat_file
        exit(1)
    lines = f.readlines()
    lines_count = len(lines)
    '''перебираем строки'''
    city_count = 0
    for line in lines:
        city_data = line.split('|')
        city_name = city_data[0].replace("'","")
        city_lastname = city_data[1].replace("'","")
        city_geometry = city_data[len(city_data)-1]
        city_count += 1
        print 'Processing city: %s (%i/%i)' % (city_name, city_count, lines_count)
        sql = "SELECT MbrMinX(GeomFromGeoJSON('"+ city_geometry +"')) as min_lng, MbrMinY(GeomFromGeoJSON('"+ city_geometry +"')) as min_lat, MbrMaxX(GeomFromGeoJSON('"+ city_geometry +"')) as max_lng, MbrMaxY(GeomFromGeoJSON('"+ city_geometry +"')) as max_lat"
        res = cur.execute(sql)
        for rec in res:
            min_lng = rec[0]
            min_lat = rec[1]
            max_lng = rec[2]
            max_lat = rec[3]
        sql = "INSERT INTO city (city_name, city_lastname, geometry, min_lng, min_lat, max_lng, max_lat) VALUES('"+city_name+"', '"+city_lastname+"', '"+city_geometry+"'," + str(min_lng) + "," + str(min_lat) + "," + str(max_lng) + "," + str(max_lat)+")"
        #print sql
        cur.execute(sql)
    conn.commit()
    f.close()
cur.close()
conn.close()

___________________________________________________________________________________________________________________________________________

II. Извлечение данных о координатах центров населенных пунктов

1. Скачиваем OSM базу с сайта http://download.geofabrik.de по интересующей стране
Например, wget http://download.geofabrik.de/russia-latest.osm.pbf
2. Используем утилиту spatialite_osm_map для создания базы данных
Например, spatialite_osm_map -o russia-latest.osm.pbf -d russia-latest.osm.sqlite
3. Повторяем пункты 1-2 для всех интересующих стран
4. Создаем каталог(например, mkdir places) и помещаем в него все созданные .sqlite базы
5. Запускаем скрипт создания базы:
	chmod +x mk_placesbase.py
	./mk_placesbase.py -d places -f places.sqlite
	
Будет создана база 	places.sqlite содержащая таблицу place c полями:
id, place_name, place_type, geometry, lat, lng, country

Пример пары строк:
1	Skarszewy	town	{"type":"Point","coordinates":[18.4456673,54.0717245]}	54.071725	18.445667	poland
2	Nowa Karczma	village	{"type":"Point","coordinates":[18.20243479999999,54.13327879999999]}	54.133279	18.202435	poland



