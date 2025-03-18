'''
Robert Davis
2025.02.10
'''

from typing import List
from time import time
import uuid
from json import loads
from random import choice, randint

from server.GameInstance import GameInstance
from server.games.Clue_Helper import shorten_list, reorder_starting_from_player


class Clue(GameInstance):

    def __init__(self, id: str, settings: str):

        # read game_date file
        with open('static/Clue/game_data.json') as f:
            self.game_data = loads(f.read())
        
        max_players = self.game_data['max_players']
        self.min_players = min(self.game_data['min_players'])
        self.characters = {
            x: {'inUse': False, 'isReady': False}
            for x in self.game_data['available_players']
        }
        self.map_id = None

        # self.characters = {
        #     'Scarlet': {
        #         'inUse': False, 'player': None, 'isReady': False
        #     },
        #     'Mustard': {'inUse': False},
        #     'Plum': {'inUse': False},
        #     'White': {'inUse': False},
        #     'Peacock': {'inUse': False},
        #     'Green': {'inUse': False}
        # }

        super().__init__(
            id, settings,
            'games/Clue/Clue.html', max_players
        )

        self.main_players = {}
        self.main_to_char = {}

        self.events = {
            'message': self.event_message,
            'character_select': self.event_character_select,
            'ready': self.event_ready,
            'update_position': self.event_update_position,
            'suggestion': self.event_suggestion,
            'accusation': self.event_accusation
        }

        self.ready_data = {
            'id': '',
            'counter': 0
        }
        # self.min_players = 3

        # Game States
        #    0: Waiting for players
        #    1: Game started
        self.game_state = 0

        self.already_suggested = False

    
    def send_data(self, sid: str, data: dict):
        'Proccesses chat messages from the client'

        print(sid, data)

        # verify user
        user = self.sockets[sid]
        if user not in self.users:
            return 'Invalid User'
        if not self.is_main_player(sid):
            return 'User is Spectator'
        
        # call correct event
        event_type = data.get('event')
        packet = data.get('packet')
        if not event_type:
            return 'Invalid Data - Missing "event"'
        if packet == None:
            return 'Invalid Data - Missing "packet"'
        if event_type not in self.events:
            return f'Invalid Data - event "{event_type}"'
        
        return self.events[event_type](sid, packet)
    


    # ----------------------------------------------
    #                  GAME EVENTS
    # ----------------------------------------------

    def event_message(self, sid, packet):
        # print('event_message:', packet)

        self.updates.append({
            'event': 'chat_event',
            'targets': [self.id],
            'packet': self.sockets[sid] + ': ' + packet
        })

        # timed events test
        # self.updates.append({
        #     'event': 'chat_event',
        #     'targets': [self.id],
        #     'packet': 'wassup nerd',
        #     'timer': 10
        # })


    def event_character_select(self, sid, packet):
        # print('event_character_select:', packet)

        user = self.sockets[sid]
        
        # data validation
        if not (self.game_state == 0):
            return 'Error selecting character: game_state != 0'
        if not (packet in self.characters):
            return f'Error selecting character: {packet} character not found'
        if self.characters[packet]['inUse']:
            return f'Error selecting character: {packet} already taken'
        
        

        # server: deselect previously selected character
        if user in self.main_to_char:
            old_char = self.main_to_char[user]

            if self.characters[old_char].get('isReady'):
                return f'Error selecting character: {old_char} is in ready'
            
            self.characters[old_char]['inUse'] = False
            self.characters[old_char]['player'] = None
        
        # server: select selected character
        self.characters[packet]['inUse'] = True
        self.characters[packet]['player'] = user
        self.main_to_char[user] = packet


        # send updated character selection to clients
        self.updates.append({
            'event': 'character_selected',
            'targets': [self.id],
            'packet': self.characters
        })


    def event_ready(self, sid, packet):
        if self.game_state != 0:
            return 'Error readying up: Game is not in character selection'


        user = self.sockets[sid]
        character = self.main_to_char[user]

        self.characters[character]['isReady'] = packet

        self.updates.append({
            'event': 'character_selected',
            'targets': [self.id],
            'packet': self.characters
        })

        if self.is_ready():
            ready_id = uuid.uuid4()
            self.ready_data['id'] = ready_id
            self.ready_data['counter'] = 2

            self.updates.append({
                'event': 'chat_event',
                'targets': [self.id],
                'packet': 'Game starting in 3...',
                'server_event': lambda: self.next_ready(ready_id),
                'server_timer': 1
            })


    def event_update_position(self, sid, packet):
        user = self.sockets[sid]
        character = self.main_to_char[user]

        if self.is_turn(sid):
            self.set_piece_position(character, packet)

            self.updates.append({
                'event': 'update_position',
                'targets': [self.id],
                'packet': {
                    'character': character,
                    'coords': packet
                }
            })


    def event_suggestion(self, sid, packet):
        user = self.sockets[sid]
        character = self.main_to_char[user]

        if self.already_suggested:
            return 'Already submitted suggestion'

        if self.is_turn(sid):
            suspect = packet['suspect']
            weapon = packet['weapon']
            room = packet['room']

            ask_order = reorder_starting_from_player(self.turn_order, user)

            print(ask_order)
            print(user)
            print(character)
            print(self.main_players[user]['cards'])

            self.chat_event(
                f'{user}: I suggest that the crime was committed in the {room}'
                f' by {suspect} with the {weapon}.'
            )

            for player in ask_order:
                if (
                    suspect in self.main_players[player]['cards']
                    or weapon in self.main_players[player]['cards']
                    or room in self.main_players[player]['cards']
                ):
                    self.chat_event(
                        player + ': I suppose I\'ve heard a thing or two.'
                    )
                    break
                else:
                    self.chat_event(
                        player + ': I\'ve not heard anything of these things.'
                    )

            print(packet)
            self.already_suggested = True 
        else:
            return 'Error: It is not your turn.'


    def event_accusation(self, sid, packet):
        user = self.sockets[sid]
        character = self.main_to_char[user]

        if self.is_turn(sid):
            pass
        else:
            return 'Error: It is not your turn.'
    






    def register_sid(self, name, sid):
        '''
        Associates a user with a socket id. Returns false if there is a
        socket id collision
        '''

        if self.users.get(name):
            return False
        self.users[name] = sid
        self.sockets[sid] = name
        self.last_action = time()

        # if max players has not been reached and game is not in session,
        #    then add user to main players
        if not self.game_state and len(self.main_players.keys()) < self.max_players:
            self.main_players[name] = {
                'is_ready': False
            }

            self.updates.append({
                'event': 'chat_event',
                'targets': [self.id],
                'packet': f'{name} joined the game.'
            })

        return True
    

    def is_main_player(self, sid):
        return self.sockets[sid] in self.main_players
    

    def get_server_data(self, sid):
        data = {
            'state': self.game_state,
            'is_main_player': self.is_main_player(sid),
            'characters': self.characters,
            'username': self.sockets[sid],
            'already_suggested': self.already_suggested
        }

        if self.game_state > 0:
            data['map_data'] = self.map_data()
            data['card_data'] = self.card_data()
        if self.sockets[sid] in self.main_players and self.game_state > 0:
            data['player_cards'] = self.main_players[self.sockets[sid]]['cards']

        return data
    

    def is_ready(self):
        in_use_count = 0

        for character, data in self.characters.items():
            if data['inUse']:
                in_use_count += 1

                if not data['isReady']:
                    return False
                
        if in_use_count != len(list(self.main_players.keys())):
            return False
                
        if in_use_count >= self.min_players:
            return True
        

    def next_ready(self, id):
        # print(self.ready_data)

        if id == self.ready_data['id'] and self.is_ready():
            if self.ready_data['counter'] > 0:
                self.updates.append({
                    'event': 'chat_event',
                    'targets': [self.id],
                    'packet': f'Game starting in {self.ready_data["counter"]}...',
                    'server_event': lambda: self.next_ready(id),
                    'server_timer': 1
                })
                self.ready_data['counter'] -= 1
            else:
                self.start_game()

    
    def start_game(self):
        self.game_state = 1

        # get which game is going
        options = [
            x for x
            in self.game_data['min_players']
            if x <= len(self.main_players.keys())
        ]
        game = str(max(options))
        self.game_data_2 = self.game_data[game]


        playable_characters = list(self.main_to_char.values())
        playable_characters = shorten_list(
            [
                x for x
                in self.game_data['available_players']
                if x not in playable_characters
            ],
            self.game_data_2['player_count'] - len(playable_characters)
        ) + playable_characters
        usable_weapons = shorten_list(
            self.game_data['available_weapons'],
            self.game_data_2['weapon_count']
        )
        movable_rooms: list = self.game_data_2['rooms'].copy()

        self.game_characters = playable_characters.copy()
        self.game_weapons = usable_weapons.copy()
        self.game_rooms = movable_rooms.copy()

        # print(playable_characters)
        # print(usable_weapons)

        self.pieces = []
        i = 0
        for x in playable_characters:
            self.pieces.append({
                'character': x,
                'coords': self.game_data_2['starting_positions'][i],
                'color': self.game_data['player_colors'][x]
            })
            i += 1
    

        # pick place, weapon, killer
        place = choice(movable_rooms)
        weapon = choice(usable_weapons)
        killer = choice(playable_characters)

        self.crime = {
            'room': place,
            'weapon': weapon,
            'killer': killer
        }

        print(self.crime)


        # give out the rest of the cards
        movable_rooms.remove(place)
        usable_weapons.remove(weapon)
        playable_characters.remove(killer)

        cards = movable_rooms + usable_weapons + playable_characters

        players = list(self.main_players.keys())
        self.turn_order = players
        self.turn = 0
        
        for x in players:
            self.main_players[x]['cards'] = []

        i = 0
        while (len(cards) > 0):
            card = choice(cards)
            cards.remove(card)

            self.main_players[players[i]]['cards'].append(card)
            i += 1
            if i == len(players):
                i = 0

        # print(self.main_players)
        print(self.users)


        # send start_game event to client
        self.updates.append({
            'event': 'start_game',
            'targets': [self.id],
            'packet': {
                'map_data': self.map_data(),
                'card_data': self.card_data()
            }
        })
        
        for x in players:
            self.updates.append({
                'event': 'start_cards',
                'targets': [self.users[x]],
                'packet': self.main_players[x]['cards']
            })

        self.player_turn()
    

    def set_piece_position(self, character, coord):
        for x in self.pieces:
            if x['character'] == character:
                x['coords'] = coord
                return

    
    def map_data(self):
        return {
            'map_file': self.game_data_2['map'],
            'map_width': self.game_data_2['map_width'],
            'map_height': self.game_data_2['map_height'],
            'pieces': self.pieces,
            'turn': self.turn_order[self.turn]
        }
    
    
    def is_turn(self, sid):
        if self.turn_order[self.turn] == self.sockets[sid]:
            return True
        return False


    def next_turn(self):
        self.turn += 1
        if self.turn == len(self.turn_order):
            self.turn = 0
        self.already_suggested = False

        # let players know whose turn it is
        self.player_turn()


    def chat_event(self, message, targets:list=None):
        if targets == None:
            targets = [self.id]

        self.updates.append({
            'event': 'chat_event',
            'targets': targets,
            'packet': message
        })

    
    def player_turn(self):
        user = self.turn_order[self.turn]

        self.chat_event(f'It is {user}\'s turn.')

        roll = randint(2, 12)
        self.chat_event(f'{user} rolled a {roll}.')


    def card_data(self):
        return {
            'suspects': self.game_characters,
            'weapons': self.game_weapons,
            'rooms': self.game_rooms
        }

    