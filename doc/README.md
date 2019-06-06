# Порядок развертывания геосервиса на Python

1. Скачать и разделить на части файлы OSM. Инструкция в файле OSMOSIS/README
2. Подготовить базы данных SQLite, необходимые для сервиса маршрутов. Инструкция
в файле OSM/README.md
3. Поместить файлы полученных баз данных в нужный каталог, который указать в 
соответствующей переменной (путь к БД стоит по умолчанию в /var/www/bases/)


# (Устарел)Вариант геосервиса на node.js

Требования: установленный nodejs с модулями sqlite3,spatialite, express,
			haproxy (sudo apt-get install haproxy)

Требуемые файлы находятся в каталоге nodejs
1. Прописать в  файле geoservice_node.js путь к каталогу с базами в переменной DB_DIR
2. Выполнить

        chmod +x geoservice_node.js
        chmod +x start_nodes
        chmod +x start_haproxy
        chmod +x stop

3. Запустить серверы: ./start_nodes
4. Запустить haproxy: ./start_haproxy

    Пример запроса маршрута: 
    
        http://127.0.0.1:8000/route?data=50.40644569609247,30.494613647460938,50.476632430319945,30.56842803955078,ukraine-latest.osm,4
    
    Для нагрузочного тестирования:
    
        chmod +x ab_run
        ./ab_run 

5. Останов серверов: ./stop
 

