#!/usr/bin/env node

/**модуль для записи высотных данных из файла в базу sqlite**/
var sqlite3 = require('sqlite3');
var buffer = require('buffer');
var fs = require('fs');
var argv = process.argv;
var util = require('util');

var argv = process.argv;
var lat_min = null; /**границы региона для которого значения высотные данные будут добавляться в базу**/
var lat_max = null;
var lng_min = null;
var lng_max = null;
var partial = false; /**флаг что база будет частичная**/
var output = '';

var data_file = argv[2];
var db_file = argv[3];
if ( db_file == undefined || data_file == undefined){
	console.log('Usage: '+argv[1].split('/').pop()+' <data_file> <db_file> [<lat_min>] [<lat_max>] [<lng_min>] [<lng_max>]');
	process.exit(0);
}

if ( fs.existsSync(db_file) ) fs.unlinkSync(db_file); /*если файл есть удаляем*/



/**
* проверяем аргументы и в зависимости от результата 
* или выводим помощь или инициализируем границы региона и флаг частичности
**/
if ( argv.length == 3 && ( argv[2] == '-h' || argv[2] == '--help')){
	console.log('Usage: '+argv[1].split('/').pop()+' <data_file> <db_file> [<lat_min>] [<lat_max>] [<lng_min>] [<lng_max>]');
	process.exit(0);
}else if( argv.length > 7 ){
	lat_min = parseFloat(argv[4]);
	lat_max = parseFloat(argv[5]);
	lng_min = parseFloat(argv[6]);
	lng_max = parseFloat(argv[7])
	if ( !isNaN(lat_min) && !isNaN(lat_max) && !isNaN(lng_min) && !isNaN(lng_max) ){
		if ( lat_min < lat_max && lng_min < lng_max ){
			var coordRangeTrue = lat_min <= 90 && lat_min >= -90 &&
								 lat_max <= 90 && lat_max >= -90 &&
								 lng_min <= 180 && lat_min >= -180 &&
								 lng_max <= 180 && lat_max >= -180;
			if ( coordRangeTrue ){
				partial = true;
			}else{
				console.log('Incorrect parameters');
			}
		}else{
			console.log('Incorrect relation between parameters');
		}
	}else{
		console.log('Incorrect parameters');
	}
}


if ( partial ){
	console.log('will be created partial base:');
	console.log('lat_min: '+lat_min);
	console.log('lat_max: '+lat_max);
	console.log('lng_min: '+lng_min);
	console.log('lng_max: '+lng_max);
}else{
	console.log('will be created full base');
}


/*создаем базу*/
var db = new sqlite3.cached.Database(db_file);

var sql_opt = "PRAGMA journal_mode = PERSIST";
db.run(sql_opt);

/**создаем пустые таблицы**/
createTable(null,-90,90, function(){
	loadFileToDb(data_file, 4096);
});





/**
* создание таблиц высот с именем зависящим от входного индекса
* функция вызывается рекурсивно пока не достигнет максимального индекса
* @param index текущий индекс
* @param min, max минимальный и максимальный индексы
* @param callback функция обратного вызова, вызываемая по окончании операции
**/
function createTable(index, min, max, callback){
	if ( index == null || index == undefined ) index = min;
	var tableName = number2tablename(index);
	var sql = "CREATE TABLE IF NOT EXISTS " + tableName + " (id INTEGER PRIMARY KEY AUTOINCREMENT, lat REAL, lng REAL, el REAL)";
	//console.log(sql);
	db.run(sql,function(err){
		if ( err != null ){
			console.log(err);
		} else{
			for ( var i = 0; i < output.length; i++ ){
				util.print('\b');
			}
			output = 'table ' + tableName + ' has been created';
			util.print(output);
		}
		index++;
		if ( index <= max ){
			createTable(index, min, max,callback);
		}else{
			util.print('\n');
			callback();
		}
	});
}



/**
* проверка принадлежности координат точки к выбранному региону
* @param lat,lng широта и долгота точки
* @return true если точка принадлежит региону и false в противном случае
**/
function checkCoordRange(lat,lng){
	if ( !partial ) return true;
	var coordInRange = lat <= lat_max && lat >= lat_min &&
					   lng <= lng_max && lng >= lng_min;
	return coordInRange;
}


/**
* запуск sql запроса
* @param sql запрос
* @param callback функция обратного вызова
**/
function queryRun(sql, callback){
	db.run(sql, function(err){
		callback();
	});	
}

/**
* выполнение нескольких запросов последовательно (использование рекурсии)
* @param index индекс запроса в массиве запросов
* @param arrSQL массив запросов (массив строк)
* @param callback функция обратного вызова, вызываемая после выполнения всех запросов
**/
function queryArrayRun(index, arrSQL, callback){
	db.run(arrSQL[index], function(err){
		index++;
		if ( index < arrSQL.length ){
			queryArrayRun(index, arrSQL, callback);
		}else{
			callback();
		}
	});
	
}

/**
* удаление из данных точек не попадающих в выбранный регион
* @param data массив распарсеных данных вида [lng1, lat2, el1, lng2, lat2, el2, ...]
**/
function selectByRange(data){
	for ( var i = 0; i < data.length-2; i += 3 ){
		if ( !checkCoordRange( data[i+1], data[i] ) ){
			data.splice(i,3);
			i -= 3;
		}
	}
	return data;
}

