import os

from settings import get_settings
from worlds.tloz_ooa.common.patching.RomData import RomData
from worlds.tloz_ooa.common.patching.rooms.decoding import decompress_rooms
from worlds.tloz_ooa.common.patching.rooms.encoding import write_room_data
from worlds.tloz_ooa.common.patching.rooms.tools import dump_rooms_to_txt

if __name__ == "__main__":
    if not os.path.isdir("output"):
        os.mkdir("output")
    file_name = get_settings()["tloz_ooa_options"]["rom_file"]
    rom = RomData(bytes(open(file_name, "rb").read()))
    rooms = decompress_rooms(rom, False)
    dump_rooms_to_txt(rooms, "output")
    write_room_data(rom, rooms, False)
    rooms2 = decompress_rooms(rom, False)

    for room_id in range(len(rooms)):
        assert rooms[room_id] == rooms2[room_id], f"Room {hex(room_id)} was parsed wrong"
