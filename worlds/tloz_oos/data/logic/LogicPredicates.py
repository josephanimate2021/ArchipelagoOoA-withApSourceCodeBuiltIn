from rule_builder.rules import And, Or, CanReachRegion
from .Rulebuilder import *
from ..Constants import *
from ...Tloz_oo_common.Options import OraclesLogicDifficulty, OraclesDefaultSeedType, OraclesMasterKeys, OraclesDungeonShuffle, OraclesAnimalCompanion
from ...Options import OracleOfSeasonsD0AltEntrance, OracleOfSeasonsD2AltEntrance, OracleOfSeasonsLostWoodsItemSequence, OracleOfSeasonsLostWoodsMainSequence, OracleOfSeasonsHoronSeason
from ...Tloz_oo_common.data.logic.LogicPredicates import *


# Items predicates ############################################################


def oos_has_fools_ore() -> Rule:
    return Has("Fool's Ore")


def oos_has_feather() -> Rule:
    return Has("Progressive Feather")


def oos_has_cape() -> Rule:
    return Has("Progressive Feather", 2)


def oos_has_slingshot() -> Rule:
    return Has("Progressive Slingshot")


def oos_has_hyper_slingshot() -> Rule:
    return Has("Progressive Slingshot", 2)


def oos_has_boomerang() -> Rule:
    return Has("Progressive Boomerang")


def oos_has_magic_boomerang() -> Rule:
    return Has("Progressive Boomerang", 2)


def oos_has_bracelet() -> Rule:
    return Has("Power Bracelet")


# Cross items


def oos_has_seed_thrower() -> Rule:
    return Or(
        oos_has_slingshot(),
        oo_has_shooter()
    )


def oos_has_season(season: int) -> Rule:
    return Has(SEASON_ITEMS[season])


def oos_has_summer() -> Rule:
    return Has(SEASON_ITEMS[SEASON_SUMMER])


def oos_has_spring() -> Rule:
    return Has(SEASON_ITEMS[SEASON_SPRING])


def oos_has_winter() -> Rule:
    return Has(SEASON_ITEMS[SEASON_WINTER])


def oos_has_autumn() -> Rule:
    return Has(SEASON_ITEMS[SEASON_AUTUMN])


def oos_has_magnet_gloves() -> Rule:
    return Has("Magnetic Gloves")


# Options and generation predicates ###########################################


def oos_option_no_d0_alt_entrance() -> Rule:
    return from_option(OracleOfSeasonsD0AltEntrance, OracleOfSeasonsD0AltEntrance.option_false)


def oos_option_no_d2_alt_entrance() -> Rule:
    return from_option(OracleOfSeasonsD2AltEntrance, OracleOfSeasonsD2AltEntrance.option_false)



def oos_is_default_season(area_name: str, season: int, is_season: bool = True) -> Rule:
    return Season(area_name, season, is_season)


def oos_can_remove_season(season: int) -> Rule:
    # Test if player has any other season than the one we want to remove
    return Or(
        *[Has(item_name) for season_name, item_name in SEASON_ITEMS.items() if season_name != season]
    )


def oos_has_essences_for_treehouse() -> Rule:
    return HasGroupOption("Essences", "treehouse_old_man_requirement")


def oos_has_required_jewels() -> Rule:
    return HasGroupOption("Jewels", "tarm_gate_required_jewels")


def oos_can_reach_lost_woods_pedestal(allow_default: bool = False) -> Rule:
    return And(
        LostWoods([], False, allow_default),
        Or(
            CanReachRegion("lost woods phonograph"),
            And(
                # if sequence is vanilla, medium+ players are expected to know it
                oo_option_medium_logic(),
                from_option(OracleOfSeasonsLostWoodsItemSequence, OracleOfSeasonsLostWoodsItemSequence.option_false)
            )
        )
    )


def oos_can_complete_lost_woods_main_sequence(allow_default: bool = False) -> Rule:
    return And(
        LostWoods([], True, allow_default),
        Or(
            CanReachRegion("lost woods deku"),
            And(
                # if sequence is vanilla, medium+ players are expected to know it
                oo_option_medium_logic(),
                from_option(OracleOfSeasonsLostWoodsMainSequence, OracleOfSeasonsLostWoodsMainSequence.option_false)
            )
        )
    )


