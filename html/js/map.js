    //создаем карту
	var mapCenter = [56.605, 47.9];
	var zoom = 13;
	var maxZoom = 16;               /*максимальный масштаб*/
    var minZoom = 5                /*минимальный масштаб*/
	var id = 'examples.map-zr0njcqy'; /*ключ*/
	var map = null;


	map = L.map('map-block').setView( mapCenter, zoom );

	//создаем tile-слой и добавляем его на карту 
	var mapbox = L.tileLayer('https://{s}.tiles.mapbox.com/v3/{id}/{z}/{x}/{y}.png', {
		maxZoom: maxZoom,
		minZoom: minZoom,
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
			'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
			'Imagery © <a href="http://mapbox.com">Mapbox</a>',
		id: id
	});
	
	//создаем другие базовые слои от других провайдеров     
	var osmde = L.tileLayer.provider('OpenStreetMap.DE',{maxZoom: maxZoom, minZoom: minZoom});
	var osmBW = L.tileLayer.provider('OpenStreetMap.BlackAndWhite',{maxZoom: maxZoom, minZoom: minZoom});
	var ersiwi = L.tileLayer.provider('Esri.WorldImagery',{maxZoom: maxZoom, minZoom: minZoom});
	 /*создаем tile-слои Google*/ 
	var ggl = new L.Google('SATELLITE',{maxZoom: maxZoom, minZoom: minZoom});
	var ggl2 = new L.Google('TERRAIN',{maxZoom: maxZoom, minZoom: minZoom});
    map.addLayer(ggl2);
	//создаем контрол для переключения слоев
	var baseLayers = 	{
							"OpenStreetMap": osmde,
                            "Mapbox": mapbox,
							"OpenStreetMap Black and White": osmBW,
							'Esri WorldImagery': ersiwi,
							 "Google Satellite": ggl,
                            "Google Terrain": ggl2
						};

	L.control.layers(baseLayers).addTo(map);