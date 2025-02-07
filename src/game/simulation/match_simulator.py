import random
import logging
from typing import Tuple, List
from src.game.roster.league import Match

class MatchSimulator:
    @staticmethod
    def simulate_map(home_rating: int, away_rating: int) -> tuple[int, int]:
        """
        Simulate a single map and determine the score
        
        Args:
            home_rating: Rating of home team (0-100)
            away_rating: Rating of away team (0-100)
            
        Returns:
            Tuple of (home_rounds, away_rounds)
        """
        # Calculate base win probability from ratings
        rating_diff = home_rating - away_rating
        home_win_prob = 0.5 + (rating_diff * 0.005)  # Each 10 rating difference is 5% advantage
        
        home_rounds = 0
        away_rounds = 0
        
        # Simulate rounds until a team wins
        while True:
            # Need 13 rounds to win, and must win by 2
            if (home_rounds >= 13 or away_rounds >= 13) and abs(home_rounds - away_rounds) >= 2:
                break
                
            # If 12-12, continue until someone wins by 2
            if home_rounds == 12 and away_rounds == 12:
                # Simulate one round at a time
                if random.random() < home_win_prob:
                    home_rounds += 1
                else:
                    away_rounds += 1
                continue
            
            # Normal round simulation
            if random.random() < home_win_prob:
                home_rounds += 1
            else:
                away_rounds += 1
                
        return home_rounds, away_rounds

    @staticmethod
    def simulate_match(match: Match, team_ratings: dict) -> Tuple[int, int]:
        """
        Simulate a match and determine the winner
        
        Args:
            match: The match to simulate
            team_ratings: Dictionary of team ratings
            
        Returns:
            Tuple of (maps_won_home, maps_won_away)
        """
        home_rating = team_ratings[match.home_team].rating
        away_rating = team_ratings[match.away_team].rating
        
        maps_won_home = 0
        maps_won_away = 0
        match.map_scores = []  # Reset map scores
        
        # Simulate maps until a team wins enough maps
        while maps_won_home < match.maps_needed and maps_won_away < match.maps_needed:
            home_rounds, away_rounds = MatchSimulator.simulate_map(home_rating, away_rating)
            match.map_scores.append((home_rounds, away_rounds))
            
            if home_rounds > away_rounds:
                maps_won_home += 1
            else:
                maps_won_away += 1
                
        logging.info(f'Match simulated: {match.home_team} vs {match.away_team} - Maps: {maps_won_home}-{maps_won_away}')
        for i, (home_rounds, away_rounds) in enumerate(match.map_scores, 1):
            logging.info(f'Map {i}: {home_rounds}-{away_rounds}')
            
        return maps_won_home, maps_won_away

    @staticmethod
    def simulate_week(current_matches: List[Match], team_ratings: dict) -> List[Match]:
        """
        Simulate all matches for the current week
        
        Args:
            current_matches: List of matches to simulate
            team_ratings: Dictionary of team ratings
            
        Returns:
            List of simulated matches
        """
        simulated_matches = []
        for match in current_matches:
            # Simulate the match
            home_score, away_score = MatchSimulator.simulate_match(match, team_ratings)
            
            # Update match data
            match.completed = True
            match.home_score = home_score
            match.away_score = away_score
            
            # Update team records
            home_team = team_ratings[match.home_team]
            away_team = team_ratings[match.away_team]
            
            if home_score > away_score:
                home_team.wins += 1
                away_team.losses += 1
            else:
                away_team.wins += 1
                home_team.losses += 1
                
            simulated_matches.append(match)
            
        return simulated_matches 