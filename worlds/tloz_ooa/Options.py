from dataclasses import dataclass

from Options import Choice, DeathLink, DefaultOnToggle, PerGameCommonOptions, Range, Toggle, StartInventoryPool, OptionDict, OptionSet, OptionError, ItemsAccessibility

from .data.Constants import *
from .common.Options import *


class OracleOfAgesMinibossLocations(Toggle):
    """
    When enabled, each time you defeat a miniboss inside a dungeon, 
    a chest will appear in the miniboss room where if you open it, a randomized item will be inside.
    This is an option requested by Run_In_A_Week on discord over at the Archipelago Server.
    """
    display_name = "Miniboss Locations"

    include_in_patch = True
    include_in_slot_data = True

class OracleOfAgesWarpToStartLocation(Choice):
    """
    This option changes the spot you warp in when you press select or start, A, and B buttons to warp back to the forest of time.
    Please note that depending on the option you select, logic will be affected.
    """
    display_name = "Warp to Start Location"

    option_near_timeportal = 0
    option_near_triforce_stone = 1

    default = 1

    include_in_patch = True
    include_in_slot_data = True

class OracleOfAgesLynnaGardener(Toggle):
    """
    When enabled, a friendly gardener will have trimmed the bushes outside of Lynna City and cleared the path
    so you don't have to! This will expand the sphere 0 checks to include everything past the bushes that you
    normally would need nothing for.
    """
    display_name = "Lynna Gardener"
    
    include_in_patch = True
    include_in_slot_data = True

class OracleOfAgesRequiredSlates(Range):
    """
    The amount of slate that need to be obtained in order to get to the boss of the eigth dungeons.
    """
    display_name = "Required Slates"
    range_start = 0
    range_end = 4
    default = 4

    include_in_patch = True
    include_in_slot_data = True

class OracleOfAgesLinkedHerosCave(Choice):
    """
    When enabled, en entrance to linked hero's cave will be placed anywhere you specify.
    - Maku Tree Entrance (Right Side): an entrance is placed near the cave on the left that leads to Maku Road.
    - D2 Present: an entrance will be initialized and placed inside the cave that would've collapsed when you pick up a rock that blocks the way.
    - Zora's Domain: An unused warp will be taken advantage of to place hero's cave inside it.
    - Seawater Cure Room Present: A cave that takes you to a fairy room full of nothing will be occupied by Hero's Cave.
    """
    display_name = "Linked Hero's Cave"

    option_disabled = 0
    option_maku_tree_entrance_right_side = 1
    option_d2_present = 2
    option_zoras_domain = 3
    option_seawater_cure_room_present = 4

    default = 0

    include_in_patch = True
    include_in_slot_data = True


class OracleOfAgesDuplicateSeedTrees(OptionSet):
    """
    The game contains 10 seed trees (8 of which has valid choices), but only 5 types of seeds. This means that some types of seeds can appear on
    multiple trees. This setting lets you choose seed trees that will be guaranteed to not hold a unique type of
    seed. You can choose up to 3.
    Regardless of what you choose, each seed type will appear on at most 2 trees.
    Valid choices are:
    - Lynna City
    - Ambi's Palace
    - Deku Forest
    - Symmetry City
    - Crescent Island
    - Rolling Ridge West
    - Rolling Ridge East
    - Zora Village
    """
    display_name = "Duplicate Seed Trees"
    default = {"Crescent Island", "Zora Village", "Rolling Ridge East"}
    valid_keys = {key for key in TREES_TABLE.keys()}

    include_in_patch = True
    include_in_slot_data = True

class OracleOfAgesEntrancePlando(OptionDict):
    """
    This option allows you to plan out which entrances are or are not randomized for the game. 
    For example, you can make the d4 entrance lead to d0 even though the dungeon shuffler never wanted that. It's all in your imagination.
    Please note that right now this option only works on dungeons because ER is not implemented yet. This option may also not work when shuffle_dungeons is on.
    """
    display_name = "Entrance Plando"
    default = DUNGEON_ENTRANCES.copy()

    verify_item_name = False

    include_in_patch = True
    include_in_slot_data = True


class OracleOfAgesSlateShuffle(Toggle):
    """
    If enabled, Slates can be found anywhere instead of being confined in Dungeon 8.
    """
    display_name = "Slates Outside Dungeon 8"

    include_in_patch = True
    include_in_slot_data = True

@dataclass
class OracleOfAgesOptions(PerGameCommonOptions):
    accessibility: ItemsAccessibility
    start_inventory_from_pool: StartInventoryPool
    entrance_plando: OracleOfAgesEntrancePlando
    # remove_items_from_pool: OraclesRemoveItemsFromPool
    # cross_items: OraclesIncludeCrossItems
    miniboss_locations: OracleOfAgesMinibossLocations
    lynna_gardener: OracleOfAgesLynnaGardener
    quick_flute: OraclesQuickFlute
    # bird_hints: OraclesBirdHint
    deterministic_gasha_locations: OraclesGashaLocations
    gasha_nut_kill_requirement: OraclesGashaNutKillRequirement
    goal: OraclesGoal
    linked_heros_cave: OracleOfAgesLinkedHerosCave
    shuffle_old_men: OraclesOldMenShuffle
    secret_locations: OraclesIncludeSecretLocations
    logic_difficulty: OraclesLogicDifficulty
    required_essences: OraclesRequiredEssences
    placed_essences: OraclesPlacedEssences
    shuffle_essences: OraclesEssenceSanity
    warp_to_start_location: OracleOfAgesWarpToStartLocation
    exclude_dungeons_without_essence: OraclesExcludeDungeonsWithoutEssence
    show_dungeons_with_map: OraclesShowDungeonsWithMap
    show_dungeons_with_essence: OraclesShowDungeonsWithEssence
    required_slates: OracleOfAgesRequiredSlates
    animal_companion: OraclesAnimalCompanion
    default_seed: OraclesDefaultSeedType
    duplicate_seed_trees: OracleOfAgesDuplicateSeedTrees
    enforce_potion_in_shop: OraclesEnforcePotionInShop
    shuffle_dungeons: OraclesDungeonShuffle
    master_keys: OraclesMasterKeys
    keysanity_small_keys: OraclesSmallKeyShuffle
    keysanity_boss_keys: OraclesBossKeyShuffle
    keysanity_maps_compasses: OraclesMapCompassShuffle
    keysanity_slates: OracleOfAgesSlateShuffle
    required_rings: OraclesRequiredRings
    excluded_rings: OraclesExcludedRings
    shop_prices: OraclesShopPrices
    shuffle_business_scrubs: OraclesBusinessScrubsShuffle
    advance_shop: OraclesAdvanceShop
    combat_difficulty: OraclesCombatDifficulty
    death_link: DeathLink
    move_link: OraclesMoveLink
    # randomize_enemy_ai: OraclesRandomizeAi
