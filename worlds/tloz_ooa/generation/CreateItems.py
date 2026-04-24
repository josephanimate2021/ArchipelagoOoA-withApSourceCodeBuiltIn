from .Data import *
from ..data.Items import *
from ..Options import *
from ..data import LOCATIONS_DATA
from ..data.Constants import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import OracleOfAgesWorld

def create_item(world: "OracleOfAgesWorld", name: str) -> Item:
    if name.endswith("!PROG"):
        # If item name has a "!PROG" suffix, force it to be progression. This is typically used to create the right
        # amount of progression rupees while keeping them a filler item as default
        name = name.removesuffix("!PROG")
        classification = ItemClassification.progression_skip_balancing
    elif name.endswith("!USEFUL"):
        # Same for above but with useful. This is typically used for Required Rings,
        # as we don't want those locked in a barren dungeon
        name = name.removesuffix("!USEFUL")
        classification = ITEMS_DATA[name]["classification"]
        if classification == ItemClassification.filler:
            classification = ItemClassification.useful
    else:
        classification = ITEMS_DATA[name]["classification"]
    ap_code = world.item_name_to_id[name]

    # A few items become progression only in hard logic
    progression_items_in_medium_logic = [
        "Expert's Ring",
        "Fist Ring",
        "Toss Ring",
        "Energy Ring",
    ]
    if (
        world.options.logic_difficulty == "medium"
        and name in progression_items_in_medium_logic
    ):
        classification = ItemClassification.progression

    return Item(name, classification, ap_code, world.player)

def location_is_active(world: "OracleOfAgesWorld", location_name, location_data):
    if (
        "conditional" not in location_data
        or location_data["conditional"] is False
    ):
        return True

    region_id = location_data["region_id"]
    if region_id == "advance shop":
        return world.options.advance_shop.value

    if "dungeon" in location_data:
        if location_data["dungeon"] == 11:
            return world.options.linked_heros_cave.value > 0
        if location_data["symbolic_name"] == f"d{location_data["dungeon"]}Miniboss":
            return world.options.miniboss_locations
        
    if "vasu" in region_id:
        return not world.options.vasu_ring_checks_requirement.get("disable_entirely")

    if "secret_location" in location_data and not False:
        return world.options.secret_locations

    # TODO FUNNY LOCATION ?

    return False