def oos_can_beat_required_golden_beasts() -> Rule:
    return HasFromListOption("_beat_golden_darknut", "_beat_golden_lynel", "_beat_golden_moblin", "_beat_golden_octorok",
                             option_name="golden_beasts_requirement")


def oos_can_complete_d11_puzzle() -> bool:
    return Or(
        from_option(OraclesDungeonShuffle, OraclesDungeonShuffle.option_false),
        CanReachNumRegions([f"enter d{i}" for i in range(1, 9)], 7)  # And then deduce the last
    )


# Various item predicates ###########################################


def oos_can_farm_rupees() -> Rule:
    # Having a weapon to get  or a shovel is enough to guarantee that we can reach a significant amount of rupees
    return Or(
        oos_can_kill_normal_enemy(False, False),
        oo_has_shovel()
    )


def oos_can_buy_market() -> Rule:
    return HasOresForShop()


def oos_can_farm_ore_chunks() -> Rule:
    return Or(
        oo_has_shovel(),
        And(
            oo_option_medium_logic(),
            Or(
                oos_has_magic_boomerang(),
                oo_has_sword()
            )
        ),
        And(
            oo_option_hard_logic(),
            Or(
                CanReachRegion("subrosian dance hall"),
                oos_has_bracelet(),
                oo_has_switch_hook()
            )
        )
    )


def oos_can_date_rosa() -> Rule:
    return And(
        CanReachRegion("subrosia market sector"),
        Has("Ribbon")
    )


def oos_can_trigger_far_switch() -> Rule:
    return Or(
        oos_has_boomerang(),
        oo_has_bombs(),
        oos_has_seed_thrower(),
        oo_shoot_beams(),
        oo_has_switch_hook()
    )


def oos_has_rod() -> Rule:
    return Or(
        oos_has_winter(),
        oos_has_summer(),
        oos_has_spring(),
        oos_has_autumn()
    )

# Jump-related predicates ###########################################

def oos_can_jump_1_wide_liquid(can_summon_companion: bool) -> Rule:
    return Or(
        oos_has_feather(),
        And(
            oo_option_medium_logic(),
            from_bool(can_summon_companion),
            oo_can_summon_ricky()
        )
    )


def oos_can_jump_2_wide_liquid() -> Rule:
    return Or(
        oos_has_cape(),
        And(
            oos_has_feather(),
            oos_can_use_pegasus_seeds()
        ),
        And(
            # Hard logic expects bomb jumps over 2-wide liquids
            oo_option_hard_logic(),
            oos_has_feather(),
            oo_has_bombs()
        )
    )


def oos_can_jump_3_wide_liquid() -> Rule:
    return Or(
        oos_has_cape(),
        And(
            oo_option_hard_logic(),
            oos_has_feather(),
            oos_can_use_pegasus_seeds(),
            oo_has_bombs(),
        )
    )


def oos_can_jump_4_wide_liquid() -> Rule:
    return And(
        oos_has_cape(),
        Or(
            oos_can_use_pegasus_seeds(),
            And(
                # Hard logic expects player to be able to cape bomb-jump above 4-wide liquids
                oo_option_hard_logic(),
                oo_has_bombs()
            )
        )
    )


def oos_can_jump_5_wide_liquid() -> Rule:
    return And(
        oos_has_cape(),
        oos_can_use_pegasus_seeds(),
    )


def oos_can_jump_1_wide_pit(can_summon_companion: bool) -> Rule:
    return Or(
        oos_has_feather(),
        And(
            from_bool(can_summon_companion),
            Or(
                oo_can_summon_moosh(),
                oo_can_summon_ricky()
            )
        )
    )


def oos_can_jump_2_wide_pit() -> Rule:
    return Or(
        oos_has_cape(),
        And(
            oos_has_feather(),
            Or(
                # Medium logic expects player to be able to jump above 2-wide pits without pegasus seeds
                oo_option_medium_logic(),
                oos_can_use_pegasus_seeds()
            )
        )
    )


def oos_can_jump_3_wide_pit() -> Rule:
    return Or(
        oos_has_cape(),
        And(
            oo_option_medium_logic(),
            oos_has_feather(),
            oos_can_use_pegasus_seeds(),
        )
    )


def oos_can_jump_4_wide_pit() -> Rule:
    return And(
        oos_has_cape(),
        Or(
            oo_option_medium_logic(),
            oos_can_use_pegasus_seeds(),
        )
    )


