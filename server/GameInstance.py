'''
Robert Davis
2024.05.05
'''

from time import time


class GameInstance:

    def __init__(self, id: str):
        self.id = id
        self.last_action = time()
