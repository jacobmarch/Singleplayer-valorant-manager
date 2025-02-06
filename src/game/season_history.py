from dataclasses import dataclass, field
from typing import List, Dict, Optional
import logging

@dataclass
class SeasonRecord:
    """Represents a single season's record"""
    year: int
    region: str
    champion: str
    champion_record: tuple[int, int]  # (wins, losses)
    player_team: str
    player_record: tuple[int, int]  # (wins, losses)
    player_position: int  # Final position in standings

@dataclass
class SeasonHistory:
    """Manages the history of all seasons played"""
    seasons: List[SeasonRecord] = field(default_factory=list)
    current_year: int = 2024  # Start with current year
    
    def add_season(self, region: str, champion: str, champion_record: tuple[int, int],
                  player_team: str, player_record: tuple[int, int], player_position: int) -> None:
        """
        Add a completed season to the history
        
        Args:
            region: The region the season was played in
            champion: The team that won the championship
            champion_record: Tuple of (wins, losses) for the champion
            player_team: The team controlled by the player
            player_record: Tuple of (wins, losses) for the player's team
            player_position: The final position the player's team finished in
        """
        season = SeasonRecord(
            year=self.current_year,
            region=region,
            champion=champion,
            champion_record=champion_record,
            player_team=player_team,
            player_record=player_record,
            player_position=player_position
        )
        self.seasons.append(season)
        self.current_year += 1
        logging.info(f'Added season {self.current_year-1} to history: {champion} won championship')
        
    def get_season_history(self) -> List[SeasonRecord]:
        """Get all seasons in chronological order"""
        return sorted(self.seasons, key=lambda x: x.year) 