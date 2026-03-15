import json
import pkgutil

import yaml

from worlds.Files import APProcedurePatch, APTokenMixin, APPatchExtension
from .Functions import *
from .data_manager.text import apply_seasons_edits, get_modded_ages_text_data
from ..common.patching.text.encoding import write_text_data
from ..common.patching.z80asm.Assembler import Z80Assembler, Z80Block, GameboyAddress

from tkinter.filedialog import askopenfilename


class OoAPatchExtensions(APPatchExtension):
    game = "The Legend of Zelda - Oracle of Ages"

    @staticmethod
    def apply_patches(caller: APProcedurePatch, rom: bytes, patch_file: str) -> bytes:
        rom_data = RomData(rom)
        patch_data = json.loads(caller.get_file(patch_file).decode("utf-8"))

        if not (patch_data["version"] in RETRO_COMPAT_VERSION):
            raise Exception(f"Invalid version: this seed was generated on v{patch_data['version']}, "
                            f"and is not compatible with current : v{VERSION}")

        # if patch_data["options"]["cross_items"]:
            # file_name = get_settings().tloz_ooa_options.seasons_rom_file
            # file_path = Utils.user_path(file_name)
            # rom_file = open(file_path, "rb")
            # seasons_rom = bytes(rom_file.read())
            # rom_file.close()

            # for bank in range(0x40, 0x80):
                # bank = 0xdd  # TODO: this is an invalid instruction that hangs the game, it's easier to debug but looks worse, remove/comment out once stable
                # rom_data.add_bank(bank)
            # rom_data.update_rom_size()
        # else:
        seasons_rom = bytes()

        # Initialize random seed with the one used for generation + the player ID, so that cosmetic stuff set
        # to "random" always generate the same for successive patchings for a given slot
        random.seed(patch_data["seed"] + caller.player)

        assembler = Z80Assembler(EOB_ADDR, DEFINES, rom, seasons_rom)
        dictionary, texts = get_modded_ages_text_data(rom_data)
        # if patch_data["options"]["cross_items"]:
            # if texts["TX_0053"] == "":  # Check if cane text exists
                # If not, add the Ages texts
                # apply_seasons_edits(texts, RomData(ages_rom))

        # Generate dungeon entrance/exit data
        dungeon_entrances = dict(DUNGEON_ENTRANCES)
        dungeon_exits = dict(DUNGEON_EXITS)
        if patch_data["options"]["linked_heros_cave"] != OracleOfAgesLinkedHerosCave.option_disabled:
            dungeon_exits["d11"] = GameboyAddress(0x04, 0x7ae2).address_in_rom()
            dungeon_entrances["d11"] = {
                "group": 0x00,
                "shifted": False,
                "default": "d11"
            }
            if patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_maku_tree_entrance_right_side:
                dungeon_entrances["d11"]["addr"] = GameboyAddress(0x04, 0x770c).address_in_rom()
                dungeon_entrances["d11"]["room"] = 0x48
                dungeon_entrances["d11"]["map_tile"] = 0x048
                dungeon_entrances["d11"]["position"] = 0x28
            # elif patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_d2_present:
                # dungeon_entrances["d11"] = dungeon_entrances["d2 present"]
                # dungeon_entrances["d11"]["default"] = "d11"

        # Define assembly constants & floating chunks
        item_data = define_foreign_item_data(assembler, texts, patch_data)
        define_location_constants(assembler, patch_data, item_data)
        define_option_constants(assembler, patch_data)
        make_text_data(assembler, texts, patch_data)
        define_compass_rooms_table(assembler, patch_data, item_data)
        define_collect_properties_table(assembler, patch_data, item_data)
        define_additional_tile_replacements(assembler, patch_data)
        define_dungeon_items_text_constants(texts, patch_data)
        define_essence_sparkle_constants(assembler, patch_data, dungeon_entrances)
        # define_tree_sprites(assembler, patch_data, item_data)
        set_file_select_text(assembler, caller.player_name)
        # set_player_start_inventory(assembler, patch_data)
        if not hasattr(get_settings().tloz_ooa_options, "beat_tutorial"):
            set_faq_trap(assembler)

        # Parse assembler files, compile them and write the result in the ROM
        print("Compiling ASM files...")
        write_text_data(rom_data, dictionary, texts, False)
        for file_path in get_asm_files(patch_data):
            data_loaded = yaml.safe_load(pkgutil.get_data(__name__, file_path))
            for metalabel, contents in data_loaded.items():
                assembler.add_block(Z80Block(metalabel, contents))
        assembler.compile_all()
        for block in assembler.blocks:
            rom_data.write_bytes(block.addr.address_in_rom(), block.byte_array)

        # if patch_data["options"]["linked_heros_cave"] & OracleOfSeasonsLinkedHerosCave.samasa:
            # dungeon_entrances["d11"]["addr"] = assembler.global_labels["warpSourceDesert"].address_in_rom() + 2

        # Perform direct edits on the ROM
        alter_treasure_types(rom_data, item_data)
        write_chest_contents(rom_data, patch_data, item_data)
        # set_old_men_rupee_values(rom_data, patch_data)
        set_dungeon_warps(rom_data, patch_data, dungeon_entrances, dungeon_exits)
        apply_miscellaneous_options(rom_data, patch_data)
        # if patch_data["options"]["randomize_ai"]:
            # randomize_ai_for_april_fools(rom_data, patch_data["seed"] + caller.player)

        # Apply cosmetic settings
        set_heart_beep_interval_from_settings(rom_data)
        set_character_sprite_from_settings(rom_data)
        inject_slot_name(rom_data, caller.player_name)

        rom_data.update_header_checksum()
        rom_data.update_checksum(0x14e)
        return rom_data.output()


class OoAProcedurePatch(APProcedurePatch, APTokenMixin):
    hash = [AGES_ROM_HASH]
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
            file_name = get_settings().tloz_ooa_options.rom_file
            file_name = Utils.user_path(file_name)

            rom_file = open(file_name, "rb")
            base_rom_bytes = bytes(rom_file.read())
            rom_file.close()

            setattr(cls, "base_rom_bytes", base_rom_bytes)
        return base_rom_bytes