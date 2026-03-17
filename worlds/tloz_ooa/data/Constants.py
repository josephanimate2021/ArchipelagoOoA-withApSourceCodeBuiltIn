from ..common.data.Constants import *

OLD_MAN_RUPEE_VALUES = {
    "rolling ridge past old man": 200,
    "rolling ridge present old man": -200,
}

VALID_SEED_PRICE_VALUES = [
    1, 2, 5, 10, 20, 25, 30, 40, 50, 60, 70, 80, 99
]

RUPEE_OLD_MAN_LOCATIONS = [
    "Rolling Ridge (Present): Old Man",
    "Rolling Ridge (Past): Old Man"
]

SCRUB_LOCATIONS = [
    # "Spool Swamp: Business Scrub",
    # "Snake's Remains: Business Scrub",
    # "Dancing Dragon Dungeon (1F): Business Scrub",
    # "Samasa Desert: Business Scrub"
]

SECRETS = [
    # "Horon Village: Clock Shop Secret",
    # "Western Coast: Graveyard Secret",
    # "Subrosia: Subrosian Secret",
    # "Sunken City: Diver Secret",
    # "Subrosia: Smith Secret",
    # "Subrosia: Piratian Secret",
    # "Subrosia: Temple Secret",
    # "Natzu Region: Deku Secret",
    # "Goron Mountain: Biggoron Secret",
    "Lynna City: Mayor Secret"
]

TREES_TABLE = {
    "Lynna City": "Lynna City: Seed Tree",
    "Ambi's Palace": "Ambi's Palace: Seed Tree",
    "Deku Forest": "Deku Forest: Seed Tree",
    "Crescent Island": "Crescent Island: Seed Tree",
    "Symmetry city": "Symmetry city: Seed Tree",
    "Rolling Ridge West": "Rolling Ridge West: Seed Tree",
    "Rolling Ridge East": "Rolling Ridge East: Seed Tree",
    "Zora Village": "Zora Village: Seed Tree",
}


DUNGEON_NAMES = [
    "Maku Path",
    "Spirit's Grave",
    "Wing Dungeon",
    "Moonlit Grotto",
    "Skull Dungeon",
    "Crown Dungeon",
    "Mermaid's Cave Present",
    "Jabu-Jabu's Belly",
    "Ancient Tomb",
    "Mermaid's Cave Past",
    "",
    "Hero's Cave"
]

DUNGEON_ENTRANCES = {
    "d0 entrance": "enter d0",
    "d1 entrance": "enter d1",
    "d2 past entrance": "enter d2",
    "ambi's palace entrance": "enter ambi's palace",
    "d3 entrance": "enter d3",
    "d4 entrance": "enter d4",
    "d5 entrance": "enter d5",
    "d6 past entrance": "enter d6 past",
    "d6 present entrance": "enter d6 present",
    "d7 entrance": "enter d7",
    "d8 entrance": "enter d8",
}

VANILLA_SHOP_PRICES = {
    "lynnaShop1": 20,
    "lynnaShop2": 30,
    "lynnaShop3": 150,
    "hiddenShop1": 300,
    "hiddenShop2": 300,
    "hiddenShop3": 200,
    "advanceShop1": 100,
    "advanceShop2": 100,
    "advanceShop3": 100,
    "syrupShop1": 100,
    "syrupShop2": 300,
    "syrupShop3": 300,
    "tokayMarket1": 10,
    "tokayMarket2": 10,
    # "spoolSwampScrub": 100,
    # "samasaCaveScrub": 100,
    # "d2Scrub": 30,
    # "d4Scrub": 20,
}

ITEM_GROUPS = {
    "Small Keys": [
        "Small Key (Maku Path)",
        "Small Key (Spirit's Grave)",
        "Small Key (Wing Dungeon)",
        "Small Key (Moonlit Grotto)",
        "Small Key (Skull Dungeon)",
        "Small Key (Crown Dungeon)",
        "Small Key (Mermaid's Cave Present)",
        "Small Key (Jabu-Jabu's Belly)",
        "Small Key (Ancient Tomb)",
        "Small Key (Mermaid's Cave Past)",
        "Small Key (Hero's Cave)"
    ],
    "Boss Keys": [
        "Boss Key (Spirit's Grave)",
        "Boss Key (Wing Dungeon)",
        "Boss Key (Moonlit Grotto)",
        "Boss Key (Skull Dungeon)",
        "Boss Key (Crown Dungeon)",
        "Boss Key (Mermaid's Cave)",
        "Boss Key (Jabu-Jabu's Belly)",
        "Boss Key (Ancient Tomb)",
    ],
    "Compasses": [
        "Compass (Spirit's Grave)",
        "Compass (Wing Dungeon)",
        "Compass (Moonlit Grotto)",
        "Compass (Skull Dungeon)",
        "Compass (Crown Dungeon)",
        "Compass (Mermaid's Cave Present)",
        "Compass (Jabu-Jabu's Belly)",
        "Compass (Ancient Tomb)",
        "Compass (Mermaid's Cave Past)",
    ],
    "Dungeon Maps": [
        "Dungeon Map (Spirit's Grave)",
        "Dungeon Map (Wing Dungeon)",
        "Dungeon Map (Moonlit Grotto)",
        "Dungeon Map (Skull Dungeon)",
        "Dungeon Map (Crown Dungeon)",
        "Dungeon Map (Mermaid's Cave Present)"
        "Dungeon Map (Jabu-Jabu's Belly)",
        "Dungeon Map (Ancient Tomb)",
        "Dungeon Map (Mermaid's Cave Past)",
    ],
    "Master Keys": [
        "Master Key (Maku Path)",
        "Master Key (Spirit's Grave)",
        "Master Key (Wing Dungeon)",
        "Master Key (Moonlit Grotto)",
        "Master Key (Skull Dungeon)",
        "Master Key (Crown Dungeon)",
        "Master Key (Mermaid's Cave Present)",
        "Master Key (Jabu-Jabu's Belly)",
        "Master Key (Ancient Tomb)",
        "Master Key (Mermaid's Cave Past)",
        "Master Key (Hero's Cave)"
    ],
    "Essences": [
        "Eternal Spirit",
        "Ancient Wood",
        "Echoing Howl",
        "Burning Flame",
        "Sacred Soil",
        "Lonely Peak",
        "Rolling Sea",
        "Falling Star",
    ]
}

