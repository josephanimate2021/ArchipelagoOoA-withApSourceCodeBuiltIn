import logging
import os
import yaml

from typing import ClassVar, Any, Optional, Type, TextIO
from Options import Option
from BaseClasses import Region, Location, LocationProgressType
from Options import Accessibility, OptionError
from typing import Any, Set, List, Dict, Optional, Tuple, ClassVar, TextIO, Union
from .generation.Data import *
from .data.Items import *
from .Options import *
from .generation.PatchWriter import ooa_create_appp_patch
from .data import LOCATIONS_DATA
from .data.Constants import *
from .Client import OracleOfAgesClient  # Unused, but required to register with BizHawkClient
from .Settings import OOASettings
from .WebWorld import *

class OracleOfAgesWorld(World):
    """
    The Legend of Zelda: Oracles of Ages is one of the rare Capcom entries to the series.
    Nayru, the oracle of ages, has been possessed by Veran, and she is now making a mess in Labrynna
    Gather the Essences of Times, exorcice Nayru and defeat Veran to save the timeline of Labrynna
    """
    game = "The Legend of Zelda - Oracle of Ages"
    options_dataclass = OracleOfAgesOptions
    options: OracleOfAgesOptions
    required_client_version = (0, 5, 1)
    web = OracleOfAgesWeb()
    topology_present = True

    location_name_to_id = build_location_name_to_id_dict()
    item_name_to_id = build_item_name_to_id_dict()
    item_name_groups = ITEM_GROUPS
    location_name_groups = LOCATION_GROUPS

    pre_fill_items: List[Item]
    dungeon_items: List[Item]
    shuffled_entrances: Dict[str, str]
    shop_prices: Dict[str, int]

    settings: ClassVar[OOASettings]
    settings_key = "tloz_ooa_options"

    ages = True
    seasons = False
    romhack = False

    tracker_world: ClassVar = {
        "external_pack_key": "ut_pack_path",
        "map_page_maps": "maps/maps.json",
        "map_page_locations": [
            "locations/dungeons.json",
            "locations/overworld_past.json",
            "locations/overworld_present.json",
        ],
        "poptracker_name_mapping": dict[str, int]
    }


    @classmethod
    def version(cls) -> str:
        return cls.world_version.as_simple_string()

    def __init__(self, multiworld, player):

        self.tracker_world["poptracker_name_mapping"] = {}
        for location_name, location_data in LOCATIONS_DATA.items():
            split = location_name.split(": ")
            poptrackerName = split[-1] + "/"
            self.tracker_world["poptracker_name_mapping"][poptrackerName] = self.location_name_to_id[location_name]
            print(f"{poptrackerName} ({location_name}) => {self.location_name_to_id[location_name]}")

        super().__init__(multiworld, player)

        self.pre_fill_items = []
        self.dungeon_items = []
        self.random_rings_pool: list[str] = []
        self.shop_prices = SHOP_PRICES_DIVIDERS.copy()

    def fill_slot_data(self) -> dict:
        # Put options that are useful to the tracker inside slot data
        slot_data = {
            "version": f"{self.version()}",
            "options": self.options.as_dict(
                *[option_name for option_name in OracleOfAgesOptions.type_hints
                  if hasattr(OracleOfAgesOptions.type_hints[option_name], "include_in_slot_data")]),
            "shuffled_entrances": self.shuffled_entrances,
            "shop_costs": self.shop_prices,
        }

        return slot_data
    
    def determine_warp_to_start_variables(self):
        # Mashy wasn't sure if he liked the new warp to start location on his first video on playing my 1.0.0 beta hotfix. 
        # Adding this to not force the new warp to start location on anyone that is still used to the old one.
        if self.options.warp_to_start_location == OracleOfAgesWarpToStartLocation.option_near_timeportal:
            return {
                "room": 0x39,
                "pos": 0x21
            }
        else:
            return {
                # The syntax is like this:
                # "room" represents a byte number for the screen that link will go to when warp to start is activated.
                # "pos" represents a byte number for a position link will be in when warp to start is active.
                # "group" represents a byte number for a screen group that link will be in once warp to start is activated.
                # "dest_transittion" is a number that will changes the screen after the warp
                # "src_transittion" is a number that will changes the screen before the warp
            }

    def generate_early(self):
        from .generation.GenerateEarly import generate_early
        generate_early(self)

    def create_regions(self):
        from .generation.CreateRegions import create_regions
        create_regions(self)

    def create_item(self, name: str) -> Item:
        from .generation.CreateItems import create_item
        return create_item(self, name)
    
    def create_items(self):
        from .generation.CreateItems import create_items
        return create_items(self)

    def get_pre_fill_items(self):
        return self.pre_fill_items

    def pre_fill(self) -> None:
        from .generation.PreFill import pre_fill
        pre_fill(self)
    
    def generate_output(self, output_directory: str):
        patch = ooa_create_appp_patch(self)
        rom_path = os.path.join(output_directory, f"{self.multiworld.get_out_file_name_base(self.player)}"
                                                  f"{patch.patch_file_ending}")
        patch.write(rom_path)
        return

    def write_spoiler(self, spoiler_handle):
        spoiler_handle.write(f"Apworld version : {self.version()}\n")
        if self.options.shuffle_dungeons != "vanilla":
            spoiler_handle.write(f"Shuffled Entrances ({self.multiworld.player_name[self.player]}):\n")
            for entrance, dungeon in self.shuffled_entrances.items():
                spoiler_handle.write(f"\t- outside {entrance} --> inside {dungeon}\n")

    
    def interpret_slot_data(self, slot_data: Optional[dict[str, Any]]) -> Any:
        if slot_data is not None:
            return slot_data

        if not hasattr(self.multiworld, "re_gen_passthrough") or self.game not in self.multiworld.re_gen_passthrough:
            return False

        slot_data = self.multiworld.re_gen_passthrough[self.game]

        for option in [option_name for option_name in OracleOfAgesOptions.type_hints
                       if hasattr(OracleOfAgesOptions.type_hints[option_name], "include_in_slot_data")]:
            option_class: Type[Option] = OracleOfAgesOptions.type_hints[option]
            self.options.__setattr__(option, option_class.from_any(slot_data["options"][option]))

        self.shuffled_entrances = slot_data["shuffled_entrances"]
        self.shop_prices = slot_data["shop_costs"]

        return True
