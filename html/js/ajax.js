/*отправка AJAX запроса нативным JS*/
var Ajax = 
{
    /*получение объекта XMLHttpRequest*/
    getXMLHttp: function(){
        var xmlHttp
        try
        {
            //Firefox, Opera 8.0+, Safari
            xmlHttp = new XMLHttpRequest();
            console.log('xmlHttp ', xmlHttp);
        }catch(e){
            //Internet Explorer
            try{
                xmlHttp = new ActiveXObject("Msxml2.XMLHTTP");
                }catch(e){
                try{
                    xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
                }catch(e){
                    alert("Your browser does not support AJAX!");
                    return false;
                }
            }
        }
        return xmlHttp;
    },

    /**
    * отправка запроса
    * @param method метод запроса
    * @param url
    * @param params
    * callback  
    **/
    sendRequest: function(method, url, params, callback){
        XMLHttp = Ajax.getXMLHttp();
    //    console.log('XMLHttp ', XMLHttp);
    //    console.log('method ', method);
        console.log('url ', url);


        if( method == 'GET' || method == 'get' ){
			url += '?' + params;
		}
        console.log('url ', url);


        XMLHttp.open(method, url, true);
        XMLHttp.onreadystatechange = function(){
            console.log('XMLHttp.readyState ', XMLHttp.readyState);
            console.log('XMLHttp.status ', XMLHttp.status);
            console.log('XMLHttp.responseText ', XMLHttp.responseText);


            if ( XMLHttp.readyState == 4 ){
                if ( XMLHttp.status == 200 ){
                    callback(JSON.parse(XMLHttp.responseText));
                }
                else{
                    callback(null);
                }
            }
        };
        if( method == 'POST' || method == 'post' ){
            XMLHttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
            XMLHttp.send(params);
        }else{
            XMLHttp.send(null);
        }
    },
    
    /**
    * отправка запроса
    * @param method метод запроса
    * @param url
    * @param params
    * callback  
    **/
    sendRequestRaw: function(method, url, params, callback){
        XMLHttp = Ajax.getXMLHttp();
        if( method == 'GET' || method == 'get' ){
            url += '?' + params;
        }
        XMLHttp.open(method, url, true);
        XMLHttp.onreadystatechange = function(){
            if ( XMLHttp.readyState == 4 ){
                if ( XMLHttp.status == 200 ){
                    callback(XMLHttp.responseText);
                }
                else{
                    callback(null);
                }
            }
        };
        if( method == 'POST' || method == 'post' ){
            XMLHttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
            XMLHttp.send(params);
        }else{
            XMLHttp.send(null);
        }
    }
    
};