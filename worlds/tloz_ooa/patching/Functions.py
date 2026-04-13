from typing import List, Any, Dict

import os
import random
import Utils
from settings import get_settings
from ..common.patching.RomData import *
from .Util import *
from ..common.patching.Util import simple_hex
from ..common.patching.z80asm.Assembler import Z80Assembler
from ..common.patching.text import *
from ..data.Constants import *
from .Constants import *
from pathlib import Path

from .. import LOCATIONS_DATA
from ..Options import *


def get_treasure_addr(rom: RomData, item_name: str):
    item_id, item_subid = get_item_id_and_subid(item_name)
    addr = 0x59332 + (item_id * 4)
    if rom.read_byte(addr) & 0x80 != 0:
        addr = 0x54000 + rom.read_word(addr + 1)
    return addr + (item_subid * 4)

def apworld_path(file_path) -> str:
    path = Utils.user_path("lib/" if os.path.exists(Utils.user_path("lib")) else "")
    path += "custom_" if os.path.exists(os.path.join(path, Utils.user_path("custom_worlds"))) else ""
    world_path = "worlds/tloz_ooa"
    world_path_from_source = Utils.user_path(world_path)
    path += world_path
    
    def path_exists(p):
        if not os.path.exists(p):
            raise FileNotFoundError(f"Your apworld could not be found inside {p} for some reason.")
        path = os.path.join(p, file_path)
        if os.path.exists(path):
            return path
        raise FileNotFoundError(f"Your file could not be found inside {path}") 
    
    return path_exists(world_path_from_source if os.path.exists(world_path_from_source) else path)

def list_files(dir_name) -> dict[str, Any]:
    dir_name = apworld_path(dir_name)
    files = {}
    for filename in os.listdir(dir_name):
        fullpath = os.path.join(dir_name, filename)
        files[fullpath] = list_files(fullpath) if os.path.isdir(fullpath) else None
    return files


def set_treasure_data(rom: RomData,
                      item_name: str, text_id: int | None,
                      sprite_id: int | None = None,
                      param_value: int | None = None):
    addr = get_treasure_addr(rom, item_name)
    if text_id is not None:
        rom.write_byte(addr + 0x02, text_id)
    if sprite_id is not None:
        rom.write_byte(addr + 0x03, sprite_id)
    if param_value is not None:
        rom.write_byte(addr + 0x01, param_value)

def make_text_edits(texts: Dict[str, str], patch_data: Dict[str, Any]):
    texts["TX_2e0d"] = (
        f"Find {patch_data["options"]["required_essences"]} essences\nto get the Seed.\\stop"
        f"\nFind {patch_data["options"]["required_slates"]} slates\nto beat D8 boss."
    )
    # Overwrite town shop card text
    texts["TX_0045"] = "You got\n🟥King Zora's\nMagic Potion⬜!"
    # Change name to Linked Hero's Cave
    texts["TX_020b"] = "Linked\nHero's Cave"
    # Impa monologue
    texts["TX_012c"] = ("Come see me if\n"
                        "you need a\n"
                        "refill!")
    # TODO: Forgin item implementation

def alter_treasures(rom: RomData):

    set_treasure_data(rom, "Potion", 0x6d)

    # Set data for remote Archipelago items
    set_treasure_data(rom, "Archipelago Item", 0x57, 0x5a)
    set_treasure_data(rom, "Archipelago Progression Item", 0x57, 0x59)
    set_treasure_data(rom, "King Zora's Potion", 0x45, 0x5e)

    # Make bombs increase max carriable quantity when obtained from treasures,
    # not drops (see asm/seasons/bomb_bag_behavior)
    set_treasure_data(rom, "Bombs (10)", None, None, 0x90)