def oos_can_jump_5_wide_pit() -> Rule:
    return And(
        oos_has_cape(),
        oos_can_use_pegasus_seeds(),
    )


def oos_can_jump_6_wide_pit() -> Rule:
    return And(
        oo_option_medium_logic(),
        oos_has_cape(),
        oos_can_use_pegasus_seeds(),
    )


# Seed-related predicates ###########################################

def oos_can_use_seeds() -> Rule:
    return Or(
        oos_has_slingshot(),
        oo_has_shooter(),
        oo_has_satchel()
    )

def oos_can_use_ember_seeds(accept_mystery_seeds: bool) -> Rule:
    return And(
        oos_can_use_seeds(),
        Or(
            oo_has_ember_seeds(),
            And(
                # Medium logic expects the player to know they can use mystery seeds
                # to randomly get the ember effect in some cases
                from_bool(accept_mystery_seeds),
                oo_option_medium_logic(),
                oo_has_mystery_seeds(),
            )
        )
    )

def oos_can_use_scent_seeds() -> Rule:
    return And(
        oos_can_use_seeds(),
        oo_has_scent_seeds()
    )


def oos_can_use_pegasus_seeds() -> Rule:
    return And(
        # Unlike other seeds, pegasus only have an interesting effect with the satchel
        oo_has_satchel(),
        oo_has_pegasus_seeds()
    )


def oos_can_use_gale_seeds_offensively() -> Rule:
    return And(
        oo_has_satchel(2),
        oo_option_medium_logic(),
        Or(
            oo_has_gale_seeds(),
            oo_has_mystery_seeds()
        ),
        Or(
            oos_has_seed_thrower(),
            And(
                oo_has_satchel(),
                Or(
                    oo_option_hard_logic(),
                    oos_has_feather()
                ),
            )
        )
    )

def oos_can_use_mystery_seeds() -> Rule:
    return And(
        oos_can_use_seeds(),
        oo_has_mystery_seeds()
    )


# Break / kill predicates ###########################################

def oos_can_break_bush(can_summon_companion: bool = False, allow_bombchus: bool = False) -> Rule:
    return Or(
        oos_can_break_flowers(can_summon_companion, allow_bombchus),
        oos_has_bracelet()
    )


def oos_can_harvest_regrowing_bush() -> Rule:
    return Or(
        oo_has_sword(),
        oos_has_fools_ore(),
        oo_has_bombs(),
        And(
            oo_option_medium_logic(),
            oo_has_bombchus(4)
        )
    )


def oos_can_break_mushroom(can_use_companion: bool) -> Rule:
    return Or(
        oos_has_bracelet(),
        And(
            oo_option_medium_logic(),
            Or(
                oos_has_magic_boomerang(),
                And(
                    from_bool(can_use_companion),
                    oo_can_summon_dimitri()
                )
            )
        ),
    )


def oos_can_break_pot() -> Rule:
    return Or(
        oos_has_bracelet(),
        oo_has_noble_sword(),
        Has("Biggoron's Sword"),
        oo_has_switch_hook()
    )


def oos_can_break_flowers(can_summon_companion: bool = False, allow_bombchus: bool = False) -> Rule:
    return Or(
        oo_has_sword(),
        oos_has_magic_boomerang(),
        oo_has_switch_hook(),
        And(
            from_bool(can_summon_companion),
            oo_has_flute()
        ),
        And(
            # Consumables need at least medium logic, since they need a good knowledge of the game
            # not to be frustrating
            oo_option_medium_logic(),
            Or(
                oo_has_bombs(2),
                oos_can_use_ember_seeds(False),
                And(
                    oos_has_seed_thrower(),
                    oo_has_gale_seeds()
                ),
                And(
                    from_bool(allow_bombchus),
                    oo_has_bombchus(4)
                )
            )
        ),
    )


def oos_can_break_crystal() -> Rule:
    return Or(
        oo_has_sword(),
        oo_has_bombs(),
        oos_has_bracelet(),
        And(
            oo_option_medium_logic(),
            Has("Expert's Ring")
        ),
        And(
            oo_option_medium_logic(),
            oo_has_bombchus(4)
        ),
    )


def oos_can_break_sign() -> Rule:
    return Or(
        oo_has_noble_sword(),
        Has("Biggoron's Sword"),
        oos_has_bracelet(),
        oos_can_use_ember_seeds(False),
        oos_has_magic_boomerang(),
        oo_has_switch_hook()
    )


