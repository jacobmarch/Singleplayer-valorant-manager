"""
Entities Package

This package contains the core domain entities for the sports management system.
Each entity represents a key business object in the system.

Available Entities:
- Team: Represents a sports team
- Player: Represents a player in a team
- Coach: Represents a team coach
- Contract: Represents contractual agreements

Usage:
    from entities import Team, Player, Coach
"""

# Import all entity classes to make them available at package level
from .team import Team
from .player import Player
from .coach import Coach

# Define what should be imported with 'from entities import *'
__all__ = ['Team', 'Player', 'Coach']
