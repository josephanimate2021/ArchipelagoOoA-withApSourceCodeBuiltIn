from typing import List, Any

import os
import random
from collections import defaultdict
from pathlib import Path

import Utils
from settings import get_settings
from .Constants import *
from ..Options import OraclesOldMenShuffle, OraclesGoal, OraclesAnimalCompanion, \
    OraclesMasterKeys, OraclesShowDungeonsWithEssence, OracleOfAgesLinkedHerosCave
from ..common.patching.RomData import RomData
from ..common.patching.Util import get_available_random_colors_from_sprite_name, simple_hex
from ..common.patching.text import normalize_text
from ..common.patching.z80asm.Assembler import Z80Assembler
from ..common.patching.z80asm.Util import parse_hex_string_to_value
from ..data.Constants import *
from ..data import LOCATIONS_DATA, ITEMS_DATA
from ..generation.Hints import make_hint_texts
from .Util import *


def define_foreign_item_data(assembler: Z80Assembler, texts: dict[str, str], patch_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    # Register all foreign items and save their text as TX_0cxx, id 0x41, subid xx
    item_data = ITEMS_DATA.copy()
    current_subid = 0
    foreign_item_data = []

    all_locations = patch_data["locations"]
    for location in all_locations:
        location_content = all_locations[location]
        if "player" not in location_content:
            continue
        texts[f"TX_0c{simple_hex(current_subid)}"] = normalize_text(f"You got a 🟥{location_content["item"]}⬜ for 🟦{location_content["player"]}⬜!")
        foreign_item_data.extend([
            0x00, # grab mode, doesn't really matter
            current_subid, # parameter, not sure it matters
            current_subid, # text id, will need special handling
            0x52 if location_content["progression"] else 0x53 # sprite
        ])
        item_data[f"{location_content["item"]}|{location_content["player"]}"] = {
            "id": 0x41,
            "subid": current_subid,
        }
        current_subid += 1

    assembler.add_floating_chunk("archipelago_items", foreign_item_data)
    return item_data


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
        elif patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_d2_present:
            asm_files.append("asm/conditional/d11_in_d2_present.yaml")
    if patch_data["options"]["miniboss_locations"]:
        asm_files.append("asm/conditional/miniboss_locations.yaml")
    return asm_files


def write_chest_contents(rom: RomData, patch_data: dict[str, Any], item_data: dict[str, dict[str, Any]]) -> None:
    """
    Chest locations are packed inside several big tables in the ROM, unlike other more specific locations.
    This puts the item described in the patch data inside each chest in the game.
    """
    locations_data = patch_data["locations"]
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
        item = locations_data[location_name]
        item_id, item_subid = get_item_id_and_subid(item_data, item)
        rom.write_byte(chest_addr, item_id)
        rom.write_byte(chest_addr + 1, item_subid)


def define_compass_rooms_table(assembler: Z80Assembler, patch_data: dict[str, Any], item_data: dict[str, dict[str, Any]]) -> None:
    table = []
    for location_name, item in patch_data["locations"].items():
        item_id, item_subid = get_item_id_and_subid(item_data, item)
        dungeon = 0xff
        if item_id == 0x30:  # Small Key or Master Key
            dungeon = item_subid
        elif item_id == 0x31:  # Boss Key
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


def define_collect_properties_table(assembler: Z80Assembler, patch_data: dict[str, Any], item_data: dict[str, dict[str, Any]]) -> None:
    """
    Defines a table of (group, room, collect mode) entries for randomized items
    to determine how they spawn, how they are grabbed and whether they set
    a room flag when obtained.
    """
    table = []
    for location_name, item in patch_data["locations"].items():
        location_data = LOCATIONS_DATA[location_name]
        if "collect" not in location_data or "room" not in location_data:
            continue
        mode = location_data["collect"]

        # Use no pickup animation for falling small keys
        item_id, _ = get_item_id_and_subid(item_data, item)
        if item_id == 0x30 and mode == COLLECT_DROP:
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


def define_additional_tile_replacements(assembler: Z80Assembler, patch_data: dict[str, Any]) -> None:
    """
    Define a list of entries following the format of `tileReplacementsTable` (see ASM for more info) which end up
    being tile replacements on various rooms in the game.
    """
    # TODO: Figure out tile bytes for each soil in ages
    table = []
    # Remove Gasha spots when harvested once if deterministic Gasha locations are enabled
    if patch_data["options"]["deterministic_gasha_locations"] > 0:
        table.extend([
            0x00, 0xa6, 0x20, 0x54, 0xe1,  # North Horon: Gasha Spot Above Impa
            0x00, 0xc8, 0x20, 0x67, 0xe1,  # Horon Village: Gasha Spot Near Mayor's House
            0x00, 0xac, 0x20, 0x27, 0xe1,  # Eastern Suburbs: Gasha Spot
            0x00, 0x95, 0x20, 0x32, 0xe1,  # Holodrum Plain: Gasha Spot Near Mrs. Ruul's House
            0x00, 0x75, 0x20, 0x34, 0xe1,  # Holodrum Plain: Gasha Spot on Island Above D1
            0x00, 0x80, 0x20, 0x53, 0xe1,  # Spool Swamp: Gasha Spot Near Floodgate Keyhole
            0x00, 0xc0, 0x20, 0x61, 0xe1,  # Spool Swamp: Gasha Spot Near Portal
            0x00, 0x3f, 0x20, 0x44, 0xe1,  # Sunken City: Gasha Spot
            0x00, 0x1f, 0x20, 0x21, 0xe1,  # Mt. Cucco: Gasha Spot
            0x00, 0x38, 0x20, 0x25, 0xe1,  # Goron Mountain: Gasha Spot Left of Entrance
            0x00, 0x3b, 0x20, 0x53, 0xe1,  # Goron Mountain: Gasha Spot Right of Entrance
            0x00, 0x89, 0x20, 0x24, 0xe1,  # Eyeglass Lake: Gasha Spot Near D5
            0x00, 0x22, 0x20, 0x45, 0xe1,  # Tarm Ruins: Gasha Spot
            0x00, 0xf0, 0x20, 0x22, 0xe1,  # Western Coast: Gasha Spot South of Graveyard
            0x00, 0xef, 0x20, 0x66, 0xe1,  # Samasa Desert: Gasha Spot
            0x00, 0x44, 0x20, 0x44, 0xe1,  # Path to Onox Castle: Gasha Spot
        ])
    assembler.add_floating_chunk("additionalTileReplacements", table)


def define_location_constants(assembler: Z80Assembler, patch_data: dict[str, Any], item_data: dict[str, dict[str, Any]]):
    # If "Enforce potion in shop" is enabled, put a Potion in a specific location in Lynna Shop that was
    # disabled at generation time to prevent trackers from tracking it
    if patch_data["options"]["enforce_potion_in_shop"]:
        patch_data["locations"]["Lynna Shop #3"] = {"item": "Potion"}

    # Define shop prices as constants
    for symbolic_name, price in patch_data["shop_prices"].items():
        assembler.define_byte(f"shopPrices.{symbolic_name}", RUPEE_VALUES[price])

    for location_name, location_data in LOCATIONS_DATA.items():
        if "symbolic_name" not in location_data:
            continue

        symbolic_name = location_data["symbolic_name"]
        if location_name in patch_data["locations"]:
            item = patch_data["locations"][location_name]
        else:
            # Put a fake item for disabled locations, since they are unreachable anwyway
            item = {"item": "Friendship Ring"}

        item_id, item_subid = get_item_id_and_subid(item_data, item)
        assembler.define_byte(f"locations.{symbolic_name}.id", item_id)
        assembler.define_byte(f"locations.{symbolic_name}.subid", item_subid)
        assembler.define_word(f"locations.{symbolic_name}", (item_id << 8) + item_subid)

    # Process deterministic Gasha Nut locations to define a table
    deterministic_gasha_table = []
    for i in range(int(patch_data["options"]["deterministic_gasha_locations"])):
        item = patch_data["locations"][f"Gasha Nut #{i + 1}"]
        item_id, item_subid = get_item_id_and_subid(item_data, item)
        deterministic_gasha_table.extend([item_id, item_subid])
    assembler.add_floating_chunk("deterministicGashaLootTable", deterministic_gasha_table)


def define_option_constants(assembler: Z80Assembler, patch_data: dict[str, Any]) -> None:
    options = patch_data["options"]

    assembler.define_byte("option.startingGroup", 0x00)
    assembler.define_byte("option.startingRoom", 0x39)
    assembler.define_byte("option.startingPosY", 0x02)
    assembler.define_byte("option.startingPosX", 0x01)

    assembler.define_byte("option.warpingGroup", patch_data["warp_to_start_variables"]["group"] if "group" in patch_data["warp_to_start_variables"] else 0x00)
    assembler.define_byte("option.warpingRoom", patch_data["warp_to_start_variables"]["room"] if "room" in patch_data["warp_to_start_variables"] else 0x59)
    assembler.define_byte("option.warpingPos", patch_data["warp_to_start_variables"]["pos"] if "pos" in patch_data["warp_to_start_variables"] else 0x55)
    assembler.define_byte("option.warpingDestTransittion", patch_data["warp_to_start_variables"]["dest_transittion"] if "dest_transittion" in patch_data["warp_to_start_variables"] else 0x05)
    assembler.define_byte("option.warpingSrcTransittion", patch_data["warp_to_start_variables"]["src_transittion"] if "src_transittion" in patch_data["warp_to_start_variables"] else 0x03)

    if options["secret_locations"]:
        assembler.define_byte("option.secretLocationsEnabled", 1)
    if options["linked_heros_cave"] != OracleOfAgesLinkedHerosCave.option_disabled:
        assembler.define_byte("option.enabledLinkedHerosCave", 1)

    assembler.define_byte("option.animalCompanion", 0x0b + patch_data["options"]["animal_companion"])
    assembler.define_byte("option.defaultSeedType", 0x20 + patch_data["options"]["default_seed"])
    assembler.define_byte("option.receivedDamageModifier", options["combat_difficulty"])
    assembler.define_byte("option.openAdvanceShop", options["advance_shop"])

    assembler.define_byte("option.requiredEssences", options["required_essences"])
    assembler.define_byte("option.required_slates", options["required_slates"])

    assembler.define_byte("option.deterministicGashaLootCount", options["deterministic_gasha_locations"])

    assembler.define_byte("option.keysanity_small_keys", patch_data["options"]["keysanity_small_keys"])
    keysanity = patch_data["options"]["keysanity_small_keys"] or patch_data["options"]["keysanity_boss_keys"]
    assembler.define_byte("option.customCompassChimes", 1 if keysanity else 0)

    master_keys_as_boss_keys = patch_data["options"]["master_keys"] == OraclesMasterKeys.option_all_dungeon_keys
    assembler.define_byte("option.smallKeySprite", 0x43 if master_keys_as_boss_keys else 0x42)

    scrubs_all_refill = not patch_data["options"]["shuffle_business_scrubs"]
    # TODO: BUSINESS SCRUBS

    if patch_data["options"]["show_dungeons_with_map"]:
        assembler.define_byte("showDungeonWithMap", 0x01)


def define_tree_sprites(assembler: Z80Assembler, patch_data: dict[str, Any], item_data: dict[str, dict[str, Any]]) -> None:
    #TODO: Make custom tree sprite creation work for ages.
    tree_data = {  # Name: (map, position)
        "Horon Village: Seed Tree": (0xf8, 0x48),
        "Woods of Winter: Seed Tree": (0x9e, 0x88),
        "Holodrum Plain: Seed Tree": (0x67, 0x88),
        "Spool Swamp: Seed Tree": (0x72, 0x88),
        "Sunken City: Seed Tree": (0x5f, 0x86),
        "Tarm Ruins: Seed Tree": (0x10, 0x48),
    }
    i = 1
    for tree_name in tree_data:
        seed = patch_data["locations"][tree_name]
        if seed["item"] == "Ember Seeds":
            continue
        seed_id, _ = get_item_id_and_subid(item_data, seed)
        assembler.define_byte(f"seedTree{i}.map", tree_data[tree_name][0])
        assembler.define_byte(f"seedTree{i}.position", tree_data[tree_name][1])
        assembler.define_byte(f"seedTree{i}.gfx", seed_id - 26)
        assembler.define(f"seedTree{i}.rectangle", f"treeRect{seed_id}")
        i += 1
    if i == 5:
        # Duplicate ember, we have to blank some data
        assembler.define_byte("seedTree5.enabled", 0x0e)
        assembler.define_byte("seedTree5.map", 0xff)
        assembler.define_byte("seedTree5.position", 0)
        assembler.define_byte("seedTree5.gfx", 0)
        assembler.define_word("seedTree5.rectangle", 0)
    else:
        assembler.define_byte("seedTree5.enabled", 0x0d)


def get_treasure_addr(rom: RomData, item_name: str, item_data: dict[str, dict[str, Any]]) -> int:
    item_id, item_subid = get_item_id_and_subid(item_data, {"item": item_name})
    addr = 0x59332 + (item_id * 4)
    if rom.read_byte(addr) & 0x80 != 0:
        addr = 0x54000 + rom.read_word(addr + 1)
    return addr + (item_subid * 4)


def set_treasure_data(rom: RomData, item_data: dict[str, dict[str, Any]],
                      item_name: str, text_id: int | None,
                      sprite_id: int | None = None,
                      param_value: int | None = None) -> None:
    addr = get_treasure_addr(rom, item_name, item_data)
    if text_id is not None:
        rom.write_byte(addr + 0x02, text_id)
    if sprite_id is not None:
        rom.write_byte(addr + 0x03, sprite_id)
    if param_value is not None:
        rom.write_byte(addr + 0x01, param_value)


def set_player_start_inventory(assembler: Z80Assembler, patch_data: dict[str, Any]) -> None:
    #TODO: Make this function work for ages.
    obtained_treasures_address = parse_hex_string_to_value(DEFINES["wObtainedTreasureFlags"])
    start_inventory_changes = defaultdict(int)

    # ###### Base changes ##############################################
    start_inventory_changes[parse_hex_string_to_value(DEFINES["wIsLinkedGame"])] = 0x00  # No linked gaming
    start_inventory_changes[parse_hex_string_to_value(DEFINES["wAnimalTutorialFlags"])] = 0xff  # Animal vars
    # Remove the requirement to go in the screen under Sunken City tree to make Dimitri bullies appear
    start_inventory_changes[parse_hex_string_to_value(DEFINES["wDimitriState"])] = 0x20
    # Give L-3 ring box
    start_inventory_changes[0xc697] = 0x10
    start_inventory_changes[parse_hex_string_to_value(DEFINES["wRingBoxLevel"])] = 0x03

    # Starting map/compass
    if patch_data["options"]["starting_maps_compasses"]:
        dungeon_compass = parse_hex_string_to_value(DEFINES["wDungeonCompasses"])
        for i in range(dungeon_compass, dungeon_compass + 4):
            start_inventory_changes[i] = 0xff

    start_inventory_data: dict[str, int] = patch_data["start_inventory"]
    # Handle leveled items
    if "Progressive Shield" in start_inventory_data:
        start_inventory_changes[parse_hex_string_to_value(DEFINES["wShieldLevel"])] \
            = start_inventory_data["Progressive Shield"]
    bombs = 0
    if "Bombs (10)" in start_inventory_data:
        bombs += start_inventory_data["Bombs (10)"] * 0x10
    if "Bombs (20)" in start_inventory_data:
        bombs += start_inventory_data["Bombs (20)"] * 0x20
    if bombs > 0:
        start_inventory_changes[parse_hex_string_to_value(DEFINES["wCurrentBombs"])] \
            = start_inventory_changes[parse_hex_string_to_value(DEFINES["wMaxBombs"])] \
            = min(bombs, 0x99)
        # The bomb amounts are stored in decimal
    if "Progressive Sword" in start_inventory_data:
        start_inventory_changes[0xc6ac] = start_inventory_data["Progressive Sword"]
    if "Progressive Boomerang" in start_inventory_data:
        start_inventory_changes[0xc6b1] = start_inventory_data["Progressive Boomerang"]  # Boomerang level
    if "Ricky's Flute" in start_inventory_data:
        start_inventory_changes[parse_hex_string_to_value(DEFINES["wFluteIcon"])] = 0x01  # Flute icon
        start_inventory_changes[0xc643] |= 0x80  # Ricky State
    if "Dimitri's Flute" in start_inventory_data:
        start_inventory_changes[parse_hex_string_to_value(DEFINES["wFluteIcon"])] = 0x02  # Flute icon
        start_inventory_changes[0xc644] |= 0x80  # Dimitri State
    if "Moosh's Flute" in start_inventory_data:
        start_inventory_changes[parse_hex_string_to_value(DEFINES["wFluteIcon"])] = 0x03  # Flute icon
        start_inventory_changes[0xc645] |= 0x20  # Moosh State
    if "Progressive Feather" in start_inventory_data:
        start_inventory_changes[parse_hex_string_to_value(DEFINES["wFeatherLevel"])] \
            = start_inventory_data["Progressive Feather"]
    if "Switch Hook" in start_inventory_data:
        start_inventory_changes[parse_hex_string_to_value(DEFINES["wSwitchHookLevel"])] \
            = start_inventory_data["Switch Hook"]
    bombchus = 0
    if "Bombchus (10)" in start_inventory_data:
        bombchus += start_inventory_data["Bombchus (10)"] * 0x10
    if "Bombchus (20)" in start_inventory_data:
        bombchus += start_inventory_data["Bombchus (20)"] * 0x20
    if bombchus > 0:
        start_inventory_changes[parse_hex_string_to_value(DEFINES["wNumBombchus"])] \
            = start_inventory_changes[parse_hex_string_to_value(DEFINES["wMaxBombchus"])] \
            = min(bombchus, 0x99)
        # The bombchus amounts are stored in decimal

    seed_amount = 0
    if "Progressive Slingshot" in start_inventory_data:
        start_inventory_changes[0xc6b3] = start_inventory_data["Progressive Slingshot"]  # Slingshot level
        seed_amount = 0x20
    if "Seed Shooter" in start_inventory_data:
        seed_amount = 0x20
    if "Seed Satchel" in start_inventory_data:
        satchel_level = start_inventory_data["Seed Satchel"]
        start_inventory_changes[parse_hex_string_to_value(DEFINES["wSeedSatchelLevel"])] = satchel_level
        if satchel_level == 1:
            seed_amount = 0x20
        elif satchel_level == 2:
            seed_amount = 0x50
        else:
            seed_amount = 0x99
    if seed_amount:
        start_inventory_data[SEED_ITEMS[patch_data["options"]["default_seed"]]] = 1  # Add seeds to the start inventory

    # Inventory obtained flags
    current_inventory_index = parse_hex_string_to_value(DEFINES["wInventoryB"])
    for item in start_inventory_data:
        item_id = ITEMS_DATA[item]["id"]
        item_address = obtained_treasures_address + item_id // 8
        item_mask = 0x01 << (item_id % 8)

        start_inventory_changes[item_address] |= item_mask
        if item_id < 0x20:  # items prior to 0x20 are all usable
            if item == "Biggoron's Sword":
                # Biggoron needs special care since it occupies both hands
                if current_inventory_index == parse_hex_string_to_value(DEFINES["wInventoryB"]):
                    start_inventory_changes[current_inventory_index] \
                        = start_inventory_changes[current_inventory_index + 1] \
                        = item_id
                    current_inventory_index += 2
                elif current_inventory_index == parse_hex_string_to_value(DEFINES["wInventoryB"]) + 1:
                    current_inventory_index += 1
                    start_inventory_changes[current_inventory_index] = item_id
                    current_inventory_index += 1
            else:
                start_inventory_changes[current_inventory_index] = item_id  # Place the item in the inventory
                current_inventory_index += 1

        if item_id == 0x07:  # Rod of Seasons
            season = ITEMS_DATA[item]["subid"] - 2
            start_inventory_changes[0xc6b0] |= 0x01 << season
        elif item_id == 0x28:  # Rupees
            amount = int(item.split("(")[1][:-1])  # Find the value in the item name
            start_inventory_changes[0xc6a5] += amount * start_inventory_data[item]
        elif item_id == 0x37:  # Ore Chunks
            amount = int(item.split("(")[1][:-1])  # Find the value in the item name
            start_inventory_changes[0xc6a7] += amount * start_inventory_data[item]
        elif item_id == 0x30:  # Small keys
            subid = ITEMS_DATA[item]["subid"] % 0x80
            start_inventory_changes[0xc66e + subid] += start_inventory_data[item]
        elif item_id == 0x31:  # Boss keys
            subid = ITEMS_DATA[item]["subid"]
            start_inventory_changes[0xc67a + subid // 8] |= 0x01 << subid % 8
        elif item_id == 0x32:  # Compasses
            subid = ITEMS_DATA[item]["subid"]
            start_inventory_changes[0xc67c + subid // 8] |= 0x01 << subid % 8
        elif item_id == 0x33:  # Maps
            subid = ITEMS_DATA[item]["subid"]
            start_inventory_changes[0xc67e + subid // 8] |= 0x01 << subid % 8
        elif item_id == 0x2d:  # Rings
            subid = ITEMS_DATA[item]["subid"] - 4
            start_inventory_changes[parse_hex_string_to_value(DEFINES["wRingsObtained"]) + subid // 8] |= 0x01 << subid % 8
        elif item_id == 0x40:  # Essences
            subid = ITEMS_DATA[item]["subid"]
            start_inventory_changes[parse_hex_string_to_value(DEFINES["wEssencesObtained"])] |= 0x01 << subid % 8
        elif 0x20 <= item_id <= 0x24:  # Seeds
            seed_address = parse_hex_string_to_value(DEFINES["wNumEmberSeeds"]) + item_id - 0x20
            start_inventory_changes[seed_address] = seed_amount

    if 0xc6a5 in start_inventory_changes:
        hex_rupee_count = parse_hex_string_to_value(f"${start_inventory_changes[0xc6a5]}")
        start_inventory_changes[0xc6a5] = hex_rupee_count % 0x100
        start_inventory_changes[0xc6a6] = hex_rupee_count // 0x100
    if 0xc6a7 in start_inventory_changes:
        hex_ore_count = parse_hex_string_to_value(f"${start_inventory_changes[0xc6a7]}")
        start_inventory_changes[0xc6a7] = hex_ore_count % 0x100
        start_inventory_changes[0xc6a8] = hex_ore_count // 0x100
    if obtained_treasures_address in start_inventory_changes:
        start_inventory_changes[obtained_treasures_address] |= 1 << 2  # Add treasure punch flag

    heart_pieces = (start_inventory_data.get("Piece of Heart", 0) + start_inventory_data.get("Rare Peach Stone", 0))
    additional_hearts = (start_inventory_data.get("Heart Container", 0) + heart_pieces // 4)
    if additional_hearts:
        start_inventory_changes[0xc6a2] = start_inventory_changes[0xc6a3] = 12 + additional_hearts * 4
    if heart_pieces % 4:
        start_inventory_changes[0xc6a4] = heart_pieces % 4
    if "Gasha Seed" in start_inventory_data:
        start_inventory_changes[0xc6ba] = start_inventory_data["Gasha Seed"]

    # Make the list used in asm
    start_inventory = []
    for address in start_inventory_changes:
        start_inventory.append(address // 0x100)
        start_inventory.append(address % 0x100)
        start_inventory.append(start_inventory_changes[address])

    start_inventory.append(0x00)  # End of the list
    assembler.add_floating_chunk("startingInventory", start_inventory)


def alter_treasure_types(rom: RomData, item_data: dict[str, dict[str, Any]]) -> None:
    # Some treasures don't exist as interactions in base game, we need to add
    # text & sprite references for them to work properly in a randomized context
    set_treasure_data(rom, item_data, "Potion", 0x6d)

    # Set data for remote Archipelago items
    set_treasure_data(rom, item_data, "Archipelago Item", 0x57, 0x5a)
    set_treasure_data(rom, item_data, "Archipelago Progression Item", 0x57, 0x59)
    set_treasure_data(rom, item_data, "King Zora's Potion", 0x45, 0x5e)

    # Make bombs increase max carriable quantity when obtained from treasures,
    # not drops (see asm/seasons/bomb_bag_behavior)
    set_treasure_data(rom, item_data, "Bombs (10)", None, None, 0x90)


def set_old_men_rupee_values(rom: RomData, patch_data: dict[str, Any]) -> None:
    #TODO: Figure out bytes that handle old men taking/giving rupees.
    if patch_data["options"]["shuffle_old_men"] == OraclesOldMenShuffle.option_turn_into_locations:
        return
    for i, name in enumerate(OLD_MAN_RUPEE_VALUES.keys()):
        if name in patch_data["old_man_rupee_values"]:
            value = patch_data["old_man_rupee_values"][name]
            value_byte = RUPEE_VALUES[abs(value)]
            rom.write_byte(0x56233 + i, value_byte)

            if abs(value) == value:
                rom.write_word(0x2987b + (i * 2), 0x7472)  # Give rupees
            else:
                rom.write_word(0x2987b + (i * 2), 0x7488)  # Take rupees


def apply_miscellaneous_options(rom: RomData, patch_data: dict[str, Any]) -> None:
    # If lynna shop 3 is set to be a renewable Potion, manually edit the shop flag for
    # that slot to zero to make it stay after buying
    if patch_data["options"]["enforce_potion_in_shop"]:
        rom.write_byte(GameboyAddress(0x08, 0x4cfb).address_in_rom(), 0x00) # TODO: I don't know if that's right for lynna shop 3.

    if patch_data["options"]["master_keys"] != OraclesMasterKeys.option_disabled:
        # Remove small key consumption on keydoor opened
        rom.write_byte(0x18366, 0x00)
    if patch_data["options"]["master_keys"] == OraclesMasterKeys.option_all_dungeon_keys:
        # Remove boss key consumption on boss keydoor opened
        rom.write_word(0x1835e, 0x0000)
    # TODO: Figure out bank and rom addresses that handle the amount of enemies you have to kill for gasha seed planting.
    # rom.write_byte(GameboyAddress(0x0a, 0x46ed).address_in_rom(),
                   #patch_data["options"]["gasha_nut_kill_requirement"])
    # rom.write_byte(GameboyAddress(0x04, 0x6a31).address_in_rom(),
                   #patch_data["options"]["gasha_nut_kill_requirement"] // 2)


def set_file_select_text(assembler: Z80Assembler, slot_name: str) -> None:
    def char_to_tile(c: str) -> int:
        if "0" <= c <= "9":
            return ord(c) - 0x20
        if "A" <= c <= "Z":
            return ord(c) + 0xa1
        if c == "+":
            return 0xfd
        if c == "-":
            return 0xfe
        if c == ".":
            return 0xff
        else:
            return 0xfc  # All other chars are blank spaces

    row_1 = [char_to_tile(c) for c in
             f"AP {VERSION}"
             .center(16, " ")]
    row_2 = [char_to_tile(c) for c in slot_name.replace("-", " ").upper().center(16, " ")]

    text_tiles = [0x74, 0x31]
    text_tiles.extend(row_1)
    text_tiles.extend([0x41, 0x40])
    text_tiles.extend([0x02] * 12)  # Offscreen tiles

    text_tiles.extend([0x40, 0x41])
    text_tiles.extend(row_2)
    text_tiles.extend([0x51, 0x50])
    text_tiles.extend([0x02] * 12)  # Offscreen tiles

    assembler.add_floating_chunk("dma_FileSelectStringTiles", text_tiles)


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

def ancient_process_item_name_for_shop_text(item_name: str) -> List[int]:
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


def make_text_data(assembler: Z80Assembler, text: dict[str, str], patch_data: dict[str, Any]) -> None:
    # Process shops
    OVERWORLD_SHOPS = [
        "Lynna Shop",
        "Hidden Shop",
        "Syrup Shop",
        "Advance Shop"
    ]
    tx_indices = {
        "lynnaShop1": "TX_0e04",
        "lynnaShop2": "TX_0e03",
        "lynnaShop3": "TX_0e02",
        "hiddenShop1": "TX_0e1c",
        "hiddenShop2": "TX_0e1d",
        "hiddenShop3": "TX_0e1e",
        "syrupShop1": "TX_0d0a",
        "syrupShop2": "TX_0d01",
        "syrupShop3": "TX_0d05",
        "advanceShop1": "TX_0e22",
        "advanceShop2": "TX_0e23",
        "advanceShop3": "TX_0e25",
        "tokayMarket1": "TX_0a2a",
        "tokayMarket2": "TX_0a31",
    }

    for shop_name in OVERWORLD_SHOPS:
        for i in range(1, 4):
            location_name = f"{shop_name} #{i}"
            symbolic_name = LOCATIONS_DATA[location_name]["symbolic_name"]
            if location_name not in patch_data["locations"]:
                continue
            item_text = process_item_name_for_shop_text(patch_data["locations"][location_name])
            item_text += (" \\num1 Rupees\n"
                          "  \\optOK \\optNo thanks\\cmd(0f)")
            text[tx_indices[symbolic_name]] = item_text

    #Tokay Market (It's shop works differently than normal shops, so I don't think that I can adapt this section of code into Ishigh's work without overhaul of things I don't know anything about.)
    shop_name = "Tokay Market"
    for i in range(1, 3):
        location_name = f"{shop_name} #{i}"
        symbolic_name = LOCATIONS_DATA[location_name]["symbolic_name"]
        text_bytes = []
        if location_name in patch_data["locations"]:
            item_name_bytes = ancient_process_item_name_for_shop_text(patch_data["locations"][location_name]["item"])
            text_bytes = [0x09, 0x01] + item_name_bytes + [0x09, 0x00, 0x0c, 0x18, 0x00]  # Item name
            assembler.add_floating_chunk(f"text.{symbolic_name}", text_bytes)
    text_bytes = [0x31, 0x30, 0x20, 0x02, 0x12, 0x01, 0x02, 0x00, 0x00]
    assembler.add_floating_chunk(f"text.tokayMarket1Validation", text_bytes)

    BUSINESS_SCRUBS = [
        # TODO: Implement business scrubs
    ]
    for location_name in BUSINESS_SCRUBS:
        symbolic_name = LOCATIONS_DATA[location_name]["symbolic_name"]
        if location_name not in patch_data["locations"]:
            continue
        # Scrub string asking the player if they want to buy the item
        item_text = ("\\sfx(c6)Greetings!\n"
                     + process_item_name_for_shop_text(patch_data["locations"][location_name])
                     + f"for 🟩{patch_data['shop_prices'][symbolic_name]} Rupees⬜\n"
                       "  \\optOK \\optNo thanks")
        text[tx_indices[symbolic_name]] = item_text

    # Cross items (TODO)

    # Default satchel seed
    seed_name = SEED_ITEMS[patch_data["options"]["default_seed"]].replace(" ", "\n")
    text["TX_002d"] = text["TX_002d"].replace("Ember\nSeeds", seed_name)

    # TODO: Implement text on lynna village gasha farmer to tell the player how many nuts are good.
    

    # TODO: Implement hint texts
    # make_hint_texts(text, patch_data)


def set_heart_beep_interval_from_settings(rom: RomData) -> None:
    heart_beep_interval = get_settings()["tloz_ooa_options"]["heart_beep_interval"]
    if heart_beep_interval == "half":
        rom.write_byte(0x914B, 0x3f * 2)
    elif heart_beep_interval == "quarter":
        rom.write_byte(0x914B, 0x3f * 4)
    elif heart_beep_interval == "disabled":
        rom.write_bytes(0x914B, [0x00, 0xc9])  # Put a return to avoid beeping entirely


def set_character_sprite_from_settings(rom: RomData) -> None:
    sprite = get_settings()["tloz_ooa_options"]["character_sprite"]
    sprite_dir = Path(Utils.local_path(os.path.join("data", "sprites", "oos_ooa")))
    if sprite == "random":
        sprite_weights = {f: 1 for f in os.listdir(sprite_dir) if sprite_dir.joinpath(f).is_file() and f.endswith(".bin")}
    elif isinstance(sprite, str):
        sprite_weights = {sprite: 1}
    else:
        sprite_weights = sprite

    weights = random.randrange(sum(sprite_weights.values()))
    for sprite, weight in sprite_weights.items():
        weights -= weight
        if weights < 0:
            break

    palette_option = get_settings()["tloz_ooa_options"]["character_palette"]
    if palette_option == "random":
        palette_weights = {palette: 1 for palette in get_available_random_colors_from_sprite_name(sprite)}
    elif isinstance(palette_option, str):
        palette_weights = {palette_option: 1}
    else:
        valid_palettes = get_available_random_colors_from_sprite_name(sprite)
        palette_weights = {}
        for palette, weight in palette_option.items():
            splitted_palette = palette.split("|")
            if len(splitted_palette) == 2 and splitted_palette[1] != sprite:
                continue
            palette_name = splitted_palette[0]
            if palette_name == "random":
                for valid_palette in valid_palettes:
                    palette_weights[valid_palette] = weight
            elif palette_name in valid_palettes:
                palette_weights[palette_name] = weight
        if len(palette_weights) == 0:
            palette_weights["green"] = 1

    weights = random.randrange(sum(palette_weights.values()))
    for palette, weight in palette_weights.items():
        weights -= weight
        if weights < 0:
            break

    if not sprite.endswith(".bin"):
        sprite += ".bin"
    if sprite != "link.bin":
        sprite_path = sprite_dir.joinpath(sprite)
        if not (sprite_path.exists() and sprite_path.is_file()):
            raise ValueError(f"Path '{sprite_path}' doesn't exist")
        sprite_bytes = list(Path(sprite_path).read_bytes())
        rom.write_bytes(0x68000, sprite_bytes)

    # noinspection PyUnboundLocalVariable
    if palette == "green":
        return  # Nothing to change
    # noinspection PyUnboundLocalVariable
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


def inject_slot_name(rom: RomData, slot_name: str) -> None:
    slot_name_as_bytes = list(str.encode(slot_name))
    slot_name_as_bytes += [0x00] * (0x40 - len(slot_name_as_bytes))
    rom.write_bytes(0xfffc0, slot_name_as_bytes)


def set_dungeon_warps(rom: RomData, patch_data: dict[str, Any], dungeon_entrances: dict[str, Any], dungeon_exits: dict[str, Any]) -> None:
    warp_matchings = patch_data["dungeon_entrances"]
    enter_values = {name: rom.read_word(dungeon["addr"]) for name, dungeon in dungeon_entrances.items()}
    exit_values = {name: rom.read_word(addr) for name, addr in dungeon_exits.items()}

    # Apply warp matchings expressed in the patch
    for from_name, to_name in warp_matchings.items():
        entrance_addr = dungeon_entrances[from_name]["addr"]
        exit_addr = dungeon_exits[to_name]
        rom.write_word(entrance_addr, enter_values[to_name])
        rom.write_word(exit_addr, exit_values[from_name])

    # Build a map dungeon => entrance (useful for essence warps)
    entrance_map = dict((v, k) for k, v in warp_matchings.items())

    # D1-D8 Essence Warps (hardcoded in one array using a unified format)
    for i in range(8):
        # if i == 8:
            # if patch_data["options"]["linked_heros_cave"] == OracleOfAgesLinkedHerosCave.option_disabled:
                # continue
            # i = 10
        entrance_name = f"d{i + 1}"
        if i == 5:
            entrance_name += " past"
        entrance = dungeon_entrances[entrance_map[entrance_name]]
        rom.write_bytes(0x2874f + (i * 4), [
            entrance["group"] | 0x80,
            entrance["room"],
            entrance["position"],
            0x0e if entrance["shifted"] else 0x01
        ])

    # Change Minimap popups to indicate the randomized dungeon's name
    # TODO: Figure out the byte that handles the showing of a dungeon's name.
    # for i in range(8):
        # entrance_name = f"d{i}"
        # dungeon_index = int(warp_matchings[entrance_name][1:])
        # map_tile = dungeon_entrances[entrance_name]["map_tile"]
        # rom.write_byte(0xaa19 + map_tile, 0x81 | (dungeon_index << 3))

    # if patch_data["options"]["linked_heros_cave"]:
        # Change Minimap popups
        # entrance_name = "d11"
        # dungeon_index = int(warp_matchings[entrance_name][1:])
        # map_tile = dungeon_entrances[entrance_name]["map_tile"]
        # rom.write_byte(0xaa19 + map_tile, 0x81 | (dungeon_index << 3))


def define_dungeon_items_text_constants(texts: dict[str, str], patch_data: dict[str, Any]) -> None:
    base_id = 0x73
    for i in range(11):
        if i == 0:
            dungeon_precision = " for\nMaku Path"
        if i == 10:
            i = 11
            dungeon_precision = " for\nHero's Cave"
        elif i == 6 or i == 9:
            dungeon_precision = f" for\nMermaid's Cave\n{"(Past)" if i == 9 else "(Present)"}"
        else:
            dungeon_precision = f" for\nDungeon {i}"

        # ###### Small keys ##############################################
        small_key_text = "You found a\n🟥"
        if patch_data["options"]["master_keys"]:
            small_key_text += "Master Key"
        else:
            small_key_text += "Small Key"
        if patch_data["options"]["keysanity_small_keys"]:
            small_key_text += dungeon_precision
        small_key_text += "⬜!"
        texts[f"TX_00{simple_hex(base_id + i)}"] = small_key_text

        # Hero's Cave and Maku path only has Small Keys, so skip other texts
        if i == 0 or i == 11:
            continue

        # ###### Boss keys ##############################################
        boss_key_text = "You found the\n🟥Boss Key"
        if patch_data["options"]["keysanity_boss_keys"]:
            boss_key_text += dungeon_precision
        boss_key_text += "⬜!"
        texts[f"TX_00{simple_hex(base_id + i + 9)}"] = boss_key_text

        # ###### Dungeon maps ##############################################
        dungeon_map_text = "You found the\n🟥"
        if patch_data["options"]["keysanity_maps_compasses"]:
            dungeon_map_text += "Map"
            dungeon_map_text += dungeon_precision
        else:
            dungeon_map_text += "Dungeon Map"
        dungeon_map_text += "⬜!"
        texts[f"TX_00{simple_hex(base_id + i + 17)}"] = dungeon_map_text

        # ###### Compasses ##############################################
        compasses_text = "You found the\n🟥Compass"
        if patch_data["options"]["keysanity_maps_compasses"]:
            compasses_text += dungeon_precision
        compasses_text += "⬜!"
        texts[f"TX_00{simple_hex(base_id + i + 25)}"] = compasses_text

    if patch_data["options"]["master_keys"]:
        texts["TX_001a"] = texts["TX_001a"].replace("Small", "Master")


def define_essence_sparkle_constants(assembler: Z80Assembler, patch_data: dict[str, Any], dungeon_entrances: dict[str, Any]) -> None:
    byte_array = []
    show_dungeons_with_essence = patch_data["options"]["show_dungeons_with_essence"]

    essence_pedestals = [k for k, v in LOCATIONS_DATA.items() if v.get("essence", False)]
    if show_dungeons_with_essence and not patch_data["options"]["shuffle_essences"]:
        for i, pedestal in enumerate(essence_pedestals):
            if patch_data["locations"][pedestal]["item"] not in ITEM_GROUPS["Essences"]:
                byte_array.extend([0xF0, 0x00])  # Nonexistent room, for padding
                continue

            # Find where dungeon entrance is located, and place the sparkle hint there
            dungeon = f"d{i + 1}"
            dungeon_entrance = [k for k, v in patch_data["dungeon_entrances"].items() if v == dungeon][0]
            entrance_data = dungeon_entrances[dungeon_entrance]
            byte_array.extend([entrance_data["group"], entrance_data["room"]])
    assembler.add_floating_chunk("essenceLocationsTable", byte_array)

    require_compass = show_dungeons_with_essence == OraclesShowDungeonsWithEssence.option_with_compass
    assembler.define_byte("option.essenceSparklesRequireCompass", 1 if require_compass else 0)


def set_faq_trap(assembler: Z80Assembler) -> None:
    assembler.define_byte("option.startingGroup", 0x03, True)
    assembler.define_byte("option.startingRoom", 0xbf, True)
    assembler.define_byte("option.startingPosY", 0x50, True)
    assembler.define_byte("option.startingPosX", 0x78, True)


def randomize_ai_for_april_fools(rom: RomData, seed: int):
    # TODO: Make this function work for ages. Do we really want to do this though???
    code_table = 0x2f16
    # TODO : properly implement that ?
    enemy_table = [
        # enemy id in (08, 2f), specially for the blade traps since they can't take the beamos AI, or they'd block d6
        {
            0: [
                0x08,  # river zora
                0x09,  # octorok
                0x0c,  # arrow moblin
                0x0d,  # lynel
                0x0f,
                0x11,  # Pokey is too unreliable and laggy
                0x12,  # gibdo
                0x13,  # spark
                0x14,  # spiked beetle
                0x15,  # bubble
                0x18,  # buzzblob
                0x19,  # whisp
                0x1a,  # crab
                0x20,  # masked moblin
                0x22,
                0x23,  # pol's voice
                0x25,  # goponga flower
                0x29,
                0x2d,
                0x2e,
                0x2f
            ],
            1: [
                0x0a,  # boomerang moblin
                0x1c,  # iron mask
                0x1e,  # piranha
                0x25,
                0x2c,  # cheep cheep, will probably break
            ],
            2: [
                0x0b,  # leever
                0x17,  # ghini
                0x21,  # arrow darknut
            ],
            3: [
                0x1b,  # spiny beetle
                0x24,  # like like, flagged as unkillable as the spawner, and is logically not required
                0x2a,
            ],
            4: [
                0x10,  # rope
            ],
            5: [
                0x0e,  # blade trap
                0x2b,
            ],
        },
        # enemy id in (08, 2f)
        {
            0: [
                0x08,  # river zora
                0x09,  # octorok
                0x0c,  # arrow moblin
                0x0d,  # lynel
                0x0f,
                0x11,  # Pokey is too unreliable and laggy
                0x12,  # gibdo
                0x13,  # spark
                0x14,  # spiked beetle
                0x15,  # bubble
                0x16,  # beamos
                0x18,  # buzzblob
                0x19,  # whisp
                0x1a,  # crab
                0x20,  # masked moblin
                0x22,
                0x23,  # pol's voice
                0x25,  # goponga flower
                0x29,
                0x2d,
                0x2e,
                0x2f
            ],
            1: [
                0x0a,  # boomerang moblin
                0x1c,  # iron mask
                0x1e,  # piranha
                0x25,
                0x2c,  # cheep cheep, will probably break
            ],
            2: [
                0x0b,  # leever
                0x17,  # ghini
                0x21,  # arrow darknut
            ],
            3: [
                0x1b,  # spiny beetle
                0x24,  # like like, flagged as unkillable as the spawner, and is logically not required
                0x2a,
            ],
            4: [
                0x10,  # rope
            ],
            5: [
                0x2b,
            ],
        },
        # enemy id in (08, 2f), killable
        {
            0: [
                0x09,  # octorok
                0x12,  # gibdo
                0x14,  # spiked beetle
                0x18,  # buzzblob
                0x1a,  # crab
                0x22,
                0x23,  # pol's voice
                0x0d,  # lynel
                0x0c,  # arrow moblin
                0x20,  # masked moblin
            ],
            1: [
                0x0a,  # boomerang moblin
                0x1c,  # iron mask
                0x1e,  # piranha
                0x25,
            ],
            2: [
                0x0b,  # leever
                0x17,  # ghini
                0x21,  # arrow darknut
            ],
            4: [
                0x10,  # rope
            ],
        },

        # enemy id in (30, 60)
        {
            0: [
                0x30,
                0x31,
                0x33,
                0x36,
                0x37,
                0x38,
                0x3b,
                0x3c,
                0x3d,
                0x3e,
                0x43,
                0x46,
                0x48,
                0x49,
                0x4a,
                0x4b,
                0x4d,
                0x4e,
                0x5e,
            ],
            1: [
                0x32,
                0x34,
                0x39,
                0x41,
                0x4c,
                0x4f,
            ],
            2: [
                # 0x40,
                0x52,
            ],
            3: [
                0x51,
                0x58,
            ],
            4: [
                0x45,  # pincer
            ]
        },

        # enemy id in (30, 60), killable
        {
            0: [
                0x30,
                0x31,
                0x3c,
                0x3d,
                0x3e,
                0x43,
                0x48,
                0x49,
                0x4a,
                0x4b,
                0x4d,
                0x4e,
            ],
            1: [
                0x32,
                0x34,
                0x39,
                0x4c,
                0x4f,
            ],
            2: [
                # 0x40
            ],
        }
    ]
    r = random.Random(seed)
    ai_table = {}

    for bank in enemy_table:
        for cat in bank:
            enemies = bank[cat]
            if isinstance(cat, int) and cat != 0:
                ais = list(bank[cat])
                for cat2 in bank:
                    if isinstance(cat2, int):
                        if cat2 == 0:
                            ais.extend(bank[cat2])
                        elif cat2 >= cat:
                            ais.extend(bank[cat2])
                            ais.extend(bank[cat2])
            else:
                ais = list(bank[cat])
            r.shuffle(ais)
            for i in range(len(enemies)):
                enemy = enemies[i]
                ai = ais.pop()
                ai_table[enemy] = ai

    ai_table[0x2f] = 0x2f  # Thwomps have to stay vanilla for platforming
    for enemy in ai_table:
        ai = ai_table[enemy]
        rom.write_word(code_table + enemy * 2, rom.read_word(code_table + ai * 2))

    blinkers = {
        0x08,
        0x0b,
        0x10,
        0x24,
        0x34,
        0x40,
        0x41
    }

    # Make some enemies hittable without having access to their AI
    if ai_table[0x08] not in blinkers:
        rom.write_byte(0xFDD92, 0x8F)  # river zora
    if ai_table[0x0b] not in blinkers:
        rom.write_byte(0xFDD9E, 0x90)  # leever
    if ai_table[0x10] not in blinkers:
        rom.write_byte(0xFDDB2, 0x90)  # rope
    if ai_table[0x24] not in blinkers:
        rom.write_byte(0xFDE02, 0xA2)  # like-like
    if ai_table[0x34] not in blinkers:
        rom.write_byte(0xFDE42, 0xAA)  # zol
    # if ai_table[0x40] not in blinkers:
    #     rom.write_byte(0xFDE72, 0xAF)  # wizzrobes
    if ai_table[0x41] not in blinkers:
        rom.write_byte(0xFDE76, 0xB0)  # crow

    if ai_table[0x14] != 0x14:
        rom.write_byte(0xFDDC2, 0xCE)  # Make spiked beetles have the flipped collisions
    if ai_table[0x1C] != 0x1C:
        rom.write_byte(0xFDDE2, 0xD0)  # Make iron mask have the unmasked collisions
    if ai_table[0x3e] != 0x3e:
        rom.write_byte(0xFDE6A, 0xAE)  # Make peahats have vulnerable collisions

    if ai_table[0x24] != 0x24:
        # make like like deal low knockback instead of softlocking by grabbing him then never releasing him due to the lack of AI
        rom.write_byte(0x1EED0, 0x01)