def oos_can_harvest_tree(can_use_companion: bool) -> Rule:
    return And(
        oos_can_use_seeds(),
        Or(
            oo_has_sword(),
            oos_has_fools_ore(),
            oos_has_rod(),
            oo_can_punch(),
            And(
                from_bool(can_use_companion),
                oo_option_medium_logic(),
                oo_can_summon_dimitri()
            )
        )
    )


def oos_can_harvest_gasha(count: int) -> Rule:
    return And(
        HasFromList(*[f"_reached_{region_name}" for region_name in GASHA_SPOT_REGIONS], count=count),  # Enough soils are reachable
        Has("Gasha Seed", count),  # Enough seeds to plant
        Or(
            # Can actually harvest the nut, and get kills
            oo_has_sword(),
            oos_has_fools_ore()
        )
    )


def oos_can_push_enemy() -> Rule:
    return Or(
        oos_has_rod(),
        oo_has_shield(),
        And(
            oo_option_medium_logic(),
            oo_has_shovel()
        )
    )


def oos_can_kill_normal_enemy(pit_available: bool = False,
                              allow_gale_seeds: bool = True) -> Rule:
    return Or(
        oos_can_kill_normal_enemy_no_cane(pit_available, allow_gale_seeds),
        (oo_option_medium_logic() & oo_has_cane())
    )


def oos_can_kill_normal_enemy_no_cane(pit_available: bool = False,
                                      allow_gale_seeds: bool = True) -> Rule:
    return Or(
        And(
            # If a pit is avaiable nearby, it can be used to put the enemies inside using
            # items that are usually non-lethal
            from_bool(pit_available),
            oos_can_push_enemy()
        ),
        oo_has_sword(),
        oos_has_fools_ore(),
        oos_can_kill_normal_using_satchel(allow_gale_seeds),
        oos_can_kill_normal_using_slingshot(allow_gale_seeds),
        And(
            oo_option_medium_logic(),
            oo_has_bombs(4)
        ),
        oo_has_bombchus(2),
        oo_can_punch()
    )


def oos_can_kill_normal_using_satchel(allow_gale_seeds: bool = True) -> Rule:
    # Expect a 50+ seed satchel to ensure we can chain dungeon rooms to some extent if that's our only kill option
    return oo_has_satchel(2) & Or(
        # Casual logic => only ember
        oo_has_ember_seeds(),
        And(
            # Medium logic => allow scent or gale+feather
            oo_option_medium_logic(),
            Or(
                oo_has_scent_seeds(),
                oo_has_mystery_seeds(),
                And(
                    from_bool(allow_gale_seeds),
                    oo_has_gale_seeds(),
                    oos_has_feather()
                )
            )
        ),
        And(
            # Hard logic => allow gale without feather
            from_bool(allow_gale_seeds),
            oo_option_hard_logic(),
            oo_has_gale_seeds()
        )
    )


def oos_can_kill_normal_using_slingshot(allow_gale_seeds: bool = True) -> Rule:
    return And(
        # Expect a 50+ seed satchel to ensure we can chain dungeon rooms to some extent if that's our only kill option
        oo_has_satchel(2),
        oos_has_seed_thrower(),
        Or(
            oo_has_ember_seeds(),
            oo_has_scent_seeds(),
            And(
                oo_option_medium_logic(),
                Or(
                    And(
                        from_bool(allow_gale_seeds),
                        oo_has_gale_seeds(),
                    ),
                    oo_has_mystery_seeds(),
                )
            )
        )
    )


def oos_can_kill_armored_enemy(allow_cane: bool, allow_bombchus: bool) -> Rule:
    return Or(
        oo_has_sword(),
        oos_has_fools_ore(),
        And(
            oo_option_medium_logic(),
            oo_has_bombs(4)
        ),
        And(
            from_bool(allow_bombchus),
            oo_has_bombchus(2)
        ),
        And(
            oo_has_satchel(2),  # Expect a 50+ seeds satchel to be able to chain rooms in dungeons
            oo_has_scent_seeds(),
            Or(
                oos_has_seed_thrower(),
                oo_option_medium_logic()
            )
        ),
        And(
            from_bool(allow_cane),
            oo_option_medium_logic(),
            oo_has_cane()
        ),
        oo_can_punch()
    )


