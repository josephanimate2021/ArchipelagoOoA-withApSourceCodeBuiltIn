from PIL.Image import Image

from . import bw_palette, link_palette


def has_separator(image: Image) -> bool:
    if image.width > 8:
        return image.getpixel((8, 0)) == 4
    else:
        # Just to cover the case where it's a single column
        return image.getpixel((0, 8)) == 4


def encode_tile(img: Image, x: int, y: int) -> bytes:
    data = bytearray(32)

    for j in range(16):
        b1 = 0
        b2 = 0
        for i in range(8):
            c = img.getpixel((x + (7 - i), y + j))
            assert c < 4

            b1 |= (c & 1) << i
            b2 |= ((c >> 1) & 1) << i

        data[j * 2] = b1
        data[j * 2 + 1] = b2

    return data


def encode_sprite(image: Image) -> bytes:
    x = y = 0
    sprite_data = []
    if has_separator(image):
        x_step = 9
        y_step = 17
    else:
        x_step = 8
        y_step = 16
    for sprite_id in range(279):
        sprite_data.append(encode_tile(image, x, y))
        x += x_step
        if x >= image.width:
            x = 0
            y += y_step
    return b"".join(sprite_data)


def remap_sprite(image: Image) -> Image:
    if len(image.getpalette("RGB")) > 15:
        image = image.convert("RGBA")
        image = image.quantize(5)
        image.save("output/link_g3.png")
    img_palette = image.getpalette("RGBA")
    mapping = list(range(5))

    transparent_tiles = []
    if len(img_palette) > 3:
        for i in range(3, len(img_palette), 4):
            if img_palette[i] < 0x80:
                transparent_tiles.append(img_palette[i // 4])
    elif isinstance(image.info["transparency"], int):
        transparent_tiles.append(image.info["transparency"])
    elif isinstance(image.info["transparency"], bytes):
        for i in range(len(image.info["transparency"])):
            if image.info["transparency"][i] < 0x80:  # Why not leave a margin, not like we expect anything other than 0xff or 0x00
                transparent_tiles.append(image.info["transparency"])
    else:
        raise TypeError("transparency_data must be either int or bytes")

    if len(transparent_tiles) == 0:
        # Assume bw
        palette = bw_palette
        for i in range(0, len(img_palette), 4):
            r = img_palette[i]
            if r < 0x20:
                mapping[0] = i // 4
            elif r < 0x80:
                mapping[1] = i // 4
            elif r < 0xc0:
                mapping[2] = i // 4
            elif img_palette[i + 1] < 0x20:
                mapping[4] = i // 4  # Dead
            else:
                mapping[3] = i // 4
    elif len(transparent_tiles) == 1:
        # Assume green
        palette = link_palette
        mapping[0] = transparent_tiles[0]
        for i in range(0, len(img_palette), 4):
            r = img_palette[i]
            g = img_palette[i + 1]
            if transparent_tiles[0] == i:
                continue
            elif r < 0x80 and g < 0x80:
                mapping[1] = i // 4  # Black
            elif r < 0x80 <= g:
                mapping[2] = i // 4  # Green
            elif r >= 0x80 and g >= 0x80:
                mapping[3] = i // 4  # White/Yellow
            else:
                mapping[4] = i // 4  # Dead
    else:
        raise TypeError("Too many transparent tiles")

    image = image.remap_palette(mapping)
    image.putpalette(palette, "RGBA")
    return image
