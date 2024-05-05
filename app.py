from flask import Flask, render_template, url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('send_json')
def handle_send_json():
    emit('json_response', {'test': True})


@socketio.on('send_server')
def handle_send_server(json):
    socketio.emit('send_client', json)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port='42069', debug=True)