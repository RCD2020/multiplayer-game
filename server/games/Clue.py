'''
Robert Davis
2025.02.10
'''

from typing import List
from time import time
import uuid
from json import loads

from server.GameInstance import GameInstance
from server.games.Clue_Helper import shorten_list


class Clue(GameInstance):

    def __init__(self, id: str, settings: str):

        # read game_date file
        with open('static/Clue/game_data.json') as f:
            self.game_data = loads(f.read())
        
        max_players = self.game_data['max_players']
        self.min_players = min(self.game_data['min_players'])
        self.characters = {
            x.split('.')[0]: {'inUse': False}
            for x in self.game_data['available_players']
        }
        self.map_id = None

        # self.characters = {
        #     'Scarlet': {
        #         'inUse': False, 'player': None, 'isReady': False
        #     },
        #     'Mustard': {'inUse': False},
        #     'Plum': {'inUse': False},
        #     'White': {'inUse': False},
        #     'Peacock': {'inUse': False},
        #     'Green': {'inUse': False}
        # }

        super().__init__(
            id, settings,
            'games/Clue/Clue.html', max_players
        )

        self.main_players = {}
        self.main_to_char = {}

        self.events = {
            'message': self.event_message,
            'character_select': self.event_character_select,
            'ready': self.event_ready
        }

        self.ready_data = {
            'id': '',
            'counter': 0
        }
        # self.min_players = 3

        # Game States
        #    0: Waiting for players
        #    1: Game started
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

        # timed events test
        # self.updates.append({
        #     'event': 'chat_event',
        #     'targets': [self.id],
        #     'packet': 'wassup nerd',
        #     'timer': 10
        # })


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

            if self.characters[old_char].get('isReady'):
                return f'Error selecting character: {old_char} is in ready'
            
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


    def event_ready(self, sid, packet):
        if self.game_state != 0:
            return 'Error readying up: Game is not in character selection'


        user = self.sockets[sid]
        character = self.main_to_char[user]

        self.characters[character]['isReady'] = packet

        self.updates.append({
            'event': 'character_selected',
            'targets': [self.id],
            'packet': self.characters
        })

        if self.is_ready():
            ready_id = uuid.uuid4()
            self.ready_data['id'] = ready_id
            self.ready_data['counter'] = 2

            self.updates.append({
                'event': 'chat_event',
                'targets': [self.id],
                'packet': 'Game starting in 3...',
                'server_event': lambda: self.next_ready(ready_id),
                'server_timer': 1
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
    

    def is_ready(self):
        in_use_count = 0

        for character, data in self.characters.items():
            if data['inUse']:
                in_use_count += 1

                if not data['isReady']:
                    return False
                
        if in_use_count >= self.min_players:
            return True
        

    def next_ready(self, id):
        # print(self.ready_data)

        if id == self.ready_data['id'] and self.is_ready():
            if self.ready_data['counter'] > 0:
                self.updates.append({
                    'event': 'chat_event',
                    'targets': [self.id],
                    'packet': f'Game starting in {self.ready_data["counter"]}...',
                    'server_event': lambda: self.next_ready(id),
                    'server_timer': 1
                })
                self.ready_data['counter'] -= 1
            else:
                self.start_game()

    
    def start_game(self):
        self.game_state = 1

        # get which game is going
        options = [
            x for x
            in self.game_data['min_players']
            if x <= len(self.main_players.keys())
        ]
        game = str(max(options))
        self.game_data_2 = self.game_data[game]


        playable_characters = list(self.main_to_char.values())
        playable_characters = shorten_list(
            [
                x for x
                in [
                    x.split('.')[0] for x
                    in self.game_data['available_players']
                ]
                if x not in playable_characters
            ],
            self.game_data_2['player_count'] - len(playable_characters)
        ) + playable_characters
        usable_weapons = shorten_list(
            self.game_data['available_weapons'],
            self.game_data_2['weapon_count']
        )
        usable_weapons = [
            x.split('.')[0] for x
            in usable_weapons
        ]

        print(playable_characters)
        print(usable_weapons)

        # send start_game event to client
        self.updates.append({
            'event': 'start_game',
            'targets': [self.id],
            'packet': {
                'test': 'data here'
            }
        })
    