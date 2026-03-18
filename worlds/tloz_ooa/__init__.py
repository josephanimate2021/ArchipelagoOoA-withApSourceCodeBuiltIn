import logging
import os
from threading import Event

from BaseClasses import Item
from worlds.AutoWorld import World
from typing import List, Dict, ClassVar, Any
from .generation.Data import *
from .generation.Logic import create_connections, apply_self_locking_rules
from .Options import *
from .generation.PatchWriter import ooa_create_appp_patch
from .data.Constants import *
from .data import ITEMS_DATA
from .Client import OracleOfAgesClient  # Unused, but required to register with BizHawkClient
from .Settings import OOASettings
from .WebWorld import OracleOfAgesWeb

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
    item_name_to_id = build_item_name_to_id_dict(ITEMS_DATA)
    item_name_groups = ITEM_GROUPS
    location_name_groups = LOCATION_GROUPS

    pre_fill_items: List[Item]
    dungeon_items: List[Item]
    dungeon_entrances: Dict[str, str]
    shop_prices: Dict[str, int]

    settings: ClassVar[OOASettings]
    settings_key = "tloz_ooa_options"

    seasons = False
    ages = True
    romhack = False

    city_name = "Lynna City"

    @classmethod
    def version(cls) -> str:
        return cls.world_version.as_simple_string()

    def __init__(self, multiworld, player):
        super().__init__(multiworld, player)
        self.pre_fill_items: List[Item] = []
        self.dungeon_items: List[Item] = []
        self.dungeon_entrances: Dict[str, str] = DUNGEON_ENTRANCES.copy()
        self.old_man_rupee_values: Dict[str, int] = OLD_MAN_RUPEE_VALUES.copy()
        self.shop_prices: Dict[str, int] = VANILLA_SHOP_PRICES.copy()
        self.shop_order: List[List[str]] = []
        self.shop_rupee_requirements: Dict[str, int] = {}
        self.essences_in_game: List[str] = ITEM_GROUPS["Essences"].copy()
        self.random_rings_pool: List[str] = []
        self.remaining_progressive_gasha_seeds = 0
        self.item_mapping_collect: dict[str, tuple[str, int]] = {}

        self.made_hints = Event()
        self.region_hints: list[tuple[str, str | int]] = []
        self.item_hints: list[Item | None] = []
        

    def fill_slot_data(self) -> dict:
        # Put options that are useful to the tracker inside slot data
        # TODO MOAR DATA ?

        slot_data = self.options.as_dict(*[option_name for option_name in OracleOfAgesOptions.type_hints if hasattr(OracleOfAgesOptions.type_hints[option_name], "include_in_slot_data")])
        slot_data["version"] = f"{self.version()}",
        slot_data["animal_companion"] = COMPANIONS[self.options.animal_companion.value]
        slot_data["default_seed"] = SEED_ITEMS[self.options.default_seed.value]
        slot_data["dungeon_entrances"] = self.dungeon_entrances

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
                # "room" repersents a byte number for the screen that link will go to when warp to start is activated.
                # "pos" repersents a byte number for a position link will be in when warp to start is active.
                # "group" repersents a byte number for a screen group that link will be in once warp to start is activated.
                # "dest_transittion" is a number that will changes the screen after the warp
                # "src_transittion" is a number that will changes the screen before the warp
            }

    def generate_early(self):
        from .common.generation.GenerateEarly import generate_early
        generate_early(self)

    def restrict_non_local_items(self):
        # Restrict non_local_items option in cases where it's incompatible with other options that enforce items
        # to be placed locally (e.g. dungeon items with keysanity off)
        if not self.options.keysanity_small_keys:
            self.options.non_local_items.value -= self.item_name_groups["Small Keys"]
        if not self.options.keysanity_boss_keys:
            self.options.non_local_items.value -= self.item_name_groups["Boss Keys"]
        if not self.options.keysanity_maps_compasses:
            self.options.non_local_items.value -= self.item_name_groups["Dungeon Maps"]
            self.options.non_local_items.value -= self.item_name_groups["Compasses"]
        if not self.options.keysanity_slates:
            self.options.non_local_items.value -= set(["Slate"])

    
    def shuffle_dungeons(self):
        shuffled_dungeons = list(self.dungeon_entrances.values())
        while True:
            self.random.shuffle(shuffled_dungeons)
            if shuffled_dungeons[4] != "enter d0": # Ensure D4 entrance doesn't lead to d0
                break
        
        self.dungeon_entrances = dict(zip(self.dungeon_entrances, shuffled_dungeons))

    def location_is_active(self, location_name, location_data):
        if "conditional" not in location_data or location_data["conditional"] is False:
            return True

        region_id = location_data["region_id"]
        if region_id == "advance shop":
            return self.options.advance_shop.value
        
        if location_name in RUPEE_OLD_MAN_LOCATIONS:
            return self.options.shuffle_old_men == OraclesOldMenShuffle.option_turn_into_locations
        
        if "dungeon" in location_data:
            if location_data["dungeon"] == 11:
                return self.options.linked_heros_cave.value > 0
            if location_data["region_id"] == "d" + str(location_data["dungeon"]) + " miniboss":
                return self.options.miniboss_locations
            
        if "secret_location" in location_data and not False:
            return self.options.secret_locations
        


        # TODO FUNNY LOCATION ?

        return False

    def create_regions(self):
        from .common.generation.CreateRegions import create_regions
        create_regions(self)

    def create_event(self, region_name: str, event_item_name: str):
        from .common.generation.CreateRegions import create_event
        create_event(self, region_name, event_item_name)

    def create_events(self):
        from .generation.CreateEvents import create_events
        create_events(self)

    def set_rules(self):
        create_connections(self.multiworld, self.player, self.options)
        apply_self_locking_rules(self.multiworld, self.player)
        self.multiworld.completion_condition[self.player] = lambda state: state.has("_beaten_game", self.player)

    def create_item(self, name: str) -> Item:
        from .common.generation.CreateItems import create_item
        return create_item(self, name)

    def create_items(self):
        from .generation.CreateItems import create_items
        create_items(self)

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
        from .common.generation.SpoilerLog import write_spoiler
        write_spoiler(self, spoiler_handle)