"use strict"

function pollBackend(output) {
    var request = new xmlHttpRequest();
    request.open("GET", "/backend/status", true);
    request.send(null)
    res = request.responseText;
    output = JSON.parse(res);
}
    


window.onload = function() {
    output = { "status": "", "username": ""};
    setInterval( function() { pollBackend(output); }, 500 );
    console.log(output)
}
