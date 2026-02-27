from dataclasses import dataclass
from datetime import datetime

from Options import Choice, DeathLink, DefaultOnToggle, PerGameCommonOptions, Range, Toggle, StartInventoryPool, \
    ItemDict, ItemsAccessibility, ItemSet, Visibility, OptionGroup, NamedRange
from .data.Items import ITEMS_DATA

from .common.Options import *


class OracleOfSeasonsDefaultSeasons(Choice):
    """
    The world of Holodrum is split in regions, each one having its own default season being forced when entering it.
    This options gives several ways of manipulating those default seasons.
    - Vanilla: default seasons for each region are the ones from the original game
    - Randomized: each region has its own random default season picked at generation time
    - Random Singularity: a single season is randomly picked and put as default season in every region in the game
    - Specific Singularity: the given season is put as default season in every region in the game
    """
    display_name = "Default Seasons"

    option_vanilla = 0
    option_randomized = 1
    option_random_singularity = 2
    option_spring_singularity = 3
    option_summer_singularity = 4
    option_autumn_singularity = 5
    option_winter_singularity = 6

    default = 1
    include_in_slot_data = True


class OracleOfSeasonsHoronSeason(DefaultOnToggle):
    """
    In the vanilla game, Horon Village default season is chaotic: every time you enter it, it sets a random season.
    This nullifies every condition where a season is required inside Horon Village, since you can leave and re-enter
    again and again until you get the season that suits you.
    Enabling this option disables that behavior and makes Horon Village behave like any other region in the game.
    This means it will have a default season picked at generation time that follows the global behavior defined
    in the "Default Seasons" option.
    """
    display_name = "Normalize Horon Village Season"


class OracleOfSeasonsDuplicateSeedTree(Choice):
    """
    The game contains 6 seed trees but only 5 seed types, which means two trees
    must contain the same seed type. This option enables choosing which tree will
    always contain a duplicate of one of the other 5 trees.
    It is strongly advised to set this to "Tarm Ruins Tree" since it's by far the hardest tree to reach
    (and being locked out of a useful seed type can lead to very frustrating situations).
    """
    display_name = "Duplicate Seed Tree"

    option_horon_village = 0
    option_woods_of_winter = 1
    option_north_horon = 2
    option_spool_swamp = 3
    option_sunken_city = 4
    option_tarm_ruins = 5

    default = 5


class OracleOfSeasonsPortalShuffle(Choice):
    """
    - Vanilla: pairs of portals are the same as in the original game
    - Shuffle Outwards: each portal is connected to a random portal in the opposite dimension picked at generation time
    - Shuffle: each portal is connected to a random portal, which might be in the same dimension (with the guarantee of
      having at least one portal going across dimensions)
    """
    display_name = "Shuffle Subrosia Portals"

    option_vanilla = 0
    option_shuffle_outwards = 1
    option_shuffle = 2

    default = 0
    include_in_slot_data = True


class OracleOfSeasonsGoldenOreSpotsShuffle(Toggle):
    """
    This option adds the 7 hidden digging spots in Subrosia (containing 50 Ore Chunks each) to the pool
    of randomized locations.
    """
    display_name = "Shuffle Golden Ore Spots"

    include_in_patch = True
    include_in_slot_data = True


class OracleOfSeasonsD0AltEntrance(Toggle):
    """
    If enabled, remove the hole acting as an alternate entrance to Hero’s Cave. Stairs will be added inside the dungeon to make the chest reachable.
    This is especially useful when shuffling dungeons, since only main dungeon entrances are shuffled.
    If this option is not set in such a case, you could potentially have two distant entrances leading to the same dungeon.
    """
    display_name = "Remove Hero's Cave Alt. Entrance"

    include_in_patch = True
    include_in_slot_data = True


class OracleOfSeasonsD2AltEntrance(Toggle):
    """
    If enabled, remove both stairs acting as alternate entrances to Snake’s Remains and connect them together inside the dungeon.
    This is especially useful when shuffling dungeons, since only main dungeon entrances are shuffled.
    If this option is not set in such a case, you could potentially have two distant entrances leading to the same dungeon.
    """
    display_name = "Remove D2 Alt. Entrance"

    include_in_patch = True
    include_in_slot_data = True


