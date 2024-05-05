from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return 'test'


@socketio.on('test')
def handle_test(json_data):
    print('Received', json_data)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port='42069', debug=True)