def get_asm_files(patch_data):
    asm_files = ASM_FILES.copy()
    if get_settings()["tloz_ooa_options"]["qol_quick_flute"]:
        asm_files.append("asm/conditional/quick_flute.yaml")
    if get_settings()["tloz_ooa_options"]["skip_tokkey_dance"]:
        asm_files.append("asm/conditional/skip_dance.yaml")
    if get_settings()["tloz_ooa_options"]["skip_boi_joke"]:
        asm_files.append("asm/conditional/skip_joke.yaml")
    if get_settings()["tloz_ooa_options"]["qol_mermaid_suit"]:
        asm_files.append("asm/conditional/qol_mermaid_suit.yaml")
    if get_settings()["tloz_ooa_options"]["mute_music"]:
        asm_files.append("asm/conditional/mute_music.yaml")
    if patch_data["options"]["lynna_gardener"]:
        asm_files.append("asm/conditional/lynna_gardener.yaml")
    if patch_data["options"]["secret_locations"]:
        asm_files.append("asm/conditional/secret_locations.yaml")
    if patch_data["options"]["goal"] == OraclesGoal.option_beat_ganon:
        asm_files.append("asm/conditional/ganon_goal.yaml")
    if get_settings()["tloz_ooa_options"]["skip_intro_cinematic"]:
        asm_files.append("asm/conditional/intro_cinematic_skip.yaml")
    if patch_data["options"]["linked_heros_cave"]:
        asm_files.append("asm/conditional/d11.yaml")
        if patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_maku_tree_entrance_right_side:
            asm_files.append("asm/conditional/d11_in_maku_tree_entrance_right_side.yaml")
    return asm_files

def define_location_constants(assembler: Z80Assembler, patch_data):
    for location_name, location_data in LOCATIONS_DATA.items():
        if "symbolic_name" not in location_data:
            continue
        symbolic_name = location_data["symbolic_name"]

        if location_name in patch_data["locations"]:
            item_name = patch_data["locations"][location_name]
        else:
            item_name = location_data["vanilla_item"]

        if item_name == "Flute":
            item_name = COMPANIONS[patch_data["options"]["animal_companion"]] + "'s Flute"

        item_id, item_subid = get_item_id_and_subid(item_name)
        assembler.define_byte(f"locations.{symbolic_name}.id", item_id)
        assembler.define_byte(f"locations.{symbolic_name}.subid", item_subid)
        assembler.define_word(f"locations.{symbolic_name}", (item_id << 8) + item_subid)

def set_faq_text(assembler: Z80Assembler):
    faq_intro_text = text_to_binary(("Welcome to the "
                        "OoA randomizer "
                        "for Archipelago! "
                        "Did you read "
                        "the FAQ, because there are important randomizer mechanics in it."))
    faq_intro_text.extend([0x00])
    assembler.add_floating_chunk("text.faqIntro", faq_intro_text)
        
def define_option_constants(assembler: Z80Assembler, patch_data):
    options = patch_data["options"]

    # if not hasattr(get_settings().tloz_ooa_options, "beat_tutorial"):
        # assembler.define_byte("option.startingGroup", 0x03)
        # assembler.define_byte("option.startingRoom", 0xbf)
        # assembler.define_byte("option.startingXPos", 0x60)
        # assembler.define_byte("option.startingYPos", 0x70)
    # else: # Redirect user to the first item check, saving them some time.
    assembler.define_byte("option.startingGroup", 0x00)
    assembler.define_byte("option.startingRoom", 0x39)
    assembler.define_byte("option.startingXPos", 0x58)
    assembler.define_byte("option.startingYPos", 0x58)

    assembler.define_byte("option.warpingGroup", patch_data["warp_to_start_variables"]["group"] if "group" in patch_data["warp_to_start_variables"] else 0x00)
    assembler.define_byte("option.warpingRoom", patch_data["warp_to_start_variables"]["room"] if "room" in patch_data["warp_to_start_variables"] else 0x59)
    assembler.define_byte("option.warpingPos", patch_data["warp_to_start_variables"]["pos"] if "pos" in patch_data["warp_to_start_variables"] else 0x55)
    assembler.define_byte("option.warpingDestTransittion", patch_data["warp_to_start_variables"]["dest_transittion"] if "dest_transittion" in patch_data["warp_to_start_variables"] else 0x05)
    assembler.define_byte("option.warpingSrcTransittion", patch_data["warp_to_start_variables"]["src_transittion"] if "src_transittion" in patch_data["warp_to_start_variables"] else 0x03)

    assembler.define_byte("option.animalCompanion", 0x0b + patch_data["options"]["animal_companion"])
    assembler.define_byte("option.defaultSeedType", 0x20 + patch_data["options"]["default_seed"])
    assembler.define_byte("option.receivedDamageModifier", options["combat_difficulty"])
    assembler.define_byte("option.openAdvanceShop", options["advance_shop"])

    assembler.define_byte("option.requiredEssences", options["required_essences"])
    assembler.define_byte("option.required_slates", options["required_slates"])
    
    assembler.define_byte("option.keysanity_small_keys", patch_data["options"]["keysanity_small_keys"])
    keysanity = patch_data["options"]["keysanity_small_keys"] or patch_data["options"]["keysanity_boss_keys"]
    assembler.define_byte("option.customCompassChimes", 1 if keysanity else 0)

    master_keys_as_boss_keys = patch_data["options"]["master_keys"] == OraclesMasterKeys.option_all_dungeon_keys
    assembler.define_byte("option.smallKeySprite", 0x43 if master_keys_as_boss_keys else 0x42)

    if options["secret_locations"]:
        assembler.add_floating_chunk("unsetglobalflag_librarySecret", [
            0xb6, (0x4f | 0x80)
        ])

