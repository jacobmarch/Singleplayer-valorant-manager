import random
from dataclasses import dataclass
from typing import List

@dataclass
class Person:
    first_name: str
    last_name: str
    skill_rating: int

    @classmethod
    def generate(cls, first_names: List[str], last_names: List[str]) -> 'Person':
        """Generate a person with random name and skill rating"""
        return cls(
            first_name=random.choice(first_names).lower().capitalize(),
            last_name=random.choice(last_names).lower().capitalize(),
            skill_rating=int(random.gauss(mu=50, sigma=15))
        )

@dataclass
class Player(Person):
    position: str

@dataclass
class Coach(Person):
    pass

def generate_team_members(first_names: List[str], last_names: List[str]) -> tuple[List[Player], Coach]:
    """
    Generate 5 players and 1 coach with random names and skill ratings
    
    Args:
        first_names: List of possible first names
        last_names: List of possible last names
    
    Returns:
        Tuple containing list of players and a coach
    """
    positions = ['Sentinel', 'Flex', 'Initiator', 'Controller', 'Duelist']
    
    players = []
    for position in positions:
        player = Player(
            first_name=random.choice(first_names).lower().capitalize(),
            last_name=random.choice(last_names).lower().capitalize(),
            skill_rating=int(random.gauss(mu=50, sigma=15)),
            position=position
        )
        players.append(player)
    
    coach = Coach.generate(first_names, last_names)
    
    return players, coach 