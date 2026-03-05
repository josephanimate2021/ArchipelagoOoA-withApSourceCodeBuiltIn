from typing import Union
import settings

from .common.patching.Constants import AGES_ROM_HASH
from .common.Settings import OraclesSettings


class OOASettings(settings.Group):
    class OOARomFile(settings.UserFilePath):
        """File path of the OOA US rom"""
        description = "Oracle of Ages (USA) ROM File"
        copy_to = "Legend of Zelda, The - Oracle of Ages (USA).gbc"
        md5s = [AGES_ROM_HASH]
    
    class OoAQolMermaidSuit(str):
        """
        Defines if you don't want to spam the buttons to swim with the mermaid suit.
        """

    class OoASkipTokkeyDance(str):
        """
        Defines if you want to skip the small dance that tokkay does
        """

    class OoASkipSadBoiJoke(str):
        """
        Defines if you want to skip the joke you tell to the sad boi
        """

    rom_file: OOARomFile = OOARomFile(OOARomFile.copy_to)
    heart_beep_interval: Union[OraclesSettings.OoHeartBeepInterval, str] = "vanilla"
    character_sprite: Union[OraclesSettings.OoCharacterSprite, str] = "link"
    character_palette: Union[OraclesSettings.OoCharacterPalette, str] = "green"
    qol_mermaid_suit: Union[OoAQolMermaidSuit, bool] = True
    skip_tokkey_dance: Union[OoASkipTokkeyDance, bool] = False
    skip_boi_joke: Union[OoASkipSadBoiJoke, bool] = False