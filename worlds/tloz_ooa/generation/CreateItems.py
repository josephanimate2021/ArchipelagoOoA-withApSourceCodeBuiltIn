from ..data import LOCATIONS_DATA, ITEMS_DATA
from ..data.Constants import *
from ..Options import *
from ..common.generation.CreateItems import *

def get_filler_item_name(world) -> str:
    FILLER_ITEM_NAMES = [
        "Rupees (1)", "Rupees (5)", "Rupees (10)", "Rupees (10)",
        "Rupees (20)", "Rupees (30)",
        "Random Ring", "Random Ring", "Random Ring",
        "Gasha Seed", "Gasha Seed",
        "Potion"
    ]

    item_name = world.random.choice(FILLER_ITEM_NAMES)
    if item_name == "Random Ring":
        return world.get_random_ring_name()
    return item_name


def build_item_pool_dict(world) -> dict[str, int]:
    excluded_mapass = set()
    if world.options.exclude_dungeons_without_essence and not world.options.shuffle_essences:
        for i, essence_name in enumerate(ITEM_GROUPS["Essences"], 1):
            if essence_name not in world.essences_in_game:
                excluded_mapass.add(f"Dungeon Map ({DUNGEON_NAMES[i]})")
                excluded_mapass.add(f"Compass ({DUNGEON_NAMES[i]})")

    item_pool_dict = {}
    filler_item_count = 0
    rupee_item_count = 0
    ore_item_count = 0
    extra_items = 0
    for loc_name, loc_data in LOCATIONS_DATA.items():
        if not world.location_is_active(loc_name, loc_data):
            continue
        if "vanilla_item" not in loc_data:
            continue

        item_name = loc_data["vanilla_item"]
        if "Ring" in item_name:
            item_name = "Random Ring"
        if item_name == "Filler Item":
            filler_item_count += 1
            continue
        if item_name.startswith("Rupees ("):
            if world.options.shop_prices == OraclesShopPrices.option_free:
                filler_item_count += 1
            else:
                rupee_item_count += 1
            continue
        if world.options.master_keys != OraclesMasterKeys.option_disabled and "Small Key" in item_name:
            # Small Keys don't exist if Master Keys are set to replace them
            filler_item_count += 1
            continue
        if world.options.master_keys == OraclesMasterKeys.option_all_dungeon_keys and "Boss Key" in item_name:
            # Boss keys don't exist if Master Keys are set to replace them
            filler_item_count += 1
            continue
        if world.options.starting_maps_compasses and ("Compass" in item_name or "Dungeon Map" in item_name):
            # Compasses and Dungeon Maps don't exist if player starts with them
            filler_item_count += 1
            continue
        if "essence" in loc_data and loc_data["essence"] is True:
            # If essence was decided not to be placed because of "Placed Essences" option or
            # because of pedestal being an excluded location, replace it with a filler item
            if item_name not in world.essences_in_game:
                filler_item_count += 1
                continue
            # If essences are not shuffled, place and lock this item directly on the pedestal.
            # Otherwise, the fill algorithm will take care of placing them anywhere in the multiworld.
            if not world.options.shuffle_essences:
                essence_item = create_item(world, item_name)
                world.multiworld.get_location(loc_name, world.player).place_locked_item(essence_item)
                continue

        if item_name == "Gasha Seed":
            # Remove all gasha seeds from the pool to read as many as needed a later while limiting their impact on the item pool
            filler_item_count += 1
            continue

        if item_name == "Flute":
            item_name = world.options.animal_companion.current_key.title() + "'s Flute"
        elif item_name in excluded_mapass:
            item_name += "!FILLER"

        item_pool_dict[item_name] = item_pool_dict.get(item_name, 0) + 1

    # If Master Keys are enabled, put one for every dungeon
    if world.options.master_keys != OraclesMasterKeys.option_disabled:
        for small_key_name in ITEM_GROUPS["Master Keys"]:
            if world.options.linked_heros_cave or small_key_name != "Master Key (Hero's Cave)":
                item_pool_dict[small_key_name] = 1
                extra_items += 1

    # Add the required gasha seeds to the pool
    required_gasha_seeds = world.options.deterministic_gasha_locations.value
    item_pool_dict["Gasha Seed"] = required_gasha_seeds
    extra_items += required_gasha_seeds

    if rupee_item_count > 0:
        rupee_item_pool, filler_item_count = build_rupee_item_dict(world, rupee_item_count, filler_item_count)
        item_pool_dict.update(rupee_item_pool)

    # Remove items from pool
    for item, removed_amount in world.options.remove_items_from_pool.items():
        if item in item_pool_dict:
            current_amount = item_pool_dict[item]
        else:
            current_amount = 0
        new_amount = current_amount - removed_amount
        if new_amount < 0:
            logging.warning(f"Not enough {item} to satisfy {world.player_name}'s remove_items_from_pool: "
                            f"{-new_amount} missing")
            new_amount = 0
        item_pool_dict[item] = new_amount
        filler_item_count += current_amount - new_amount

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

    assert filler_item_count >= extra_items
    filler_item_count -= extra_items

    # Add as many filler items as required
    for _ in range(filler_item_count):
        random_filler_item = world.get_filler_item_name()
        item_pool_dict[random_filler_item] = item_pool_dict.get(random_filler_item, 0) + 1

    if "Random Ring" in item_pool_dict:
        quantity = item_pool_dict["Random Ring"]
        for _ in range(quantity):
            ring_name = world.get_random_ring_name()
            item_pool_dict[ring_name] = item_pool_dict.get(ring_name, 0) + 1
        del item_pool_dict["Random Ring"]

    return item_pool_dict


def create_items(world):
    item_pool_dict = build_item_pool_dict(world)
    for item_name, quantity in item_pool_dict.items():
        for i in range(quantity):
            if (
                "Small Key" in item_name or "Master Key" in item_name
            ) and not world.options.keysanity_small_keys:
                world.dungeon_items.append(world.create_item(item_name))
            elif "Boss Key" in item_name and not world.options.keysanity_boss_keys:
                world.dungeon_items.append(world.create_item(item_name))
            elif (
                "Compass" in item_name or "Dungeon Map" in item_name
            ) and not world.options.keysanity_maps_compasses:
                world.dungeon_items.append(world.create_item(item_name))
            elif "Slate" in item_name and not world.options.keysanity_slates:
                world.dungeon_items.append(world.create_item(item_name))
            else:
                world.multiworld.itempool.append(world.create_item(item_name))


def create_rings(world, amount):
    # Get a subset of as many rings as needed
    ring_names = [name for name, idata in ITEMS_DATA.items() if "ring" in idata]
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