class OraclesOfSeasonsTreehouseOldManRequirement(Range):
    """
    The amount of essences that you need to bring to the treehouse old man for him to give his item.
    """
    display_name = "Treehouse Old Man Requirement"

    range_start = 0
    range_end = 8

    default = 5
    include_in_patch = True
    include_in_slot_data = True


class OraclesOfSeasonsTarmGateRequirement(Range):
    """
    The number of jewels that you need to bring to Tarm Ruins gate to be able to open it.
    """
    display_name = "Tarm Ruins Gate Required Jewels"

    range_start = 0
    range_end = 4

    default = 4
    include_in_patch = True
    include_in_slot_data = True


class OraclesOfSeasonsGoldenBeastsRequirement(Range):
    """
    The amount of golden beasts that need to be beaten for the golden old man to give his item.
    Golden beasts are 4 unique enemies that appear at specific spots on specific seasons, and beating all four of them
    requires all seasons and having access to most of the overworld.
    """
    display_name = "Golden Beasts Requirement"

    range_start = 0
    range_end = 4

    default = 1
    include_in_patch = True
    include_in_slot_data = True


class OracleOfSeasonsSignGuyRequirement(NamedRange):
    """
    In Subrosia, a NPC will "punish" you if you break more than 100 signs in the vanilla game by giving you an item.
    This option lets you configure how many signs are required to obtain that item, since breaking 100 signs is not
    everyone's cup of tea.
    """
    display_name = "Sign Guy Requirement"

    range_start = 0
    range_end = 250

    default = 10
    special_range_names = {
        "vanilla": 100
    }
    include_in_patch = True


class OracleOfSeasonsLostWoodsItemSequence(DefaultOnToggle):
    """
    If enabled, the secret sequence leading to the Noble Sword pedestal will be randomized (both directions to
    take and seasons to use).
    To know the randomized combination, you will need to bring the Phonograph to the Deku Scrub near the stump, just
    like in the vanilla game.
    """
    display_name = "Randomize Lost Woods Item Sequence"

    include_in_slot_data = True


class OracleOfSeasonsLostWoodsMainSequence(Toggle):
    """
    If enabled, the secret sequence leading to D6 sector will be randomized (both directions to take and
    seasons to use).
    To know the randomized combination, you will need to stun the Deku Scrub near the jewel gate using a shield, just
    like in the vanilla game.
    """
    display_name = "Randomize Lost Woods Main Sequence"

    include_in_slot_data = True


class OracleOfSeasonsSamasaGateCode(Toggle):
    """
    This option defines if the secret combination which opens the gate to Samasa Desert should be randomized.
    You can then configure the length of the sequence with the next option.
    """
    display_name = "Randomize Samasa Desert Gate Code"


class OracleOfSeasonsSamasaGateCodeLength(Range):
    """
    The length of the randomized combination for Samasa Desert gate.
    This option has no effect if "Randomize Samasa Desert Gate Code" is disabled.
    """
    display_name = "Samasa Desert Gate Code Length"

    range_start = 1
    range_end = 40

    default = 8


class OracleOfSeasonsFoolsOre(Choice):
    """
    In the vanilla game, the Fool's Ore is the item "given" by the strange brothers in "exchange" for your feather.
    The way the vanilla game is done means you never get to use it, but it's by far the strongest weapon in the game
    (dealing 4 times more damage than an L-2 sword!)
    - Vanilla: Fool's Ore appears in the item pool with its stats unchanged
    - Balanced: Fool's Ore appears in the item pool but its stats are lowered to become comparable to an L-2 sword
    - Excluded: Fool's Ore doesn't appear in the item pool at all. Problem solved!
    """
    display_name = "Fool's Ore"

    option_vanilla = 0
    option_balanced = 1
    option_excluded = 2

    default = 1
    include_in_patch = True


