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
                var tokenInput = document.querySelector("#login > .token");
                tokenInput.value = output.token;
                var usernameInput = document.querySelector("#login > .username");
                usernameInput.value = output.username;
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
    var pollingInterval = setInterval( function() { setTimeout(function() {pollBackend(output);}, 500);}, 500);
}
