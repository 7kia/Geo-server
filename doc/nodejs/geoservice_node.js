#!/usr/bin/env node

var port =  8081;//parseInt(process.argv[2]);
//console.log(process.argv);
if (port == undefined) port = 8000;
var express = require('express');
var app = express();
var server = require('http').Server(app);
var fs = require('fs');
var sqlite = require('spatialite');
var DB_DIR = '/home/ilya/war-on-map/Geo-server/bases/';
var MIN_SIZE_DEFAULT = 1000;
server.listen(port,function(){
	console.log('Server start at port '+port);
});

var foundRoute = function (req, res, dbName) {
	var data = req.query.data;
	data = data.split(',');
	var lat_start = parseFloat(data[0]);
	var lng_start = parseFloat(data[1]);
	var lat_end = parseFloat(data[2]);
	var lng_end = parseFloat(data[3]);
	var filename = data[4];
	var db_file = searchBestDbFile([lat_start,lng_start],[lat_end,lng_end],filename);
	console.log('used db_file='+db_file);
	var db = new sqlite.Database(DB_DIR + '/' + db_file);
	var scale = parseInt(data[5]);
	getRoute([lat_start,lng_start], [lat_end,lng_end], db, scale, dbName, function(result){
		db.close();
		res.writeHead(200, {"Content-Type": "text/html","Access-Control-Allow-Origin": "*"});
		res.write(JSON.stringify(result));
		res.end();
	});
};

/*маршрут для GET запроса маршрута от модуля spatialite через запрос к базе с определение id узлов через запрос к базе*/
app.get('/route',function(req,res){
	foundRoute(req, res, 'roads_net');
});

app.get('/route_railway',function(req,res){
	foundRoute(req, res, 'rails_net');
});

var foundNearest = function (req, res, dbName) {
	var data = req.query.data;
	data = data.split(',');
	var lat_point = parseFloat(data[0]);
	var lng_point = parseFloat(data[1]);
	var filename = data[2];
	var db_file = searchBestDbFile([lat_point,lng_point],[lat_point,lng_point],filename);
	console.log('used db_file='+db_file);
	var db = new sqlite.Database(DB_DIR + '/' + db_file);
	var scale = parseInt(data[3]);
	getNearest([lat_point,lng_point], db,scale, dbName, function(result){
		res.writeHead(200, {"Content-Type": "text/html","Access-Control-Allow-Origin": "*"});
		res.write(JSON.stringify({coordinates:result}));
		res.end();
	});
};
/*маршрут для GET запроса координат ближайшего к заданной точке узла с определение id узла через запрос к базе*/
app.get('/nearest',function(req,res){
	foundNearest(req, res, "roads_net");
});

app.get('/nearest_railway',function(req,res){
	foundNearest(req, res, "rails_net");
});
/*поиск маршрута*/
function getRoute(from, to, db, scale, dbName, callback){
	getNodeId(from, db, scale, dbName, function(start){
	     getNodeId(to, db, scale, dbName,function(end){
			console.log(start+':'+end);
			var sql = "SELECT AsGeoJSON(geometry) AS geometry FROM " + dbName + " WHERE ";
			sql += "NodeFrom=" + start + " AND NodeTo=" + end; 
			sql += " LIMIT 1;";

			//console.log(sql);
			db.spatialite(function(err) {
				db.get(sql, function(err, row) {
				//console.log(JSON.stringify(row));
				var route = [];
					if ( row != undefined ){
						if ( row.geometry != null ){
							var obj = JSON.parse(row.geometry);
							route = obj.coordinates;
						}
					}
					//console.log(JSON.stringify(reverse(route)));
				  callback(route);
				});
			});
	    });
	  
	});
    
}


/*поиск ближайшего узла*/
function getNearest(point, db,scale, dbName, callback){
	getNodeId(point, db, scale, dbName,function(node_id){
		var sql = 'SELECT AsGeoJSON(geometry) AS geometry FROM ' + dbName + ' WHERE node_id='+node_id+' LIMIT 1';
		db.spatialite(function(err) {
				db.get(sql, function(err, row) {
				//console.log(JSON.stringify(row));
					var coords = null;
						if ( row != undefined ){
							if ( row.geometry != null ){
								var obj = JSON.parse(row.geometry);
								coords = obj.coordinates;
							}
						}
						//console.log(JSON.stringify(reverse(route)));
					  callback(coords);
					});
			});
	});	
}

/**
* получение id узла по координатам методом запроса из базы
* @param dot массив координат [lat,lng]
* @return id узла 
**/
function getNodeId(dot, db, scale, dbName ,callback){
	var nodeDbName = "";
	if (dbName == 'roads_net') {
		nodeDbName = "roads_nodes";
	} else if (dbName == 'rails_net') {
		nodeDbName = "rails_nodes";
	}
	var sector = latlng2sector(dot[0],dot[1],scale);
	var sql = "select node_id, MIN(Pow(("+dot[1]+"-X(geometry)),2) +Pow(("+dot[0]+"-Y(geometry)),2)) as rast from " + nodeDbName +" where connected=1 and sector="+sector;
	db.spatialite(function(err) {
		db.get(sql, function(err, row) {
            //console.log(JSON.stringify(row));
			if ( row != undefined ){
				if ( row.node_id != null ){
					var node_id = row.node_id;
				}
			}
			
            callback(node_id);
		});
	});
}

/*поиск наименьшего файла базы*/
function searchBestDbFile(point1,point2,filename){
	var db_files = fs.readdirSync(DB_DIR);
	var min_size = MIN_SIZE_DEFAULT;
	var best_file = undefined;
	var size = 0;
	for (var i = 0; i < db_files.length; i++){
		if (db_files[i].indexOf(filename) != 0) continue;
		if (isInside(db_files[i],point1,point2)){
			size = getAreaSize(db_files[i]);
			if (size <= min_size){
				min_size = size;
				best_file = db_files[i];
			}
		}
	}
	return best_file;
}



/*calculating sector by coordinates*/
function latlng2sector(lat,lng,scale){
	var row = Math.floor(scale*(lat + 90.0));
	var col = Math.floor(scale*(lng + 180));
	var sector = row * 360 * scale + col;
	return sector;
}


function getAreaSize(filename){
	var boundary = getBoundaryFromName(filename);
	if (boundary.top == undefined) return MIN_SIZE_DEFAULT;
	var size = boundary['top'] - boundary['bottom'];
	return size;
}

function isInside(filename, point1, point2){
	var boundary = getBoundaryFromName(filename)
	if (isPointInside(boundary, point1) && isPointInside(boundary, point2))
		return true
	return false
}


function isPointInside(b,point){
	if  (b.top == undefined)
		return true;
	if (point[0] <= b['top'] && point[0] >= b['bottom'] && point[1] <= b['right'] && point[1] >= b['left'])
		return true;
	return false;
}

function getBoundaryFromName(name){
	var boundary = {};
	var ls1 = name.split('[');
	if (ls1[1] == undefined) return boundary; 
	var ls = ls1[1].split(']')[0].split(',');
	if (ls.length < 4) return boundary;
	boundary['top'] = parseFloat(ls[0]);
	boundary['left'] = parseFloat(ls[1]);
	boundary['bottom'] = parseFloat(ls[2]);
	boundary['right'] = parseFloat(ls[3]);
	return boundary;	
}
