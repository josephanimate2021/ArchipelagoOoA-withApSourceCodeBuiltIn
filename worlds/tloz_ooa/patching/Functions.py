from typing import List, Any

import os
import random
import Utils
from settings import get_settings
from ..common.patching.RomData import RomData
from ..common.patching.Util import *
from ..common.patching.z80asm.Assembler import Z80Assembler
from ..data.Constants import *
from .Constants import *
from pathlib import Path

from .. import LOCATIONS_DATA, OraclesMasterKeys, OracleOfAgesLinkedHerosCave, OraclesGoal, OraclesOldMenShuffle, ITEMS_DATA

def get_item_id_and_subid(item_name: str):
    if item_name == "Archipelago Item":
        return 0x41, 0x00
    elif item_name == "Archipelago Progression Item":
        return 0x41, 0x01

    item_data = ITEMS_DATA[item_name]
    item_id = item_data["id"]
    item_subid = item_data["subid"] if "subid" in item_data else 0x00
    return item_id, item_subid


def get_treasure_addr(rom: RomData, item_name: str):
    item_id, item_subid = get_item_id_and_subid(item_name)
    addr = 0x59332 + (item_id * 4)
    if rom.read_byte(addr) & 0x80 != 0:
        addr = 0x54000 + rom.read_word(addr + 1)
    return addr + (item_subid * 4)


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
    if patch_data["options"]["quick_flute"]:
        asm_files.append("asm/conditional/quick_flute.yaml")
    if get_settings()["tloz_ooa_options"]["skip_tokkey_dance"]:
        asm_files.append("asm/conditional/skip_dance.yaml")
    if get_settings()["tloz_ooa_options"]["skip_boi_joke"]:
        asm_files.append("asm/conditional/skip_joke.yaml")
    if get_settings()["tloz_ooa_options"]["qol_mermaid_suit"]:
        asm_files.append("asm/conditional/qol_mermaid_suit.yaml")
    if patch_data["options"]["goal"] == OraclesGoal.option_beat_ganon:
        asm_files.append("asm/conditional/ganon_goal.yaml")
    if patch_data["options"]["shuffle_old_men"] == OraclesOldMenShuffle.option_turn_into_locations:
        asm_files.append("asm/conditional/old_men_as_locations.yaml")
    if patch_data["options"]["lynna_gardener"]:
        asm_files.append("asm/conditional/lynna_gardener.yaml")
    if patch_data["options"]["secret_locations"]:
        asm_files.append("asm/conditional/secret_locations.yaml")
    if patch_data["options"]["linked_heros_cave"] != OracleOfAgesLinkedHerosCave.option_disabled:
        asm_files.append("asm/conditional/d11.yaml")
        if patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_maku_tree_entrance_right_side:
            asm_files.append("asm/conditional/d11_in_maku_tree_entrance_right_side.yaml")
        else:
            asm_files.append(f"asm/conditional/d11_custom_warp_group_{2 if patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_zoras_domain else 0}.yaml")
            if patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_d2_present:
                asm_files.append("asm/conditional/d11_in_d2_present.yaml")
    if patch_data["options"]["miniboss_locations"]:
        asm_files.append("asm/conditional/miniboss_locations.yaml")
    return asm_files

