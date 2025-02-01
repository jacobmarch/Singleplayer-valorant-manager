"""
Manages team ratings and schedule generation for the league.
"""

import random
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from src.game.person import Player, Coach

@dataclass
class TeamRating:
    """Represents a team's rating and related data"""
    name: str
    rating: int
    wins: int = 0
    losses: int = 0
    playoff_seed: Optional[int] = None
    eliminated: bool = False

@dataclass
class Match:
    """Represents a scheduled match"""
    home_team: str
    away_team: str
    week: int
    completed: bool = False
    home_score: int = 0  # Number of maps won
    away_score: int = 0  # Number of maps won
    map_scores: List[tuple[int, int]] = None  # List of (home_rounds, away_rounds) for each map
    is_playoff: bool = False
    playoff_round: Optional[str] = None  # "quarterfinal", "semifinal", "final"
    maps_needed: int = 2  # Default for regular season and early playoffs
    
    def __post_init__(self):
        """Initialize map_scores if not provided"""
        if self.map_scores is None:
            self.map_scores = []
        if self.is_playoff and self.playoff_round == "final":
            self.maps_needed = 3  # Best of 5 for finals
            
    def get_winner(self) -> Optional[str]:
        """Returns the name of the winning team, or None if match not completed"""
        if not self.completed:
            return None
        return self.home_team if self.home_score > self.away_score else self.away_team
    
    def get_loser(self) -> Optional[str]:
        """Returns the name of the losing team, or None if match not completed"""
        if not self.completed:
            return None
        return self.away_team if self.home_score > self.away_score else self.home_team
    
    def get_map_score_display(self) -> str:
        """Returns a formatted string of map scores"""
        if not self.map_scores:
            return "Not Played"
        
        map_displays = []
        for i, (home_rounds, away_rounds) in enumerate(self.map_scores, 1):
            map_displays.append(f"Map {i}: {home_rounds}-{away_rounds}")
        return " | ".join(map_displays)

@dataclass
class Playoffs:
    """Manages playoff bracket and progression"""
    teams: List[TeamRating]
    current_round: str = "quarterfinal"  # "quarterfinal", "semifinal", "final"
    matches: List[Match] = field(default_factory=list)
    completed: bool = False
    champion: Optional[str] = None
    
    def generate_playoff_matches(self, week: int) -> List[Match]:
        """Generate matches for the current playoff round"""
        matches = []
        
        if self.current_round == "quarterfinal":
            # 1v8, 4v5, 2v7, 3v6 matchups
            # Sort teams by seed to ensure proper matchups
            sorted_teams = sorted(self.teams, key=lambda x: x.playoff_seed)
            matchups = [
                (sorted_teams[0], sorted_teams[7]),  # 1 vs 8
                (sorted_teams[3], sorted_teams[4]),  # 4 vs 5
                (sorted_teams[1], sorted_teams[6]),  # 2 vs 7
                (sorted_teams[2], sorted_teams[5])   # 3 vs 6
            ]
            
            for higher_seed, lower_seed in matchups:
                match = Match(
                    home_team=higher_seed.name,
                    away_team=lower_seed.name,
                    week=week,
                    is_playoff=True,
                    playoff_round=self.current_round
                )
                matches.append(match)
                
        elif self.current_round == "semifinal":
            # Get non-eliminated teams and sort by seed
            remaining = [t for t in self.teams if not t.eliminated]
            remaining.sort(key=lambda x: x.playoff_seed)
            
            # Create semifinal matchups (winners of 1v8/4v5 and 2v7/3v6)
            matchups = [
                (remaining[0], remaining[1]),
                (remaining[2], remaining[3])
            ]
            
            for higher_seed, lower_seed in matchups:
                match = Match(
                    home_team=higher_seed.name,
                    away_team=lower_seed.name,
                    week=week,
                    is_playoff=True,
                    playoff_round=self.current_round
                )
                matches.append(match)
                
        else:  # final
            # Get the two remaining teams
            finalists = [t for t in self.teams if not t.eliminated]
            finalists.sort(key=lambda x: x.playoff_seed)
            
            if len(finalists) == 2:
                match = Match(
                    home_team=finalists[0].name,
                    away_team=finalists[1].name,
                    week=week,
                    is_playoff=True,
                    playoff_round=self.current_round
                )
                matches.append(match)
        
        # Clear previous matches and add new ones
        self.matches = matches
        return matches
    
    def advance_round(self) -> None:
        """Advance to the next playoff round"""
        if self.current_round == "quarterfinal":
            self.current_round = "semifinal"
        elif self.current_round == "semifinal":
            self.current_round = "final"
        else:
            self.completed = True
            # Find champion from the final match
            final_match = next(m for m in self.matches if m.playoff_round == "final")
            self.champion = final_match.get_winner()

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
        self.playoffs: Optional[Playoffs] = None
        self.regular_season_complete = False
        
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
        
    def display_upcoming_matches(self) -> List[Match]:
        """
        Get all upcoming matches, ensuring one match per week is shown
        
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
                
        # Sort by week and return all matches
        return sorted(matches_by_week.values(), key=lambda x: x.week)

    def start_playoffs(self) -> None:
        """Initialize playoffs with top 8 teams"""
        if not self.regular_season_complete:
            return
            
        # Sort teams by wins (and rating for tiebreaker) to determine playoff seeds
        playoff_teams = sorted(
            self.team_ratings.values(),
            key=lambda x: (x.wins, x.rating),
            reverse=True
        )[:8]
        
        # Assign playoff seeds
        for seed, team in enumerate(playoff_teams, 1):
            team.playoff_seed = seed
            
        self.playoffs = Playoffs(teams=playoff_teams)
        logging.info('Playoffs initialized with top 8 teams')
        
    def get_playoff_round_name(self) -> Optional[str]:
        """Get the current playoff round name, or None if not in playoffs"""
        if not self.playoffs:
            return None
        return self.playoffs.current_round 