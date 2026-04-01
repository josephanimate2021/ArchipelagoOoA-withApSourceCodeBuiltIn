from typing import Union
from .common.data.Constants import AGES_ROM_HASH

import settings

class OOASettings(settings.Group):
    class OOARomFile(settings.UserFilePath):
        """File path of the OOA US rom"""
        description = "Oracle of Ages (USA) ROM File"
        copy_to = "Legend of Zelda, The - Oracle of Ages (USA).gbc"
        md5s = [AGES_ROM_HASH]

    class OoACharacterSprite(str):
        """
        The name of the sprite file to use (from "data/sprites/oos_ooa/").
        Putting "link" as a value uses the default game sprite.
        Putting "random" as a value randomly picks a sprite from your sprites directory for each generated ROM.
        """
    class OoACharacterPalette(str):
        """
        The color palette used for character sprite throughout the game.
        Valid values are: "green", "red", "blue", "orange", and "random"
        """
    class OoAHeartBeepInterval(str):
        """
        A factor applied to the infamous heart beep sound interval.
        Valid values are: "vanilla", "half", "quarter", "disabled"
        """
    
    class OoAQolMermaidSuit(str):
        """
        Defines if you don't want to spam the buttons to swim with the mermaid suit.
        """
        
    class OoAQuickFlute(str):
        """
        When enabled, playing the flute and the harp will immobilize you during a very small amount of time compared to vanilla game.
        """

    class OoASkipTokkeyDance(str):
        """
        Defines if you want to skip the small dance that tokkay does
        """

    class OoASkipSadBoiJoke(str):
        """
        Defines if you want to skip the joke you tell to the sad boi
        """
    
    class OoADungeonPrecisionTextSimplification(str):
        """
        Defines if you want to simplify the text for a dungeon that appears when keysanity related settings are turned on.
        """

    class OoAIntroCinematicSkip(str):
        """
        Defines if you want to skip the intro cinematic scene that plays after the capcom screen is shown.
        """

    rom_file: OOARomFile = OOARomFile(OOARomFile.copy_to)
    heart_beep_interval: Union[OoAHeartBeepInterval, str] = "vanilla"
    character_sprite: Union[OoACharacterSprite, str] = "link"
    character_palette: Union[OoACharacterPalette, str] = "green"
    qol_mermaid_suit: Union[OoAQolMermaidSuit, bool] = True
    qol_quick_flute: Union[OoAQuickFlute, bool] = True
    skip_tokkey_dance: Union[OoASkipTokkeyDance, bool] = False
    skip_boi_joke: Union[OoASkipSadBoiJoke, bool] = False
    simplify_dungeon_precision_text: Union[OoADungeonPrecisionTextSimplification, bool] = True
    skip_intro_cinematic: Union[OoAIntroCinematicSkip, bool] = False