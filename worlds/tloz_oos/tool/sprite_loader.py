from PIL import Image

from worlds.tloz_oos.spriter.sprite import link_palette
from worlds.tloz_oos.spriter.sprite.encoding import remap_sprite

if __name__ == "__main__":
    # Test reader
    image = Image.open("output/link_bw.png")
    image = remap_sprite(image)
    image.putpalette(link_palette, "RGBA")
    image.save("output/link_g2.png")
