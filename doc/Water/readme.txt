Создание базы данных рек и каналов

1. Скачиваем OSM базу с сайта http://download.geofabrik.de по интересующей стране
Например, wget http://download.geofabrik.de/russia-latest.osm.pbf
2. Используем утилиту spatialite_osm_map для создания базы данных
Например, spatialite_osm_map -o russia-latest.osm.pbf -d russia-latest.osm.sqlite
3. Повторяем пункты 1-2 для всех интересующих стран
4. Создаем каталог(например, mkdir dat) и помещаем в него все созданные .sqlite базы
5. Запускаем скрипт создания базы:
	chmod +x mk_waterbase.py
	./mk_waterbase.py -d dat -f water.sqlite
	
Будет создана база 	water.sqlite содержащая таблицу water c полями: 
id, name, sub_type, geometry, country