def parse_int(s):
    try:
        return int(s)
    except ValueError:
        return None # Return None if parsing fails

def process_item_name_for_shop_text(item: dict[str, str | bool]) -> str:
    if "player" in item:
        player_name = item["player"]
        if len(player_name) > 14:
            player_name = player_name[:13] + "."
        item_name = f"🟦{player_name}⬜'s 🟥"
    else:
        item_name = "🟥"
    item_name += item["item"]
    item_name = normalize_text(item_name)
    item_name += "⬜\\stop\n"
    return item_name

def define_text_constants(assembler: Z80Assembler, patch_data: Dict[str, Any], texts: Dict[str, str]):
    overworld_shops = [
        "Lynna City: Shop",
        "Lynna City: Hidden Shop",
        "Yoll Graveyard: Syrup Shop",
        "Lynna Village: Advance Shop",
        "Crescent Island (Past): Market"
    ]

    tx_indices = {
        "lynnaShop1": "TX_0e04",
        "lynnaShop2": "TX_0e03",
        "lynnaShop3": "TX_0e02",
        "advanceShop1": "TX_0e1d",
        "advanceShop2": "TX_0e23",
        "advanceShop3": "TX_0e24",
        "syrupShop1": "TX_0d0a",
        "syrupShop2": "TX_0d01",
        "syrupShop3": "TX_0d05",
        "hiddenShop1": "TX_0e09",
        "hiddenShop2": "TX_0e1c",
        "hiddenShop3": "TX_0e25",
        "tokayMarket1": "TX_0a2a",
        "tokayMarket2": "TX_0a31",
        # TODO: Fill out the rest of the shops once implemented.
    }

    tokay_market_curency_texts = [
        "10 Mystery Seeds⬜",
        "10 Scent Seeds⬜"
    ]

    for shop_name in overworld_shops:
        for i in range(1, 4 if shop_name != "Crescent Island (Past): Market" else 3):
            location_name = f"{shop_name} Item #{i}"
            symbolic_name = LOCATIONS_DATA[location_name]["symbolic_name"]
            item_text = process_item_name_for_shop_text({"item": patch_data["locations"][location_name]})
            if shop_name != "Crescent Island (Past): Market":
                item_text += " \\num1 Rupees"
            else:
                item_text += tokay_market_curency_texts[i - 1]
            item_text += '\n  \\optOK \\optNo thanks\\cmd(0f)'
            # TX_0a3c and TX_0a2b are free now.
            texts[tx_indices[symbolic_name]] = item_text


def write_chest_contents(rom: RomData, patch_data):
    """
    Chest locations are packed inside several big tables in the ROM, unlike other more specific locations.
    This puts the item described in the patch data inside each chest in the game.
    """
    locations_data = patch_data["locations"]
    for location_name, location_data in LOCATIONS_DATA.items():
        if (
            'collect' not in location_data 
            or 'room' not in location_data 
            or location_data['collect'] != COLLECT_CHEST
            or location_name not in locations_data
        ) and location_name != "Rolling Ridge (Present): Bush Cave Chest":
            continue
        if location_name == "Nuun Highlands: Southern Cave":
            chest_addr = rom.get_chest_addr(location_data['room'][patch_data["options"]["animal_companion"]], 0x16, 0x5108)
        else:
            chest_addr = rom.get_chest_addr(location_data['room'], 0x16, 0x5108)
        item_name = locations_data[location_name]
        item_id, item_subid = get_item_id_and_subid(item_name)
        rom.write_byte(chest_addr, item_id)
        rom.write_byte(chest_addr + 1, item_subid)


