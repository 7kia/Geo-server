var start = null; //объект стартовой точки
var end = null; //объект конечной точки
var startPoint = null; //круг начальной точки
var endPoint = null; //круг конечной точки
var route_line = L.polyline([],{color:'blue'}).addTo(map);
var roads = []; //массив полилиний для дорог
var nodes = []; //массив точек для узлов
var enemies = []; //массив объектов вражеских полков
var enemyCircle = []; //массив кругов вражеских полков
var radius = 0.01; //радиус действия полка
var restr_nodes = []; //массив кругов запрещенных узлов
var readySpatialite = false //флаг готовности модуля spatialite
var zoom = 13; //масштаб карты
var nearestPoint = null; //маркер ближайшей точки
var nearest = null;//объект ближайшей точки
var point = null;//объект произвольной точки
var pointPoint = null;//маркер произвольной точки
var scale = 4; //масштаб сетки (1/4 градуса)
var city = null; //мультиполигон города(или объекта ландшафта)
var waters = []; //массив найденных рек

var nearestIcon = L.icon({
    iconUrl: 'img/nearest.jpg',
    iconRetinaUrl: 'img/nearest.jpg',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [12, 12]
});

/**
* установка начальной и конечной точек на карте
**/
map.on('click',function(e){
	if (getRadio('task') == 'route'){
        clearCity();
        clearWaters();
        clearPoint();
        clearNearestPoint();
        if ( start == null ){
            start = {lat:e.latlng.lat, lng:e.latlng.lng, radius:radius};
            startPoint = L.marker(L.latLng(start.lat,start.lng), {draggable:true}).addTo(map);
            startPoint.on('dragend',function(e){
                start.lat = startPoint.getLatLng().lat;
                start.lng = startPoint.getLatLng().lng;
                showRoute(start, end, enemies);
            });
        }else if ( end == null ){
            end = {lat:e.latlng.lat, lng:e.latlng.lng, radius:radius};
            endPoint = L.marker(L.latLng(end.lat,end.lng), { draggable:true}).addTo(map);
            endPoint.on('dragend',function(e){
                end.lat = endPoint.getLatLng().lat;
                end.lng = endPoint.getLatLng().lng;
                showRoute(start, end, enemies);
            });
            showRoute(start, end, enemies);
        }else{
            clearPoints();
            clearRoute();
        }
    }
    else if (getRadio('task') == 'railwayRoute'){
        clearCity();
        clearWaters();
        clearPoint();
        clearNearestPoint();
        if ( start == null ){
            start = {lat:e.latlng.lat, lng:e.latlng.lng, radius:radius};
            startPoint = L.marker(L.latLng(start.lat,start.lng), {draggable:true}).addTo(map);
            startPoint.on('dragend',function(e){
                start.lat = startPoint.getLatLng().lat;
                start.lng = startPoint.getLatLng().lng;
                showRailwayRoute(start, end, enemies);
            });
        }else if ( end == null ){
            end = {lat:e.latlng.lat, lng:e.latlng.lng, radius:radius};
            endPoint = L.marker(L.latLng(end.lat,end.lng), { draggable:true}).addTo(map);
            endPoint.on('dragend',function(e){
                end.lat = endPoint.getLatLng().lat;
                end.lng = endPoint.getLatLng().lng;
                showRailwayRoute(start, end, enemies);
            });
            showRailwayRoute(start, end, enemies);
        }else{
            clearPoints();
            clearRoute();
        }
    }
    else if (getRadio('task') == 'city'){
        clearPoints();
        clearRoute();
        clearWaters();
        point = {lat:e.latlng.lat, lng:e.latlng.lng, radius:radius};
        pointPoint = L.marker(L.latLng(point.lat,point.lng), {draggable:true}).addTo(map);
        showCity(point);
        pointPoint.on('dragend',function(e){
            point.lat = pointPoint.getLatLng().lat;
            point.lng = pointPoint.getLatLng().lng;
            clearNearestPoint();
            showCity(point);
        });
        
    } else if (getRadio('task') == 'nearest'){
        clearPoints();
        clearCity();
        clearWaters();
        clearRoute();
        point = {lat:e.latlng.lat, lng:e.latlng.lng, radius:radius};
        pointPoint = L.marker(L.latLng(point.lat,point.lng), {draggable:true}).addTo(map);
        showNearest(point);
        pointPoint.on('dragend',function(e){
            point.lat = pointPoint.getLatLng().lat;
            point.lng = pointPoint.getLatLng().lng;
            if (nearestPoint != null) map.removeLayer(nearestPoint);
            nearest = null;
            showNearest(point);
        });
    } else if (getRadio('task') == 'nearest_railway'){
        clearPoints();
        clearCity();
        clearWaters();
        clearRoute();
        point = {lat:e.latlng.lat, lng:e.latlng.lng, radius:radius};
        pointPoint = L.marker(L.latLng(point.lat,point.lng), {draggable:true}).addTo(map);
        showNearestRailway(point);
        pointPoint.on('dragend',function(e){
            point.lat = pointPoint.getLatLng().lat;
            point.lng = pointPoint.getLatLng().lng;
            if (nearestPoint != null) map.removeLayer(nearestPoint);
            nearest = null;
            showNearestRailway(point);
        });
    } else if (getRadio('task') == 'land'){
        clearPoints();
        clearRoute();
        clearCity();
        point = {lat:e.latlng.lat, lng:e.latlng.lng, radius:radius};
        pointPoint = L.marker(L.latLng(point.lat,point.lng), {draggable:true}).addTo(map);
        showLand(point);
        pointPoint.on('dragend',function(e){
            point.lat = pointPoint.getLatLng().lat;
            point.lng = pointPoint.getLatLng().lng;
            if (nearestPoint != null) map.removeLayer(nearestPoint);
            nearest = null;
            showLand(point);
        });
    }  else if (getRadio('task') == 'water'){
        clearWaters();
        clearCity();
        clearNearestPoint();
        clearPoint();
        if ( start == null ){
            start = {lat:e.latlng.lat, lng:e.latlng.lng, radius:radius};
            startPoint = L.marker(L.latLng(start.lat,start.lng), {draggable:true}).addTo(map);
            startPoint.on('dragend',function(e){
                start.lat = startPoint.getLatLng().lat;
                start.lng = startPoint.getLatLng().lng;
                showWater(start, end);
            });
        }else if ( end == null ){
            end = {lat:e.latlng.lat, lng:e.latlng.lng, radius:radius};
            endPoint = L.marker(L.latLng(end.lat,end.lng), { draggable:true}).addTo(map);
            endPoint.on('dragend',function(e){
                end.lat = endPoint.getLatLng().lat;
                end.lng = endPoint.getLatLng().lng;
                showWater(start, end);
            });
            showWater(start, end);
        }else{
            clearPoints();
            clearRoute();
        }
        
    }      
});


