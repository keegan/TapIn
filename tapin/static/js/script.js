"use strict"

const url = new URL(window.location.href);
const params = new URLSearchParams(url.search);
//if (params.has('token')) {
const token = params.get('token');
//} else {
//    const token = null;
//if (params.has('token')) {
const hostname = params.get('hostname');

function pollBackend(output) {
    var request = new XMLHttpRequest();
    request.open("GET", "/backend/status?hostname=" + hostname + "&token=" + token, true);
    request.onreadystatechange = function (e) {
        if (request.readyState === 4 && request.status === 200) { 
            var res = request.responseText;
            console.log("hello: " + res);
            output = JSON.parse(res);
            if (output.status === "success") {
                if ("session_token" in output && "username" in output && "uid" in output) {
                    var loginForm = document.querySelector("#login-wrapper");
                    console.log(loginForm);
                    loginForm.style.visibility = "visible";
                    loginForm.style.opacity = 1;

                    var submit = document.querySelector("form#login");
                    
                    submit.style.visibility = "visible";
                    submit.style.opacity = 1;

                    var usernameInput = document.querySelector("h1#status");
                    usernameInput.innerHTML = "You are " + output.username;

                    var uidInput = document.querySelector("input.uid");
                    uidInput.value = output.uid;

                    var hostnameInput = document.querySelector("input.hostname");
                    hostnameInput.value = hostname;

                    var sessiontokenInput = document.querySelector("input.session_token");
                    console.log(output.session_token);
                    sessiontokenInput.value = output.session_token;

                }
            } else if (output.status === "failure") {
                console.error("Card failed.");
		location.reload()
            } else {
                setTimeout(pollBackend(output), 1000);
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
