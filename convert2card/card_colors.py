from oklab import rgb2oklab

COLORS = [ # this is the Microsoft Paint color palette
    (  0,   0,   0),
    (255, 255, 255),
    (127, 127, 127),
    (200, 191, 231),
    (136,   0,  20),
    (185, 120,  88),
    (255, 125,  39),
    (255, 202,  12),
    (255, 242,   0),
    (238, 229, 178),
    ( 34, 177,  77),
    (180, 230,  29),
    (  0, 162, 232),
    (153, 217, 235),
    ( 62,  71, 203),
    (112, 146, 190),
    (162,  73, 164),
    (237,  28,  35),
    (255, 174, 201),
    (194, 195, 196)
]

def color_palette(isOklabs = False):
    if isOklabs:
        return [rgb2oklab(*color) for color in COLORS]
    return COLORS
