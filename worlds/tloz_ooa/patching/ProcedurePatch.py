import hashlib
import os
import pkgutil
import json

import yaml

import Utils
from worlds.Files import APProcedurePatch, APTokenMixin, APPatchExtension

from .Functions import *
from .Constants import *
from ..common.patching.RomData import RomData
from .xdelta import apply_xdelta_patch
from .PyPatcherGBA.src.pypatchergba import apply_patch
from ..common.patching.z80asm.Assembler import Z80Assembler, Z80Block, GameboyAddress
from tkinter.filedialog import askopenfilename

class OoAPatchExtensions(APPatchExtension):
    game = "The Legend of Zelda - Oracle of Ages"

    @staticmethod
    def apply_patches(caller: APProcedurePatch, rom: bytes, patch_file: str) -> bytes:
        if get_settings().tloz_ooa_options["qol_waves_removal"]:
            rom = apply_patch(rom, apworld_path("patching/ips/no_waves.ips"))
        rom_data = RomData(rom)
        patch_data = json.loads(caller.get_file(patch_file).decode("utf-8"))
        from .. import OracleOfAgesWorld
        version = patch_data["version"].split(".")
        world_version = OracleOfAgesWorld.world_version
        if int(version[0]) != world_version.major or int(version[1]) > world_version.minor:
            raise Exception(f"Invalid version: this patch was generated on v{patch_data['version']}, "
                            f"you are currently using v{world_version.as_simple_string()}")

        #if patch_data["options"]["enforce_potion_in_shop"]:
        #    patch_data["locations"]["Horon Village: Shop #3"] = "Potion"

        # if patch_data["options"]["cross_items"]:
            # file_name = get_settings().tloz_ooa_options.seasons_rom_file
            # file_path = Utils.user_path(file_name)
            # rom_file = open(file_path, "rb")
            # seasons_rom = bytes(rom_file.read())
            # rom_file.close()

            # for bank in range(0x40, 0x80):``
                # bank = 0xdd  # TODO: this is an invalid instruction that hangs the game, it's easier to debug but looks worse, remove/comment out once stable
                # rom_data.add_bank(bank)
            # rom_data.update_rom_size()
        # else:
        seasons_rom = bytes()

        assembler = Z80Assembler(EOB_ADDR, DEFINES, rom, seasons_rom) # type: ignore

        # Generate dungeon entrance/exit data
        dungeon_entrances = dict(DUNGEON_ENTRANCES)
        dungeon_exits = dict(DUNGEON_EXITS)
        if patch_data["options"]["linked_heros_cave"] != OracleOfAgesLinkedHerosCave.option_disabled:
            dungeon_entrances["d11"] = {
                "addr": GameboyAddress(0x04, 0x770c).address_in_rom(),
                "warp_source_addr": [0x07, 0x44],
                "group": 0x00,
                "shifted": False,
                "default": "d11"
            }
            dungeon_exits["d11"] = {
                "warp_source_addr": [0x04, 0xce],
                "addr_custom_warp": GameboyAddress(0x04, 0x7ad6).address_in_rom(),
                "addr": 0x13ae4
            }
            if patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_maku_tree_entrance_right_side:
                dungeon_entrances["d11"]["room"] = 0x48
                dungeon_entrances["d11"]["position"] = 0x28
            elif patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_d2_present:
                dungeon_entrances["d11"]["room"] = 0x83
                dungeon_entrances["d11"]["position"] = 0x25
            elif patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_graveyard:
                dungeon_entrances["d11"]["room"] = 0x7c
                dungeon_entrances["d11"]["position"] = 0x35
            elif patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_seawater_cure_room_present:
                dungeon_entrances["d11"]["room"] = 0xa3
                dungeon_entrances["d11"]["position"] = 0x32
            elif (
                patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_zoras_domain
                or patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_under_fishers_house_present
            ):
                dungeon_entrances["d11"]["group"] = 0x02
                if patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_under_fishers_house_present:
                    dungeon_entrances["d11"]["room"] = 0xc5
                    dungeon_entrances["d11"]["position"] = 0x50
                else:
                    dungeon_entrances["d11"]["room"] = 0xc0
                    dungeon_entrances["d11"]["position"] = 0x43

            if "map_tile" not in dungeon_entrances["d11"]:
                dungeon_entrances["d11"]["map_tile"] = dungeon_entrances["d11"]["room"]

        # Fill warps (pre stage)
        prefill_warps(assembler, patch_data, dungeon_entrances, dungeon_exits, rom_data)

        # Define static values & data blocks
        for symbolic_name, price in patch_data["shop_prices"].items():
            assembler.define_byte(f"shopPrices.{symbolic_name}", RUPEE_VALUES[price])

        define_tile_replacements_table(assembler, patch_data)
        define_location_constants(assembler, patch_data)
        define_option_constants(assembler, patch_data)
        define_text_constants(assembler, patch_data)
        define_dungeon_items_text_constants(assembler, patch_data)

        # Define dynamic data blocks
        define_compass_rooms_table(assembler, patch_data)
        define_collect_properties_table(assembler, patch_data)
        set_file_select_text(assembler, caller.player_name)

        # Parse assembler files, compile them and write the result in the ROM
        print("Compiling ASM files...")
        # write_text_data(rom_data, dictionary, texts, False)
        for file_path in get_asm_files(patch_data):
            data_loaded = yaml.safe_load(pkgutil.get_data(__name__, file_path)) # type: ignore
            for metalabel, contents in data_loaded.items():
                assembler.add_block(Z80Block(metalabel, contents))
        assembler.compile_all()
        for block in assembler.blocks:
            rom_data.write_bytes(block.addr.address_in_rom(), block.byte_array)

        alter_treasures(rom_data)
        write_chest_contents(rom_data, patch_data)
        write_seed_tree_content(rom_data, patch_data)

        # Fill warps (post stage)
        set_dungeon_warps(rom_data, patch_data, dungeon_entrances, dungeon_exits)

        #apply_miscellaneous_options(rom_data, patch_data)

        set_heart_beep_interval_from_settings(rom_data)
        set_character_sprite_from_settings(rom_data)
        apply_misc_option(rom_data, patch_data)
        inject_slot_name(rom_data, caller.player_name)

        rom_data.update_checksum(0x14e)
        return rom_data.output()

class OoAProcedurePatch(APProcedurePatch, APTokenMixin):
    hash = [AGES_ROM_HASH] # type: ignore
    patch_file_ending: str = ".apooa"
    result_file_ending: str = ".gbc"

    game = "The Legend of Zelda - Oracle of Ages"
    procedure = [
        ("apply_patches", ["patch.dat"])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        base_rom_bytes = getattr(cls, "base_rom_bytes", None)
        if not base_rom_bytes:
            file_name = get_settings().tloz_ooa_options["rom_file"]
            if not os.path.exists(file_name):
                file_name = Utils.user_path(file_name)
            if not os.path.exists(file_name):
                file_name = askopenfilename() 
            base_rom_bytes = bytes(open(file_name, "rb").read())

            basemd5 = hashlib.md5()
            basemd5.update(base_rom_bytes)
            if AGES_ROM_HASH != basemd5.hexdigest():
                raise Exception("Supplied ROM does not match known MD5 for Oracle of Ages US version."
                                "Get the correct game and version, then dump it.")
            setattr(cls, "base_rom_bytes", base_rom_bytes)
        return base_rom_bytes

