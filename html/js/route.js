/**модуль получения маршрутов**/
var Route =
{
	/** используемый сервис маршрутов, допустимые значения
	* 'spatialite_python', 'spatialite_nodejs'
	**/
	service: 'spatialite_python',
	geoserver_py: 'http://localhost:8080',
	geoserver_php: 'http://php_spa.loc',
	geoserver_node: 'http://127.0.0.1:8000',
	directionsService: new google.maps.DirectionsService(),
	
	/**функция получения маршрутов
    * @param start, end начальная и конечная точки в виде {lat:lat, lng:lng}
	* @param enemies объекты описывающие юнитов противника в виде [{lat:lat, lng:lng, radius:radius}, ...]
    * @param callback функция обратного вызова в которую передается результат
    **/
    getRoute: function(start,end,enemies,callback){
		if(Route.service == 'spatialite_php' ){
			Route.getRouteSpatialitePHP(start,end,callback);
		}else if(Route.service == 'spatialite_python' ){
			Route.getRouteSpatialitePython(start,end,callback);
		}else if ( Route.service == 'spatialite_nodejs' ){
            Route.getRouteSpatialiteNodeJs(start,end,callback);
        }else if ( Route.service == 'google' ) {
			Route.getRouteGoogle(start, end, callback);
		}else{
			callback([]);
		}
	},
	
    /**
    * получение маршрута от сервиса на PHP
    * @param start, end начальная и конечная точки в виде {lat:lat, lng:lng}
    * @param callback функция обратного вызова в которую передается результат
    **/
    
    getRouteSpatialitePHP: function(start,end,callback){
		var db_file = selectRegion.value;
		var params = 'data=' + [start.lat,start.lng,end.lat,end.lng,db_file,scale].join(',');
		//console.log(params);
		Ajax.sendRequest('GET', Route.geoserver_php+'/srv2.php', params, function(res) {
			//console.log(res.coordinates);
            callback(Route.reverse(res.coordinates));
		});
	},
	
    /**
    * получение маршрута от сервиса на Python
    * @param start, end начальная и конечная точки в виде {lat:lat, lng:lng}
    * @param callback функция обратного вызова в которую передается результат
    **/
    
    getRouteSpatialitePython: function(start,end,callback){
		console.log('spatialite python');
		var db_file = selectRegion.value;
		var bounds = map.getBounds();
		var params = 'data=' + [start.lat,start.lng,end.lat,end.lng,db_file, scale].join(',');
								//bounds['_southWest'].lat,bounds['_southWest'].lng,
								//bounds['_northEast'].lat,bounds['_northEast'].lng].join(',');
		console.log('params', params);
        console.log('bounds', bounds);
        console.log('db_file', db_file);
        Ajax.sendRequest('GET', Route.geoserver_py+'/route', params, function(res) {
			//console.log(res);
            callback(Route.reverse(res.coordinates));
		});
	},
		
	/**
    * получение маршрута от сервиса на NodeJs
    * @param start, end начальная и конечная точки в виде {lat:lat, lng:lng}
    * @param callback функция обратного вызова в которую передается результат
    **/
    
    getRouteSpatialiteNodeJs: function(start,end,callback){
		var db_file = selectRegion.value;
		var bounds = map.getBounds();
		var params = 'data=' + [start.lat,start.lng,end.lat,end.lng,db_file, scale].join(',');
								//bounds['_southWest'].lat,bounds['_southWest'].lng,
								//bounds['_northEast'].lat,bounds['_northEast'].lng].join(',');
		console.log(params);
		Ajax.sendRequest('GET', Route.geoserver_node+'/route', params, function(route) {
			//console.log(route);
            callback(Route.reverse(route));
		});
	},

	/**получение маршрута с сервиса маршрутов Google через JS API
	 * @param start точка куда двигаться [lat,lng]
	 * @param end точка откуда двигаться [lat,lng]
	 * @param callback объект в который передается маршрут в виде массива точек
	 **/
	getRouteGoogle: function(start,end,callback){
		var start = new google.maps.LatLng(start.lat, start.lng);
		var end = new google.maps.LatLng(end.lat, end.lng);
		var request = {
			origin: start,
			destination: end,
			//задание путевой точки
			//waypoints: [{location: new google.maps.LatLng(56.64,47.82 ), stopover: false}],
			travelMode: google.maps.TravelMode.DRIVING
		};
		Route.directionsService.route(request, function(response, status) {
			if (status == google.maps.DirectionsStatus.OK) {
				var points = response.routes[0].overview_path;
				/*
				var liters = [];
				for ( var key in points[0]){
					liters.push(key);
					if (liters.length >1 ) break;
				}
				*/
				var route = [];
				for ( var i = 0; i < points.length; i++ ){
					route.push([points[i].lat(),points[i].lng()]);
				}
				callback(route);
			}
		});
	},

    /**функция получения железнодорожных маршрутов
     * @param start, end начальная и конечная точки в виде {lat:lat, lng:lng}
     * @param enemies объекты описывающие юнитов противника в виде [{lat:lat, lng:lng, radius:radius}, ...]
     * @param callback функция обратного вызова в которую передается результат
     **/
    getRailwayRoute: function(start,end,enemies,callback){
        if(Route.service == 'spatialite_python' ){
            Route.getRailwayRouteSpatialitePython(start,end,callback);
        }else{
            callback([]);
        }
    },

    /**
     * получение железнодорожного маршрута от сервиса на Python
     * @param start, end начальная и конечная точки в виде {lat:lat, lng:lng}
     * @param callback функция обратного вызова в которую передается результат
     **/

    getRailwayRouteSpatialitePython: function(start,end,callback){
        console.log('spatialite python');
        var db_file = selectRegion.value;
        var bounds = map.getBounds();
        var params = 'data=' + [start.lat,start.lng,end.lat,end.lng,db_file, scale].join(',');
        Ajax.sendRequest('GET', Route.geoserver_py+'/route_railway', params, function(res) {
            //console.log(res);
            callback(Route.reverse(res.coordinates));
        });
    },

	/**
    * получение узла, ближайшего к заданной точке
    * @param start, end начальная и конечная точки в виде {lat:lat, lng:lng}
    * @param callback функция обратного вызова в которую передается результат
    **/
    
    getNearest: function(start, callback){
		var db_file = selectRegion.value;
		var params = 'data=' + [start.lat,start.lng,db_file,scale].join(',')
		console.log(params);
		if (Route.service == 'spatialite_python'){
			var url = Route.geoserver_py+'/nearest';
		}else if( Route.service == 'spatialite_nodejs'){
			var url = Route.geoserver_node+'/nearest';
		}
		
		
		Ajax.sendRequest('GET', url, params, function(result) {
			console.log(JSON.stringify(result));
            callback(result);
		});
	},

    getNearestRailway: function(start, callback){
        var db_file = selectRegion.value;
        var params = 'data=' + [start.lat,start.lng,db_file,scale].join(',')
        console.log("getNearestRailway: function(start, callback){ " + params);
        if (Route.service == 'spatialite_python'){
            var url = Route.geoserver_py+'/nearest_railway';
        }else if( Route.service == 'spatialite_nodejs'){
            var url = Route.geoserver_node+'/nearest';
        }


        Ajax.sendRequest('GET', url, params, function(result) {
            console.log(JSON.stringify(result));
            callback(result);
        });
    },
    /**
    * определение принадлежности точки городу
    * @param start заданная точка {lat:lat, lng:lng}
    * @param callback функция обратного вызова в которую передается результат
    **/
    
    getCity: function(start, callback){
        var db_file = 'city.sqlite';
        var params = 'data=' + [start.lat,start.lng,db_file].join(',');
        console.log(params);
        var url = Route.geoserver_py+'/incity';
        console.log(url)
        Ajax.sendRequest('GET', url, params, function(result) {
            callback(result);
        });
    },
	
	/**
	* обмен местами широты о долготы в массиве точек маршрута
	**/
	reverse: function(route){
	    var reverse_route = [];
	    for (var i = 0; i < route.length; i++){
		var dot = [route[i][1], route[i][0]];
		reverse_route.push(dot);
	    }
	    return reverse_route;
	},
	
	/**
    * определение принадлежности точки объекту ландшафта
    * @param start заданная точка {lat:lat, lng:lng}
    * @param callback функция обратного вызова в которую передается результат
    **/
    
    getLandscape: function(start, callback){
        var params = 'data=' + [start.lat,start.lng].join(',');
        console.log(params);
        var url = Route.geoserver_py+'/land';
        console.log(url)
        Ajax.sendRequest('GET', url, params, function(result) {
            callback(result);
        });
    },
    
    /**
    * определение наличия реки между двумя точками
    * @param start, end заданные точки {lat:lat, lng:lng}
    * @param callback функция обратного вызова в которую передается результат
    **/
    
    getWater: function(start, end, callback){
        var params = 'data=' + [start.lat,start.lng,end.lat,end.lng].join(',');
        console.log(params);
        var url = Route.geoserver_py+'/water';
        console.log(url)
        Ajax.sendRequest('GET', url, params, function(result) {
            console.log(JSON.stringify(result));
            callback(result);
        });
    }
    
}