def oos_can_kill_stalfos() -> Rule:
    return Or(
        oos_can_kill_normal_enemy(),
        And(
            oo_option_medium_logic(),
            oos_has_rod()
        )
    )


def oos_can_kill_moldorm(pit_available: bool = False) -> Rule:
    return Or(
        oos_can_kill_armored_enemy(True, True),
        oo_has_switch_hook(),
        And(
            from_bool(pit_available),
            Or(
                oo_has_shield(),
                And(
                    oo_option_medium_logic(),
                    oo_has_shovel()
                )
            )
        )
    )


def oos_can_trigger_lever() -> Rule:
    return Or(
        oos_can_trigger_lever_from_minecart(),
        oo_has_switch_hook(),
        And(
            oo_option_medium_logic(),
            oo_has_shovel()
        )
    )


def oos_can_trigger_lever_from_minecart() -> Rule:
    return Or(
        oo_can_punch(),
        oo_has_sword(),
        oos_has_fools_ore(),
        oos_has_boomerang(),
        oos_has_rod(),

        oos_can_use_scent_seeds(),
        oos_can_use_mystery_seeds(),
        oos_can_use_ember_seeds(False),
        oos_has_seed_thrower(),  # any seed works using slingshot
    )


def oos_can_kill_d2_hardhat() -> Rule:
    return Or(
        oo_has_sword(),
        oos_has_fools_ore(),
        oos_has_boomerang(),
        oos_can_push_enemy(),
        oo_has_switch_hook(),  # Also push the hardhat
        And(
            oo_option_medium_logic(),
            oo_has_satchel(2),
            Or(
                oos_has_seed_thrower(),
                And(
                    oo_option_hard_logic(),
                    oo_has_satchel(),
                )
            ),
            Or(
                oo_has_scent_seeds(),
                oo_has_gale_seeds(),
                oo_has_mystery_seeds()
            ),
            oo_has_bombchus(2)
        )
    )


def oos_can_kill_d2_far_moblin() -> Rule:
    return Or(
        oos_can_kill_normal_using_slingshot(),
        And(
            Or(
                oos_has_feather(),
                And(
                    # Switch with a moblin, kill the other, jump in the pit, kill the first
                    oo_option_medium_logic(),
                    oo_has_switch_hook()
                )
            ),
            oos_can_kill_normal_enemy(True),
        ),
        And(
            oo_option_hard_logic(),
            Or(
                oos_can_use_ember_seeds(False),
                oo_can_punch(),
                oo_has_cane()
            )
        )
    )


def oos_can_kill_spiked_beetle() -> Rule:
    return Or(
        And(  # Regular flip + kill
            oo_can_flip_spiked_beetle(),
            Or(
                oo_has_sword(),
                oos_has_fools_ore(),
                oos_can_kill_normal_using_satchel(),
                oos_can_kill_normal_using_slingshot(),
                oo_has_switch_hook()
            )
        ),
        # Instant kill using Gale Seeds
        oos_can_use_gale_seeds_offensively()
    )


def oos_can_kill_magunesu() -> Rule:
    return Or(
        oo_has_sword(),
        oos_has_fools_ore(),
        # Has("expert's ring")
    )


# Action predicates ###########################################


def oos_can_meet_maple() -> Rule:
    return oos_can_kill_normal_enemy(False, False)


def oos_can_dimitri_clip() -> Rule:
    return And(
        oo_option_hell_logic(),
        oo_can_summon_dimitri(),
        oos_has_bracelet(),
        oo_has_gale_seeds(),
        oo_has_satchel()
    )


# Season in region predicates ##########################################

def oos_season_in_spool_swamp(season: int) -> Rule:
    return Or(
        oos_is_default_season("SPOOL_SWAMP", season),
        And(
            oos_has_season(season),
            CanReachRegion("spool stump")
        )
    )


def oos_season_in_eyeglass_lake(season: int) -> Rule:
    return Or(
        oos_is_default_season("EYEGLASS_LAKE", season),
        And(
            oos_has_season(season),
            Or(
                CanReachRegion("d1 stump"),
                CanReachRegion("d5 stump"),
            )
        )
    )


def oos_season_in_temple_remains(season: int) -> Rule:
    return Or(
        oos_is_default_season("TEMPLE_REMAINS", season),
        And(
            oos_has_season(season),
            Or(
                CanReachRegion("temple remains lower stump"),
                CanReachRegion("temple remains upper stump"),
            )
        )
    )


