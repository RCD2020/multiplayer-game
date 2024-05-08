// Robert Davis
// 2024.05.06

// elements
var login_div = document.getElementById('login');
var username = document.getElementById('username');
var join_button = document.getElementById('join');

var errors = document.getElementById('errors');
var messages = document.getElementById('messages');

// connects to socket
function join_game() {
    var url = window.location.href;
    var game_id = url.slice(-6);
    url = url.slice(0, url.length - 12);

    var socket = io.connect(url);

    socket.on('connect', function() {
        var data = {
            'game_id': game_id,
            'username': username.value
        };

        errors.innerHTML = '';
        socket.emit('connect_server', data);
    });

    socket.on('initialization', function(server_data) {
        // initialization data here
    });

    // backend validation
    socket.on('login_error', function(message) {
        login_div.style.display = 'block';
        var error = document.createElement('p');
        error.innerText = message;
        errors.appendChild(error);
    })

    socket.on('update', function(data) {
        // handle update data
    });

    socket.on('message', function(data) {
        var message = document.createElement('p');
        message.innerText += data['user'];
        message.innerText += ': ';
        message.innerText += data['message'];

        messages.appendChild(message);
    });
}

// join game button
join_button.onclick = function() {
    if (!username.value) {
        return;
    }
    login_div.style.display = 'None';
    join_game();
};