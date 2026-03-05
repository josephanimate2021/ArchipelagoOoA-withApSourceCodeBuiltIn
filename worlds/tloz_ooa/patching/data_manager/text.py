import json
from pathlib import Path

from typing import Any

import Utils
from ...common.patching.RomData import RomData
from ...common.patching.data_manager.text import get_text_data
from ...common.patching.text import normalize_text


def load_modded_ages_text_data() -> None | tuple[dict[str, str], dict[str, str]]:
    from ... import OracleOfAgesWorld
    text_dir = Path(Utils.cache_path("oos_ooa/text"))
    dict_file = text_dir.joinpath(f"ages_dict.json")
    if not dict_file.is_file():
        return None

    text_file = text_dir.joinpath(f"ages_texts.json")
    if text_file.is_file():
        texts: dict[str, Any] = json.load(open(text_file, encoding="utf-8"))
        version = texts.pop("version")
        if version == OracleOfAgesWorld.version():
            return json.load(open(dict_file, encoding="utf-8")), texts

    vanilla_text_file = text_dir.joinpath(f"ages_texts_vanilla.json")
    if not vanilla_text_file.is_file():
        return None
    texts = json.load(open(vanilla_text_file, encoding="utf-8"))
    apply_text_edits(texts)
    save_ages_edited_text_data(texts)
    return json.load(open(dict_file, encoding="utf-8")), texts


def save_ages_edited_text_data(texts: dict[str, str]) -> None:
    from ... import OracleOfAgesWorld
    texts["version"] = OracleOfAgesWorld.version()

    text_dir = Path(Utils.cache_path("oos_ooa/text"))
    text_file = text_dir.joinpath(f"ages_texts.json")

    with text_file.open("w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False)

    del texts["version"]


def apply_text_edits(texts: dict[str, str]) -> None:
    # New items
    # Replace ring box 1
    texts["TX_0034"] = ("You got 🟥Ember\n"
                        "Seeds⬜! Open\n"
                        "your 🟥Seed\n"
                        "Satchel⬜ to use\n"
                        "them.")
    # Replace ring box 1 unused text
    texts["TX_0057"] = ("You found an\n"
                        "item for another\n"
                        "world!")

    # Appraisal text
    texts["TX_301c"] = ("You got the\n"
                        "\\call(fd)!")

    # Cross items
    # Obtain text
    texts["TX_003b"] = ""  # Strange flute
    texts["TX_0051"] = ""  # Warrior child heart
    texts["TX_0053"] = ""  # Warrior child heart refill
    texts["TX_0054"] = ""  # Unappraised ring
    # Inventory text
    texts["TX_091d"] = ""  # Replaces ring box 1
    texts["TX_091e"] = ""  # Replaces ring box 2
    texts["TX_0917"] = ""  # Replaces unappraised ring
    texts["TX_092e"] = ""  # Replaces strange flute

    # Replace the shield selling part of dekus which will never be used
    texts["TX_450a"] = ("\\sfx(c6)Greetings!\n"
                        "I can refill\n"
                        "your bag for\n"
                        "🟩30 Rupees⬜ only.\n"
                        "  \\optOK \\optNo thanks")

    # Impa refills
    texts["TX_0122"] = ("Come see me if\n"
                        "you need a\n"
                        "refill!")

    texts["TX_020b"] = "Linked Hero's Cave"

    # FAQ room
    texts["TX_4d00"] = ("Welcome to the\n"
                        "OoA randomizer\n"
                        "for Archipelago!\n"
                        "Did you read\n"
                        "the FAQ?\n"
                        "  \\optYes \\optNo")
    texts["TX_4d01"] = ("Reading the FAQ\n"
                        "is important, as\n"
                        "rando mechanics\n"
                        "are in it.\n"
                        "Please read it\n"
                        "\\optOk \\optWhere?")
    texts["TX_4d02"] = ("It is linked\n"
                        "in the setup.\n"
                        "If you don't\n"
                        "have it, check\n"
                        "tinyurl.com\n"
                        "/2yfdvhk5\n")
    texts["TX_4d03"] = ("How do you\n"
                        "refill your\n"
                        "satchel and\n"
                        "shield?\n"
                        "\\optShop \\optImpa")
    texts["TX_4d04"] = ("Wrong. Please\n"
                        "check the FAQ,\n"
                        "you will get\n"
                        "stuck otherwise.")
    texts["TX_4d05"] = ("Right! You can\n"
                        "get out of\n"
                        "here by warping\n"
                        "to the start")
    texts["TX_4d06"] = ("Just warp to\n"
                        "start, you\n"
                        "can do it\n"
                        "everywhere")


def apply_seasons_edits(ages_texts: dict[str, str], seasons_rom: RomData) -> None:
    _, ages_texts = get_text_data(seasons_rom, False, False)
    # Cross items
    # Obtain text
    ages_texts["TX_0053"] = ages_texts["TX_0073"]  # Cane
    ages_texts["TX_003b"] = ages_texts["TX_0030"]  # Hook 1
    ages_texts["TX_0051"] = ages_texts["TX_0028"]  # Hook 2
    ages_texts["TX_0054"] = ages_texts["TX_002e"]  # Shooter
    # Inventory text
    ages_texts["TX_091d"] = ages_texts["TX_093c"]  # Cane
    ages_texts["TX_091e"] = ages_texts["TX_093d"]  # Hook 1
    ages_texts["TX_0917"] = ages_texts["TX_093e"]  # Hook 2
    ages_texts["TX_092e"] = ages_texts["TX_0940"]  # Shooter
    save_ages_edited_text_data(ages_texts)


def get_modded_ages_text_data(rom_data: RomData) -> tuple[dict[str, str], dict[str, str]]:
    result = load_modded_ages_text_data()
    if result is not None:
        return result

    dictionary, texts = get_text_data(rom_data, True, True)
    apply_text_edits(texts)
    save_ages_edited_text_data(texts)
    return dictionary, texts