class OracleOfSeasonsQuickFlute(DefaultOnToggle):
    """
    When enabled, playing the flute will immobilize you during a very small amount of time compared to vanilla game.
    """
    display_name = "Quick Flute"

    include_in_patch = True


class OracleOfSeasonsRosaQuickUnlock(Toggle):
    """
    When enabled, Rosa will instantly unlock all subrosia locks when given the Ribbon
    """
    display_name = "Rosa Quick Unlock"

    include_in_patch = True


class OracleOfSeasonsLinkedHerosCave(Choice):
    """
    Sets whether and how the link version of the hero's cave is placed in the world.
    - Samasa: an entrance is placed in the Samasa desert, below the oasis
    """
    display_name = "Linked Hero's Cave"
    samasa = 0b01
    no_alt_entrance = 0b10

    option_disabled = 0b00
    option_samasa = 0b01
    option_samasa_without_alt_entrance = 0b11

    include_in_patch = True
    include_in_slot_data = True


class OracleOfSeasonsDeathLink(DeathLink):
    """
    When you die, everyone who enabled death link dies. Of course, the reverse is true too.
    """
    include_in_slot_data = True  # This is for the bizhawk client


@dataclass
class OracleOfSeasonsOptions(PerGameCommonOptions):
    accessibility: ItemsAccessibility
    goal: OraclesGoal
    logic_difficulty: OraclesLogicDifficulty
    death_link: OracleOfSeasonsDeathLink

    # Optional locations
    advance_shop: OraclesShop
    shuffle_old_men: OraclesOldMenShuffle
    shuffle_business_scrubs: OraclesScrubsShuffle
    shuffle_golden_ore_spots: OracleOfSeasonsGoldenOreSpotsShuffle
    deterministic_gasha_locations: OraclesGashaLocations
    secret_locations: OraclesIncludeSecretLocations
    linked_heros_cave: OracleOfSeasonsLinkedHerosCave

    # Essences
    required_essences: OraclesRequiredEssences
    shuffle_essences: OraclesEssenceSanity
    placed_essences: OraclesPlacedEssences
    exclude_dungeons_without_essence: OraclesExcludeDungeonsWithoutEssence
    show_dungeons_with_map: OraclesShowDungeonsWithMap
    show_dungeons_with_essence: OraclesShowDungeonsWithEssence

    # Seasons
    default_seasons: OracleOfSeasonsDefaultSeasons
    normalize_horon_village_season: OracleOfSeasonsHoronSeason

    # Overworld layout options
    animal_companion: OraclesAnimalCompanion
    shuffle_portals: OracleOfSeasonsPortalShuffle
    shuffle_dungeons: OraclesDungeonShuffle
    remove_d0_alt_entrance: OracleOfSeasonsD0AltEntrance
    remove_d2_alt_entrance: OracleOfSeasonsD2AltEntrance
    default_seed: OraclesDefaultSeedType
    duplicate_seed_tree: OracleOfSeasonsDuplicateSeedTree

    # Dungeon items
    master_keys: OraclesMasterKeys
    keysanity_small_keys: OraclesSmallKeyShuffle
    keysanity_boss_keys: OraclesBossKeyShuffle
    keysanity_maps_compasses: OraclesMapCompassShuffle
    starting_maps_compasses: OraclesStartingMapsCompasses

    # Numeric requirements for some checks / access to regions
    treehouse_old_man_requirement: OraclesOfSeasonsTreehouseOldManRequirement
    tarm_gate_required_jewels: OraclesOfSeasonsTarmGateRequirement
    golden_beasts_requirement: OraclesOfSeasonsGoldenBeastsRequirement
    sign_guy_requirement: OracleOfSeasonsSignGuyRequirement
    gasha_nut_kill_requirement: OraclesGashaNutKillRequirement

    # Other randomizable stuff
    randomize_lost_woods_item_sequence: OracleOfSeasonsLostWoodsItemSequence
    randomize_lost_woods_main_sequence: OracleOfSeasonsLostWoodsMainSequence
    randomize_samasa_gate_code: OracleOfSeasonsSamasaGateCode
    samasa_gate_code_length: OracleOfSeasonsSamasaGateCodeLength

    # QOL
    quick_flute: OraclesQuickFlute
    rosa_quick_unlock: OracleOfSeasonsRosaQuickUnlock

    # Miscellaneous options
    shop_prices: OraclesShopPrices
    enforce_potion_in_shop: OraclesEnforcePotionInShop
    required_rings: OraclesRequiredRings
    excluded_rings: OraclesExcludedRings
    fools_ore: OracleOfSeasonsFoolsOre
    cross_items: OraclesIncludeCrossItems
    combat_difficulty: OraclesCombatDifficulty
    bird_hint: OraclesBirdHint
    randomize_ai: OraclesRandomizeAi
    move_link: OraclesMoveLink

    start_inventory_from_pool: StartInventoryPool
    remove_items_from_pool: OraclesRemoveItemsFromPool


