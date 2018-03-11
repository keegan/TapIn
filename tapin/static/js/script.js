"use strict"

const hostname = "pi3-curie";
const url = new URL(window.location.href);
const params = new URLSearchParams(url.search);
const token = params.get('token')

function pollBackend(output) {
    var request = new XMLHttpRequest();
    
    request.open("GET", "/backend/status?hostname=" + hostname + "&token=" + token, true);
    request.onreadystatechange = function (e) {
        if (request.readyState === 4 && request.status === 200) { 
            var res = request.responseText;
            console.log("hello: " + res);
            output = JSON.parse(res);
            if (output.status === "success") {
                if ("token" in output && "username" in output) {
                    console.log(output.token);
                    console.log("ready");
                    var tokenInput = document.querySelector("#login > .token");
                    tokenInput.value = output.token;
                    var usernameInput = document.querySelector("h1#status");
                    usernameInput.innerHTML = "You are " + output.username;
                    var loginForm = document.querySelector("#login");
                    loginForm.style.visibility = "visible";
                    loginForm.style.opacity = 1;
                }
            } else {
                setTimeout(pollBackend(output), 500);
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
    pollBackend(output);
}
