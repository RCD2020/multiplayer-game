'''
Robert Davis
2024.05.04
'''

from server.ServerInstance import ServerInstance

from flask import Flask, render_template, redirect, request
from flask_socketio import (
    SocketIO, emit, join_room, leave_room, disconnect
)

app = Flask(__name__)
socketio = SocketIO(app)
server = ServerInstance()


# ----------------------------------------------------------------------
# PRODUCTION LANDINGS
# ----------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('game_id.html', errors=[])


@app.route('/game/<game_id>')
def game(game_id):
    # get valid game
    game = server.get_game(game_id)
    if game == None:
        return render_template(
            'game_id.html', errors=['Game not found']
        )

    return render_template('game.html', id=game_id)


@app.route('/create')
def create_game():
    return render_template('create_game.html')


@app.route('/start_game', methods=['POST'])
def start_game():
    'Initializes a game and then joins it'
    # start game
    id = server.create_game()

    # redirect to game page
    return redirect(f'/game/{id}')


# ----------------------------------------------------------------------
# PRODUCTION SOCKETS
# ----------------------------------------------------------------------
# TODO handle identification of clients
@socketio.on('connect_server')
def handle_connect_server(data):
    'Authenticates each client'
    # use request.sid to identify client and get request data
    sid = request.sid
    username = data.get('username')
    game_id = data.get('game_id')

    # validate request data
    # TODO all emits should go to same channel to cutdown on client code
    if not username:
        emit('invalid_username')
        disconnect(sid)
        return
    game = server.get_game(game_id)
    if not game:
        emit('invalid_game')
        disconnect(sid)
        return

    # register user in ServerInstance and GameInstance
    if not server.register_sid(game_id, username, sid):
        emit('username_taken')
        disconnect(sid)
        return

    # join room and send connect message
    join_room(game_id)
    socketio.emit('message', {
        'user': 'system',
        'message': f'{username} has joined the game'
    }, to=game_id)


# TODO handle deregistration of connected user
@socketio.on('disconnect')
def handle_disconnect():
    'Disconnects user from game'

    # get user sid
    sid = request.sid

    # TODO deregister sid from game instance
    server.deregister_sid(sid)


# TODO handle sockets between server and client
@socketio.on('server_data')
def handle_data(data: dict):
    socketio.emit('client_data', data)


# ----------------------------------------------------------------------
# TEST
# ----------------------------------------------------------------------
@app.route('/test')
def test_landing():
    return render_template('test_landing.html')


@socketio.on('send_json')
def handle_send_json():
    emit('json_response', {'test': True})


@socketio.on('send_server')
def handle_send_server(json):
    socketio.emit('send_client', json)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port='42069', debug=True)
