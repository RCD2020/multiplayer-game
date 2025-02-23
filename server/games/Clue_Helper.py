'''
Robert Davis
2025.02.22
'''

from random import randint


def shorten_list(arr: list, count):
    arr = arr.copy()
    
    while len(arr) > count:
        arr.pop(randint(0, len(arr)-1))
    
    return arr


if __name__ == '__main__':
    print(shorten_list([0, 1, 2, 3, 4, 5], 3))
