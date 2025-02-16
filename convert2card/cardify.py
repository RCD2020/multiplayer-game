from PIL import Image
from scipy import spatial

from oklab import rgb2oklab
from card_colors import color_palette


ISOKLABS = True
WIDTH = 216
HEIGHT = 302
IMG_NAME = 'mustard.jpg'
IMG_URL = 'convert2card/images/input/' + IMG_NAME


im = Image.open(IMG_URL)
im = im.resize((WIDTH, HEIGHT))
pixels = im.load()
values = color_palette()
tree = spatial.KDTree(color_palette(ISOKLABS))


for i in range(im.size[0]):
    for j in range(im.size[1]):
        if ISOKLABS:
            _, k = tree.query(rgb2oklab(*pixels[i,j]))
        else:
            _, k = tree.query(pixels[i,j])
        
        pixels[i, j] = values[k]

img_type = 'rgb'
if ISOKLABS:
    img_type = 'OKlabs'

im.save(f'convert2card/images/output/{IMG_NAME.split(".")[0]}_{img_type}.png')