def define_compass_rooms_table(assembler: Z80Assembler, patch_data):
    table = []
    for location_name, item_name in patch_data["locations"].items():
        _, item_subid = get_item_id_and_subid(item_name)
        dungeon = 0xff
        if item_name.startswith("Small Key") or item_name.startswith("Master Key"):
            dungeon = item_subid
        elif item_name.startswith("Boss Key"):
            dungeon = item_subid + 1

        if dungeon != 0xff:
            location_data = LOCATIONS_DATA[location_name]
            rooms = location_data["room"]
            if not isinstance(rooms, list):
                rooms = [rooms]
            for room in rooms:
                room_id = room & 0xff
                group_id = room >> 8
                table.extend([group_id, room_id, dungeon])
    table.append(0xff)  # End of table
    assembler.add_floating_chunk("compassRoomsTable", table)
       

def define_collect_properties_table(assembler: Z80Assembler, patch_data):
    """
    Defines a table of (group, room, collect mode) entries for randomized items
    to determine how they spawn, how they are grabbed and whether they set
    a room flag when obtained.
    """
    table = []
    for location_name, item_name in patch_data["locations"].items():
        location_data = LOCATIONS_DATA[location_name]
        if "collect" not in location_data or "room" not in location_data:
            continue
        mode = location_data["collect"]

        # Use no pickup animation for falling small keys
        if mode == COLLECT_DROP and item_name.startswith("Small Key"):
            mode &= 0xf8  # Set grab mode to TREASURE_GRAB_INSTANT

        rooms = location_data["room"]
        if not isinstance(rooms, list):
            rooms = [rooms]
        for room in rooms:
            room_id = room & 0xff
            group_id = room >> 8
            table.extend([group_id, room_id, mode])

    table.append(0xff)
    assembler.add_floating_chunk("collectPropertiesTable", table)

    
def inject_slot_name(rom: RomData, slot_name: str):
    slot_name_as_bytes = list(str.encode(slot_name))
    slot_name_as_bytes += [0x00] * (0x40 - len(slot_name_as_bytes))
    rom.write_bytes(0xfffc0, slot_name_as_bytes)

    
def write_seed_tree_content(rom: RomData, patch_data):
    for _, tree_data in SEED_TREE_DATA.items():
        original_data = rom.read_byte(tree_data["codeAdress"])
        item_name = patch_data["locations"][tree_data["location"]]
        item_id, _ = get_item_id_and_subid(item_name)
        newdata = (original_data & 0x0f) | (item_id - 0x20) << 4
        rom.write_bytes(tree_data["codeAdress"], [newdata])

def set_dungeon_warps(rom: RomData, patch_data):
    warp_matchings = patch_data["dungeon_entrances"]
    enter_values = {name: rom.read_word(dungeon["addr"]) for name, dungeon in DUNGEON_ENTRANCES.items()}
    exit_values = {name: rom.read_word(addr) for name, addr in DUNGEON_EXITS.items()}

    # Apply warp matchings expressed in the patch
    for from_name, to_name in warp_matchings.items():
        default_entrance_of_to_name = [name for name, dungeon in DUNGEON_ENTRANCES.items() if dungeon["default"] == to_name][0]
        default_exit_of_from_name = DUNGEON_ENTRANCES[from_name]["default"]
        entrance_addr = DUNGEON_ENTRANCES[from_name]["addr"]
        exit_addr = DUNGEON_EXITS[to_name]
        rom.write_word(entrance_addr, enter_values[default_entrance_of_to_name])
        rom.write_word(exit_addr, exit_values[default_exit_of_from_name])

    # Build a map dungeon => entrance (useful for essence warps)
    entrance_map = dict((v, k) for k, v in warp_matchings.items())

    # D1-D8 Essence Warps (hardcoded in one array using a unified format)
    for i in range(0, 9):
        if i == 8:
            if patch_data["options"]["linked_heros_cave"] > 0:
                i = 10
            else:
                continue
        entrance_name = f"d{i + 1}"
        if i == 5:
            entrance_name += " past"
        entrance = DUNGEON_ENTRANCES[entrance_map[entrance_name]]
        if i == 10:
            rom.write_bytes(GameboyAddress(0x0a, 0x7204).address_in_rom(), [
                entrance["group"] | 0x80,
                entrance["room"], 
                0x0e if entrance["shifted"] else 0x01, 
                entrance["position"], 
                (entrance["group"] * 10) + 0x03
            ])
        else:
            rom.write_bytes(0x2874f + (i * 4), [
                entrance["group"] | 0x80,
                entrance["room"],
                entrance["position"],
                0x0e if entrance["shifted"] else 0x01
            ])