def oos_season_in_holodrum_plain(season: int) -> Rule:
    return Or(
        oos_is_default_season("HOLODRUM_PLAIN", season),
        And(
            oos_has_season(season),
            CanReachRegion("ghastly stump")
        )
    )


def oos_season_in_western_coast(season: int) -> Rule:
    return Or(
        oos_is_default_season("WESTERN_COAST", season),
        And(
            oos_has_season(season),
            CanReachRegion("coast stump"),
        )
    )


def oos_season_in_eastern_suburbs(season: int) -> Rule:
    return Or(
        oos_is_default_season("EASTERN_SUBURBS", season),
        oos_has_season(season)
    )


def oos_not_season_in_eastern_suburbs(season: int) -> Rule:
    return Or(
        oos_is_default_season("EASTERN_SUBURBS", season, False),
        oos_can_remove_season(season)
    )


def oos_season_in_sunken_city(season: int) -> Rule:
    return Or(
        oos_is_default_season("SUNKEN_CITY", season),
        And(
            oos_has_season(season),
            Or(
                oos_is_default_season("SUNKEN_CITY", SEASON_WINTER),
                oo_can_swim(True),
                CanReachRegion("sunken city dimitri")
            )
        )
    )


def oos_season_in_woods_of_winter(season: int) -> Rule:
    return Or(
        oos_is_default_season("WOODS_OF_WINTER", season),
        oos_has_season(season)
    )


def oos_season_in_central_woods_of_winter(season: int) -> Rule:
    return Or(
        oos_is_default_season("WOODS_OF_WINTER", season),
        And(
            oos_has_season(season),
            CanReachRegion("d2 stump")
        )
    )


def oos_season_in_mt_cucco(season: int) -> Rule:
    return Or(
        oos_is_default_season("SUNKEN_CITY", season),
        oos_has_season(season)
    )


def oos_season_in_lost_woods(season: int) -> Rule:
    return Or(
        oos_is_default_season("LOST_WOODS", season),
        oos_has_season(season)
    )


def oos_season_in_tarm_ruins(season: int) -> Rule:
    return Or(
        oos_is_default_season("TARM_RUINS", season),
        oos_has_season(season)
    )


def oos_season_in_horon_village(season: int) -> Rule:
    # With vanilla behavior, you can randomly have any season inside Horon, making any season virtually accessible
    return Or(
        from_option(OracleOfSeasonsHoronSeason, OracleOfSeasonsHoronSeason.option_false),
        oos_is_default_season("HORON_VILLAGE", season),
        oos_has_season(season)
    )


# Self-locking items helper predicates ##########################################

def oos_self_locking_item(location_name: str, item_name: str) -> Rule:
    return ItemInLocation(location_name, item_name)


def oos_self_locking_small_key(region_name: str, dungeon: int) -> Rule:
    item_name = f"Small Key ({DUNGEON_NAMES[dungeon]})"
    return oos_self_locking_item(region_name, item_name)


# Rooster adventure logic  ######################################################

POSITION_BOTH = 0
POSITION_TOP = 1
POSITION_BOTTOM = 2


