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

        self.main_players = set()
        self.main_to_char = {}

        # Game States
        #    0: Waiting for players
        self.game_state = 0

    
    def send_data(self, sid: str, data: dict):
        'Proccesses chat messages from the client'

        print(sid, data)

        # initialize out_data
        out_data = {}


        # verify user
        user = self.sockets[sid]
        if user not in self.users:
            return 'Invalid User'
        if not self.is_main_player(sid):
            return 'User is Spectator'
        

        # verify correctly formatted
        data_type = data.get('type')
        if not data_type or not user:
            return 'Invalid Data'
        

        # read data
        elif data_type == 'message':
            message = data.get('message')
            address = data.get('address')
            if message == None or not address:
                return 'Missing Message or Address'
            
            out_data['type'] = data_type
            out_data['user'] = user
            out_data['message'] = message
            out_data['address'] = address

            if address == 'user':
                target = data.get('target')
                if not target:
                    return 'Missing "target" on address type "user"'
                
                out_data['target'] = []
                for recipient in target:
                    if self.users[recipient]:
                        out_data['target'].append(self.users[recipient])

        elif (
            data_type == 'character_select'
            and self.game_state == 0
            and data.get('character')
            and data.get('character') in self.characters
            and not self.characters[data.get('character')]['inUse']
        ):
            character = data.get('character')

            out_data['type'] = 'character_selected'
            out_data['address'] = 'room'

            if user in self.main_to_char:
                old_char = self.main_to_char[user]
                self.characters[old_char]['inUse'] = False
                self.characters[old_char]['player'] = None
            
            self.characters[character]['inUse'] = True
            self.characters[character]['player'] = user
            self.main_to_char[user] = character

            out_data['characters'] = self.characters

            # self.updates.append({
            #     'type': 'character_select_success',
            #     'character': character,
            #     'address': 'user',
            #     'target': [sid]
            # })
            # print(self.characters)



        if out_data:
            self.updates.append(out_data)
    

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
        if not self.game_state and len(self.main_players) < self.max_players:
            self.main_players.add(name)

            self.updates.append({
                'type': 'chat_event',
                'message': f'{name} joined the game.',
                'address': 'room'
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
    