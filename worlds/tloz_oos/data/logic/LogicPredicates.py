from itertools import count

from rule_builder.rules import Has, And, Or, CanReachRegion
from .Rulebuilder import *
from ..Constants import *
from ...Options import OracleOfSeasonsLogicDifficulty, OracleOfSeasonsDefaultSeedType, OracleOfSeasonsMasterKeys, OracleOfSeasonsDungeonShuffle, \
    OracleOfSeasonsD0AltEntrance, OracleOfSeasonsD2AltEntrance, OracleOfSeasonsAnimalCompanion, OracleOfSeasonsLostWoodsItemSequence, \
    OracleOfSeasonsLostWoodsMainSequence, OracleOfSeasonsHoronSeason


# Items predicates ############################################################


def oos_has_sword(accept_biggoron: bool = True) -> Rule:
    return Or(
        Has("Progressive Sword"),
        And(
            from_bool(accept_biggoron),
            Has("Biggoron's Sword")
        )
    )


def oos_has_noble_sword() -> Rule:
    return Has("Progressive Sword", 2)


def oos_has_shield() -> Rule:
    return Has("Progressive Shield")


def oos_has_fools_ore() -> Rule:
    return Has("Fool's Ore")


def oos_has_feather() -> Rule:
    return Has("Progressive Feather")


def oos_has_cape() -> Rule:
    return Has("Progressive Feather", 2)


def oos_has_satchel(level: int = 1) -> Rule:
    return Has("Seed Satchel", level)


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


def oos_has_shovel() -> Rule:
    return Has("Shovel")


def oos_has_flippers() -> Rule:
    return Has("Flippers")


# Cross items
def oos_has_cane() -> Rule:
    return Has("Cane of Somaria")


def oos_has_switch_hook(level: int = 1) -> Rule:
    return Has("Switch Hook", level)


def oos_has_tight_switch_hook() -> Rule:
    return Or(
        oos_has_switch_hook(2),
        And(
            oos_option_medium_logic(),
            oos_has_switch_hook()
        )
    )


def oos_has_shooter() -> Rule:
    return Has("Seed Shooter")