def prefill_warps(assembler: Z80Assembler, patch_data: dict[str, dict[str, Any]], dungeon_entrances: dict[str, dict[str, Any]], dungeon_exits: dict[str, dict[str, Any]], rom: RomData):
    """
    Fills custom made warps with warp addresses that lead to either dungeons or other misc places (Helps with dungeon shuffle and possibly ER).
    """
    if (
        patch_data["options"]["linked_heros_cave"] != OracleOfAgesLinkedHerosCave.option_disabled
        and patch_data["options"]["linked_heros_cave"] != OracleOfAgesLinkedHerosCave.option_maku_tree_entrance_right_side
    ):
        d11Exit = patch_data["dungeon_entrances"]["d11"]

        if d11Exit == "d2":
            d11Entrance = "d2 past"
        else:
            d11Entrance = d11Exit

        # Breakdown on how warp destinations work:

        # First byte (not sure what that's for)
        # Second byte is the dest room
        # Third byte is link's postion after the warp in the form of $yx
            
        rom.write_bytes(GameboyAddress(0x04, 0x702d).address_in_rom(), [
            (0x0e if dungeon_entrances["d11"]["shifted"] else 0x01), 
            dungeon_entrances["d11"]["room"], 
            dungeon_entrances["d11"]["position"]
        ])
        assembler.add_floating_chunk("warpSourceHerosCaveEntrance", dungeon_entrances[d11Entrance]["warp_source_addr"])

        # Writes down the new exit source for the hero's cave custom warp.
        rom.write_bytes(dungeon_exits["d11"]["addr_custom_warp"], dungeon_exits[d11Exit]["warp_source_addr"])
        rom.write_bytes(dungeon_exits["d11"]["addr_custom_warp"] + 2, [
            0x41, (dungeon_entrances[d11Entrance]["group"] * 10) + 0x04
        ])

def define_tile_replacements_table(assembler: Z80Assembler, patch_data: dict[str, dict[str, Any]]):

    # data for applyAllTileSubstitutions: group,room,flags,yx,tile
    tiles_to_replace = [
        0x03, 0xbf, 0x00, 0x74, 0xb2, # block off exit for faq room
        0x03, 0xbf, 0x00, 0x75, 0xb2, # block off exit for faq room
        0x00, 0x20, 0x00, 0x61, 0xd7, # portal in talus peaks
        0x01, 0x48, 0x00, 0x45, 0xd7, # portal south of past maku tree
        0x00, 0x37, 0x02, 0x43, 0xd7, # portal in southeast ricky/moosh nuun
        0x00, 0x6b, 0x00, 0x42, 0x3a, # removed tree in yoll graveyard
        0x00, 0x6b, 0x02, 0x42, 0xce, # not removed tree in yoll graveyard
        0x00, 0x83, 0x00, 0x43, 0x3a, # path outside D2 present
        0x03, 0x0f, 0x00, 0x66, 0xf9, # water in d6 past entrance
        0x01, 0x13, 0x00, 0x61, 0xd7, # portal in symmetry city past
        0x01, 0x13, 0x00, 0x68, 0xd7, # portal in symmetry city past
        0x00, 0x25, 0x00, 0x37, 0xd7, # portal in nuun highlands
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
        0x01, 0x48, 0x02, 0x31, 0xcd, # past maku road: remove dirt when exiting
    ]

    if patch_data["options"]["secret_locations"]:
        tiles_to_replace.extend([
            0x01, 0xc7, 0x00, 0x48, 0xd0, # add stair tile in sea of storms past to allow players to time travel to the present sea of storms.
            0x03, 0xc7, 0x00, 0x48, 0x2c, # add statue in sea of storms past underwater prevent players from resurfacing on that area.

            # add walkable tiles to black tower present entrance
            0x00, 0x76, 0x00, 0x55, 0xa7,
            0x00, 0x76, 0x00, 0x54, 0xa7,
        ])

    if patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_zoras_domain:
        tiles_to_replace.extend([
            0x02, 0xc0, 0x00, 0x43, 0xdc # Add stair tile near chest in zora's vilage present
        ])

    assembler.add_floating_chunk("tileReplacementTable", tiles_to_replace)

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

        
def define_option_constants(assembler: Z80Assembler, patch_data):
    options = patch_data["options"]

    if not hasattr(get_settings().tloz_ooa_options, "beat_tutorial"):
        assembler.define_byte("option.startingGroup", 0x03)
        assembler.define_byte("option.startingRoom", 0xbf)
    else: # Redirect user to the first item check, saving them some time.
        assembler.define_byte("option.startingGroup", 0x00)
        assembler.define_byte("option.startingRoom", 0x39)

    assembler.define_byte("option.warpingGroup", patch_data["warp_to_start_variables"]["group"] if "group" in patch_data["warp_to_start_variables"] else 0x00)
    assembler.define_byte("option.warpingRoom", patch_data["warp_to_start_variables"]["room"] if "room" in patch_data["warp_to_start_variables"] else 0x59)
    assembler.define_byte("option.warpingPos", patch_data["warp_to_start_variables"]["pos"] if "pos" in patch_data["warp_to_start_variables"] else 0x55)
    assembler.define_byte("option.warpingDestTransittion", patch_data["warp_to_start_variables"]["dest_transittion"] if "dest_transittion" in patch_data["warp_to_start_variables"] else 0x05)
    assembler.define_byte("option.warpingSrcTransittion", patch_data["warp_to_start_variables"]["src_transittion"] if "src_transittion" in patch_data["warp_to_start_variables"] else 0x03)

    if options["secret_locations"]:
        assembler.define_byte("option.secretLocationsEnabled", 1)
    if options["linked_heros_cave"] != OracleOfAgesLinkedHerosCave.option_disabled:
        assembler.define_byte("option.enabledLinkedHerosCave", 1)
    # assembler.define_byte("option.currentsActivatesPortals", 0x01 if options["currents_activates_portals"] else 0x00)


    assembler.define_byte("option.animalCompanion", 0x0b + options["animal_companion"])
    assembler.define_byte("option.defaultSeedType", 0x20 + options["default_seed"])
    assembler.define_byte("option.receivedDamageModifier", options["combat_difficulty"])
    assembler.define_byte("option.openAdvanceShop", options["advance_shop"])

    assembler.define_byte("option.requiredEssences", options["required_essences"])
    assembler.define_byte("option.required_slates", options["required_slates"])
    
    assembler.define_byte("option.keysanity_small_keys", options["keysanity_small_keys"])
    keysanity = options["keysanity_small_keys"] or options["keysanity_boss_keys"]
    assembler.define_byte("option.customCompassChimes", 1 if keysanity else 0)

    master_keys_as_boss_keys = options["master_keys"] == OraclesMasterKeys.option_all_dungeon_keys
    assembler.define_byte("option.smallKeySprite", 0x43 if master_keys_as_boss_keys else 0x42)

