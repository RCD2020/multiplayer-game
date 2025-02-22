'''
Robert Davis
2024.05.04
'''

from server.ServerInstance import ServerInstance

from flask import Flask, render_template, redirect, request
from flask_socketio import SocketIO, emit, join_room, disconnect

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
socketio = SocketIO(app)
server = ServerInstance()
scheduler = BackgroundScheduler()


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

    return render_template(game.template, id=game_id)


@app.route('/create')
def create_game():
    return render_template('create_game.html', game_types=ServerInstance.GAME_TYPES)


@app.route('/start_game', methods=['POST'])
def start_game():
    'Initializes a game and then joins it'

    game_type = request.form['game_type']
    # start game
    id = server.create_game(game_type)

    # redirect to game page
    return redirect(f'/game/{id}')


# ----------------------------------------------------------------------
# PRODUCTION SOCKETS
# ----------------------------------------------------------------------
def send_update(game):
    # grab updates
    updates = game.get_update_data()

    # emit data to appropriate channels
    # legacy update handler
    # for update in updates:
    #     print(update)
    #     if update['address'] == 'room':
    #         emit('update', update, to=game_id)
    #     elif update['address'] == 'user':
    #         for user in update['target']:
    #             emit('update', update, to=user)

    print(updates)

    for update in updates:
        for target in update['targets']:
            # targets consist of either the game_id or the socket id
            if update.get('timer'):
                scheduler.add_job(
                    func=lambda : socketio.emit(
                        update['event'], update['packet'], to=target
                    ),
                    trigger='interval',
                    seconds=update['timer']
                )
            else:
                socketio.emit(update['event'], update['packet'], to=target)


@socketio.on('connect_server')
def handle_connect_server(data):
    'Authenticates each client'
    # use request.sid to identify client and get request data
    sid = request.sid
    username = data.get('username')
    game_id = data.get('game_id')

    # validate request data
    # all emits should go to same channel to cutdown on client code
    if not username:
        emit('login_error', 'Invalid Username')
        disconnect(sid)
        return
    game = server.get_game(game_id)
    if not game:
        emit('login_error', 'Invalid Game')
        disconnect(sid)
        return

    # register user in ServerInstance and GameInstance
    if not server.register_sid(game_id, username, sid):
        emit('login_error', 'Username Taken')
        disconnect(sid)
        return
    
    # send game initialization data
    server_data = game.get_server_data(sid)
    emit('initialization', server_data)

    # join room and send connect message
    join_room(game_id)
    socketio.emit('message', {
        'user': 'system',
        'message': f'{username} has joined the game'
    }, to=game_id)

    send_update(game)


@socketio.on('disconnect')
def handle_disconnect():
    'Disconnects user from game'

    # get user sid
    sid = request.sid

    # deregister sid from game instance
    server.deregister_sid(sid)


# TODO handle sockets between server and client
@socketio.on('server_data')
def handle_data(data: dict):
    sid = request.sid
    game_id = server.lookup_sid(sid)
    game = server.get_game(game_id)

    # send data to GameInstance
    error = game.send_data(sid, data)
    if error:
        print(error, data)
        emit('game_error', error)

    send_update(game)


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
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    socketio.run(app, host='0.0.0.0', debug=True)

