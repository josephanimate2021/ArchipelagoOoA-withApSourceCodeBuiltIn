from typing import Union

import settings
from .common.data.Constants import SEASONS_ROM_HASH, AGES_ROM_HASH
from .common.Settings import *


class OracleOfSeasonsSettings(settings.Group):
    class RomFile(settings.UserFilePath):
        """File name of the Oracle of Seasons US ROM"""
        copy_to = "Legend of Zelda, The - Oracle of Seasons (USA).gbc"
        description = "OoS ROM File"
        md5s = [SEASONS_ROM_HASH]

    class AgesRomFile(settings.UserFilePath):
        """File name of the Oracle of Ages US ROM (only needed for cross items)"""
        copy_to = "Legend of Zelda, The - Oracle of Ages (USA).gbc"
        description = "OoA ROM File"
        md5s = [AGES_ROM_HASH]

    class OoSRevealDiggingSpots(str):
        """
        If enabled, hidden digging spots in Subrosia are revealed as diggable tiles.
        """

    rom_file: RomFile = RomFile(RomFile.copy_to)
    ages_rom_file: AgesRomFile = AgesRomFile(AgesRomFile.copy_to)
    rom_start: bool = True
    character_sprite: Union[OraclesSettings.OoCharacterSprite, str] = "link"
    character_palette: Union[OraclesSettings.OoCharacterPalette, str] = "green"
    reveal_hidden_subrosia_digging_spots: Union[OoSRevealDiggingSpots, bool] = True
    heart_beep_interval: Union[OraclesSettings.OoHeartBeepInterval, str] = "vanilla"
    remove_music: Union[OraclesSettings.OoRemoveMusic, bool] = False