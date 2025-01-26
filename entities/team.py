from .player import Player
from .coach import Coach

class Team:
    def __init__(
        self,
        name: str,
        players: list[Player],
        coach: Coach,
        region: str,
        fans: int,
    ):
        self.name = name
        self.players = players
        self.coach = coach
        self.region = region
        self.fans = fans
