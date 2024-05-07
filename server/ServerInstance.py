'''
Robert Davis
2024.05.05
'''

from server.GameInstance import GameInstance

from typing import Dict

from random import choice
from time import time


class ServerInstance:
    games: Dict[str, GameInstance] = {}

    def __init__(self):
        'TODO initialization'


    def create_game(self) -> str:
        'Creates a new game and returns the id'

        # create id for game
        id = self._new_game_id()

        # create game instance
        new_game = GameInstance(id)

        # add game instance to games
        self.games[id] = new_game

        # return id
        return id


    def clear_old_games(self):
        'clear games with a last_action of over an hour ago'

        # TODO get barrier for deletion (current time - an hour)

        # TODO loop through games and destroy old games

    
    def _new_game_id(self) -> str:
        '''
        Creates a new game id that doesn\'t collide with any other
        game instances
        '''

        # generate random id
        def generate_id() -> str:
            'Generates the id'
            valid_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            
            return ''.join([choice(valid_chars) for _ in range(6)])


        # check for collision
        id = generate_id()
        while id in self.games:
            id = generate_id()

        # return id
        return id
    

    def get_game(self, id: str) -> GameInstance:
        'Gets the game with the matching id'

        if id in self.games:
            return self.games[id]
        else:
            return None

    
    def check_user(self, game_id: str, name: str) -> bool:
        '''
        Checks for user with name in game_id in the GameInstance
        Returns true or false if user exists
        '''

        return self.games[game_id].check_user(name)

    
    def is_user_online(self, game_id: str, name: str) -> bool:
        'Checks if the user has a sid registered in the GameInstance'

        return self.games[game_id].is_logged_in(name)


    def add_user(self, game_id: str, name: str, sid: str):
        'Registers a user to the GameInstance'

        # call GameInstance function to add new user
        self.games[game_id].add_user(name, sid)


    def register_sid(self, game_id: str, name: str, sid: str):
        'Updates socket id for user in GameInstance'

        # TODO add sid to user
    
    
    def deregister_sid(self, game_id: str, name: str):
        'Deregisters associated socket id with user in GameInstance'

        # TODO remove sid from user