#    # Change Minimap popups to indicate the randomized dungeon's name
#    for i in range(8):
#        entrance_name = f"d{i}"
#        dungeon_index = int(warp_matchings[entrance_name][1:])
#        map_tile = DUNGEON_ENTRANCES[entrance_name]["map_tile"]
#        rom.write_byte(0x???? + map_tile, 0x81 | (dungeon_index << 3))

def define_tile_replacements_table(assembler: Z80Assembler, patch_data):
    new_tiles_table = [
        0x00, 0x20, 0x00, 0x61, 0xd7, # portal in talus peaks
        0x01, 0x48, 0x00, 0x45, 0xd7, # portal south of past maku tree
        0x00, 0x37, 0x02, 0x43, 0xd7, # portal in southeast ricky/moosh nuun
        0x00, 0x6b, 0x00, 0x42, 0x3a, # removed tree in yoll graveyard
        0x00, 0x6b, 0x02, 0x42, 0xce, # not removed tree in yoll graveyard
        0x00, 0x83, 0x00, 0x43, 0xa4, # rock outside D2
        0x03, 0x0f, 0x00, 0x66, 0xf9, # water in d6 past entrance
        0x01, 0x13, 0x00, 0x61, 0xd7, # portal in symmetry city past
        0x01, 0x13, 0x00, 0x68, 0xd7, # portal in symmetry city past
        0x00, 0x25, 0x00, 0x37, 0xd7, # portal in nuun highlands
        0x05, 0xda, 0x01, 0xa4, 0xb2, # tunnel to moblin keep
        0x05, 0xda, 0x01, 0xa5, 0xb2, # cont.
        0x05, 0xda, 0x01, 0xa6, 0xb2, # cont.
        0x00, 0x24, 0x02, 0x49, 0x63, # other side of symmetry city bridge
        0x00, 0x24, 0x02, 0x59, 0x63, # cont.
        0x00, 0x24, 0x02, 0x69, 0x63, # cont.
        0x00, 0x24, 0x02, 0x79, 0x73, # cont.
        0x01, 0x2c, 0x00, 0x70, 0x69, # ledge in rolling ridge east past
        0x01, 0x2c, 0x00, 0x71, 0x06, # cont.
        0x01, 0x2c, 0x00, 0x72, 0x67, # cont.
        0x01, 0xa5, 0x00, 0x35, 0x48, # ledge by library past
        0x01, 0xa5, 0x00, 0x45, 0x0b, # cont.
        0x01, 0xa5, 0x00, 0x55, 0x6c, # cont.
        0x00, 0x83, 0x00, 0x44, 0xd7, # portal outside D2 present
        0x01, 0x48, 0x02, 0x31, 0xcd, # past maku road: remove dirt when exiting
        # 0x00, 0x5d, 0x00, 0x66, 0x0b, # ledge by the linked ghini ghost (traps link in ghini's interaction space until warp to start is initialized (used for faq room space))
        # 0x00, 0x5d, 0x00, 0x57, 0xf4, # waterblock for preventing the trapped player from escaping into the graveyard
    ]

    if patch_data["options"]["secret_locations"]:
        new_tiles_table.extend([
            0x01, 0xc7, 0x00, 0x48, 0xd0, # add stair tile in sea of storms past to allow players to time travel to the present sea of storms.
            0x03, 0xc7, 0x00, 0x48, 0x2c, # add statue in sea of storms past underwater prevent players from resurfacing on that area.
            0x00, 0x76, 0x00, 0x55, 0xa7, # add walkable tiles to black tower present entrance
            0x00, 0x76, 0x00, 0x54, 0xa7, # ^
        ])

    assembler.add_floating_chunk("tileReplacementsTable", new_tiles_table)