def process_item_name_for_shop_text(item_name: str) -> List[int]:
    words = item_name.split(" ")
    current_line = 0
    lines = [""]
    while len(words) > 0:
        line_with_word = lines[current_line]
        if len(line_with_word) > 0:
            line_with_word += " "
        line_with_word += words[0]
        if len(line_with_word) <= 16:
            lines[current_line] = line_with_word
        else:
            current_line += 1
            lines.append(words[0])
        words = words[1:]

    result = []
    for line in lines:
        if len(result) > 0:
            result.append(0x01)  # Newline
        result.extend(line.encode())
    return result

def define_text_constants(assembler: Z80Assembler, patch_data):
    overworld_shops = [
        "Lynna Shop",
        "Hidden Shop",
        "Syrup Shop",
        "Advance Shop",
    ]

    for shop_name in overworld_shops:
        for i in range(1, 4):
            location_name = f"{shop_name} #{i}"
            symbolic_name = LOCATIONS_DATA[location_name]["symbolic_name"]
            text_bytes = []
            if location_name in patch_data["locations"]:
                item_name_bytes = process_item_name_for_shop_text(patch_data["locations"][location_name])
                text_bytes = [0x09, 0x01] + item_name_bytes + [0x09, 0x00, 0x0c, 0x18, 0x01]  # Item name
                if shop_name != "Tokay Market":
                    text_bytes.extend([0x20, 0x0c, 0x08, 0x20, 0x03, 0x7b, 0x01])  # Price
                    text_bytes.extend([0x02, 0x00, 0x00])  # OK / No thanks
            assembler.add_floating_chunk(f"text.{symbolic_name}", text_bytes)

    #Tokay Market
    shop_name = "Tokay Market"
    for i in range(1, 3):
        location_name = f"{shop_name} #{i}"
        symbolic_name = LOCATIONS_DATA[location_name]["symbolic_name"]
        text_bytes = []
        if location_name in patch_data["locations"]:
            item_name_bytes = process_item_name_for_shop_text(patch_data["locations"][location_name])
            text_bytes = [0x09, 0x01] + item_name_bytes + [0x09, 0x00, 0x0c, 0x18, 0x00]  # Item name
            assembler.add_floating_chunk(f"text.{symbolic_name}", text_bytes)
    text_bytes = [0x31, 0x30, 0x20, 0x02, 0x12, 0x01, 0x02, 0x00, 0x00]
    assembler.add_floating_chunk(f"text.tokayMarket1Validation", text_bytes)


