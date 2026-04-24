from BaseClasses import Region, Location, LocationProgressType
from Options import Accessibility, OptionError, Option
from ..data.Constants import *
from .Data import *
from .Logic import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import OracleOfAgesWorld

def generate_early(world: "OracleOfAgesWorld"):
    if world.interpret_slot_data(None):
        return
    conflicting_rings = (
        world.options.required_rings.value & world.options.excluded_rings.value
    )
    if len(conflicting_rings) > 0:
        raise OptionError(
            "Required Rings and Excluded Rings contain the same element(s)",
            conflicting_rings,
        )

    if world.options.shuffle_dungeons:
        world.shuffled_entrances = {}
        for warpName, warpData in WARPS_DATA.items():
            if "dungeon" not in warpData:  # Not a dungeon, skip it
                continue
            if (
                "require_option" not in warpData
                or hasattr(world.options, warpData["require_option"])
                and getattr(world.options, warpData["require_option"])
            ):
                world.shuffled_entrances[warpName] = warpName
        shuffle_entrances(world)

    restrict_non_local_items(world)

    randomize_shop_prices(world)


def restrict_non_local_items(world: "OracleOfAgesWorld"):
    # Restrict non_local_items option in cases where it's incompatible with other options that enforce items
    # to be placed locally (e.g. dungeon items with keysanity off)
    if not world.options.keysanity_small_keys:
        world.options.non_local_items.value -= world.item_name_groups[
            "Small Keys"
        ]
    if not world.options.keysanity_boss_keys:
        world.options.non_local_items.value -= world.item_name_groups[
            "Boss Keys"
        ]
    if not world.options.keysanity_maps_compasses:
        world.options.non_local_items.value -= world.item_name_groups[
            "Dungeon Maps"
        ]
        world.options.non_local_items.value -= world.item_name_groups[
            "Compasses"
        ]
    if not world.options.keysanity_slates:
        world.options.non_local_items.value -= set(["Slate"])


def shuffle_entrances(world: "OracleOfAgesWorld"):
    shuffled = list(world.shuffled_entrances.values())
    world.random.shuffle(shuffled)
    world.shuffled_entrances = dict(zip(world.shuffled_entrances, shuffled))


def randomize_shop_prices(world: "OracleOfAgesWorld"):
    prices_pool = get_prices_pool()
    world.random.shuffle(prices_pool)
    global_prices_factor = world.options.shop_prices_factor.value / 100.0
    for key, divider in world.shop_prices.items():
        floating_price = prices_pool.pop() * global_prices_factor / divider
        for i, value in enumerate(VALID_RUPEE_VALUES):
            if value > floating_price:
                world.shop_prices[key] = VALID_RUPEE_VALUES[i - 1]
                break


def exclude_problematic_locations(world: "OracleOfAgesWorld"):
    locations_to_exclude = []
    # If goal essence requirement is set to a specific value, prevent essence-bound checks which require more
    # essences than this goal to hold anything of value
    # if world.options.required_essences < 7:
    #    locations_to_exclude.append("Horon Village: Item Inside Maku Tree (7+ Essences)")
    #    if world.options.required_essences < 5:
    #        locations_to_exclude.append("Horon Village: Item Inside Maku Tree (5+ Essences)")
    #        if world.options.required_essences < 3:
    #            locations_to_exclude.append("Horon Village: Item Inside Maku Tree (3+ Essences)")

    # TODO PROBLEMATIC LOCATIONS

    for name in locations_to_exclude:
        world.multiworld.get_location(name, world.player).progress_type = (
            LocationProgressType.EXCLUDED
        )


def set_rules(world: "OracleOfAgesWorld"):
    create_connections(world)
    apply_self_locking_rules(world.multiworld, world.player)
    world.multiworld.completion_condition[world.player] = (
        lambda state: state.has("_beaten_game", world.player)
    )
