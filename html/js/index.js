window.onload = function(){
    
	
	selectRegion = document.getElementById('region');
	initSpatialite(selectRegion.value);
	selectRegion.onchange = function(){
		initSpatialite(selectRegion.value);
	};
	
	
	var preloader = document.getElementById('preloader');
	var time = document.getElementById('time');
	
	
};	