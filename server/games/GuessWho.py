'''
Robert Davis
2025.02.08
'''

from typing import List
from server.GameInstance import GameInstance


class GuessWho(GameInstance):

    def __init__(self, id: str, settings: str):
        super().__init__(id, settings, 'games/GuessWho/GuessWho.html', 2)

    
    def send_data(self, sid: str, data: dict):
        'Proccesses chat messages from the client'

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
        event = 'chat_event'
        targets = []
        packet = user + ': ' + message

        if address == 'user':
            target = data.get('target')
            if not target:
                return 'Missing "target" on address type "user"'
            
            for recipient in target:
                if self.users[recipient]:
                    targets.append(self.users[recipient])
        else:
            targets.append(self.id)

        self.updates.append({
            'event': event,
            'targets': targets,
            'packet': packet
        })

    
    def get_update_data(self) -> List[dict]:
        return super().get_update_data()
    

    def register_sid(self, name, sid):
        registered = super().register_sid(name, sid)
        if registered:
            self.updates.append({
                'event': 'chat_event',
                'targets': [self.id],
                'packet': f'{name} joined the game.'
            })

        return registered
    