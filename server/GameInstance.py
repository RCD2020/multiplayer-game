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
    

    def check_user(self, name: str) -> bool:
        'Checks if there is a user with name'

        return name in self.users
    

    def is_logged_in(self, name: str) -> bool:
        'Checks if there is an associated socket id with name'

        return True if self.users[name] else False
    

    def add_user(self, name: str, sid: str):
        'Adds a user associated with a socket'

        self.users[name] = sid
