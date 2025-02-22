'''
Robert Davis
2024.05.08
'''

from typing import List
from server.GameInstance import GameInstance


class ChatRoom(GameInstance):


    def __init__(self, id: str, settings: str):
        super().__init__(id, settings, 'ChatRoom.html', 99)

        self.events = {
            'message': self.event_message
        }

    
    def send_data(self, sid: str, data: dict):
        'Processes chat messages from the client'

        # print(sid, data)

        # verify user
        user = self.sockets[sid]
        if user not in self.users:
            return 'Invalid User'

        # call correct event
        event_type = data.get('event')
        packet = data.get('packet')
        if not event_type:
            return 'Invalid Data - Missing "event"'
        if not packet:
            return 'Invalid Data - Missing "packet"'
        if event_type not in self.events:
            return f'Invalid Data - event "{event_type}"'
        
        return self.events[event_type](sid, packet)


        # legacy data
        # return
        # # verify correctly formatted
        # user = self.sockets[sid]
        # message = data.get('message')
        # address = data.get('address')
        # if not user or message == None or not address:
        #     return 'Invalid Data'

        # # verify user
        # if user not in self.users:
        #     return 'Invalid User'

        # # add to updates
        # event = 'chat_event'
        # targets = []
        # packet = user + ': ' + message
        # # packet = {
        # #     'message': message,
        # # }
        # if address == 'user':
        #     target = data.get('target')
        #     if not target:
        #         return 'Missing "target" on address type "user"'
            
        #     for recipient in target:
        #         if self.users[recipient]:
        #             targets.append(self.users[recipient])
        # else:
        #     targets.append(self.id)

        # self.updates.append({
        #     'event': event,
        #     'targets': targets,
        #     'packet': packet
        # })


    def event_message(self, sid, packet):
        # print('event_message:', packet)

        self.updates.append({
            'event': 'chat_event',
            'targets': [self.id],
            'packet': self.sockets[sid] + ': ' + packet
        })

    
    def get_update_data(self) -> List[dict]:
        return super().get_update_data()
    
    
    def register_sid(self, name, sid):
        registered = super().register_sid(name, sid)
        if registered:
            self.updates.append({
                'event': 'chat_event',
                'packet': f'{name} joined the game.', # {'message': f'{name} joined the game.'},
                'targets': [self.id]
            })

        return registered