def build_item_pool_dict(world: "OracleOfAgesWorld"):
    item_pool_dict = {}
    filler_item_count = 0
    remaining_rings = len(
        {name for name, idata in ITEMS_DATA.items() if "ring" in idata}
    ) - len(world.options.excluded_rings.value)
    for loc_name, loc_data in LOCATIONS_DATA.items():

        if "vanilla_item" not in loc_data:
            # print("Can't create item from location '",loc_name ,"' because it doesn't have one")
            continue

        item_name = loc_data["vanilla_item"]
        if "randomized" in loc_data and loc_data["randomized"] is False:
            item = world.create_item(item_name)
            location = world.multiworld.get_location(loc_name, world.player)
            location.place_locked_item(item)
            # print("placing locked item '",loc_data['vanilla_item'] ,"' in '",loc_name ,"'")
            continue
        if not location_is_active(world, loc_name, loc_data):
            # print("Can't create item '",loc_data['vanilla_item'] ,"' because '",loc_name ,"' is not active")
            continue

        if (
            world.options.master_keys != OraclesMasterKeys.option_disabled
            and "Small Key" in item_name
        ):
            # Small Keys don't exist if Master Keys are set to replace them
            filler_item_count += 1
            continue
        if (
            world.options.master_keys
            == OraclesMasterKeys.option_all_dungeon_keys
            and "Boss Key" in item_name
        ):
            # Boss keys don't exist if Master Keys are set to replace them
            filler_item_count += 1
            continue

        item_name = loc_data["vanilla_item"]
        if "Ring" in item_name:
            if remaining_rings > 0:
                item_name = "Random Ring"
                remaining_rings -= 1
            else:
                filler_item_count += 1
                continue

        if "essence" in loc_data and loc_data["essence"] is True:
            # If essences are not shuffled, place and lock this item directly on the pedestal.
            # Otherwise, the fill algorithm will take care of placing them anywhere in the multiworld.
            if not world.options.shuffle_essences:
                essence_item = world.create_item(item_name)
                world.multiworld.get_location(
                    loc_name, world.player
                ).place_locked_item(essence_item)
                continue

        item_pool_dict[item_name] = item_pool_dict.get(item_name, 0) + 1

    # If Master Keys are enabled, put one for every dungeon
    if world.options.master_keys != OraclesMasterKeys.option_disabled:
        for small_key_name in ITEM_GROUPS["Master Keys"]:
            if (
                world.options.linked_heros_cave.value > 0
                or small_key_name != "Master Key (Linked Hero's Cave)"
            ):
                item_pool_dict[small_key_name] = 1
                filler_item_count -= 1

    # Add the required rings
    ring_copy = sorted(world.options.required_rings.value.copy())
    for _ in range(len(ring_copy)):
        ring_name = f"{ring_copy.pop()}!USEFUL"
        item_pool_dict[ring_name] = item_pool_dict.get(ring_name, 0) + 1

        if item_pool_dict["Random Ring"] > 0:
            # Take from set ring pool first
            item_pool_dict["Random Ring"] -= 1
        else:
            # Take from filler after
            filler_item_count -= 1

    # Add as many filler items as required
    for _ in range(filler_item_count):
        random_filler_item = get_filler_item_name(world)
        item_pool_dict[random_filler_item] = (
            item_pool_dict.get(random_filler_item, 0) + 1
        )

    # Perform adjustments on the item pool
    item_pool_adjustements = [
        [
            "Flute",
            world.options.animal_companion.current_key.title() + "'s Flute",
        ],  # Put a specific flute
        [
            "Gasha Seed",
            "Seed Satchel",
        ],  # Add a 3rd satchel that is usually obtained in linked games (99 seeds)
        [
            "Gasha Seed",
            "Bombs (10)",
        ],  # Add one more bomb compared to vanilla to reach 99 max bombs
        ["Gasha Seed", "Potion"],  # Replace some Gasha Seed by 2 potions.
        ["Gasha Seed", "Potion"],  # ^
        ["Gasha Seed", "Rupees (200)"],  # and one by rupees
        [
            "Gasha Seed",
            "Progressive Sword",
        ],  # Need an additionnal sword to go to L3
    ]

    for i, pair in enumerate(item_pool_adjustements):
        original_name = pair[0]
        replacement_name = pair[1]
        item_pool_dict[original_name] -= 1
        item_pool_dict[replacement_name] = (
            item_pool_dict.get(replacement_name, 0) + 1
        )

    return item_pool_dict


def create_items(world: "OracleOfAgesWorld"):
    item_pool_dict = build_item_pool_dict(world)

    # Create items following the dictionary that was previously constructed
    if item_pool_dict.get("Random Ring"):
        create_rings(world, item_pool_dict["Random Ring"])
        del item_pool_dict["Random Ring"]

    for item_name, quantity in item_pool_dict.items():
        for i in range(quantity):
            if (
                "Small Key" in item_name or "Master Key" in item_name
            ) and not world.options.keysanity_small_keys:
                world.dungeon_items.append(world.create_item(item_name))
            elif (
                "Boss Key" in item_name
                and not world.options.keysanity_boss_keys
            ):
                world.dungeon_items.append(world.create_item(item_name))
            elif (
                "Compass" in item_name or "Dungeon Map" in item_name
            ) and not world.options.keysanity_maps_compasses:
                world.dungeon_items.append(world.create_item(item_name))
            elif "Slate" in item_name and not world.options.keysanity_slates:
                world.dungeon_items.append(world.create_item(item_name))
            else:
                world.multiworld.itempool.append(world.create_item(item_name))


def create_rings(world: "OracleOfAgesWorld", amount):
    # Get a subset of as many rings as needed
    ring_names = [
        name for name, idata in ITEMS_DATA.items() if "ring" in idata
    ]
    # Remove excluded rings, and required rings because they'll be added later anyway
    ring_names = [
        name
        for name in ring_names
        if name not in world.options.required_rings.value
        and name not in world.options.excluded_rings.value
    ]

    world.random.shuffle(ring_names)
    del ring_names[amount:]
    for ring_name in ring_names:
        world.multiworld.itempool.append(world.create_item(ring_name))
    world.random_rings_pool = ring_names


def get_filler_item_name(world: "OracleOfAgesWorld") -> str:
    FILLER_ITEM_NAMES = [
        "Rupees (1)",
        "Rupees (5)",
        "Rupees (5)",
        "Rupees (10)",
        "Rupees (10)",
        "Rupees (20)",
        "Rupees (30)",
        "Gasha Seed",
        "Gasha Seed",
        "Potion",
    ]

    item_name = world.random.choice(FILLER_ITEM_NAMES)
    return item_name