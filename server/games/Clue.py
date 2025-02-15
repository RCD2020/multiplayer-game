'''
Robert Davis
2025.02.10
'''

from typing import List
from time import time

from server.GameInstance import GameInstance


class Clue(GameInstance):

    def __init__(self, id: str, settings: str):
        super().__init__(id, settings, 'games/Clue/Clue.html', 6)

        self.main_players = set()

        # Game States
        #    0: Waiting for players
        self.game_state = 0

    
    def send_data(self, sid: str, data: dict):
        'Proccesses chat messages from the client'

        print(sid, data)

        # verify correctly formatted
        user = self.sockets[sid]
        message = data.get('message')
        address = data.get('address')
        if not user or message == None or not address:
            return 'Invalid Data'

        # verify user
        if user not in self.users:
            return 'Invalid User'

        # add to updates
        out_data = {
            'user': user,
            'message': message,
            'address': address
        }
        if address == 'user':
            target = data.get('target')
            if not target:
                return 'Missing "target" on address type "user"'
            
            out_data['target'] = []
            for recipient in target:
                if self.users[recipient]:
                    out_data['target'].append(self.users[recipient])

        self.updates.append(out_data)

    
    def get_update_data(self, sid) -> List[dict]:
        return super().get_update_data(sid)
    

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

        return True
    