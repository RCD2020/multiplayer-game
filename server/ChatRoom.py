'''
Robert Davis
2024.05.08
'''

from typing import List
from server.GameInstance import GameInstance


class ChatRoom(GameInstance):

    def __init__(self, id: str):
        super().__init__(id)

    
    def send_data(self, sid: str, data: dict):
        'Proccesses chat messages from the client'

        # verify correctly formatted
        user = data.get('user')
        message = data.get('message')
        address = data.get('address')
        if not user or message == None or not address:
            return 'Invalid Data'

        # verify user
        if user not in self.users:
            return 'Invalid User'

        # add to updates
        out_data = {
            'message': message,
            'address': address
        }
        if address == 'user':
            target = data.get('target')
            if not target:
                return 'Missing "target" on address type "user"'
            
            out_data['target'] = []
            for recipient in target:
                out_data['target'].append(self.users[recipient])

    
    def get_update_data(self) -> List[dict]:
        return super().get_update_data()
    