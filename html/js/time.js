/**
* модуль подсчета времени
*
**/
var Time = 
{
	begin: null,
	
	end: null,

	start: function(){
		Time.begin = new Date();
	},

	stop: function(){
		Time.end = new Date();
		delta = Time.end.getTime() - Time.begin.getTime();
		return delta;
	}
}