/**
* преобразование массива точек в массив объектов latlng
**/
function dots2latlngs(dots){
	if (dots == null) return [];
	latlngs = new Array();
	for ( var i = 0; i < dots.length; i++ ) latlngs.push(L.latLng(dots[i][0],dots[i][1]));
	return latlngs;
}//end func





/**
* запрос маршрута у сервера и отображение маршрута на карте
**/

function showRoute(start,end, enemies){
    console.log('get route');
	if (start == null || end == null) return false;
    Route.service = getRadio('service');
	clearRoute();
	showElem(preloader);
	Time.start();
	Route.getRoute(start,end,enemies,function(route){
		var timeStop = Time.stop();
		time.textContent = timeStop + ' мс';
		time.innerText = timeStop + ' мс';
		console.log(JSON.stringify(route));
		hideElem(preloader);
		if ( route.length == 0 ){
			alert('Route not found');
		} 
		route_line.setLatLngs(dots2latlngs(route));
	});
}


/**
 * запрос ж/д маршрута у сервера и отображение маршрута на карте
 **/

function showRailwayRoute(start,end, enemies){
    console.log('get route');
    if (start == null || end == null) return false;
    Route.service = getRadio('service');
    clearRoute();
    showElem(preloader);
    Time.start();
    Route.getRailwayRoute(start,end,enemies,function(route){
        var timeStop = Time.stop();
        time.textContent = timeStop + ' мс';
        time.innerText = timeStop + ' мс';
        console.log(JSON.stringify(route));
        hideElem(preloader);
        if ( route.length == 0 ){
            alert('Railway route not found');
        }
        route_line.setLatLngs(dots2latlngs(route));
    });
}

