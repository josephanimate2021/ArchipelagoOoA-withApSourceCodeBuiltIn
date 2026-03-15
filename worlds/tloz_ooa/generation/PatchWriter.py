import json
from collections import defaultdict

from typing import TYPE_CHECKING
from ..patching.ProcedurePatch import OoAProcedurePatch
from ..data.Constants import *
from ..Options import OracleOfAgesOptions


if TYPE_CHECKING:
    from .. import OracleOfAgesWorld


def ooa_create_ap_procedure_patch(world: "OracleOfAgesWorld") -> OoAProcedurePatch:
    patch = OoAProcedurePatch()

    patch.player = world.player
    patch.player_name = world.multiworld.get_player_name(world.player)

    patch_data = {
        "version": f"{VERSION}",
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
    }

    for loc in world.multiworld.get_locations(world.player):
        # Skip event locations which are not real in-game locations that need to be patched
        if loc.address is None:
            continue
        if loc.item.player == loc.player:
            patch_data["locations"][loc.name] = {
                "item": loc.item.name
            }
        else:
            patch_data["locations"][loc.name] = {
                "item": loc.item.name,
                "player": world.multiworld.get_player_name(loc.item.player),
                "progression": loc.item.advancement
            }

    patch_data_item_hints = []
    for item_hint in world.item_hints:
        if item_hint is None:
            # Joke hint
            patch_data_item_hints.append(None)
            continue
        location = item_hint.location
        player = location.player
        if player == world.player:
            player = None
        else:
            player = world.multiworld.get_player_name(player)
        patch_data_item_hints.append((item_hint.name, location.name, player))
    patch_data["item_hints"] = patch_data_item_hints

    start_inventory = defaultdict(int)
    for item in world.multiworld.precollected_items[world.player]:
        start_inventory[item.name] += 1
    patch_data["start_inventory"] = dict(start_inventory)

    patch.write_file("patch.dat", json.dumps(patch_data).encode("utf-8"))
    return patch