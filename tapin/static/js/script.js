"use strict"

function pollBackend(output) {
    var request = new XMLHttpRequest();
    request.open("GET", "/backend/status", true);
    request.onreadystatechange = function (e) {
        if (request.readyState === 4 && request.status === 200) { 
            var res = request.responseText;
            console.log("hello: " + res);
            output = JSON.parse(res);
            if("token" in output && "username" in output) {
                console.log(output.token);
                console.log("ready");
                var token_input = document.querySelector("#login > .token");
                token_input.value = output.token;
                var username_input = document.querySelector("#login > .username");
                username_input.value = output.username;
            }
        }
    };
    request.onerror = function (e) {
        console.error(request.statusText);
    };
    request.send(null);
}
    


window.onload = function() {
    var output = { "status": "", "username": ""};
    setInterval( function() { pollBackend(output); }, 500 );
}