oos_option_groups = [
    OptionGroup("General", [
        ItemsAccessibility,
        OraclesGoal,
        OraclesLogicDifficulty,
        OracleOfSeasonsDeathLink,
    ]),
    OptionGroup("Items", [
        OraclesIncludeCrossItems,
    ]),
    OptionGroup("Optional Locations", [
        OraclesAdvanceShop,
        OraclesOldMenShuffle,
        OraclesBusinessScrubsShuffle,
        OracleOfSeasonsGoldenOreSpotsShuffle,
        OraclesGashaLocations,
        OraclesIncludeSecretLocations,
        OracleOfSeasonsLinkedHerosCave
    ]),
    OptionGroup("Essences", [
        OraclesRequiredEssences,
        OraclesEssenceSanity,
        OraclesPlacedEssences,
        OraclesExcludeDungeonsWithoutEssence,
        OraclesShowDungeonsWithMap,
        OraclesShowDungeonsWithEssence,
    ]),
    OptionGroup("Seasons", [
        OracleOfSeasonsDefaultSeasons,
        OracleOfSeasonsHoronSeason,
    ]),
    OptionGroup("Overworld Layout Options", [
        OraclesAnimalCompanion,
        OracleOfSeasonsPortalShuffle,
        OraclesDungeonShuffle,
        OracleOfSeasonsD0AltEntrance,
        OracleOfSeasonsD2AltEntrance,
        OraclesDefaultSeedType,
        OracleOfSeasonsDuplicateSeedTree,
    ]),
    OptionGroup("Dungeon Items", [
        OraclesMasterKeys,
        OraclesSmallKeyShuffle,
        OraclesBossKeyShuffle,
        OraclesMapCompassShuffle,
        OraclesStartingMapsCompasses
    ]),
    OptionGroup("Numeric Requirements", [
        OraclesOfSeasonsTreehouseOldManRequirement,
        OraclesOfSeasonsTarmGateRequirement,
        OraclesOfSeasonsGoldenBeastsRequirement,
        OracleOfSeasonsSignGuyRequirement,
        OraclesGashaNutKillRequirement,
    ]),
    OptionGroup("Randomizable Sequences", [
        OracleOfSeasonsLostWoodsItemSequence,
        OracleOfSeasonsLostWoodsMainSequence,
        OracleOfSeasonsSamasaGateCode,
        OracleOfSeasonsSamasaGateCodeLength,
    ]),
    OptionGroup("QOL", [
        OraclesQuickFlute,
        OracleOfSeasonsRosaQuickUnlock,
    ]),
    OptionGroup("Others", [
        OraclesShopPrices,
        OraclesEnforcePotionInShop,
        OraclesRequiredRings,
        OraclesExcludedRings,
        OracleOfSeasonsFoolsOre,
        OraclesCombatDifficulty,
        OraclesBirdHint,
        OraclesRandomizeAi,
        OraclesMoveLink,
        OraclesRemoveItemsFromPool
    ]),
]
