var socket = null;
var isopen = false;
var server = null;
var pubkey = null;
var user = null;
var password = null;

window.onload = function() {

    socket = new WebSocket("ws://127.0.0.1:9000");
    socket.binaryType = "arraybuffer";

    socket.onopen = function() {
        console.log("Connected!");
        isopen = true;
    };

    socket.onmessage = function(e) {
        if (typeof e.data == "string") {
            console.log("Text message received: " + e.data);
            var command = e.data.split("#");

            if (command.length != 4) {
                console.log('Command length not valid!');
                return
            }

            if (command[0] != "FASTR") {
                console.log('Command is not a fastr command');
                return
            }

            if (command[1] != "0") {
                console.log('Command version is not supported');
                return
            }

            var name = command[2];

            var arguments = null;

            if (command[3].length > 0) {
                arguments = JSON.parse(command[3]);
            }

            executeCommand(name, arguments)


        } else {
            var arr = new Uint8Array(e.data);
            var hex = '';
            for (var i = 0; i < arr.length; i++) {
                hex += ('00' + arr[i].toString(16)).substr(-2);
            }
            console.log("Binary message received: " + hex);
        }
    };

    socket.onclose = function(e) {
        console.log("Connection closed.");
        socket = null;
        isopen = false;
    };
};

// Display the argument in the msg input when clicked.
$(document).ready(function(){
    $('.argument').on('click', function(){
        $('#msg').val($(this).text());
    });
});

function executeCommand(name, arguments) {
    console.log('executeCommand: name: ' + name);
    console.log('executeCommand: arguments: ' + arguments);
    if (name == 'LOG') {
        addLog(arguments);
    } else if (name == 'error') {
        do_error(arguments);
    } else if (name == 'warning') {
        do_warning(arguments);
    } else if (name == 'WSAUTH_PUBLICKEY') {
        pubkey = arguments;
        do_wsauth_publickey(arguments);
    } else if (name == 'WSAUTH_RESULT') {
        do_wsauth_result(arguments);
    } else if (name == 'LISTWORKERS_RESULT') {
        do_listworkers_result(arguments);
    } else if (name == 'STATUSWORKER_RESULT') {
        do_statusworker_result(arguments);
    } else {
        console.log("Unknown function: " + name);
    }
}

function sendTextFromInput() {
    if (isopen) {
        var msg = document.getElementById("msg").value;
        socket.send(msg);
        console.log("Text message sent.");
    } else {
        console.log("Connection not open.");
    }
}

function sendText() {
    if (isopen) {
        socket.send("Hello, world!");
        console.log("Text message sent.");
    } else {
        console.log("Connection not open.");
    }
}

function sendBinary() {
    if (isopen) {
        var buf = new ArrayBuffer(32);
        var arr = new Uint8Array(buf);
        for (i = 0; i < arr.length; ++i) arr[i] = i;
        socket.send(buf);
        console.log("Binary message sent.");
    } else {
        console.log("Connection not open.");
    }
}

function sendLoginRequest() {
    if (isopen) {
        server = $('#server').val();
        user = $('#user').val();
        password = $('#password').val();
        console.log("*** sendLoginRequest()");
        console.log("server: " + server);
        console.log("user: " + user);
        var cmd = 'FASTR#0#WSAUTH_REQUESTAUTH#"' + user + '"';
        socket.send(cmd);
    } else {
        console.log("Connection not open.");
    }
}

function do_wsauth_publickey(pubkey) {
    if (isopen) {
        if (password) {
            var publicKey = forge.pki.publicKeyFromPem(pubkey);
            var encrypted = publicKey.encrypt(password, 'RSA-OAEP');
            var cmd = 'FASTR#0#WSAUTH_LOGIN#{"user": "' + user + '", "message": "' + window.btoa(encrypted) + '"}';
            socket.send(cmd);
        } else {
            console.log("No password is stored. Something went wrong!");
        }
    } else {
        console.log("Connection not open.");
    }
}

function do_wsauth_result(token) {
    if (isopen) {
        console.log("token: " + token);
        if (token) {
            console.log("login succesful");
        } else {
            console.log("login NOT succesful");
        }
    } else {
        console.log("Connection not open.");
    }
}

function do_listworkers_result(arguments) {
    if (isopen) {
        console.log("list of workers: " + arguments);
    } else {
        console.log("Connection not open.");
    }
}

function do_statusworker_result(arguments) {
    if (isopen) {
        console.log("status of worker (" + arguments.name + "): " + arguments.status);
    } else {
        console.log("Connection not open.");
    }
}

function do_error(arguments) {
    console.log("error: " + arguments);
}

function do_warning(arguments) {
    console.log("warning: " + arguments);
}

function addLog(record) {
    console.log(record);
    var logstr = ("[" + record.processName + ":" + record.threadName + "] " + record.levelname + ": " + record.module + ":" + record.lineno.toString() + " >> " + record.msg + "\n");
    var obj = document.getElementById("fastrLog");
    var txt = document.createTextNode(logstr);
    obj.appendChild(txt);
}