def oos_roosters(region: str, any_amount: int = 0, top_amount: int = 0, bottom_amount: int = 0, visited_regions=None) -> Rule:
    # Avoid loops
    if visited_regions is None:
        visited_regions = set()
    visited_regions.add(region)

    if any_amount > top_amount + bottom_amount:
        return (oos_roosters(region, any_amount, top_amount + 1, bottom_amount, set(visited_regions)) |
                oos_roosters(region, any_amount, top_amount, bottom_amount + 1, set(visited_regions)))
    elif region == "cucco mountain":
        rule = oos_can_reach_rooster_adventure()
        if bottom_amount > 2:
            raise NotImplementedError()
        elif bottom_amount > 0:
            rule &= And(
                oos_season_in_mt_cucco(SEASON_SPRING),
                oos_can_break_flowers() | Has("Spring Banana")
            )
        if top_amount > 3:
            raise NotImplementedError()
        elif top_amount == 3:
            rule &= And(
                oo_has_shovel(),
                oos_has_boomerang()
            )
        elif top_amount == 2:
            rule &= (oo_has_shovel() |
                     (oos_has_boomerang() & oos_can_use_pegasus_seeds()))
        # sign + season gives 2 tops, one of which being sacrificed,
        # which is included in oos_can_reach_rooster_adventure()
        return rule
    elif region == "horon":
        return And(
            (oos_can_jump_3_wide_pit() | oo_can_swim(True)),  # Swim through Natzu
            oos_roosters("cucco mountain", any_amount, top_amount, bottom_amount)
        )
    elif region == "sunken":
        rule = Or(
            And(
                oos_roosters("horon", any_amount, top_amount, bottom_amount, set(visited_regions)),
                Or(
                    # Go through Natzu
                    oo_has_flute(),
                    oo_is_companion_moosh() & oos_can_jump_4_wide_liquid()
                )
            ),
            And(
                # Go through moblin fortress using a top cucco
                oos_roosters("horon", any_amount + 1, top_amount + 1, bottom_amount, set(visited_regions)),
                oo_is_companion_moosh() & oos_can_jump_3_wide_pit()
            ),
            And(
                oo_is_companion_ricky(),
                oo_can_swim(False),
                oos_can_break_flowers() | oos_roosters("cucco mountain", any_amount + 1, top_amount, bottom_amount, set(visited_regions)),
                oos_roosters("cucco mountain", any_amount, top_amount, bottom_amount, set(visited_regions))
            )
        )
        if "suburbs" not in visited_regions:
            rule |= And(
                # Suburbs flower
                oos_season_in_eastern_suburbs(SEASON_SPRING),
                oos_roosters("suburbs", any_amount, top_amount, bottom_amount, set(visited_regions))
            )
        return rule
    elif region == "suburbs":
        return Or(
            oos_roosters("sunken", any_amount, top_amount, bottom_amount, set(visited_regions)),
            And(
                oos_roosters("horon", any_amount, top_amount, bottom_amount, set(visited_regions)),
                oos_can_use_ember_seeds(False)
            ),
            And(
                # Use portal screen in suburbs
                oos_roosters("horon", any_amount + 1, top_amount, bottom_amount, set(visited_regions)),
                oos_season_in_eyeglass_lake(SEASON_WINTER),
                Or(
                    Season("EYEGLASS_LAKE", SEASON_SUMMER, True),
                    oos_can_remove_season(SEASON_SUMMER)
                ),
                oo_can_swim(True)
            )
        )
    elif region == "moblin road":
        return Or(
            And(
                oos_season_in_eastern_suburbs(SEASON_WINTER),
                oos_roosters("suburbs", any_amount, top_amount, bottom_amount, set(visited_regions))
            ),
            # Use a top rooster from top of the flower
            oos_roosters("sunken", any_amount + 1, top_amount + 1, bottom_amount, set(visited_regions))
        )
    elif region == "swamp":
        return Or(
            And(
                Or(
                    oos_season_in_holodrum_plain(SEASON_SUMMER),
                    oos_can_jump_4_wide_pit(),
                    oo_can_summon_ricky(),
                    oo_can_summon_moosh()
                ),
                oos_roosters("horon", any_amount, top_amount, bottom_amount, set(visited_regions))
            ),
            # Use bottom cucco to climb the vines
            oos_roosters("horon", any_amount + 1, top_amount, bottom_amount + 1, set(visited_regions))
        )
    elif region == "d6":
        return And(
            oos_has_required_jewels(),
            Or(
                oos_season_in_lost_woods(SEASON_SUMMER),
                And(
                    oos_season_in_lost_woods(SEASON_AUTUMN),
                    oo_option_medium_logic(),
                    oos_has_magic_boomerang(),
                    Or(
                        oos_can_jump_1_wide_pit(False),
                        oo_option_hard_logic()
                    )
                )
            ),
            oos_season_in_lost_woods(SEASON_WINTER),
            oos_can_remove_season(SEASON_WINTER),
            oos_has_autumn(),
            oos_can_break_mushroom(False),
            Or(
                oos_can_complete_lost_woods_main_sequence(False),
                And(
                    oos_can_complete_lost_woods_main_sequence(True),
                    oos_can_reach_lost_woods_pedestal(False)
                )
            )
        )
    else:
        raise NotImplementedError()


def oos_can_reach_rooster_adventure() -> Rule:
    return oo_option_hell_logic() & CanReachRegion("rooster adventure")
