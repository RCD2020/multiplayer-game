'''
Robert Davis
2024.05.04
'''

from server.ServerInstance import ServerInstance

from flask import Flask, render_template, redirect, request
from flask_socketio import SocketIO, emit, join_room, leave_room

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

    # TODO check for valid player, doesn't collide with existing player

    # TODO if invalid, redirect to homepage with invalid player error

    # TODO join game

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
def handle_connect_server(game_id):
    'Authenticates each client'
    # TODO use request.sid to identify client
    print(request.sid)
    print(game_id)

    # TODO save to custom identifier as the sid changes everytime they
    # connect


# TODO handle deregistration of connected user
@socketio.on('disconnect')
def handle_disconnect():
    'Disconnects user from game'

    # TODO get user sid
    print(request.sid)

    # TODO deregister sid from game instance


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