/**
* получение имени таблицы из числа
* @param index число
* @return string имя таблицы
**/
function number2tablename(index){
	var tableName = "";
	if ( index < 0 ){
		tableName += "n";
	}else{
		tableName += "p";
	}
	tableName += Math.floor(Math.abs(index)) + '_elevation';
	return tableName;
}

/**
* подготовка массива строк с запросами из данных
* @param data массив распарсеных данных вида [[lng1, lat2, el1], [lng2, lat2, el2], ...]
* @return sql массив строк запроса
**/
function prepSQLArray(data){
	if (data.length == 0) return['select 0'];
	var arrSQL = [];
	for ( var i = 0; i < data.length; i++ ){
		arrSQL.push(prepSQL(data[i]));
	}
	return arrSQL;
}


/**
* подготовка строки запроса из массива с данными
* @param data массив распарсеных данных вида [lng1, lat2, el1, lng2, lat2, el2, ...]
* @return sql строка запроса
**/
function prepSQL(data){
	var sql = "";
	if ( data.length > 0 ){
		sql = "INSERT INTO " + number2tablename(data[1]) + " (lat,lng,el) VALUES ";
		for ( var i = 0; i < data.length-2; i += 3 ){
			sql += "("+data[i+1]+","+data[i]+","+data[i+2]+")";
			if ( i < data.length-3 ) sql += ",";
		}
	}
	return sql;
} 

/**
* преобразование массива data в двумерный массив
* содержащий массивы с одинаковым целым значением lat
* @param data массив распарсеных данных вида [lng1, lat2, el1, lng2, lat2, el2, ...]
* @param split двумерный массив вида [[lng1, lat2, el1], [lng2, lat2, el2], ...]
**/
function splitData(data){
	var split = [];
	var last = undefined;
	
	for ( var i = 0; i < data.length-2; i += 3 ){
		if ( number2tablename(data[i+1]) != last ){
			last = number2tablename(data[i+1]);
			split.push([]);
			split[split.length-1].push(data[i]);
			split[split.length-1].push(data[i+1]);
			split[split.length-1].push(data[i+2]);
		}else{
			split[split.length-1].push(data[i]);
			split[split.length-1].push(data[i+1]);
			split[split.length-1].push(data[i+2]);
		}
	}
	return split;
}

/**
* вставка данных из массива data вида [lng1, lat2, el1, lng2, lat2, el2, ...]
* в базу sqlite  
* @param data массив распарсеных данных вида [lng1, lat2, el1, lng2, lat2, el2, ...]
* @param callback функция обратного вызова, вызываемая по завершении операции
**/
function insertRows(data,callback){
	var data = selectByRange(data);
	//if (data.length==0) { callback();return;}
	data = splitData(data);
	var arrSQL = prepSQLArray(data);
	//console.log("\n\n\n"+JSON.stringify(arrSQL));
	queryArrayRun(0, arrSQL, callback);
}

/**
* чтение высотных данных из файла 
* в базу sqlite  
* @param filename имя файла с высотными данными
* @param buffer_size размер буфера для чтения в байтах
**/
function loadFileToDb(filename, buffer_size){
	
	var fd = fs.openSync(filename,'r');
	util.print('progress: ');
	var offset = 0;
	var position = 0;
	var count = 0;
	var lastOutputLen = 0;
	var portion = [];
	var readBuf = new Buffer(buffer_size);
	var file_size = fs.statSync(filename).size;
	/**пока файл не кончится читаем частями в буфер (функция рекурсивно вызывает саму себя пока не кончится файл)**/
	loadBufferToDb(fd, portion, readBuf, offset, buffer_size, position, lastOutputLen, file_size);
	//fs.closeSync(fd);
}

/**
* чтение данных из буфера, парсинг и запись 
* в базу sqlite  
* @param fd дескриптор файла с высотными данными
* @param portion временнный буфер(массив) для хранения символов содержащих данные для одной точки
* @param readBuf буфер для чтения из файла (экземпляр класса buffer)
* @param offset смещение в буфере для чтения
* @param buffer_size размер буфера для чтения в байтах
* @param position позиция начала чтения в файле
* @param lastOutputLen  количество символов последнего вывода
* @param file_size размер исходного файла с высотными данными
**/
function loadBufferToDb(fd, portion, readBuf, offset, buffer_size, position, lastOutputLen, file_size){
	var string = '';
	var data = [];
	var readed = fs.readSync(fd, readBuf, offset, buffer_size, position);	
	if ( readed == 0 ) return true;
	/**читаем побайтно в массив**/
	for ( var i = 0; i < readed; i++ ){ 
		portion.push(readBuf[i]);
		/**если встречаем байт 0A, то парсим строку из массива и записываем координаты и высоту в массив data**/
		/** потом очищаем массив**/
		if ( readBuf[i] == 10 ){
			for ( j = 0; j < portion.length; j++ ){
				string += String.fromCharCode(portion[j]);
				if ( portion[j] == 32 || portion[j] == 10 ){
					data.push(parseFloat(string.slice(0,string.length-1)));
					string = '';
				}
			}
			portion = [];
		}	
	}
	position += buffer_size;
	/**вывод прогресса**/
	var progress = (position/file_size * 100).toFixed(6)+'%';
	for ( var i = 0; i < lastOutputLen; i++ ){
		util.print('\b');
	}
	util.print(progress);
	lastOutputLen = progress.length;
	insertRows(data, function(){
		data=[];  
		//console.log('position='+position);
		loadBufferToDb(fd, portion, readBuf, offset, buffer_size, position, lastOutputLen, file_size); 
	});
}