def define_dungeon_items_text_constants(assembler: Z80Assembler, patch_data: Dict[str, Any], texts: Dict[str, str]):

    for i in range(0, 11): # Maku Path and Hero's Cave has no map, no compass, no boss key, and the unique small key use the default text. 
        # " for\nDungeon X"
        trueI = i if i != 9 else 6
        if trueI == 10:
            trueI = 11
        dungeon_tag = f"D{trueI}"
        dungeon_precision = f"for {f"{DUNGEON_NAMES[trueI]} ({dungeon_tag})" if get_settings().tloz_ooa_options["simplify_dungeon_precision_text"] else (
            f"Dungeon {dungeon_tag[1:]}"
        )}"
        dungeon_precisionForBossKey = dungeon_precision

        if i == 6:
            #\n(present)
            dungeon_precision += "\n(Present)"
            dungeon_tag += "Present"
        if i == 9:
            #\n(past)
            dungeon_precision += "\n(Past)"
            dungeon_tag += "Past"

        # ###### Small keys ##############################################
        # "You found a\n\color(RED)"
        small_key_text = "You found a 🟥"
        if patch_data["options"]["master_keys"]:
            small_key_text += "Master Key "
        else:
            small_key_text += "Small Key "
        if patch_data["options"]["keysanity_small_keys"]:
            small_key_text += dungeon_precision
        small_key_text += "⬜!"
        texts[f"TX_01{simple_hex(i)}"] = normalize_text(small_key_text)

        # Maku Path & Hero Cave only has Small Keys, so skip other texts
        if i == 0 or i == 10:
            continue

        # ###### Boss keys ##############################################
        # "You found the\n\color(RED)Boss Key"
        if i < 9:
            boss_key_text = "You found the 🟥Boss Key "
            if patch_data["options"]["keysanity_boss_keys"]:
                boss_key_text += dungeon_precisionForBossKey
            boss_key_text += "⬜!"  # "\color(WHITE)!(end)"
            texts[f"TX_01{simple_hex(i + 10)}"] = normalize_text(boss_key_text)


        # ###### Dungeon maps ##############################################
        # "You found the\n\color(RED)"
        dungeon_map_text = "You found the 🟥Dungeon Map "
        if patch_data["options"]["keysanity_maps_compasses"]:
            dungeon_map_text += dungeon_precision
        dungeon_map_text += "⬜!"  # "\color(WHITE)!(end)"
        texts[f"TX_01{simple_hex(i + 18)}"] = normalize_text(dungeon_map_text)

        # ###### Compasses ##############################################
        # "You found the\n\color(RED)Compass"
        compasses_text = "You found the 🟥Compass "
        if patch_data["options"]["keysanity_maps_compasses"]:
            compasses_text += dungeon_precision
        compasses_text += "⬜!" # "\color(WHITE)!(end)"
        texts[f"TX_01{simple_hex(i + 27)}"] = normalize_text(compasses_text)

        if patch_data["options"]["master_keys"]:
            texts["TX_001a"] = texts["TX_001a"].replace("Small", "Master")

def set_file_select_text(assembler: Z80Assembler, slot_name: str):
    def char_to_tile(c: str) -> int:
        if '0' <= c <= '9':
            return ord(c) - 0x20
        if 'A' <= c <= 'Z':
            return ord(c) + 0xa1
        if c == '+':
            return 0xfd
        if c == '-':
            return 0xfe
        if c == '.':
            return 0xff
        else:
            return 0xfc  # All other chars are blank spaces
    from .. import OracleOfAgesWorld
    row_1 = [char_to_tile(c) for c in f"ARCHIP. {OracleOfAgesWorld.version()}"]
    row_1_left_padding = int((16 - len(row_1)) / 2)
    row_1_right_padding = int(16 - row_1_left_padding - len(row_1))
    row_1 = ([0x00] * row_1_left_padding) + row_1 + ([0x00] * row_1_right_padding)
    row_2 = [char_to_tile(c) for c in slot_name.replace("-", " ").upper()]
    row_2_left_padding = int((16 - len(row_2)) / 2)
    row_2_right_padding = int(16 - row_2_left_padding - len(row_2))
    row_2 = ([0x00] * row_2_left_padding) + row_2 + ([0x00] * row_2_right_padding)

    text_tiles = [0x74, 0x31]
    text_tiles.extend(row_1)
    text_tiles.extend([0x41, 0x40])
    text_tiles.extend([0x02] * 12)  # Offscreen tiles

    text_tiles.extend([0x40, 0x41])
    text_tiles.extend(row_2)
    text_tiles.extend([0x51, 0x50])
    text_tiles.extend([0x02] * 12)  # Offscreen tiles

    assembler.add_floating_chunk("dma_FileSelectStringTiles", text_tiles)

    
