"""
Contains game data structures for regions and teams.
"""

# Dictionary mapping regions to their teams
REGIONS = {
    "China": [
        "All Gamers",
        "Bilibili Gaming",
        "Dragon Ranger Gaming",
        "EDward Gaming",
        "FunPlus Phoenix",
        "JD Gaming",
        "Nova Esports",
        "Titan Esports Club",
        "Trace Esports",
        "TYLOO",
        "Wolves Esports",
        "XLG Esports"
    ],
    "Pacific": [
        "BOOM Esports",
        "DetonatioN FocusMe",
        "DRX",
        "Gen.G",
        "Global Esports",
        "Nongshim RedForce",
        "Paper Rex",
        "Rex Regum Qeon",
        "T1",
        "TALON",
        "Team Secret",
        "ZETA DIVISION"
    ],
    "Europe": [
        "Apeks",
        "BBL Esports",
        "Fnatic",
        "FUT Esports",
        "Gentle Mates",
        "GIANTX",
        "Karmine Corp",
        "KOI",
        "NAVI",
        "Team Heretics",
        "Team Liquid",
        "Team Vitality"
    ],
    "Americas": [
        "100 Thieves",
        "2G Esports",
        "Cloud9",
        "Evil Geniuses",
        "Furia Esports",
        "G2 Esports",
        "KRU Esports",
        "Leviatan",
        "LOUD",
        "MiBR",
        "NRG",
        "Sentinels"
    ]
}

# List of all regions for easy access
REGION_LIST = list(REGIONS.keys()) 