/**
* показ элемента
**/
function showElem(el){
	el.style.display = 'inline-block';
}
/**
* скрытие элемента
**/
function hideElem(el){
	el.style.display = 'none';
}

/**
* инициализация модуля spatialite
**/

function initSpatialite(region){
	showElem(preloader);
	var center = mapCenter[region];
	map.setView(center, zoom);
	hideElem(preloader);

}

/**
* объект содержащий центры карты для разных регионов
**/
var mapCenter = 
{
	"RU-ME.osm": [56.605, 47.9],
	"iraq-latest.osm": [33.385586,44.373779],
	"vietnam-latest.osm": [21.0845,105.820313],
	"syria-latest.osm": [33.504759,36.496582],
	"tajikistan-latest.osm": [38.548165,68.774414],
	"RU-LEN.osm": [59.95501,30.311279],
	"RU-MOS.osm": [55.751077,37.621307],
	"israel-and-palestine-latest.osm": [31.984255, 35.004911],
	"kosovo-latest.osm": [42.614833, 20.893836],
	"mongolia-latest.osm": [47.773702, 106.427558],
	"pakistan-latest.osm": [30.183729, 71.509366],
	"ukraine-latest.osm": [50.350146, 30.633554],
    "crimean-fed-district-latest.osm": [45.237, 34.1184]
};

/**
* Получение значение радио переключателя вида задачи
* @param name атрибут name радиокнопки 
* @return значение
**/

function getRadio(name){
    var inputs = document.getElementsByTagName('input');
    for ( var i = 0; i < inputs.length; i++ ){
        if ( inputs[i].attributes.name.value == name )
            if ( inputs[i].attributes.type.value == 'radio' )
                if( inputs[i].checked ) return inputs[i].value;
    }
    return null;
}

/**
* получение координаи узла графа, ближайшего к заданной точке 
* @param point заданная точка {lat:lat, lng:lng}
**/

function showNearest(point){
	Route.service = getRadio('service');
	showElem(preloader);
	Time.start();
	Route.getNearest(point, function(result){
		hideElem(preloader);
		time.textContent = Time.stop() + ' мс';
		time.innerText = Time.stop() + ' мс';
		//console.log(JSON.stringify(result));
		if ( result == null ){
			alert('Result fail');
		}
		nearest = {lat:result.coordinates[1],lng:result.coordinates[0]}
		nearestPoint = L.marker(L.latLng(nearest.lat,nearest.lng), {draggable:true,icon:nearestIcon}).addTo(map);
	})
}

function showNearestRailway(point){
    Route.service = getRadio('service');
    showElem(preloader);
    Time.start();
    Route.getNearestRailway(point, function(result){
        hideElem(preloader);
        time.textContent = Time.stop() + ' мс';
        time.innerText = Time.stop() + ' мс';
        //console.log(JSON.stringify(result));
        if ( result == null ){
            alert('Result fail');
        }
        nearest = {lat:result.coordinates[1],lng:result.coordinates[0]}
        nearestPoint = L.marker(L.latLng(nearest.lat,nearest.lng), {draggable:true,icon:nearestIcon}).addTo(map);
    })
}

/**
* определение принадлежности заданной точки к городу 
* @param point заданная точка {lat:lat, lng:lng}
**/

