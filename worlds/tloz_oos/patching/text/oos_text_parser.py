import json
import os

from settings import get_settings
from worlds.tloz_oos.patching.RomData import RomData
from worlds.tloz_oos.patching.text.decoding import parse_dict_seasons, parse_all_texts

if __name__ == '__main__':
    if not os.path.isdir("output"):
        os.mkdir("output")
    file_name = get_settings()["tloz_oos_options"]["rom_file"]
    rom = RomData(bytes(open(file_name, "rb").read()))
    dict_seasons = parse_dict_seasons(rom)
    text = parse_all_texts(rom, dict_seasons)

    with open("output/seasons_text_dict.json", "w+", encoding="utf-8") as f:
        json.dump(dict_seasons, f, ensure_ascii=False, indent=4)

    with open("output/seasons_text.json", "w+", encoding="utf-8") as f:
        json.dump(text, f, ensure_ascii=False, indent=4)
