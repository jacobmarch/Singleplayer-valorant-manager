from .team import Team

class Coach:
    def __init__(
        self, 
        name: str, 
        team: Team
    ):
        self.name = name
        self.team = team