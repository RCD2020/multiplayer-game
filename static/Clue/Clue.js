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
var username_field = document.getElementById('username');
var join_button = document.getElementById('join');

// var content = document.getElementById('content');
var character_select = document.getElementById('character_select');
var ready_button = document.getElementById('ready_button');
var game_board = document.getElementById('game_board');
var cards_container = document.getElementById('cards');

var chat = document.getElementById('chat');
var messages = document.getElementById('messages');

var errors = document.getElementById('errors');
var message_field = document.getElementById('message_field');

// data
var username = '';
var current_char = '';

var socket = {
    connect : function(url) {
        this.socket = io.connect(url);
    },
    emit : function(event, packet) {
        this.socket.emit(event, packet);
    },
    on : function(event, func) {
        this.socket.on(event, func);
    }
};

var game_canvas = {
    canvas : document.createElement('canvas'),
    start : function(
        width, height, container, piece_data, turn, settings
    ) {
        this.canvas.width = width;
        this.canvas.height = height;
        this.ctx = this.canvas.getContext('2d');
        container.appendChild(this.canvas);
        this.pieces = piece_data;
        this.settings = settings;
        this.turn = turn;

        this.canvas.addEventListener('mousedown', function (e) {
            let coords = game_canvas.getCursorPosition(e);
            // console.log(coords);

            if (game_canvas.turn == username) {
                socket.emit('server_data', {
                    'event': 'update_position',
                    'packet': coords
                });
            }
        });

        this.draw();
    },
    clear : function() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    },
    draw : function() {
        this.clear();

        for (let i = 0; i < this.pieces.length; i++) {
            let border_color = 'black';
            if (this.pieces[i]['character'] == current_char) {
                border_color = 'white';
            }
            this.draw_circle(
                this.pieces[i]['coords'], this.pieces[i]['color'], border_color
            );
        }
    },
    draw_circle : function(coords, color, border_color) {
        this.ctx.beginPath();
        this.ctx.arc(...coords, 15, 0, 2*Math.PI);
        this.ctx.fillStyle = color;
        this.ctx.fill();
        this.ctx.lineWidth = 4;
        this.ctx.strokeStyle = border_color;
        this.ctx.stroke();
        this.ctx.closePath();
    },
    update_position : function(packet) {
        for (let i = 0; i < this.pieces.length; i++) {
            if (packet['character'] == this.pieces[i]['character']) {
                this.pieces[i]['coords'] = packet['coords'];
                break;
            }
        }

        this.draw();
    },
    getCursorPosition : function (event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        return [x, y];
    },
    update_turn : function () {
        
    }
}

// page functions
function add_cards_container(cards) {
    cards_container.style.display = 'flex';
    cards_container.style.flexWrap = 'wrap';

    for (let i = 0; i < cards.length; i++) {
        var img_container = document.createElement('div');
        img_container.className = 'img_container';

        var img = document.createElement('img');
        img.src = '/static/Clue/cards/' + cards[i] + '.png';
        img.id = cards[i];

        var name = document.createElement('span');
        name.innerText = cards[i];

        img_container.appendChild(img);
        img_container.appendChild(document.createElement('br'));
        img_container.appendChild(name);
        cards_container.appendChild(img_container);
    }
}

function add_map(map_data) {
    console.log(map_data);

    game_board.style.display = 'inline-block';
    game_board.style.backgroundImage = 'url("/static/Clue/map/' + map_data['map_file'] + '")';

    // game_board.style.width = map_data['map_width'];

    // var canvas = document.createElement('canvas');
    // canvas.width = map_data['map_width'];
    // canvas.height = map_data['map_height'];

    // var ctx = canvas.getContext('2d');

    // var img = new Image();
    // img.onload = function() {
    //     ctx.drawImage(img, 0, 0);
    // };
    // img.src = '/static/Clue/map/' + map_data['map_file'];

    // game_board.appendChild(canvas);
    game_canvas.start(
        map_data['map_width'], map_data['map_height'],
        game_board, map_data['pieces'], map_data['turn']
    );
}

