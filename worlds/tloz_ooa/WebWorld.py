
from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld
from .Options import *

class OracleOfAgesWeb(WebWorld):
    theme = "grass"
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Oracle of Ages for Archipelago on your computer.",
        "English",
        "ooa_setup_en.md",
        "ooa_setup/en",
        ["SenPierre", "josephanimate2021"]
    )
    tutorials = [setup_en]
    option_groups = ooa_option_groups