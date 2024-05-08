'''
Robert Davis
2024.05.05
'''

from time import time


class GameInstance:

    def __init__(self, id: str):
        self.id = id
        self.last_action = time()
        self.users = {}
        self.sockets = {}
    

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
        return True


    def deregister_sid(self, sid: str):
        'Unassociates a user with a socket id'

        name = self.sockets[sid]
        self.users[name] = None
        del self.sockets[sid]
