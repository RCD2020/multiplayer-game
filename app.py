'''
Robert Davis
2024.05.04
'''

from server.ServerInstance import ServerInstance

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)
server = ServerInstance()


@app.route('test/')
def test_landing():
    return render_template('index.html')


@socketio.on('send_json')
def handle_send_json():
    emit('json_response', {'test': True})


@socketio.on('send_server')
def handle_send_server(json):
    socketio.emit('send_client', json)


@socketio.on('connect')
def handle_connect():
    # this can be used as a unique identifier for clients
    print('sid', request.sid)


# TODO handle sockets between server and client
@socketio.on('server_data')
def handle_data(data: dict):
    socketio.emit('client_data', data)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port='42069', debug=True)