function showCity(point){
    showElem(preloader);
    Time.start();
    Route.getCity(point, function(result){
        hideElem(preloader);
        time.textContent = Time.stop() + ' мс';
        time.innerText = Time.stop() + ' мс';
        //console.log(JSON.stringify(result));
        clearCity();
        if ( result.incity == true ){
            alert([result.city_name, result.city_lastname].join(","));
            console.log(JSON.stringify(result.city_geometry));
            city = L.geoJson(result.city_geometry).addTo(map);
        }else{
            alert('Point is not in city');
        }
        
    });
}

/**
* определение принадлежности заданной точки к объекту ландшафта
* @param point заданная точка {lat:lat, lng:lng}
**/

function showLand(point){
    showElem(preloader);
    Time.start();
    Route.getLandscape(point, function(result){
        hideElem(preloader);
        time.textContent = Time.stop() + ' мс';
        time.innerText = Time.stop() + ' мс';
        //console.log(JSON.stringify(result));
        clearCity();
        if ( result.res == true ){
            alert([result.name, result.sub_type].join(","))
            city = L.geoJson(result.geometry).addTo(map);
        }else{
            alert('landscape objects not found');
        }
    });
}

/**
* определение наличия реки между двумя точками
* @param start, end заданные точки {lat:lat, lng:lng}
**/
function showWater(start, end){
    if (start == null || end == null) return false;
    showElem(preloader);
    Time.start();
    Route.getWater(start, end, function(result){
        hideElem(preloader);
        time.textContent = Time.stop() + ' мс';
        time.innerText = Time.stop() + ' мс';
        console.log(JSON.stringify(result));
        var waterId;
        var water;
        clearWaters();
        clearCity();
        if ( result.res == true ){
            alert(JSON.stringify(result.waters))
            for (waterId in result.waters){
                
                try{
                    waters.push(L.geoJson(result.waters[waterId].geometry).addTo(map));
                }catch(e){
                    //alert("Wrong GeoJson!");
                    console.log("Error:" + e.error + ":" + e.message + ":" + JSON.stringify(result.waters[waterId]));
                }
                
            }   
        }else{
            alert('water object was not found');
        }
    });
}

/**
 *удаление с карты объектов рек 
 **/
function clearWaters(){
    var i = 0;
    while(i < waters.length){
        map.removeLayer(waters[i]);
        waters.splice(i,1);
        i++;
    }
}


/**
 *удаление с карты объектов города 
 **/
function clearCity(){
     if (city != null){
        map.removeLayer(city);
        city = null;
    }
}

/**
 *удаление с карты линии маршрута 
 **/
function clearRoute(){
     route_line.setLatLngs(dots2latlngs([]));
}

/**
 *удаление с карты всех точек 
 **/
function clearPoints(){
    start = null;
    end = null;
    nearest = null;
    point = null;
    if ( startPoint != null ) map.removeLayer(startPoint);
    if ( endPoint != null ) map.removeLayer(endPoint);
    if (nearestPoint != null) map.removeLayer(nearestPoint);
    if (pointPoint != null) map.removeLayer(pointPoint);
    startPoint = null;
    endPoint = null;
    nearestPoint = null;
    point = null;
}

/**
 *удаление с карты начальной и конечной точек 
 **/
function clearStartEndPoints(){
    start = null;
    end = null;
    if ( startPoint != null ) map.removeLayer(startPoint);
    if ( endPoint != null ) map.removeLayer(endPoint);
    startPoint = null;
    endPoint = null;
}


/**
 *удаление с карты ближайшей точки
 **/
function clearNearestPoint(){
    nearest = null; 
    if (nearestPoint != null) map.removeLayer(nearestPoint);
    nearestPoint = null;
}

/**
 *удаление с карты произвольной точки
 **/
function clearPoint(){
    point = null; 
    if (pointPoint != null) map.removeLayer(pointPoint);
    pointPoint = null;
}