// connects to socket
function join_game() {
    var url = window.location.href;
    var game_id = url.slice(-6);
    url = url.slice(0, url.length - 12);

    socket.connect(url);

    socket.on('connect', function() {
        var data = {
            'game_id': game_id,
            'username': username_field.value
        };

        errors.innerHTML = '';
        socket.emit('connect_server', data);
    });

    socket.on('initialization', function(server_data) {
        console.log(server_data);

        username = server_data['username'];

        chars = Object.keys(server_data['characters']);
        for (let i = 0; i < chars.length; i++) {
            character = chars[i];
            var img = document.createElement('img');
            img.src = '/static/Clue/cards/' + character + '.png';
            img.id = character;
            if (server_data['characters'][character]['inUse']) {
                if (server_data['characters'][character]['player'] == username) {
                    img.className = 'selected';
                    current_char = character;
                    ready_button.removeAttribute('disabled');
                    if (server_data['characters'][character]['isReady']) {
                        ready_button.className = 'cancel';
                        ready_button.innerText = 'Cancel';
                    } else {
                        ready_button.className = 'primed';
                    }
                } else {
                    img.className = 'taken';
                }
                if (server_data['characters'][character]['isReady']) {
                    img.classList.add('ready');
                }
            }
            character_select.appendChild(img);

            if (!server_data['state']) {
                img.addEventListener('click', function() {
                    let isready = current_char && document.getElementById(current_char).classList.contains('ready')

                    if (
                        this.className != 'taken'
                        && this.className != 'selected'
                        && !isready
                    ) {
                        let data = {
                            'event': 'character_select',
                            'packet': this.id
                        };
                        socket.emit('server_data', data);
                    }
                });
            } 
        }

        if (!server_data['state']) {
            character_select.removeAttribute('hidden');

            if (server_data['is_main_player']) {
                ready_button.removeAttribute('hidden');
                ready_button.addEventListener('click', function() {
                    let value = ready_button.innerText;
                    
                    if (value == 'Ready') {
                        ready_button.innerText = 'Cancel';
                        ready_button.className = 'cancel';
                        socket.emit('server_data', {
                            'event': 'ready',
                            'packet': true
                        });
                    } else {
                        ready_button.innerText = 'Ready';
                        ready_button.className = 'primed';
                        socket.emit('server_data', {
                            'event': 'ready',
                            'packet': false
                        });
                    }
                })
            }
        }

        // unhide chat
        if (server_data['is_main_player']) {
            chat.removeAttribute('hidden');
        
        
            message_field.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    message = message_field.value;
                    message_field.value = '';
                    var data = {
                        'event': 'message',
                        'packet': message
                    };
                    socket.emit('server_data', data);
                }
            });
        }

        if (server_data['state'] == 1) {
            // cards_container.removeAttribute('hidden');
            game_board.removeAttribute('hidden');
            add_map(server_data['map_data']);
        }

        if (server_data['player_cards']) {
            add_cards_container(server_data['player_cards']);
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

    socket.on('chat_event', function(packet) {
        var message = document.createElement('p');

        // TODO #3: change to innerText to prevent malicious attacks
        message.innerHTML = packet;

        messages.prepend(message);
    });

    socket.on('character_selected', function(packet) {
        chars = Object.keys(packet);
            for (let i = 0; i < chars.length; i++) {
                var character = chars[i];
                var img = document.getElementById(character);
                if (packet[character]['inUse']) {
                    if (packet[character]['player'] == username) {
                        img.className = 'selected';
                        current_char = character;

                        if (ready_button.hasAttribute('disabled')) {
                            ready_button.removeAttribute('disabled');
                            ready_button.className = 'primed';
                        }
                    } else {
                        img.className = 'taken';
                    }

                    if (packet[character]['isReady']) {
                        img.classList.add('ready');
                    }
                } else {
                    img.className = '';
                }
            }
    });

    socket.on('start_game', function(packet) {
        console.log(packet);

        character_select.setAttribute('hidden', true);
        ready_button.setAttribute('hidden', true);

        add_map(packet['map_data']);
    });

    socket.on('start_cards', function(packet) {
        console.log(packet);

        add_cards_container(packet);
    });

    socket.on('update_position', function(packet) {
        game_canvas.update_position(packet);
    });
}

// join game button
join_button.onclick = function() {
    if (!username_field.value) {
        return;
    }
    login_div.style.display = 'None';
    join_game();
};

// joins game when enter is pressed
username_field.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        join_button.click();
    }
});