def oos_has_seed_thrower() -> Rule:
    return Or(
        oos_has_slingshot(),
        oos_has_shooter()
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


def oos_has_ember_seeds() -> Rule:
    return Or(
        Has("Ember Seeds"),
        from_option(OracleOfSeasonsDefaultSeedType, OracleOfSeasonsDefaultSeedType.option_ember),
        And(
            Has("_wild_ember_seeds"),
            oos_option_medium_logic()
        )
    )


def oos_has_scent_seeds() -> Rule:
    return Or(
        Has("Scent Seeds"),
        from_option(OracleOfSeasonsDefaultSeedType, OracleOfSeasonsDefaultSeedType.option_scent),
    )


def oos_has_pegasus_seeds() -> Rule:
    return Or(
        Has("Pegasus Seeds"),
        from_option(OracleOfSeasonsDefaultSeedType, OracleOfSeasonsDefaultSeedType.option_pegasus)
    )


def oos_has_mystery_seeds() -> Rule:
    return Or(
        Has("Mystery Seeds"),
        from_option(OracleOfSeasonsDefaultSeedType, OracleOfSeasonsDefaultSeedType.option_mystery),
        And(
            Has("_wild_mystery_seeds"),
            oos_option_medium_logic()
        )
    )


def oos_has_gale_seeds() -> Rule:
    return Or(
        Has("Gale Seeds"),
        from_option(OracleOfSeasonsDefaultSeedType, OracleOfSeasonsDefaultSeedType.option_gale)
    )


def oos_has_small_keys(dungeon_id: int, amount: int = 1) -> Rule:
    return Or(
        Has(f"Small Key ({DUNGEON_NAMES[dungeon_id]})", amount,
            options=[OptionFilter(OracleOfSeasonsMasterKeys, OracleOfSeasonsMasterKeys.option_disabled)]),
        Has(f"Master Key ({DUNGEON_NAMES[dungeon_id]})",
            options=[OptionFilter(OracleOfSeasonsMasterKeys, OracleOfSeasonsMasterKeys.option_disabled, "ne")]),
    )


def oos_has_boss_key(dungeon_id: int) -> Rule:
    return Or(
        Has(f"Boss Key ({DUNGEON_NAMES[dungeon_id]})",
            options=[OptionFilter(OracleOfSeasonsMasterKeys, OracleOfSeasonsMasterKeys.option_all_dungeon_keys, "ne")]),
        Has(f"Master Key ({DUNGEON_NAMES[dungeon_id]})",
            options=[OptionFilter(OracleOfSeasonsMasterKeys, OracleOfSeasonsMasterKeys.option_all_dungeon_keys)]),
    )


# Options and generation predicates ###########################################

def oos_option_medium_logic() -> Rule:
    return from_option(OracleOfSeasonsLogicDifficulty, OracleOfSeasonsLogicDifficulty.option_medium, "ge")


def oos_option_hard_logic() -> Rule:
    return from_option(OracleOfSeasonsLogicDifficulty, OracleOfSeasonsLogicDifficulty.option_hard, "ge")


def oos_option_hell_logic() -> Rule:
    return from_option(OracleOfSeasonsLogicDifficulty, OracleOfSeasonsLogicDifficulty.option_hell, "ge")


def oos_option_shuffled_dungeons() -> Rule:
    return from_option(OracleOfSeasonsDungeonShuffle, OracleOfSeasonsDungeonShuffle.option_true)


def oos_option_no_d0_alt_entrance() -> Rule:
    return from_option(OracleOfSeasonsD0AltEntrance, OracleOfSeasonsD0AltEntrance.option_false)


def oos_option_no_d2_alt_entrance() -> Rule:
    return from_option(OracleOfSeasonsD2AltEntrance, OracleOfSeasonsD2AltEntrance.option_false)


def oos_is_companion_ricky() -> Rule:
    return from_option(OracleOfSeasonsAnimalCompanion, OracleOfSeasonsAnimalCompanion.option_ricky)


def oos_is_companion_moosh() -> Rule:
    return from_option(OracleOfSeasonsAnimalCompanion, OracleOfSeasonsAnimalCompanion.option_moosh)


def oos_is_companion_dimitri() -> Rule:
    return from_option(OracleOfSeasonsAnimalCompanion, OracleOfSeasonsAnimalCompanion.option_dimitri)


def oos_is_default_season(area_name: str, season: int) -> Rule:
    return Season(area_name, season)


def oos_can_remove_season(season: int) -> Rule:
    # Test if player has any other season than the one we want to remove
    return Or(
        *[Has(item_name) for season_name, item_name in SEASON_ITEMS.items() if season_name != season]
    )


def oos_has_essences(target_count: int) -> Rule:
    return HasGroup("Essences", target_count)


def oos_has_essences_for_maku_seed() -> Rule:
    return HasGroupOption("Essences", "required_essences")


def oos_has_essences_for_treehouse() -> Rule:
    return HasGroupOption("Essences", "treehouse_old_man_requirement")


def oos_has_required_jewels() -> Rule:
    return HasGroupOption("Jewels", "tarm_gate_required_jewels")


def oos_can_reach_lost_woods_pedestal(allow_default: bool = False) -> Rule:
    return And(
        LostWoods(False, allow_default),
        Or(
            CanReachRegion("lost woods phonograph"),
            And(
                # if sequence is vanilla, medium+ players are expected to know it
                oos_option_medium_logic(),
                from_option(OracleOfSeasonsLostWoodsItemSequence, OracleOfSeasonsLostWoodsItemSequence.option_false)
            )
        )
    )


def oos_can_complete_lost_woods_main_sequence(allow_default: bool = False) -> Rule:
    return And(
        LostWoods(True, allow_default),
        Or(
            CanReachRegion("lost woods deku"),
            And(
                # if sequence is vanilla, medium+ players are expected to know it
                oos_option_medium_logic(),
                from_option(OracleOfSeasonsLostWoodsMainSequence, OracleOfSeasonsLostWoodsMainSequence.option_false)
            )
        )
    )


def oos_can_beat_required_golden_beasts() -> Rule:
    return HasFromListOption("_beat_golden_darknut", "_beat_golden_lynel", "_beat_golden_moblin", "_beat_golden_octorok",
                             option_name="golden_beasts_requirement")


def oos_can_complete_d11_puzzle() -> bool:
    return Or(
        from_option(OracleOfSeasonsDungeonShuffle, OracleOfSeasonsDungeonShuffle.option_false),
        CanReachNumRegions([f"enter d{i}" for i in range(1, 9)], 7)  # And then deduce the last
    )


# Various item predicates ###########################################

def oos_has_rupees(amount: int) -> Rule:
    # Make free shops sphere 1 as players will get them at the start of the game anyway
    if amount == 0:
        return True
    # Rupee checks being quite approximative, being able to farm is a must-have to prevent any stupid lock
    if not oos_can_farm_rupees() -> Rule:
        return False
    # In hard logic, having the shovel is equivalent to having an infinite amount of Rupees thanks to RNG manips
    if oos_option_hard_logic() and oos_has_shovel() -> Rule:
        return True

    rupees =.count("Rupees (1)")
    rupees +=.count("Rupees (5)") * 5
    rupees +=.count("Rupees (10)") * 10
    rupees +=.count("Rupees (20)") * 20
    rupees +=.count("Rupees (30)") * 30
    rupees +=.count("Rupees (50)") * 50
    rupees +=.count("Rupees (100)") * 100
    rupees +=.count("Rupees (200)") * 200

    # Secret rooms inside D2 and D6 containing loads of rupees, but only in medium logic
    if oos_option_medium_logic() -> Rule:
        if Has("_reached_d2_rupee_room") -> Rule:
            rupees += 150
        if Has("_reached_d6_rupee_room") -> Rule:
            rupees += 90

    # Old men giving and taking rupees
    world =.multiworld.worlds[player]
    for region_name, value in world.old_man_rupee_values.items() -> Rule:
        event_name = "rupees from " + region_name
        # Always assume bad rupees are obtained, otherwise getting an item could make a shop no longer available and break AP
        if Has(event_name) or value < 0:
            rupees += value

    return rupees >= amount


def oos_has_rupees_for_shop(shop_name: str) -> Rule:
    return Or(
        And(
            oos_option_hard_logic(),
            oos_has_shovel()
        ),
        HasRupeesForShop(shop_name)
    )


def oos_can_farm_rupees() -> Rule:
    # Having a weapon to get  or a shovel is enough to guarantee that we can reach a significant amount of rupees
    return Or(
        oos_can_kill_normal_enemy(False, False),
        oos_has_shovel()
    )


def oos_can_buy_market() -> Rule:
    return HasOresForShop()


def oos_can_farm_ore_chunks() -> Rule:
    return Or(
        oos_has_shovel(),
        And(
            oos_option_medium_logic(),
            Or(
                oos_has_magic_boomerang(),
                oos_has_sword()
            )
        ),
        And(
            oos_option_hard_logic(),
            Or(
                Has("_reached_subrosian_dance_hall"),
                oos_has_bracelet(),
                oos_has_switch_hook()
            )
        )
    )


def oos_can_date_rosa() -> Rule:
    return And(
        Has("_reached_rosa"),
        Has("Ribbon")
    )


def oos_can_trigger_far_switch() -> Rule:
    return Or(
        oos_has_boomerang(),
        oos_has_bombs(),
        oos_has_seed_thrower(),
        oos_shoot_beams(),
        oos_has_switch_hook()
    )


def oos_shoot_beams() -> Rule:
    return Or(
        And(
            oos_option_medium_logic(),
            oos_has_sword(False),
            Has("Energy Ring"),
        ),
        And(
            oos_option_medium_logic(),
            oos_has_noble_sword(),
            Or(
                Has("Heart Ring L-2"),
                And(
                    oos_option_hard_logic(),
                    Has("Heart Ring L-1"),
                )
            )
        )
    )


def oos_has_rod() -> Rule:
    return Or(
        oos_has_winter(),
        oos_has_summer(),
        oos_has_spring(),
        oos_has_autumn()
    )


def oos_has_bombs(amount: int = 1) -> Rule:
    return Or(
        Has("Bombs", amount),
        And(
            # With medium logic is expected to know they can get free bombs
            # from D2 moblin room even if they never had bombs before
            amount == 1,
            oos_option_medium_logic(),
            Has("_wild_bombs"),
        )
    )


def oos_has_bombchus(amount: int = 1) -> Rule:
    return Has("Bombchus", amount)


def oos_has_flute() -> Rule:
    return Or(
        oos_can_summon_ricky(),
        oos_can_summon_moosh(),
        oos_can_summon_dimitri()
    )


def oos_can_summon_ricky() -> Rule:
    return Has("Ricky's Flute")


def oos_can_summon_moosh() -> Rule:
    return Has("Moosh's Flute")


def oos_can_summon_dimitri() -> Rule:
    return Has("Dimitri's Flute")


# Jump-related predicates ###########################################

def oos_can_jump_1_wide_liquid(can_summon_companion: bool) -> Rule:
    return Or(
        oos_has_feather(),
        And(
            oos_option_medium_logic(),
            can_summon_companion,
            oos_can_summon_ricky()
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
            oos_option_hard_logic(),
            oos_has_feather(),
            oos_has_bombs()
        )
    )


def oos_can_jump_3_wide_liquid() -> Rule:
    return Or(
        oos_has_cape(),
        And(
            oos_option_hard_logic(),
            oos_has_feather(),
            oos_can_use_pegasus_seeds(),
            oos_has_bombs(),
        )
    )


def oos_can_jump_4_wide_liquid() -> Rule:
    return And(
        oos_has_cape(),
        Or(
            oos_can_use_pegasus_seeds(),
            And(
                # Hard logic expects player to be able to cape bomb-jump above 4-wide liquids
                oos_option_hard_logic(),
                oos_has_bombs()
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
            can_summon_companion,
            Or(
                oos_can_summon_moosh(),
                oos_can_summon_ricky()
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
                oos_option_medium_logic(),
                oos_can_use_pegasus_seeds()
            )
        )
    )


def oos_can_jump_3_wide_pit() -> Rule:
    return Or(
        oos_has_cape(),
        And(
            oos_option_medium_logic(),
            oos_has_feather(),
            oos_can_use_pegasus_seeds(),
        )
    )


def oos_can_jump_4_wide_pit() -> Rule:
    return And(
        oos_has_cape(),
        Or(
            oos_option_medium_logic(),
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
        oos_option_medium_logic(),
        oos_has_cape(),
        oos_can_use_pegasus_seeds(),
    )


# Seed-related predicates ###########################################

def oos_can_use_seeds() -> Rule:
    return Or(
        oos_has_slingshot(),
        oos_has_shooter(),
        oos_has_satchel()
    )


def oos_can_use_ember_seeds(accept_mystery_seeds: bool) -> Rule:
    return And(
        oos_can_use_seeds(),
        Or(
            oos_has_ember_seeds(),
            And(
                # Medium logic expects the player to know they can use mystery seeds
                # to randomly get the ember effect in some cases
                accept_mystery_seeds,
                oos_option_medium_logic(),
                oos_has_mystery_seeds(),
            )
        )
    )


def oos_can_use_scent_seeds() -> Rule:
    return And(
        oos_can_use_seeds(),
        oos_has_scent_seeds()
    )


def oos_can_use_pegasus_seeds() -> Rule:
    return And(
        # Unlike other seeds, pegasus only have an interesting effect with the satchel
        oos_has_satchel(),
        oos_has_pegasus_seeds()
    )


def oos_can_use_gale_seeds_offensively() -> Rule:
    return And(
        oos_has_satchel(2),
        oos_option_medium_logic(),
        Or(
            oos_has_gale_seeds(),
            oos_has_mystery_seeds()
        ),
        Or(
            oos_has_seed_thrower(),
            And(
                oos_has_satchel(),
                Or(
                    oos_option_hard_logic(),
                    oos_has_feather()
                ),
            )
        )
    )


def oos_can_use_mystery_seeds() -> Rule:
    return And(
        oos_can_use_seeds(),
        oos_has_mystery_seeds()
    )


# Break / kill predicates ###########################################

def oos_can_break_bush(can_summon_companion: bool = False, allow_bombchus: bool = False) -> Rule:
    return Or(
        oos_can_break_flowers(can_summon_companion, allow_bombchus),
        oos_has_bracelet()
    )


def oos_can_harvest_regrowing_bush() -> Rule:
    return Or(
        oos_has_sword(),
        oos_has_fools_ore(),
        oos_has_bombs(),
        And(
            oos_option_medium_logic(),
            oos_has_bombchus(4)
        )
    )


def oos_can_break_mushroom(can_use_companion: bool) -> Rule:
    return Or(
        oos_has_bracelet(),
        And(
            oos_option_medium_logic(),
            Or(
                oos_has_magic_boomerang(),
                And(
                    can_use_companion,
                    oos_can_summon_dimitri()
                )
            )
        ),
    )


def oos_can_break_pot() -> Rule:
    return Or(
        oos_has_bracelet(),
        oos_has_noble_sword(),
        Has("Biggoron's Sword"),
        oos_has_switch_hook()
    )


def oos_can_break_flowers(can_summon_companion: bool = False, allow_bombchus: bool = False) -> Rule:
    return Or(
        oos_has_sword(),
        oos_has_magic_boomerang(),
        oos_has_switch_hook(),
        And(
            can_summon_companion,
            oos_has_flute()
        ),
        And(
            # Consumables need at least medium logic, since they need a good knowledge of the game
            # not to be frustrating
            oos_option_medium_logic(),
            Or(
                oos_has_bombs(2),
                oos_can_use_ember_seeds(False),
                And(
                    oos_has_seed_thrower(),
                    oos_has_gale_seeds()
                ),
                And(
                    allow_bombchus,
                    oos_has_bombchus(4)
                )
            )
        ),
    )


def oos_can_break_crystal() -> Rule:
    return Or(
        oos_has_sword(),
        oos_has_bombs(),
        oos_has_bracelet(),
        And(
            oos_option_medium_logic(),
            Has("Expert's Ring")
        ),
        And(
            oos_option_medium_logic(),
            oos_has_bombchus(4)
        ),
    )


def oos_can_break_sign() -> Rule:
    return Or(
        oos_has_noble_sword(),
        Has("Biggoron's Sword"),
        oos_has_bracelet(),
        oos_can_use_ember_seeds(False),
        oos_has_magic_boomerang(),
        oos_has_switch_hook()
    )


def oos_can_harvest_tree(can_use_companion: bool) -> Rule:
    return And(
        oos_can_use_seeds(),
        Or(
            oos_has_sword(),
            oos_has_fools_ore(),
            oos_has_rod(),
            oos_can_punch(),
            And(
                can_use_companion,
                oos_option_medium_logic(),
                oos_can_summon_dimitri()
            )
        )
    )


def oos_can_harvest_gasha(count: int) -> Rule:
    reachable_soils = [Has(f"_reached_{region_name}") for region_name in GASHA_SPOT_REGIONS]
    return And(
        reachable_soils.count(True) >= count,  # Enough soils are reachable
        Has("Gasha Seed", count),  # Enough seeds to plant
        Or(
            # Can actually harvest the nut, and get kills
            oos_has_sword(),
            oos_has_fools_ore()
        )
    )


def oos_can_push_enemy() -> Rule:
    return Or(
        oos_has_rod(),
        oos_has_shield(),
        And(
            oos_option_medium_logic(),
            oos_has_shovel()
        )
    )


def oos_can_kill_normal_enemy(pit_available: bool = False,
                              allow_gale_seeds: bool = True) -> Rule:
    return Or(
        oos_can_kill_normal_enemy_no_cane(pit_available, allow_gale_seeds),
        (oos_option_medium_logic() & oos_has_cane())
    )


def oos_can_kill_normal_enemy_no_cane(pit_available: bool = False,
                                      allow_gale_seeds: bool = True) -> Rule:
    return Or(
        And(
            # If a pit is avaiable nearby, it can be used to put the enemies inside using
            # items that are usually non-lethal
            pit_available,
            oos_can_push_enemy()
        ),
        oos_has_sword(),
        oos_has_fools_ore(),
        oos_can_kill_normal_using_satchel(allow_gale_seeds),
        oos_can_kill_normal_using_slingshot(allow_gale_seeds),
        And(
            oos_option_medium_logic(),
            oos_has_bombs(4)
        ),
        oos_has_bombchus(2),
        oos_can_punch()
    )


def oos_can_kill_normal_using_satchel(allow_gale_seeds: bool = True) -> Rule:
    # Expect a 50+ seed satchel to ensure we can chain dungeon rooms to some extent if that's our only kill option
    return oos_has_satchel(2) & Or(
        # Casual logic => only ember
        oos_has_ember_seeds(),
        And(
            # Medium logic => allow scent or gale+feather
            oos_option_medium_logic(),
            Or(
                oos_has_scent_seeds(),
                oos_has_mystery_seeds(),
                And(
                    allow_gale_seeds,
                    oos_has_gale_seeds(),
                    oos_has_feather()
                )
            )
        ),
        And(
            # Hard logic => allow gale without feather
            allow_gale_seeds,
            oos_option_hard_logic(),
            oos_has_gale_seeds()
        )
    )


def oos_can_kill_normal_using_slingshot(allow_gale_seeds: bool = True) -> Rule:
    return And(
        # Expect a 50+ seed satchel to ensure we can chain dungeon rooms to some extent if that's our only kill option
        oos_has_satchel(2),
        oos_has_seed_thrower(),
        Or(
            oos_has_ember_seeds(),
            oos_has_scent_seeds(),
            And(
                oos_option_medium_logic(),
                Or(
                    And(
                        allow_gale_seeds,
                        oos_has_gale_seeds(),
                    ),
                    oos_has_mystery_seeds(),
                )
            )
        )
    )


def oos_can_kill_armored_enemy(allow_cane: bool, allow_bombchus: bool) -> Rule:
    return Or(
        oos_has_sword(),
        oos_has_fools_ore(),
        And(
            oos_option_medium_logic(),
            oos_has_bombs(4)
        ),
        And(
            allow_bombchus,
            oos_has_bombchus(2)
        ),
        And(
            oos_has_satchel(2),  # Expect a 50+ seeds satchel to be able to chain rooms in dungeons
            oos_has_scent_seeds(),
            Or(
                oos_has_seed_thrower(),
                oos_option_medium_logic()
            )
        ),
        And(
            allow_cane,
            oos_option_medium_logic(),
            oos_has_cane()
        ),
        oos_can_punch()
    )


def oos_can_kill_stalfos() -> Rule:
    return Or(
        oos_can_kill_normal_enemy(),
        And(
            oos_option_medium_logic(),
            oos_has_rod()
        )
    )


def oos_can_kill_moldorm(pit_available: bool = False) -> Rule:
    return Or(
        oos_can_kill_armored_enemy(True, True),
        oos_has_switch_hook(),
        And(
            pit_available,
            Or(
                oos_has_shield(),
                And(
                    oos_option_medium_logic(),
                    oos_has_shovel()
                )
            )
        )
    )


def oos_can_kill_facade() -> Rule:
    return Or(
        oos_has_bombs(),
        oos_has_bombchus(2)
    )


def oos_can_punch() -> Rule:
    return And(
        oos_option_medium_logic(),
        Or(
            Has("Fist Ring"),
            Has("Expert's Ring")
        )
    )


def oos_can_trigger_lever() -> Rule:
    return Or(
        oos_can_trigger_lever_from_minecart(),
        oos_has_switch_hook(),
        And(
            oos_option_medium_logic(),
            oos_has_shovel()
        )
    )


def oos_can_trigger_lever_from_minecart() -> Rule:
    return Or(
        oos_can_punch(),
        oos_has_sword(),
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
        oos_has_sword(),
        oos_has_fools_ore(),
        oos_has_boomerang(),
        oos_can_push_enemy(),
        oos_has_switch_hook(),  # Also push the hardhat
        And(
            oos_option_medium_logic(),
            oos_has_satchel(2),
            Or(
                oos_has_seed_thrower(),
                And(
                    oos_option_hard_logic(),
                    oos_has_satchel(),
                )
            ),
            Or(
                oos_has_scent_seeds(),
                oos_has_gale_seeds(),
                oos_has_mystery_seeds()
            ),
            oos_has_bombchus(2)
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
                    oos_option_medium_logic(),
                    oos_has_switch_hook()
                )
            ),
            oos_can_kill_normal_enemy(True),
        ),
        And(
            oos_option_hard_logic(),
            Or(
                oos_can_use_ember_seeds(False),
                oos_can_punch(),
                oos_has_cane()
            )
        )
    )


def oos_can_flip_spiked_beetle() -> Rule:
    return Or(
        oos_has_shield(),
        And(
            oos_option_medium_logic(),
            oos_has_shovel()
        )
    )


def oos_can_kill_spiked_beetle() -> Rule:
    return Or(
        And(  # Regular flip + kill
            oos_can_flip_spiked_beetle(),
            Or(
                oos_has_sword(),
                oos_has_fools_ore(),
                oos_can_kill_normal_using_satchel(),
                oos_can_kill_normal_using_slingshot(),
                oos_has_switch_hook()
            )
        ),
        # Instant kill using Gale Seeds
        oos_can_use_gale_seeds_offensively()
    )


def oos_can_kill_magunesu() -> Rule:
    return Or(
        oos_has_sword(),
        oos_has_fools_ore(),
        # Has("expert's ring")
    )


# Action predicates ###########################################

def oos_can_remove_snow(can_summon_companion: bool) -> Rule:
    return Or(
        oos_has_shovel(),
        And(
            can_summon_companion,
            oos_has_flute()
        )
    )


def oos_can_swim(can_summon_companion: bool) -> Rule:
    return Or(
        oos_has_flippers(),
        And(
            can_summon_companion,
            oos_can_summon_dimitri()
        )
    )


def oos_can_remove_rockslide(can_summon_companion: bool) -> Rule:
    return Or(
        oos_has_bombs(),
        And(
            oos_option_medium_logic(),
            oos_has_bombchus(4)
        ),
        And(
            can_summon_companion,
            oos_can_summon_ricky()
        )
    )


def oos_can_meet_maple() -> Rule:
    return oos_can_kill_normal_enemy(False, False)


def oos_can_dimitri_clip() -> Rule:
    return And(
        oos_option_hell_logic(),
        oos_can_summon_dimitri(),
        oos_has_bracelet(),
        oos_has_gale_seeds(),
        oos_has_satchel()
    )


# Season in region predicates ##########################################

def oos_season_in_spool_swamp(season: int) -> Rule:
    return Or(
        oos_is_default_season("SPOOL_SWAMP", season),
        And(
            oos_has_season(season),
            Has("_reached_spool_stump")
        )
    )


def oos_season_in_eyeglass_lake(season: int) -> Rule:
    return Or(
        oos_is_default_season("EYEGLASS_LAKE", season),
        And(
            oos_has_season(season),
            Has("_reached_eyeglass_stump")
        )
    )


def oos_season_in_temple_remains(season: int) -> Rule:
    return Or(
        oos_is_default_season("TEMPLE_REMAINS", season),
        And(
            oos_has_season(season),
            Has("_reached_remains_stump")
        )
    )


def oos_season_in_holodrum_plain(season: int) -> Rule:
    return Or(
        oos_is_default_season("HOLODRUM_PLAIN", season),
        And(
            oos_has_season(season),
            Has("_reached_ghastly_stump")
        )
    )


def oos_season_in_western_coast(season: int) -> Rule:
    return Or(
        oos_is_default_season("WESTERN_COAST", season),
        And(
            oos_has_season(season),
            Has("_reached_coast_stump")
        )
    )


def oos_season_in_eastern_suburbs(season: int) -> Rule:
    return Or(
        oos_is_default_season("EASTERN_SUBURBS", season),
        oos_has_season(season)
    )


def oos_not_season_in_eastern_suburbs(season: int) -> Rule:
    return Or(
        not oos_is_default_season("EASTERN_SUBURBS", season),
        oos_can_remove_season(season)
    )


def oos_season_in_sunken_city(season: int) -> Rule:
    return Or(
        oos_is_default_season("SUNKEN_CITY", season),
        And(
            oos_has_season(season),
            Or(
                oos_is_default_season("SUNKEN_CITY", SEASON_WINTER),
                oos_can_swim(True),
                Has("_saved_dimitri_in_sunken_city")
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
            Has("_reached_d2_stump")
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

def oos_self_locking_item(region_name: str, item_name: str) -> Rule:
    if .multiworld.worlds[player].options.accessibility == Accessibility.option_full:
        return False

    region =.multiworld.get_region(region_name)
    items_in_region = [location.item for location in region.locations if location.item is not None]
    for item in items_in_region:
        if item.name == item_name and item.player == player:
            return True
    return False

def oos_self_locking_small_key(region_name: str, dungeon: int) -> Rule:
    item_name = f"Small Key ({DUNGEON_NAMES[dungeon]})"
    return oos_self_locking_item(region_name, item_name)

# Rooster adventure logic  ######################################################

def oos_roosters() -> Rule:
    if .tloz_oos_available_cuccos[player] is None:
        # This computes cuccos for the whole game then caches it (total, top, bottom)
        available_cuccos = {
            "cucco mountain": (-1, -1, -1),
            "horon": (-1, -1, -1),
            "suburbs": (-1, -1, -1),
            "moblin road": (-1, -1, -1),
            "sunken": (-1, -1, -1),
            "swamp": (-1, -1, -1),
            "d6": (-1, -1, -1),
        }

        def register_cucco(region: str, new_cuccos: tuple[int, int, int) -> Rule:
            old_cuccos = available_cuccos[region]

        available_cuccos[region] = tuple([max(old_cuccos[i], new_cuccos[i) for i in range(3))

        def use_any_cucco(cuccos: tuple[int, int, int) -> tuple[int, int, int]:

        return cuccos[0] - 1, cuccos[1], cuccos[2]

        def use_top_cucco(cuccos: tuple[int, int, int) -> tuple[int, int, int]:

        return cuccos[0] - 1, cuccos[1] - 1, cuccos[2]

        def use_bottom_cucco(cuccos: tuple[int, int, int) -> tuple[int, int, int]:

        return cuccos[0] - 1, cuccos[1], cuccos[2] - 1

        # These tops count the 2 tops that have to be sacrificed to exit mt cucco
        if Has("Shovel") -> Rule:
            if Has("Progressive Boomerang") -> Rule:
                top = 3
            else:
                top = 2
        elif Has("Progressive Boomerang") and oos_can_use_pegasus_seeds() -> Rule:
            top = 2
        else:
            top = 1  # Sign + season indicator

        if oos_season_in_mt_cucco(SEASON_SPRING) \
                and (oos_can_break_flowers() or Has("Spring Banana")) -> Rule:
            bottom = 2  # Sign
            # No more than 2 bottoms can be used in logic currently
        else:
            bottom = 0

        available_cuccos["cucco mountain"] = (top + bottom, top, bottom)

        if oos_can_jump_3_wide_pit() or oos_can_swim(True) -> Rule:
            # Either go to holdrum plains through natzu's water or through temple remains
            available_cuccos["horon"] = available_cuccos["cucco mountain"]

        if oos_has_flute() -> Rule:
            # go from holodrum to sunken
            available_cuccos["sunken"] = available_cuccos["horon"]
        elif oos_is_companion_moosh() -> Rule:
            if oos_can_jump_4_wide_liquid() or oos_has_flute() -> Rule:
                # go from holodrum to sunken
                available_cuccos["sunken"] = available_cuccos["horon"]
            elif oos_can_jump_3_wide_pit() -> Rule:
                # go from holodrum to sunken, through moblin fortress
                available_cuccos["sunken"] = use_top_cucco(available_cuccos["horon")
                elif oos_is_companion_ricky() -> Rule:
                # go from natzu north to sunken
                if oos_can_break_flowers() and oos_can_swim(False) -> Rule:  # distance bush break
                    available_cuccos["sunken"] = use_any_cucco(available_cuccos["cucco mountain")
                elif oos_can_swim(False) -> Rule:
                # go from natzu north to sunken
                    available_cuccos["sunken"] = available_cuccos["cucco mountain"]
                # Jump from sunken to suburbs
                available_cuccos["suburbs"] = available_cuccos["sunken"]

                if oos_can_use_ember_seeds(False) -> Rule:
                # Go through horon village
                available_cuccos["suburbs"] = available_cuccos["horon"]
                elif oos_season_in_eyeglass_lake(SEASON_WINTER) \
                     or ((not oos_is_default_season("EYEGLASS_LAKE", SEASON_SUMMER) or
                          oos_can_remove_season(SEASON_SUMMER)) and oos_can_swim(True)) -> Rule:
                # Go through the suburbs portal screen
                available_cuccos["suburbs"] = use_any_cucco(available_cuccos["horon")

                if oos_season_in_eastern_suburbs(SEASON_SPRING) -> Rule:
                # Use the flower to go from suburbs to sunken
                register_cucco("sunken", available_cuccos["suburbs")

                if oos_season_in_eastern_suburbs(SEASON_WINTER) -> Rule:
                # Walk
                available_cuccos["moblin road"] = available_cuccos["suburbs"]
                else:
                # Use a top cucco from the top of the spring flower to go past the tree
                available_cuccos["moblin road"] = use_top_cucco(available_cuccos["sunken")

                if Or(
                    oos_season_in_holodrum_plain(SEASON_SUMMER),
                    oos_can_jump_4_wide_pit(),
                    oos_can_summon_ricky(),
                    oos_can_summon_moosh()
                ) -> Rule:
                # Move up the swamp vines regularly
                available_cuccos["swamp"] = available_cuccos["horon"]
                else:
                # Or use a bottom cucco
                available_cuccos["swamp"] = use_bottom_cucco(available_cuccos["horon")

                if And(  # Reach tarm ruins, could probably be optimized
                    oos_has_required_jewels(),
                    Or(
                        oos_season_in_lost_woods(SEASON_SUMMER),
                        And(
                            oos_season_in_lost_woods(SEASON_AUTUMN),
                            oos_option_medium_logic(),
                            oos_has_magic_boomerang(),
                            Or(
                                oos_can_jump_1_wide_pit(False),
                                oos_option_hard_logic()
                            )
                        )
                    ),
                    oos_season_in_lost_woods(SEASON_WINTER),
                    oos_can_remove_season(SEASON_WINTER)
                ) -> Rule:
                can_reach_deku = And(
                    oos_has_shield(),
                    Or(
                        available_cuccos["swamp"][1],
                        oos_can_jump_2_wide_liquid(),
                        oos_can_swim(False)
                    )
                )
                if And(
                    oos_has_autumn(),
                    oos_can_break_mushroom(False),
                    Or(
                        oos_can_complete_lost_woods_main_sequence(False, can_reach_deku),
                        And(
                            oos_can_complete_lost_woods_main_sequence(True, can_reach_deku),
                            oos_can_reach_lost_woods_pedestal(False, And(
                                oos_can_use_ember_seeds(False),
                                Has("Phonograph")
                            )),
                        )
                    )
                ) -> Rule:
                available_cuccos["d6"] = available_cuccos["swamp"]

                for region in available_cuccos:
                    if
                Or(available_cuccos[region][i] < 0 for i in range(3)) -> Rule: \
                    available_cuccos[region] = (-1, -1, -1)
                .tloz_oos_available_cuccos[player] = available_cuccos

    return.tloz_oos_available_cuccos[player]

def oos_can_reach_rooster_adventure() -> Rule:
    # This is only safe if an indirect condition is set
    return oos_option_hell_logic() & CanReachRegion("rooster adventure")