def write_chest_contents(rom: RomData, patch_data):
    """
    Chest locations are packed inside several big tables in the ROM, unlike other more specific locations.
    This puts the item described in the patch data inside each chest in the game.
    """
    for location_name, location_data in LOCATIONS_DATA.items():
        if (location_data.get(
            "collect", COLLECT_TOUCH
        ) != COLLECT_CHEST and not location_data.get(
            "is_chest", False
        ) and location_name != "Bush Cave Chest") or (
            patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_disabled and (
                "dungeon" in location_data and location_data["dungeon"] == 11
            )
        ) or (not patch_data["options"]["secret_locations"] and "secret_location" in location_data) or (
            "dontOverwriteChestData" in location_data and location_data["dontOverwriteChestData"] is True
        ):
            continue
        if location_name == "Nuun Highlands Cave":
            chest_addr = rom.get_chest_addr(location_data['room'][patch_data["options"]["animal_companion"]], 0x16, 0x5108)
        else:
            chest_addr = rom.get_chest_addr(location_data['room'], 0x16, 0x5108)
        item_name = patch_data["locations"][location_name]
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
            print(location_name)
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

def set_dungeon_warps(rom: RomData, patch_data: dict[str, Any], dungeon_entrances: dict[str, Any], dungeon_exits: dict[str, Any]):
    warp_matchings = patch_data["dungeon_entrances"]
    enter_values = {name: rom.read_word(dungeon["addr"]) for name, dungeon in dungeon_entrances.items()}
    exit_values = {name: rom.read_word(dungeon["addr"]) for name, dungeon in dungeon_exits.items()}

    # Apply warp matchings expressed in the patch
    for from_name, to_name in warp_matchings.items():
        if from_name == "d11" and patch_data["options"]["linked_heros_cave"] != OracleOfAgesLinkedHerosCave.option_maku_tree_entrance_right_side:
            # For some reason, d11 with a custom warp is causing the d3 exit to not work right. Hopefully skipping this while d11 is present helps.
            continue
        default_entrance_of_to_name = [name for name, dungeon in dungeon_entrances.items() if dungeon["default"] == to_name][0]
        default_exit_of_from_name = dungeon_entrances[from_name]["default"]
        entrance_addr = dungeon_entrances[from_name]["addr"]
        exit_addr = dungeon_exits[to_name]["addr"]
        rom.write_word(entrance_addr, enter_values[default_entrance_of_to_name])
        rom.write_word(exit_addr, exit_values[default_exit_of_from_name])

    # Build a map dungeon => entrance (useful for essence warps)
    entrance_map = dict((v, k) for k, v in warp_matchings.items())

    # D1-D8 Essence Warps (hardcoded in one array using a unified format)
    for i in range(9):
        if i == 8:
            if patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_disabled:
                continue
            i = 10
        entrance_name = f"d{i + 1}"
        if i == 5:
            entrance_name += " past"
        entrance = dungeon_entrances[entrance_map[entrance_name]]
        if i == 10:
            rom.write_bytes(GameboyAddress(0x0a, 0x7205).address_in_rom(), [
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
#        map_tile = dungeon_entrances[entrance_name]["map_tile"]
#        rom.write_byte(0x???? + map_tile, 0x81 | (dungeon_index << 3))

def define_dungeon_items_text_constants(assembler: Z80Assembler, patch_data):

    for i in range(11): # D0 has no map, no compass, no boss key, and the unique small key use the default text. 
        # " for\nDungeon X"
        if i == 10:
            if patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_disabled:
                continue
            i = 11
        trueI = i if i != 9 else 6
        dungeon_precision = [0x03, 0x39, 0x44, 0x05, 0xe6, 0x20, (0x30 + trueI)]
        dungeon_tag = f"D{trueI}"
        dungeon_precisionForBossKey = dungeon_precision.copy()

        if i == 6:
            #\n(present)
            dungeon_precision.extend([0x01, 0x28, 0x03, 0x2e, 0x29])
            dungeon_tag += "Present"
        if i == 9:
            #\n(past)
            dungeon_precision.extend([0x01, 0x28, 0x70, 0x61, 0x73, 0x74, 0x29])
            dungeon_tag += "Past"

        # ###### Small keys ##############################################
        # "You found a\n\color(RED)"
        small_key_text = [0x02, 0x7c, 0x20, 0x61, 0x01, 0x09, 0x01]
        if patch_data["options"]["master_keys"]:
            # "Master Key"
            small_key_text.extend([0x4d, 0x61, 0x73, 0x74, 0x65, 0x72, 0x20, 0x03, 0x37])
        else:
            # "Small Key"
            small_key_text.extend([0x53, 0x6d, 0x04, 0xd2, 0x4b, 0x65, 0x79])
        if patch_data["options"]["keysanity_small_keys"]:
            small_key_text.extend(dungeon_precision)
        small_key_text.extend([0x09, 0x00, 0x21, 0x00])  # "\color(WHITE)!(end)"
        assembler.add_floating_chunk(f"text.smallKey{dungeon_tag}", small_key_text)

        # Linked Hero's Cave and Maku Path only have Small Keys, so skip other texts
        if i == 0 or i == 11:
            continue

        # ###### Boss keys ##############################################
        # "You found the\n\color(RED)Boss Key"
        if i < 9:
            boss_key_text = [
                0x02, 0x7c, 0x20, 0x05, 0xb4,
                0x09, 0x01, 0x42, 0x6f, 0x73, 0x73, 0x20, 0x4b, 0x65, 0x79
            ]
            if patch_data["options"]["keysanity_boss_keys"]:
                boss_key_text.extend(dungeon_precisionForBossKey)
            boss_key_text.extend([0x09, 0x00, 0x21, 0x00])  # "\color(WHITE)!(end)"
            assembler.add_floating_chunk(f"text.bossKeyD{trueI}", boss_key_text)

        # ###### Dungeon maps ##############################################
        # "You found the\n\color(RED)"
        dungeon_map_text = [0x02, 0x7c, 0x20, 0x05, 0xb4, 0x09, 0x01]
        if patch_data["options"]["keysanity_maps_compasses"]:
            dungeon_map_text.extend([0x4d, 0x61, 0x70])  # "Map"
            dungeon_map_text.extend(dungeon_precision)
        else:
            dungeon_map_text.extend(process_item_name_for_shop_text("Dungeon Map"))  # "Dungeon Map"
        dungeon_map_text.extend([0x09, 0x00, 0x21, 0x00])  # "\color(WHITE)!(end)"
        assembler.add_floating_chunk(f"text.dungeonMap{dungeon_tag}", dungeon_map_text)

        # ###### Compasses ##############################################
        # "You found the\n\color(RED)Compass"
        compasses_text = [
            0x02, 0x7c, 0x20, 0x05, 0xb4, 0x09, 0x01,
            0x09, 0x01, 0x43, 0x6f, 0x6d, 0x05, 0xfe
        ]
        if patch_data["options"]["keysanity_maps_compasses"]:
            compasses_text.extend(dungeon_precision)
        compasses_text.extend([0x09, 0x00, 0x21, 0x00])  # "\color(WHITE)!(end)"
        assembler.add_floating_chunk(f"text.compass{dungeon_tag}", compasses_text)

def set_file_select_text(assembler: Z80Assembler, slot_name: str):
    from .. import OracleOfAgesWorld
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