def set_heart_beep_interval_from_settings(rom: RomData):
    heart_beep_interval = get_settings()["tloz_ooa_options"]["heart_beep_interval"]
    if heart_beep_interval == "half":
        rom.write_byte(0x914B, 0x3f * 2)
    elif heart_beep_interval == "quarter":
        rom.write_byte(0x914B, 0x3f * 4)
    elif heart_beep_interval == "disabled":
        rom.write_bytes(0x914B, [0x00, 0xc9])  # Put a return to avoid beeping entirely

def set_character_sprite_from_settings(rom: RomData):
    sprite = get_settings()["tloz_ooa_options"]["character_sprite"]
    sprite_dir = Path(Utils.local_path(os.path.join('data', 'sprites', 'oos_ooa')))
    if sprite == "random":
        sprite_filenames = [f for f in os.listdir(sprite_dir) if sprite_dir.joinpath(f).is_file() and f.endswith(".bin")]
        sprite = sprite_filenames[random.randint(0, len(sprite_filenames) - 1)]
    elif not sprite.endswith(".bin"):
        sprite += ".bin"
    if sprite != "link.bin":
        sprite_path = sprite_dir.joinpath(sprite)
        if not (sprite_path.exists() and sprite_path.is_file()):
            raise ValueError(f"Path '{sprite_path}' doesn't exist")
        sprite_bytes = list(Path(sprite_path).read_bytes())
        rom.write_bytes(0x68000, sprite_bytes)

    palette = get_settings()["tloz_ooa_options"]["character_palette"]
    if palette == "random":
        palette = random.choice(get_available_random_colors_from_sprite_name(sprite))

    if palette == "green":
        return  # Nothing to change
    if palette not in PALETTE_BYTES:
        raise ValueError(f"Palette color '{palette}' doesn't exist (must be 'green', 'blue', 'red' or 'orange')")
    palette_byte = PALETTE_BYTES[palette]

    # Link in-game
    for addr in range(0x1420e, 0x14221, 2):
        rom.write_byte(addr, 0x08 | palette_byte)
    # Link palette restored after Medusa Head / Ganon stun attacks
    rom.write_byte(0x15271, 0x08 | palette_byte)
    # Link standing still in file select (fileSelectDrawLink:@sprites0)
    rom.write_byte(0x8d86, palette_byte)
    rom.write_byte(0x8d8a, palette_byte)
    # Link animated in file select (@sprites1 & @sprites2)
    rom.write_byte(0x8d8f, palette_byte)
    rom.write_byte(0x8d93, palette_byte)
    rom.write_byte(0x8d98, 0x20 | palette_byte)
    rom.write_byte(0x8d9c, 0x20 | palette_byte)

def apply_misc_option(rom: RomData, patch_data):
    if patch_data["options"]["master_keys"] != OraclesMasterKeys.option_disabled:
        # Remove small key consumption on keydoor opened
        rom.write_byte(0x18366, 0x00)
        # Change obtention text
        rom.write_bytes(0x78247, [0x4d, 0x61, 0x73, 0x74, 0x65, 0x72, 0x20, 0x4b, 0x65, 0x79, 0x09, 0x01, 0x21, 0x00]) # I really wish that the dictionnay of ages would be more useful...
    if patch_data["options"]["master_keys"] == OraclesMasterKeys.option_all_dungeon_keys:
        # Remove boss key consumption on boss keydoor opened (boss door behave like normal locked door)
        rom.write_word(0x1835e, 0x0000)