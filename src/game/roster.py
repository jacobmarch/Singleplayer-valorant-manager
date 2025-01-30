"""
Manages team ratings and schedule generation for the league.
"""

import random
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from src.game.person import Player, Coach

@dataclass
class TeamRating:
    """Represents a team's rating and related data"""
    name: str
    rating: int
    wins: int = 0
    losses: int = 0

@dataclass
class Match:
    """Represents a scheduled match"""
    home_team: str
    away_team: str
    week: int
    completed: bool = False
    home_score: int = 0
    away_score: int = 0

class LeagueManager:
    def __init__(self, region: str, teams: List[str], player_team: str, players: Optional[List[Player]] = None, coach: Optional[Coach] = None):
        """
        Initialize the league manager with teams and generate ratings
        
        Args:
            region: The region this league is in
            teams: List of team names in the league
            player_team: The team controlled by the player
            players: Optional list of players for calculating user team rating
            coach: Optional coach for calculating user team rating
        """
        self.region = region
        self.player_team = player_team
        self.team_ratings: Dict[str, TeamRating] = {}
        self.schedule: List[Match] = []
        
        # Generate ratings for all teams
        self._generate_team_ratings(teams, players, coach)
        
    def _calculate_user_team_rating(self, players: List[Player], coach: Coach) -> int:
        """
        Calculate team rating based on players and coach ratings
        
        Args:
            players: List of team players
            coach: Team coach
            
        Returns:
            Team rating (0-100)
        """
        # Players contribute 80% of rating, coach contributes 20%
        player_avg = sum(p.skill_rating for p in players) / len(players)
        team_rating = int((player_avg * 0.8) + (coach.skill_rating * 0.2))
        return min(100, max(0, team_rating))
        
    def _generate_team_ratings(self, teams: List[str], players: Optional[List[Player]] = None, coach: Optional[Coach] = None) -> None:
        """
        Generate normally distributed ratings for all teams
        
        Args:
            teams: List of team names to generate ratings for
            players: Optional list of players for calculating user team rating
            coach: Optional coach for calculating user team rating
        """
        logging.info(f'Generating team ratings for {len(teams)} teams in {self.region}')
        
        for team in teams:
            if team == self.player_team and players and coach:
                # Calculate rating based on actual team members for user's team
                rating = self._calculate_user_team_rating(players, coach)
                logging.info(f'Calculated rating {rating} for user team based on roster')
            else:
                # Generate random rating for AI teams
                rating = min(100, max(0, int(random.gauss(mu=70, sigma=10))))
                
            self.team_ratings[team] = TeamRating(name=team, rating=rating)
            
        logging.info('Team ratings generated successfully')
            
    def generate_schedule(self, start_date: datetime = None) -> None:
        """
        Generate a round-robin schedule for all teams
        
        Args:
            start_date: Optional starting date (unused, kept for compatibility)
        """
        logging.info(f'Generating schedule for {self.region}')
        
        teams = list(self.team_ratings.keys())
        if len(teams) % 2:
            teams.append("BYE")  # Add bye team if odd number of teams
            
        n = len(teams)
        matches = []
        fixtures = []
        mid = n // 2
        
        # Generate round-robin schedule
        for i in range(n - 1):
            round = []
            for j in range(mid):
                team1 = teams[j]
                team2 = teams[n - 1 - j]
                if team1 != "BYE" and team2 != "BYE":
                    if i % 2 == 0:
                        round.append((team1, team2))
                    else:
                        round.append((team2, team1))
            fixtures.append(round)
            teams = [teams[0]] + [teams[-1]] + teams[1:-1]  # Rotate teams
            
        # Convert fixtures to matches with week numbers
        current_week = 1
        for round in fixtures:
            for home, away in round:
                match = Match(
                    home_team=home,
                    away_team=away,
                    week=current_week
                )
                matches.append(match)
            current_week += 1
            
        self.schedule = matches
        logging.info(f'Generated {len(matches)} matches for the season')
        
    def display_upcoming_matches(self, num_matches: int = 5) -> List[Match]:
        """
        Get the next few upcoming matches, ensuring one match per week is shown
        
        Args:
            num_matches: Number of upcoming matches to return
            
        Returns:
            List of upcoming matches, one per week
        """
        upcoming = [m for m in self.schedule if not m.completed]
        
        # Get one match per week, prioritizing matches with the player's team
        matches_by_week = {}
        for match in upcoming:
            if match.week not in matches_by_week:
                matches_by_week[match.week] = match
            elif (self.player_team in [match.home_team, match.away_team] and 
                  self.player_team not in [matches_by_week[match.week].home_team, matches_by_week[match.week].away_team]):
                # Replace existing match if this one has player's team
                matches_by_week[match.week] = match
                
        # Sort by week and return requested number of matches
        sorted_matches = sorted(matches_by_week.values(), key=lambda x: x.week)
        return sorted_matches[:num_matches] 