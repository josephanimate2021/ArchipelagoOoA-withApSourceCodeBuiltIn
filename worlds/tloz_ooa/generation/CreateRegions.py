from BaseClasses import Region, Location
from ..data.Entrances import *
from ..data.Regions import *
from .Data import *
from ..Options import OracleOfAgesGoal
from ..data.Items import *
from .CreateItems import location_is_active
from .GenerateEarly import exclude_problematic_locations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import OracleOfAgesWorld

def create_location(world: "OracleOfAgesWorld", region_name: str, location_name: str, local: bool):
    region = world.multiworld.get_region(region_name, world.player)
    location = Location(
        world.player,
        location_name,
        world.location_name_to_id[location_name],
        region,
    )
    region.locations.append(location)
    if local:
        location.item_rule = lambda item: item.player == world.player


def create_regions(world: "OracleOfAgesWorld"):
    # Create regions

    regions = REGIONS.copy()

    for warpName, warpData in WARPS_DATA.items():
        regions.append(OUTSIDE_TAG + warpName)
        regions.append(INSIDE_TAG + warpName)

    if world.options.linked_heros_cave:
        regions.extend(D11_REGIONS)

    for region_name in regions:
        region = Region(region_name, world.player, world.multiworld)
        world.multiworld.regions.append(region)

    # Create locations
    for location_name, location_data in LOCATIONS_DATA.items():
        if not location_is_active(world, location_name, location_data):
            continue

        is_local = "local" in location_data and location_data["local"] is True
        create_location(
            world, location_data['region_id'], location_name, is_local
        )

    create_events(world)
    exclude_problematic_locations(world) # TODO


def create_event(world: "OracleOfAgesWorld", region_name, event_item_name):
    region = world.multiworld.get_region(region_name, world.player)
    location = Location(world.player, region_name + ".event", None, region)
    region.locations.append(location)
    location.place_locked_item(
        Item(
            event_item_name, ItemClassification.progression, None, world.player
        )
    )


def create_events(world):
    create_event(world, "maku seed", "Maku Seed")

    if world.options.goal == OracleOfAgesGoal.option_beat_veran:
        create_event(world, "veran beaten", "_beaten_game")
    elif world.options.goal == OracleOfAgesGoal.option_beat_ganon:
        create_event(world, "ganon beaten", "_beaten_game")

    create_event(world, "ridge move vine seed", "_access_cart")

    create_event(world, "d3 S crystal", "_d3_S_crystal")
    create_event(world, "d3 E crystal", "_d3_E_crystal")
    create_event(world, "d3 W crystal", "_d3_W_crystal")
    create_event(world, "d3 N crystal", "_d3_N_crystal")
    create_event(world, "d3 B1F spinner", "_d3_B1F_spinner")

    create_event(world, "d6 wall B bombed", "_d6_wall_B_bombed")
    create_event(world, "d6 canal expanded", "_d6_canal_expanded")

    create_event(world, "d7 boss", "_finished_d7")