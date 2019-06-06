var Helper = 
{
    addScript: function(src){
        var scriptElem = document.createElement('script');
        scriptElem.setAttribute('src',src);
        scriptElem.setAttribute('type','text/javascript');
        document.getElementsByTagName('head')[0].appendChild(scriptElem);
    },
    
    
    getRandomInt: function(min, max)
	{
	  return Math.floor(Math.random() * (max - min + 1)) + min;
	},
    
    // возвращает cookie с именем name, если есть, если нет, то undefined
    getCookie:  function(name) {
          var matches = document.cookie.match(new RegExp(
            "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
          ));
          return matches ? decodeURIComponent(matches[1]) : undefined;
    },
    
    setCookie: function(name, value, options) {
        options = options || {};
        
        var expires = options.expires;
        
        if (typeof expires == "number" && expires) {
        var d = new Date();
        d.setTime(d.getTime() + expires*1000);
        expires = options.expires = d;
        }
        if (expires && expires.toUTCString) { 
        options.expires = expires.toUTCString();
        }
        
        value = encodeURIComponent(value);
        
        var updatedCookie = name + "=" + value;
        
        for(var propName in options) {
            updatedCookie += "; " + propName;
            var propValue = options[propName];    
            if (propValue !== true) { 
              updatedCookie += "=" + propValue;
             }
        }
        document.cookie = updatedCookie;
    },
    
    deleteCookie: function(name) {
        this.setCookie(name, "", { expires: -1 })
    }
        
}

