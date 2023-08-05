import os
from PIL import Image

def resize(f, w, h):
    img = Image.open(f)
    out = img.resize((w, h), Image.ANTIALIAS)
    out.save(f)

if __name__ == '__main__':
    resize('ship.png', 32, 32)
