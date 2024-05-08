'''
Robert Davis
2024.05.05
'''

from typing import List
from time import time


class GameInstance:

    def __init__(self, id: str):
        self.id = id
        self.last_action = time()
        self.users = {}
        self.sockets = {}
        self.updates = []
        self.server_data = {}
    

    def check_user(self, name: str) -> bool:
        'Checks if there is a user with name'

        return name in self.users
    

    def is_logged_in(self, name: str) -> bool:
        'Checks if there is an associated socket id with name'

        return True if self.users[name] else False


    def register_sid(self, name: str, sid: str) -> bool:
        '''
        Associates a user with a socket id. Returns false if there is a
        socket id collision
        '''

        if self.users.get(name):
            return False
        self.users[name] = sid
        self.sockets[sid] = name
        self.last_action = time()
        return True


    def deregister_sid(self, sid: str):
        'Unassociates a user with a socket id'

        name = self.sockets[sid]
        self.users[name] = None
        del self.sockets[sid]


    def get_server_data(self) -> dict:
        'Grabs all existing server data to initialize client side'

        # return server data
        return self.server_data

    
    def send_data(self, sid: str, data):
        'Processes data from the client'

        # process data
        # this would be more processed in an actual game instance

        # send processed data to self.updates
        self.updates.append(data)
        self.last_action = time()


    def get_update_data(self) -> List[dict]:
        'Grabs all the new server updates to send out'

        # grab update data
        updates = self.updates

        # clear update data
        self.update = {}

        # return update data
        return updates
