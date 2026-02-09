import dataclasses
from typing import Any, override

from BaseClasses import CollectionState
from Options import Option, Accessibility
from rule_builder.options import OptionFilter
from rule_builder.rules import Rule, HasFromList, HasGroup, HasAll, False_, True_, Has
from worlds.tloz_oos import OracleOfSeasonsWorld
from worlds.tloz_oos.Options import OracleOfSeasonsGoldenOreSpotsShuffle
from worlds.tloz_oos.data.Constants import SEASON_CHAOTIC, SEASON_ITEMS, MARKET_LOCATIONS


@dataclasses.dataclass
class Season(Rule[OracleOfSeasonsWorld], OracleOfSeasonsWorld.game):
    area_name: str
    season: int

    @override
    def _instantiate(self, world: OracleOfSeasonsWorld) -> Rule.Resolved:
        if world.default_seasons[self.area_name] == self.season:
            return True_().resolve(world)
        else:
            return False_().resolve(world)


class HasGroupOption(HasGroup):
    option_name: str

    def __init__(self, item_name: str, option_name: str):
        self.option_name = option_name
        super().__init__(item_name)

    def _instantiate(self, world: OracleOfSeasonsWorld) -> Rule.Resolved:
        self.count = getattr(world.options, self.option_name).value
        super()._instantiate(world)


class HasFromListOption(HasFromList):
    option_name: str

    def __init__(self, *item_names: str, option_name: str):
        self.option_name = option_name
        super().__init__(item_names)

    def _instantiate(self, world: OracleOfSeasonsWorld) -> Rule.Resolved:
        self.count = getattr(world.options, self.option_name).value
        super()._instantiate(world)


@dataclasses.dataclass
class LostWoods(HasAll):
    is_main_sequence: bool
    allow_default: bool

    def _instantiate(self, world: OracleOfSeasonsWorld) -> Rule.Resolved:
        if self.is_main_sequence:
            sequence = world.lost_woods_main_sequence
        else:
            sequence = world.lost_woods_item_sequence

        if self.allow_default:
            current_season = world.default_seasons["LOST_WOODS"]
        else:
            current_season = SEASON_CHAOTIC

        needed_seasons = set()
        for season in sequence:
            if season != current_season:
                current_season = SEASON_CHAOTIC
                needed_seasons.add(SEASON_ITEMS[season])

        self.item_names = tuple(needed_seasons)
        super()._instantiate(world)


@dataclasses.dataclass
class CanReachNumRegions(Rule[OracleOfSeasonsWorld], game=OracleOfSeasonsWorld.game):
    """A rule that checks if the given region is reachable by the current player"""

    region_names: list[str]
    """The name of the regions to test access to"""

    region_need: int
    """The number of regions that need to be reached"""

    @override
    def _instantiate(self, world: OracleOfSeasonsWorld) -> Rule.Resolved:
        if self.region_need == 0:
            return True_().resolve(world)
        return self.Resolved(
            self.region_names,
            self.region_need,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    @override
    def __str__(self) -> str:
        options = f", options={self.options}" if self.options else ""
        return f"{self.__class__.__name__}({self.region_names}{options})"

    class Resolved(Rule.Resolved):
        region_names: list[str]
        region_need: int

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            reachables = 0
            for region_name in self.region_names:
                if state.can_reach_region(region_name, self.player):
                    reachables += 1
                    if reachables >= self.region_need:
                        return True
            return False

        @override
        def region_dependencies(self) -> dict[str, set[int]]:
            return {
                region_name: {id(self)} for region_name in self.region_names
            }


@dataclasses.dataclass
class HasRupeesForShop(Rule[OracleOfSeasonsWorld], game=OracleOfSeasonsWorld.game):
    shop_name: str

    @override
    def _instantiate(self, world: OracleOfSeasonsWorld) -> Rule.Resolved:
        amount = world.shop_rupee_requirements.get(self.shop_name, 0)
        if amount == 0:
            return True_().resolve(world)
        from worlds.tloz_oos.data.logic.LogicPredicates import oos_can_farm_rupees
        return (oos_can_farm_rupees() & Has("Rupees", amount / 2)).resolve(world)


class HasOresForShop(Rule[OracleOfSeasonsWorld], game=OracleOfSeasonsWorld.game):
    @override
    def _instantiate(self, world: OracleOfSeasonsWorld) -> Rule.Resolved:
        amount = sum([world.shop_prices[loc] for loc in MARKET_LOCATIONS])
        if amount == 0:
            return True_().resolve(world)
        from worlds.tloz_oos.data.logic.LogicPredicates import oos_can_farm_ore_chunks
        if world.options.shuffle_golden_ore_spots == OracleOfSeasonsGoldenOreSpotsShuffle.option_false:
            return oos_can_farm_ore_chunks().resolve(world)
        return (oos_can_farm_ore_chunks() & Has("Ore Chunks", amount / 2)).resolve(world)


@dataclasses.dataclass
class ItemInLocation(Rule[OracleOfSeasonsWorld], game=OracleOfSeasonsWorld.game):
    location: str
    item_name: str

    @override
    def _instantiate(self, world: OracleOfSeasonsWorld) -> Rule.Resolved:
        if world.options.accessibility == Accessibility.option_full:
            return False_().resolve(world)
        return self.Resolved(
            self.location,
            self.item_name,
            player=world.player
        )

    class Resolved(Rule.Resolved):
        location: str
        item_name: str

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            location = state.multiworld.get_location(self.location, self.player)
            return


def from_bool(condition: bool) -> Rule:
    return True_() if condition else False_()


def from_option(option: Option, value: Any, operator: str = "eq") -> Rule:
    return True_(options=[OptionFilter(option, value, operator)])
