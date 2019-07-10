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
        this.setCors(XMLHttp, new URL(url));
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
    * @param XMLHttp - XMLHttpRequest
    * @param url - string
    */
    setCors: function (XMLHttp, url) {
        var address = this.getAllowOrigin(url);
        console.log("setCors() { address = ", + address)
        if (address) {
            XMLHttp.setRequestHeader('Access-Control-Allow-Origin', address);
        }
    },

    /**
    * @param url - string
    * return url - string
    */
    getAllowOrigin: function (url) {
        console.log("getAllowOrigin() { url = ", + url)
        var allowedOrigins = {
            'geoserver.py': ["8080"],
            'waronmap.com': ["80", "8080"],// 8080 - порт геосервера
            'localhost': ["80", "8080"],
        };

        if (this.checkHostname(url.hostname, allowedOrigins)) {
            if (this.checkHostPort(url, allowedOrigins)) {
                return 'http://' + url.hostname + ':' + url.port;
            }
        }

        return null;
    },

    checkHostname: function (hostname, allowedOrigins) {
        const keys = Object.keys(allowedOrigins);
        return keys.indexOf(hostname) > -1;
    },

    checkHostPort: function (url, allowedOrigins) {
        const ports = allowedOrigins[url.hostname];
        return ports.indexOf(url.port) > -1;
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