'''
Robert Davis
2024.05.04
'''

from server.ServerInstance import ServerInstance

from flask import Flask, render_template, redirect, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)
server = ServerInstance()


# ----------------------------------------------------------------------
# PRODUCTION LANDINGS
# ----------------------------------------------------------------------
@app.route('/')
def join_game():
    return render_template('game_id.html')


@app.route('/game', methods=['POST'])
def game():
    # TODO check for valid game

    # TODO if invalid, redirect to homepage with invalid id error

    # TODO check for valid player, doesn't collide with existing player

    # TODO if invalid, redirect to homepage with invalid player error

    # TODO join game

    return request.form


# TODO game creation page
@app.route('/create')
def create_game():
    return render_template('create_game.html')


# ----------------------------------------------------------------------
# PRODUCTION SOCKETS
# ----------------------------------------------------------------------
# TODO handle identification of clients
@socketio.on('connect')
def handle_connect():
    'Authenticates each client'
    # TODO use request.sid to identify client

    # TODO save to custom identifier as the sid changes everytime they
    # connect


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