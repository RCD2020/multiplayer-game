from PIL import Image
from scipy import spatial

from oklab import rgb2oklab
from card_colors import color_palette


# ISOKLABS = True
WIDTH = 216
HEIGHT = 302
IMAGES = [
    'candlestick.jpg',
    'knife.jpg',
    'lead pipe.jpg',
    'revolver.jpg',
    'rope.png',
    'wrench.png'
]


for img_name in IMAGES:
    for isoklabs in [True, False]:
        IMG_URL = 'convert2card/images/input/' + img_name


        im = Image.open(IMG_URL)
        im = im.resize((WIDTH, HEIGHT))
        pixels = im.load()
        values = color_palette()
        tree = spatial.KDTree(color_palette(isoklabs))


        for i in range(im.size[0]):
            for j in range(im.size[1]):
                if isoklabs:
                    _, k = tree.query(rgb2oklab(*pixels[i,j][0:3]))
                else:
                    _, k = tree.query(pixels[i,j][0:3])
                
                pixels[i, j] = values[k]

        img_type = 'rgb'
        if isoklabs:
            img_type = 'OKlabs'

        im.save(f'convert2card/images/output/{img_name.split(".")[0]}_{img_type}.png')
