'''
Robert Davis
2024.05.05
'''

from random import choice
from time import time


class ServerInstance:
    games = {}

    def __init__(self):
        'TODO initialization'


    def create_game(self) -> str:
        'Creates a new game and returns the id'

        # create id for game
        id = self.new_game_id()

        # TODO create game instance

        # TODO add game instance to games

        # return id
        return id


    def clear_old_games(self):
        'TODO clear games with a last_action of over an hour ago'

    
    def new_game_id(self) -> str:
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
