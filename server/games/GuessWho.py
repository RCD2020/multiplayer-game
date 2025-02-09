'''
Robert Davis
2025.02.08
'''

from typing import List
from server.GameInstance import GameInstance


class GuessWho(GameInstance):

    def __init__(self, id: str, settings: str):
        super().__init__(id, settings, 'games/GuessWho/GuessWho.html')

    
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

    
    def get_update_data(self) -> List[dict]:
        return super().get_update_data()
    