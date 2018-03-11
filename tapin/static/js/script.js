"use strict"

function pollBackend(output) {
    var request = new XMLHttpRequest();
    request.open("GET", "/backend/status", false);
    request.send(null);
    var res = request.responseText;
    console.log("hello: " + res);
    output = JSON.parse(res);
}
    


window.onload = function() {
    var output = { "status": "", "username": ""};
    setInterval( function() { pollBackend(output); }, 500 );
    console.log(output);
}
