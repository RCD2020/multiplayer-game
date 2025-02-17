// Robert Davis
// 2025.02.08

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

// var content = document.getElementById('content');
var character_select = document.getElementById('character_select');
var chat = document.getElementById('chat');
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
        // console.log(server_data);

        chars = Object.keys(server_data['characters']);
        for (let i = 0; i < chars.length; i++) {
            character = chars[i];
            var img = document.createElement('img');
            img.src = '/static/Clue/cards/players/' + character + '.png';
            img.id = character;
            if (server_data['characters'][character]['inUse']) {
                img.className = 'taken';
            }
            character_select.appendChild(img);

            if (!server_data['state']) {
                img.addEventListener('click', function() {
                    if (
                        this.className != 'taken'
                        || this.className != 'selected' // change this to && once you have fixed issue where after reconnecting, you cannot choose already chosen character
                    ) {
                        let data = {
                            'type': 'character_select',
                            'character': this.id
                        };
                        socket.emit('server_data', data);
                    }
                });
            } 
        }

        if (!server_data['state']) {
            character_select.removeAttribute('hidden');
        }

        if (server_data['is_main_player']) {
            chat.removeAttribute('hidden');
        
        
            message_field.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    message = message_field.value;
                    message_field.value = '';
                    var data = {
                        'type': 'message',
                        'message': message,
                        'address': 'room'
                    };
                    socket.emit('server_data', data);
                }
            });
        }
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

    socket.on('update', function(data) {
        // handle update data
        console.log(data);
        
        // message.innerText = data['user'] + ': ' + data['message'];
        // made it so you can insert HTML for funzies
        // TODO: should probably remove this later
        if (data['type'] == 'chat_event') {
            var message = document.createElement('p')
            message.innerText = data['message'];
            messages.prepend(message);
        } else if (data['type'] == 'message') {
            var message = document.createElement('p')
            message.innerHTML = data['user'] + ': ' + data['message'];
            messages.prepend(message);
        } else if (data['type'] == 'character_selected') {
            var img = document.getElementById(data['character']);
            if (img.className != 'selected') {
                img.className = 'taken';
            }
            if (data['deselected']) {
                img = document.getElementById(data['deselected']);
                img.className = '';
            }
        } else if (data['type'] == 'character_select_success') {
            var img = document.getElementById(data['character'])
            let existing = document.getElementsByClassName('selected');
            for (let i = 0; i < existing.length; i++) {
                existing[i].className = '';
            }
            img.className = 'selected';
        }

        
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

// joins game when enter is pressed
username.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        join_button.click();
    }
});
