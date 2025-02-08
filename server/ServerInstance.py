'''
Robert Davis
2024.05.05
'''

from server.GameInstance import GameInstance
from server.games.ChatRoom import ChatRoom
from server.games.GuessWho import GuessWho

from typing import Dict

from random import choice
from time import time


class ServerInstance:
    GAME_TYPES = {
        'Chat Room': ChatRoom,
        'Guess Who': GuessWho
    }

    def __init__(self):
        'initialization'

        self.games: Dict[str, GameInstance] = {}
        self.sockets: Dict[str, str] = {}


    def create_game(self, game_type, settings=None) -> str:
        'Creates a new game and returns the id'

        # create id for game
        id = self._new_game_id()

        # create game instance
        new_game = self.GAME_TYPES[game_type](id, settings)

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
        

    def lookup_sid(self, sid: str) -> str:
        'Gets the game id based off the associated socket id'

        return self.sockets.get(sid)

    
    def is_user_online(self, game_id: str, name: str) -> bool:
        'Checks if the user has a sid registered in the GameInstance'

        return self.games[game_id].is_logged_in(name)


    def register_sid(self, game_id: str, name: str, sid: str) -> bool:
        '''
        Updates socket id for user in GameInstance and self.sockets,
        Will return False if socket id is already registered.
        '''

        # add sid to user
        if not self.games[game_id].register_sid(name, sid):
            return False
        self.sockets[sid] = game_id
        return True
    
    
    def deregister_sid(self, sid: str):
        'Deregisters associated socket id with user in GameInstance'

        # remove sid from user
        game_id = self.sockets.get(sid)
        if not game_id:
            return
        self.games[game_id].deregister_sid(sid)
        del self.sockets[sid]
