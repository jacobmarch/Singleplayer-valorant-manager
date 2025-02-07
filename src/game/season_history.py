"""
Manages the history of completed seasons.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Season:
    """Represents a completed season"""
    year: int
    champion: str
    champion_wins: int
    champion_losses: int
    team_name: str
    team_wins: int
    team_losses: int
    team_position: int

class SeasonHistory:
    def __init__(self):
        self.seasons: List[Season] = []
        self.current_year = 1

    def add_season(self, champion: str, champion_record: tuple[int, int], 
                  team_name: str, team_record: tuple[int, int], team_position: int) -> None:
        """
        Add a completed season to history
        
        Args:
            champion: Name of champion team
            champion_record: Tuple of (wins, losses) for champion
            team_name: Name of player's team
            team_record: Tuple of (wins, losses) for player's team
            team_position: Final position of player's team
        """
        season = Season(
            year=self.current_year,
            champion=champion,
            champion_wins=champion_record[0],
            champion_losses=champion_record[1],
            team_name=team_name,
            team_wins=team_record[0],
            team_losses=team_record[1],
            team_position=team_position
        )
        self.seasons.append(season)
        self.current_year += 1

    def get_season_history(self) -> List[Dict]:
        """Get list of season history for display"""
        return [
            {
                'number': s.year,
                'champion': s.champion,
                'champion_record': f"{s.champion_wins}-{s.champion_losses}",
                'team_position': s.team_position,
                'team_wins': s.team_wins,
                'team_losses': s.team_losses
            }
            for s in self.seasons
        ] 