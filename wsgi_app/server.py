from wsgiref import simple_server

import falcon
import land
import listcity_lite
import nearest
import nearest_railway
import route
import route_railway
import water

app = falcon.API()

app.add_route('/route', route.route)#
app.add_route('/water', water.waterObject)#
app.add_route('/route_railway', route_railway.routeRailway)#
app.add_route('/nearest_railway', nearest_railway.nearestRailway)#
app.add_route('/nearest', nearest.nearest)#

# TODO: may be not work because not found landscape object
app.add_route('/land', land.land)#http://localhost:8081/land?data=50.49302393675547,30.44174194335937
app.add_route('/incity', listcity_lite.listCityLite)#http://localhost:8081/incity?data=50.451070142811915,30.517959594726562,city.sqlite

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8081, app)
    httpd.serve_forever()
    #
