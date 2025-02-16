import numpy as np
from numpy.linalg import inv


# M1 = np.array([
#     [0.8189330101, 0.3618667424, -0.1288597137],
#     [0.0329845436, 0.9293118715,  0.0361456387],
#     [0.0482003018, 0.2643662691,  0.6338517070]
# ]) only for CIE XYZ to LMS
M1 = np.array([ # this is sRGB to LMS
    [0.4122214708, 0.5363325363, 0.0514459929],
    [0.2119034982, 0.6806995451, 0.1073969566],
    [0.0883024619, 0.2817188376, 0.6299787005]
])
M2 = np.array([
    [0.2104542553,  0.7936177850, -0.0040720468],
    [1.9779984951, -2.4285922050,  0.4505937099],
    [0.0259040371,  0.7827717662, -0.8086757660]
])


def rgb2oklab(r, g, b):

    rgb = np.array([
        [r],
        [g],
        [b]
    ])

    lms = np.dot(M1, rgb)
    lms_prime = lms**(1/3)
    oklabs = np.dot(M2, lms_prime)

    return np.rot90(oklabs)[0]


def oklab2rgb(oklabs):
    oklabs_prime = np.rot90([oklabs], 3)

    lms_prime = np.dot(inv(M2), oklabs_prime)
    lms = lms_prime ** 3
    rgb = np.dot(inv(M1), lms)

    return [(
        int(round(r)),
        int(round(g)),
        int(round(b))
    ) for r, g, b in np.rot90(rgb)][0]


if __name__ == '__main__':
    rgb = (255, 0, 0)
    oklabs = rgb2oklab(*rgb)
    print(oklabs)
    rgb = oklab2rgb(oklabs)
    print(rgb)
