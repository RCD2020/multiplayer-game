// Robert Davis
// 2024.05.08

// clear error function
function setRemoval(id, ms) {
    setTimeout(function() {
        var element = document.getElementById(id);
        element.remove();
    }, ms);
}

// elements
var login_div = document.getElementById('login');
var username = document.getElementById('username');
var join_button = document.getElementById('join');

var content = document.getElementById('content');
var messages = document.getElementById('messages');

var errors = document.getElementById('errors');
var message_field = document.getElementById('message_field');

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
        content.removeAttribute('hidden');
        
        message_field.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                message = message_field.value;
                message_field.value = '';
                var data = {
                    'message': message,
                    'address': 'room'
                };
                socket.emit('server_data', data);
            }
        });
    });

    // backend validation
    socket.on('login_error', function(message) {
        login_div.style.display = 'block';
        var error = document.createElement('p');
        error.innerText = message;
        errors.appendChild(error);
    });

    socket.on('game_error', function(error) {
        // implement error handling
        var error_message = document.createElement('p');
        error_message.innerText = error;
        var err_id = 'err_' + Math.random().toString(16).slice(2);
        error_message.id = err_id;
        errors.prepend(error_message);
        setRemoval(err_id, 10000);
    });

    // legacy update handler
    // socket.on('update', function(data) {
    //     // handle update data
    //     var message = document.createElement('p')

    //     if (data['type'] == 'chat_event') {
    //         message.innerText = data['message'];
    //     } else {
    //         message.innerText = data['user'] + ': ' + data['message'];
    //     }
        
    //     messages.append(message);
    // });

    socket.on('chat_event', function (packet) {
        // console.log(packet);
        var message = document.createElement('p');

        message.innerText = packet;

        messages.prepend(message);
    })

}

// join game button
join_button.onclick = function() {
    if (!username.value) {
        return;
    }
    login_div.style.display = 'None';
    join_game();
};

// joins game when enter is pressed
username.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        join_button.click();
    }
});
