import json

import os

from typing import TYPE_CHECKING
from BaseClasses import ItemClassification
from ..patching.ProcedurePatch import OoAProcedurePatch
from ..data.Constants import *
from ..Options import OracleOfAgesOptions


if TYPE_CHECKING:
    from .. import OracleOfAgesWorld

def ooa_create_appp_patch(world: "OracleOfAgesWorld") -> OoAProcedurePatch:
    patch = OoAProcedurePatch()

    patch.player = world.player
    patch.player_name = world.multiworld.get_player_name(world.player)

    patch_data = {
        "version": f"{world.version()}",
        "seed": world.multiworld.seed,
        "options": world.options.as_dict(
            *[option_name for option_name in OracleOfAgesOptions.type_hints
              if hasattr(OracleOfAgesOptions.type_hints[option_name], "include_in_patch")]),
        "warp_to_start_variables": world.determine_warp_to_start_variables(),
        "old_man_rupee_values": world.old_man_rupee_values,
        "dungeon_entrances": {a.replace(" entrance", ""): b.replace("enter ", "")
                              for a, b in world.dungeon_entrances.items()},
        "locations": {},
        "shop_prices": world.shop_prices,
        "region_hints": world.region_hints,
        "music_order": {}
    }

    # Music shuffle stuff
    mus_values = []
    mus_props = []
    for property, value in MUSIC.items():
        mus_props.append(property)
        mus_values.append(value)
    if world.options.music_shuffle:
        world.random.shuffle(mus_values)
    for i in range(len(mus_props)):
        patch_data["music_order"][mus_props[i]] = mus_values[i]


    for loc in world.multiworld.get_locations(world.player):
        if loc.address is None:
            continue
        if loc.item.player == loc.player:
            item_name = loc.item.name
        elif loc.item.classification in [ItemClassification.progression, ItemClassification.progression_skip_balancing]:
            item_name = "Archipelago Progression Item"
        else:
            item_name = "Archipelago Item"
        loc_patcher_name = loc.name
        if loc_patcher_name != "":
            patch_data["locations"][loc_patcher_name] = item_name

    patch.write_file("patch.dat", json.dumps(patch_data, indent=4).encode('utf-8'))
    return patch
