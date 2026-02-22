from BaseClasses import MultiWorld
from ..common.generation.Logic import create_connections, is_small_key, is_item, apply_self_locking_rules
from ..data.logic.DungeonsLogic import *
from ..data.logic.OverworldLogic import *
from ..data.logic.SubrosiaLogic import *

def create_connections_seasons(world: OracleOfSeasonsWorld):
    create_connections(world, [
        make_holodrum_logic(world.origin_region_name, world.options),
        make_subrosia_logic(),
        make_d0_logic(),
            make_d1_logic(),
            make_d2_logic(),
            make_d3_logic(),
            make_d4_logic(),
            make_d5_logic(),
            make_d6_logic(),
            make_d7_logic(),
            make_d8_logic(),

            make_samasa_d11_logic(world.options),
            make_d11_logic(world.options)
        ]
    )

def apply_self_locking_rules_seasons(multiworld: MultiWorld, player: int):
    key_rules = {
        "Hero's Cave: Final Chest": lambda state, item: any([
            is_small_key(item, player, 0),
            is_item(item, player, f"Master Key ({DUNGEON_NAMES[0]})")
        ]),
        "Gnarled Root Dungeon: Item in Basement": lambda state, item: all([
            is_small_key(item, player, 1),
            oo_has_small_keys(1, 1).resolve(multiworld.worlds[player])(state)
        ]),
        "Snake's Remains: Chest on Terrace": lambda state, item: all([
            is_small_key(item, player, 2),
            oo_has_small_keys(2, 2).resolve(multiworld.worlds[player])(state)
        ]),
        "Poison Moth's Lair (1F): Chest in Mimics Room": lambda state, item: all([
            is_small_key(item, player, 3),
            oos_can_kill_normal_enemy().resolve(multiworld.worlds[player])(state)
        ]),
        "Dancing Dragon Dungeon (1F): Crumbling Room Chest": lambda state, item: all([
            is_small_key(item, player, 4),
            oo_has_small_keys(4, 2).resolve(multiworld.worlds[player])(state)
        ]),
        "Dancing Dragon Dungeon (1F): Eye Diving Spot Item": lambda state, item: all([
            is_small_key(item, player, 4),
            (oo_has_small_keys(4, 2) & oo_can_swim(False)).resolve(multiworld.worlds[player])(state)
        ]),
        "Unicorn's Cave: Magnet Gloves Chest": lambda state, item: is_small_key(item, player, 5),
        "Unicorn's Cave: Treadmills Basement Item": lambda state, item: all([
            is_small_key(item, player, 5),
            And(
                oo_has_small_keys(5, 3),
                CanReachRegion("d5 drop ball"),
                oos_has_magnet_gloves(),
                Or(
                    oos_can_kill_magunesu(),
                    And(
                        oo_option_medium_logic(),
                        oos_has_feather()
                    )
                )
            ).resolve(multiworld.worlds[player])(state)
        ]),
        "Explorer's Crypt (B1F): Chest in Jumping Stalfos Room": lambda state, item: all([
            is_small_key(item, player, 7),
            And(
                oo_has_small_keys(7, 4),
                Or(
                    oos_can_jump_5_wide_pit(),
                    And(
                        oo_option_hard_logic(),
                        oos_can_jump_1_wide_pit(False)
                    )
                ),
                oos_can_kill_stalfos(),
            ).resolve(multiworld.worlds[player])(state)
        ]),
        "Explorer's Crypt (1F): Chest Right of Entrance": lambda state, item: all([
            is_small_key(item, player, 7),
            And(
                oos_can_kill_normal_enemy(),
                oo_has_small_keys(7, 1),
            ).resolve(multiworld.worlds[player])(state)
        ])
    }
    OTHER_SELF_LOCKING_ITEMS = {
        "North Horon: Malon Trade": "Cuccodex",
        "Maple Trade": "Lon Lon Egg",
        "Holodrum Plain: Mrs. Ruul Trade": "Ghastly Doll",
        "Subrosia: Subrosian Chef Trade": "Iron Pot",
        "Sunken City: Ingo Trade": "Goron Vase",
        "North Horon: Yelling Old Man Trade": "Fish",
        "Horon Village: Tick Tock Trade": "Wooden Bird",
        "Eastern Suburbs: Guru-Guru Trade": "Engine Grease",
        "Subrosia: Smithy Hard Ore Reforge": "Hard Ore",
        "Subrosia: Smithy Rusty Bell Reforge": "Rusty Bell",
        "Sunken City: Master's Plaque Trade": "Master's Plaque",
        "Subrosia: Market #1": "Star Ore",
    }
    apply_self_locking_rules(multiworld, player, {
        "keys": key_rules,
        "OTHER_SELF_LOCKING_ITEMS": OTHER_SELF_LOCKING_ITEMS
    })