LOCATION_GROUPS = {
    'D0': [
        "Maku Path: Key Chest",
        "Maku Path: Basement",
    ],
    'D1': [
        "Spirit's Grave: One-Button Chest",
        "Spirit's Grave: Two-Buttons Chest",
        "Spirit's Grave: Wide Room",
        "Spirit's Grave: Crystal Room",
        "Spirit's Grave: Crossroad",
        "Spirit's Grave: West Terrace",
        "Spirit's Grave: Pot Chest",
        "Spirit's Grave: East Terrace",
        "Spirit's Grave: Ghini Drop",
        "Spirit's Grave: Basement",
        "Spirit's Grave: Boss",
    ],
    'D2': [
        "Wing Dungeon (1F): Color Room",
        "Wing Dungeon (1F): Bombed Terrace",
        "Wing Dungeon (1F): Moblin Platform",
        "Wing Dungeon (1F): Rope Room",
        "Wing Dungeon (1F): Ladder Chest",
        "Wing Dungeon (1F): Moblin Drop",
        "Wing Dungeon (1F): Statue Puzzle",
        "Wing Dungeon (B1F): Thwomp Shelf",
        "Wing Dungeon (B1F): Thwomp Tunnel",
        "Wing Dungeon (B1F): Basement Chest",
        "Wing Dungeon (B1F): Basement Drop",
        "Wing Dungeon (1F): Boss",
    ],
    'D3': [
        "Moonlit Grotto (1F): Bridge Chest",
        "Moonlit Grotto (1F): Mimic Room",
        "Moonlit Grotto (1F): Bush Beetle Room",
        "Moonlit Grotto (1F): Crossroad",
        "Moonlit Grotto (1F): Pols Voice Chest",
        "Moonlit Grotto (1F): Armos Drop",
        "Moonlit Grotto (1F): Statue Drop",
        "Moonlit Grotto (1F): Six-Blocs Drop",
        "Moonlit Grotto (B1F): Moldorm Drop",
        "Moonlit Grotto (B1F): East",
        "Moonlit Grotto (B1F): Torch Chest",
        "Moonlit Grotto (B1F): Conveyor Belt Room",
        "Moonlit Grotto (B1F): Boss",
    ],
    'D4': [
        'Skull Dungeon (1F): Second Crystal Switch',
        'Skull Dungeon (1F): Lava Pot Chest',
        'Skull Dungeon (1F): Small Floor Puzzle',
        'Skull Dungeon (1F): First Chest',
        'Skull Dungeon (1F): Minecart Chest',
        'Skull Dungeon (1F): Cube Chest',
        'Skull Dungeon (1F): First Crystal Switch',
        'Skull Dungeon (1F): Color Tile Drop',
        'Skull Dungeon (B1F): Large Floor Puzzle',
        'Skull Dungeon (B1F): Boss',
    ],
    'D5': [
        "Crown Dungeon (1F): Diamond Chest",
        "Crown Dungeon (1F): Eyes Chest",
        "Crown Dungeon (1F): Three-Statue Puzzle",
        "Crown Dungeon (1F): Blue Peg Chest",
        "Crown Dungeon (B1F): Like-Like Chest",
        "Crown Dungeon (B1F): Red Peg Chest",
        "Crown Dungeon (B1F): Owl Puzzle",
        "Crown Dungeon (B1F): Two-Statue Puzzle",
        "Crown Dungeon (B1F): Dark Room",
        "Crown Dungeon (B1F): Six-Statue Puzzle",
        "Crown Dungeon (1F): Boss",
    ],
    'D6 Present': [
        "Mermaid's Cave (Present): Vire Chest",
        "Mermaid's Cave (Present): Spinner Chest",
        "Mermaid's Cave (Present): Rope Chest",
        "Mermaid's Cave (Present): RNG Chest",
        "Mermaid's Cave (Present): Diamond Chest",
        "Mermaid's Cave (Present): Beamos Chest",
        "Mermaid's Cave (Present): Cube Chest",
        "Mermaid's Cave (Present): Channel Chest",
    ],
    'D6 Past': [
        "Mermaid's Cave (Past) (1F): Stalfos Chest",
        "Mermaid's Cave (Past) (1F): Color Room",
        "Mermaid's Cave (Past) (1F): Pool Chest",
        "Mermaid's Cave (Past) (1F): Wizzrobe",
        "Mermaid's Cave (Past) (B1F): Diamond Chest",
        "Mermaid's Cave (Past) (B1F): Spear Chest",
        "Mermaid's Cave (Past) (B1F): Rope Chest",
        "Mermaid's Cave (Past) (1F): Boss",
    ],
    'D7': [
        "Jabu-Jabu's Belly (1F): Island Chest",
        "Jabu-Jabu's Belly (1F): Stairway Chest",
        "Jabu-Jabu's Belly (1F): Miniboss Chest",
        "Jabu-Jabu's Belly (1F): Cane/Diamond Puzzle",
        "Jabu-Jabu's Belly (1F): Boxed Chest",
        "Jabu-Jabu's Belly (1F): Flower Room",
        "Jabu-Jabu's Belly (1F): Diamond Puzzle",
        "Jabu-Jabu's Belly (1F): Crab Chest",
        "Jabu-Jabu's Belly (2F): Left Wing",
        "Jabu-Jabu's Belly (2F): Right Wing",
        "Jabu-Jabu's Belly (2F): Spike Chest",
        "Jabu-Jabu's Belly (3F): Hallway Chest",
        "Jabu-Jabu's Belly (3F): Post-Hallway Chest",
        "Jabu-Jabu's Belly (3F): Terrace",
        "Jabu-Jabu's Belly (2F): Boss",
    ],
    'D8': [
        'Ancient Tomb (1F): Single Chest',
        'Ancient Tomb (B2F): Maze Chest',
        'Ancient Tomb (B2F): NW Slate Chest',
        'Ancient Tomb (B2F): NE Slate Chest',
        'Ancient Tomb (B2F): Ghini Chest',
        'Ancient Tomb (B2F): SE Slate Chest',
        'Ancient Tomb (B2F): SW Slate Chest',
        'Ancient Tomb (B1F): NW Chest',
        'Ancient Tomb (1F): Sarcophagus Chest',
        'Ancient Tomb (B1F): Blade Trap',
        'Ancient Tomb (B1F): Blue Peg Chest',
        'Ancient Tomb (B1F): Floor Puzzle',
        'Ancient Tomb (B2F): Tile Room',
        'Ancient Tomb (1F): Stalfos',
        'Ancient Tomb (B3F): Single Chest',
        'Ancient Tomb (B3F): Boss',
    ],
    'Trade Sequence': [
        'Yoll Graveyard: Graveyard Poe',
        'Lynna Village: Postman',
        'Lynna Village: Toilet Hand',
        'Crescent Island: Tokay Chef',
        'Nuun: Happy Mask Salesman',
        'Lynna Village: Mamamu Yan',
        'Symmetry City: Middle man',
        'Lynna City: Comedian',
        'Lynna Village: Sad boi',
        'Maple Trade',
        'Lynna Village Coast: Rafton',
        'Shore of No Return: Old Zora',
        'Restoration Wall: Patch',
    ],
    'D11': [
        "Hero's Cave (1F): Pots Puzzle",
        "Hero's Cave (1F): Statue Puzzle #1",
        "Hero's Cave (1F): Bridge Puzzle #1",
        "Hero's Cave (1F): Shoot Eyes",
        "Hero's Cave (1F): Statue Puzzle #2",
        "Hero's Cave (1F): Pots Puzzle #2",
        "Hero's Cave (1F): Statue Puzzle #3",
        "Hero's Cave (1F): Bridge Puzzle #2",
        "Hero's Cave (1F): Color Room",
        "Hero's Cave (1F): Water Puzzle",
        "Hero's Cave (B1F): Water Puzzle",
        "Hero's Cave (B1F): Basement",
        "Hero's Cave (1F): Final Puzzle",
        "Hero's Cave (1F): Completion Reward"
    ]
}

GASHA_SPOT_REGIONS = [
    "crescent past spot",
    "talus lake past spot",
    "talus peak past spot",
    "zora village past spot",
    "lynna village toilet spot",
    "south shore past spot",
    "ridge west base spot",
    "ridge upper past spot",
    "yoll graveyard spot",
    "talus peak present spot",
    "fairies woods spot",
    "nuun highlands spot",
    "ridge mid present spot",
    "crescent present islet spot",
    "crescent present vine spot",
    "sea of storms spot",
]

COLLECT_MAKU_TREE = 0x80
COLLECT_TARGET_CART = 0x81
COLLECT_BIGBANG = 0x82
COLLECT_GORON_BUSH_ROOM = 0x83