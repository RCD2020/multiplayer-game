'''
Robert Davis
2025.02.10
'''

from typing import List
from time import time

from server.GameInstance import GameInstance


class Clue(GameInstance):

    def __init__(self, id: str, settings: str):
        self.characters = {
            'Scarlet': {
                'inUse': False, 'player': None
            },
            'Mustard': {'inUse': False},
            'Plum': {'inUse': False},
            'White': {'inUse': False},
            'Peacock': {'inUse': False},
            'Green': {'inUse': False}
        }

        super().__init__(
            id, settings,
            'games/Clue/Clue.html', len(self.characters.keys())
        )

        self.main_players = {}
        self.main_to_char = {}

        self.events = {
            'message': self.event_message,
            'character_select': self.event_character_select
        }

        # Game States
        #    0: Waiting for players
        self.game_state = 0

    
    def send_data(self, sid: str, data: dict):
        'Proccesses chat messages from the client'

        print(sid, data)

        # verify user
        user = self.sockets[sid]
        if user not in self.users:
            return 'Invalid User'
        if not self.is_main_player(sid):
            return 'User is Spectator'
        
        # call correct event
        event_type = data.get('event')
        packet = data.get('packet')
        if not event_type:
            return 'Invalid Data - Missing "event"'
        if packet == None:
            return 'Invalid Data - Missing "packet"'
        if event_type not in self.events:
            return f'Invalid Data - event "{event_type}"'
        
        return self.events[event_type](sid, packet)


    def event_message(self, sid, packet):
        # print('event_message:', packet)

        self.updates.append({
            'event': 'chat_event',
            'targets': [self.id],
            'packet': self.sockets[sid] + ': ' + packet
        })


    def event_character_select(self, sid, packet):
        # print('event_character_select:', packet)

        user = self.sockets[sid]
        
        # data validation
        if not (self.game_state == 0):
            return 'Error selecting character: game_state != 0'
        if not (packet in self.characters):
            return f'Error selecting character: {packet} character not found'
        if self.characters[packet]['inUse']:
            return f'Error selecting character: {packet} already taken'
        

        # server: deselect previously selected character
        if user in self.main_to_char:
            old_char = self.main_to_char[user]
            self.characters[old_char]['inUse'] = False
            self.characters[old_char]['player'] = None
        
        # server: select selected character
        self.characters[packet]['inUse'] = True
        self.characters[packet]['player'] = user
        self.main_to_char[user] = packet


        # send updated character selection to clients
        self.updates.append({
            'event': 'character_selected',
            'targets': [self.id],
            'packet': self.characters
        })
    

    def register_sid(self, name, sid):
        '''
        Associates a user with a socket id. Returns false if there is a
        socket id collision
        '''

        if self.users.get(name):
            return False
        self.users[name] = sid
        self.sockets[sid] = name
        self.last_action = time()

        # if max players has not been reached and game is not in session,
        #    then add user to main players
        if not self.game_state and len(self.main_players.keys()) < self.max_players:
            self.main_players[name] = {
                'is_ready': False
            }

            self.updates.append({
                'event': 'chat_event',
                'targets': [self.id],
                'packet': f'{name} joined the game.'
            })

        return True
    

    def is_main_player(self, sid):
        return self.sockets[sid] in self.main_players
    

    def get_server_data(self, sid):
        data = {
            'state': self.game_state,
            'is_main_player': self.is_main_player(sid),
            'characters': self.characters,
            'username': self.sockets[sid]
        }

        return data
    