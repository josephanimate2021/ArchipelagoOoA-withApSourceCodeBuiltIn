from worlds.AutoWorld import WebWorld, World
from BaseClasses import Tutorial

class OracleOfAgesWeb(WebWorld):
    theme = "grass"
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Oracle of Ages for Archipelago on your computer.",
        "English",
        "ooa_setup_en.md",
        "ooa_setup/en",
        ["SenPierre"]
    )]