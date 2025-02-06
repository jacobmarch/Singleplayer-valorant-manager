import logging
from rich.prompt import Prompt
from rich.table import Table
from datetime import datetime
from src.ui.console_manager import ConsoleManager
from src.game.data import REGIONS, REGION_LIST
from src.game.person import Player, Coach, generate_team_members
from src.game.roster import LeagueManager, Match
from src.game.season_history import SeasonHistory
from typing import List, Optional
import random
from rich.columns import Columns

class GameManager:
    def __init__(self):
        self.console = ConsoleManager()
        self.selected_region = None
        self.selected_team = None
        self.players: Optional[List[Player]] = None
        self.coach: Optional[Coach] = None
        self.league_manager: Optional[LeagueManager] = None
        self.first_names = []
        self.last_names = []
        self.last_roster_change_week = 0  # Track the week of last roster change
        self.season_history = SeasonHistory()  # Add season history tracking
        
        # Load name data
        try:
            with open('data/first_names.txt', 'r') as f:
                self.first_names = [line.strip() for line in f.readlines()]
            with open('data/last_names.txt', 'r') as f:
                self.last_names = [line.strip() for line in f.readlines()]
        except FileNotFoundError as e:
            logging.error(f'Name data files not found: {str(e)}')
            raise
        except Exception as e:
            logging.error(f'Error loading name data: {str(e)}')
            raise

    def display_region_selection(self):
        """
        Display available regions in a table format.
        """
        table = Table(show_header=False, box=None, padding=(0, 1))
        for idx, region in enumerate(REGION_LIST, 1):
            table.add_row(f"[menu_option]{idx}.[/menu_option]", f"[white]{region}[/white]")
        return table

    def display_team_selection(self, region):
        """
        Display teams from the selected region in a table format.
        """
        table = Table(show_header=False, box=None, padding=(0, 1))
        teams = REGIONS[region]
        for idx, team in enumerate(teams, 1):
            table.add_row(f"[menu_option]{idx}.[/menu_option]", f"[white]{team}[/white]")
        return table

    def display_team_members(self):
        """Display the generated team members in a table format"""
        if not self.players or not self.coach:
            return

        # Create players table
        players_table = Table(title="Team Players", show_header=True)
        players_table.add_column("Position")
        players_table.add_column("Name")
        players_table.add_column("Skill Rating")

        for player in self.players:
            players_table.add_row(
                player.position,
                f"{player.first_name} {player.last_name}",
                str(player.skill_rating)
            )

        # Create coach table
        coach_table = Table(title="Team Coach", show_header=True)
        coach_table.add_column("Name")
        coach_table.add_column("Skill Rating")
        coach_table.add_row(
            f"{self.coach.first_name} {self.coach.last_name}",
            str(self.coach.skill_rating)
        )

        return players_table, coach_table

    def generate_team_members(self):
        """Generate random players and coach for the team"""
        logging.info('Generating team members')
        
        # Load name data
        try:
            with open('data/first_names.txt', 'r') as f:
                first_names = [line.strip() for line in f.readlines()]
            with open('data/last_names.txt', 'r') as f:
                last_names = [line.strip() for line in f.readlines()]
                
            self.players, self.coach = generate_team_members(first_names, last_names)
            logging.info(f'Generated {len(self.players)} players and 1 coach')
            
        except FileNotFoundError as e:
            logging.error(f'Name data files not found: {str(e)}')
            raise
        except Exception as e:
            logging.error(f'Error generating team members: {str(e)}')
            raise

    def display_team_ratings(self):
        """Display all team ratings in the league in a table format"""
        if not self.league_manager:
            return None

        table = Table(title=f"{self.selected_region} Team Ratings")
        table.add_column("Team")
        table.add_column("Rating")
        table.add_column("Record")

        # Sort teams by rating for display
        sorted_teams = sorted(
            self.league_manager.team_ratings.values(),
            key=lambda x: x.rating,
            reverse=True
        )

        for team in sorted_teams:
            name_style = "[green]" if team.name == self.selected_team else "[white]"
            table.add_row(
                f"{name_style}{team.name}[/]",
                f"{team.rating}",
                f"{team.wins}-{team.losses}"
            )

        return table

    def display_full_schedule(self, team_only: bool = False):
        """
        Display the complete season schedule including past results and upcoming matches
        
        Args:
            team_only: If True, only show matches involving the user's team
        """
        if not self.league_manager:
            return None

        title = "Your Team's Schedule" if team_only else "Full League Schedule"
        table = Table(
            title=title,
            show_header=True,
            header_style="bold",
            box=None,
            padding=(0, 2)
        )
        table.add_column("Week", justify="center")
        table.add_column("Home Team", justify="right")
        table.add_column("Score", justify="center")
        table.add_column("Away Team", justify="left")
        table.add_column("Status", justify="center")

        # Sort matches by week
        sorted_matches = sorted(self.league_manager.schedule, key=lambda x: x.week)
        current_week = self.get_current_week()

        for match in sorted_matches:
            # Skip if team_only is True and match doesn't involve user's team
            if team_only and self.selected_team not in [match.home_team, match.away_team]:
                continue
                
            home_style = "[green]" if match.home_team == self.selected_team else "[white]"
            away_style = "[green]" if match.away_team == self.selected_team else "[white]"
            
            # Format score/status based on match completion
            if match.completed:
                score = f"{match.home_score} - {match.away_score}"
                status = "[grey]Completed[/]"
            else:
                score = "vs"
                if match.week == current_week:
                    status = "[yellow]Next Match[/]"
                else:
                    status = f"Week {match.week}"
            
            table.add_row(
                f"Week {match.week}",
                f"{home_style}{match.home_team}[/]",
                score,
                f"{away_style}{match.away_team}[/]",
                status
            )

        return table

    def display_standings(self):
        """Display current league standings in a table format"""
        if not self.league_manager:
            return None

        table = Table(title=f"{self.selected_region} Standings")
        table.add_column("Position", justify="center")
        table.add_column("Team")
        table.add_column("W", justify="center")
        table.add_column("L", justify="center")
        table.add_column("Rating", justify="center")

        # Sort teams by wins, then rating for tiebreaker
        sorted_teams = sorted(
            self.league_manager.team_ratings.values(),
            key=lambda x: (x.wins, x.rating),
            reverse=True
        )

        for pos, team in enumerate(sorted_teams, 1):
            name_style = "[green]" if team.name == self.selected_team else "[white]"
            table.add_row(
                str(pos),
                f"{name_style}{team.name}[/]",
                str(team.wins),
                str(team.losses),
                str(team.rating)
            )

        return table

    def get_current_week(self) -> int:
        """Get the current week number based on the first uncompleted week"""
        if not self.league_manager:
            return 1
            
        # Sort matches by week and find first uncompleted week
        sorted_matches = sorted(self.league_manager.schedule, key=lambda x: x.week)
        for match in sorted_matches:
            if not match.completed:
                return match.week
        
        # If all matches completed, return last week + 1
        return sorted_matches[-1].week + 1 if sorted_matches else 1

    def can_make_roster_change(self) -> bool:
        """Check if a roster change is allowed this week"""
        current_week = self.get_current_week()
        return current_week > self.last_roster_change_week

    def display_roster_management(self):
        """Display roster management options and handle user input"""
        while True:
            self.console.clear_screen()
            self.console.display_header()
            
            # Display current roster
            players_table, coach_table = self.display_team_members()
            self.console.console.print("\n[menu_title]Current Roster[/menu_title]")
            self.console.console.print("\n")
            self.console.console.print(players_table)
            self.console.console.print("\n")
            self.console.console.print(coach_table)
            
            # Check if roster changes are allowed this week
            current_week = self.get_current_week()
            if not self.can_make_roster_change():
                self.console.console.print("\n[warning]You have already made a roster change this week. Wait until next week for further changes.[/warning]")
                self.console.console.print("\nPress Enter to return to dashboard...", end="")
                input()
                break
            
            # Display options
            self.console.console.print("\n[menu_title]Roster Management[/menu_title]")
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_row("[menu_option]1.[/menu_option]", "[white]Cut Player[/white]")
            table.add_row("[menu_option]2.[/menu_option]", "[white]Cut Coach[/white]")
            table.add_row("[menu_option]3.[/menu_option]", "[white]Return to Dashboard[/white]")
            self.console.console.print(table)
            
            try:
                choice = Prompt.ask(
                    "\nEnter your choice",
                    choices=["1", "2", "3"],
                    show_choices=False
                )
                
                if choice == "1":
                    if self.manage_player_cut():  # Only update week if change was made
                        self.last_roster_change_week = current_week
                        break
                elif choice == "2":
                    if self.manage_coach_cut():  # Only update week if change was made
                        self.last_roster_change_week = current_week
                        break
                elif choice == "3":
                    break
                    
            except KeyboardInterrupt:
                break

    def manage_player_cut(self) -> bool:
        """
        Handle cutting and replacing a player
        Returns True if a change was made, False otherwise
        """
        # Display players with numbers
        self.console.clear_screen()
        self.console.display_header()
        self.console.console.print("\n[menu_title]Select Player to Cut[/menu_title]\n")
        
        table = Table(show_header=True)
        table.add_column("#", justify="center")
        table.add_column("Position")
        table.add_column("Name")
        table.add_column("Rating")
        
        for idx, player in enumerate(self.players, 1):
            table.add_row(
                str(idx),
                player.position,
                f"{player.first_name} {player.last_name}",
                str(player.skill_rating)
            )
        self.console.console.print(table)
        
        try:
            choice = Prompt.ask(
                "\nSelect player number to cut (or 'c' to cancel)",
                choices=[str(i) for i in range(1, len(self.players) + 1)] + ['c'],
                show_choices=False
            )
            
            if choice == 'c':
                return False
                
            # Generate replacement options
            selected_idx = int(choice) - 1  # Store the index of the player to replace
            cut_player = self.players[selected_idx]
            position = cut_player.position
            
            replacements = []
            for _ in range(3):
                replacement = Player(
                    first_name=random.choice(self.first_names).lower().capitalize(),
                    last_name=random.choice(self.last_names).lower().capitalize(),
                    skill_rating=int(random.gauss(mu=50, sigma=15)),
                    position=position
                )
                replacements.append(replacement)
            
            # Display replacement options
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print(f"\n[menu_title]Select Replacement {position}[/menu_title]\n")
            
            table = Table(show_header=True)
            table.add_column("#", justify="center")
            table.add_column("Name")
            table.add_column("Rating")
            
            for idx, player in enumerate(replacements, 1):
                table.add_row(
                    str(idx),
                    f"{player.first_name} {player.last_name}",
                    str(player.skill_rating)
                )
            self.console.console.print(table)
            
            choice = Prompt.ask(
                "\nSelect replacement number",
                choices=[str(i) for i in range(1, len(replacements) + 1)],
                show_choices=False
            )
            
            # Replace the player using the stored index
            replacement_idx = int(choice) - 1
            self.players[selected_idx] = replacements[replacement_idx]
            logging.info(f'Replaced player {cut_player.first_name} {cut_player.last_name} with {self.players[selected_idx].first_name} {self.players[selected_idx].last_name}')
            
            # Update team rating
            if self.league_manager:
                self.league_manager.team_ratings[self.selected_team].rating = self.league_manager._calculate_user_team_rating(self.players, self.coach)
            
            # After successful replacement
            self.console.console.print("\n[green]Player replaced successfully! No more roster changes allowed this week.[/green]")
            self.console.console.print("\nPress Enter to continue...", end="")
            input()
            return True
            
        except KeyboardInterrupt:
            return False

    def manage_coach_cut(self) -> bool:
        """
        Handle cutting and replacing the coach
        Returns True if a change was made, False otherwise
        """
        self.console.clear_screen()
        self.console.display_header()
        self.console.console.print("\n[menu_title]Current Coach[/menu_title]\n")
        
        table = Table(show_header=True)
        table.add_column("Name")
        table.add_column("Rating")
        table.add_row(
            f"{self.coach.first_name} {self.coach.last_name}",
            str(self.coach.skill_rating)
        )
        self.console.console.print(table)
        
        try:
            if not Prompt.ask(
                "\nDo you want to cut this coach? (y/n)",
                choices=["y", "n"],
                show_choices=False
            ) == "y":
                return False
            
            # Generate replacement options
            replacements = []
            for _ in range(3):
                replacement = Coach.generate(self.first_names, self.last_names)
                replacements.append(replacement)
            
            # Display replacement options
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print("\n[menu_title]Select Replacement Coach[/menu_title]\n")
            
            table = Table(show_header=True)
            table.add_column("#", justify="center")
            table.add_column("Name")
            table.add_column("Rating")
            
            for idx, coach in enumerate(replacements, 1):
                table.add_row(
                    str(idx),
                    f"{coach.first_name} {coach.last_name}",
                    str(coach.skill_rating)
                )
            self.console.console.print(table)
            
            choice = Prompt.ask(
                "\nSelect replacement number",
                choices=[str(i) for i in range(1, len(replacements) + 1)],
                show_choices=False
            )
            
            # Replace the coach
            old_coach = self.coach
            self.coach = replacements[int(choice) - 1]
            logging.info(f'Replaced coach {old_coach.first_name} {old_coach.last_name} with {self.coach.first_name} {self.coach.last_name}')
            
            # Update team rating
            if self.league_manager:
                self.league_manager.team_ratings[self.selected_team].rating = self.league_manager._calculate_user_team_rating(self.players, self.coach)
            
            # After successful replacement
            self.console.console.print("\n[green]Coach replaced successfully! No more roster changes allowed this week.[/green]")
            self.console.console.print("\nPress Enter to continue...", end="")
            input()
            return True
            
        except KeyboardInterrupt:
            return False

    def display_schedule_menu(self):
        """Handle the schedule view menu and options"""
        team_only = True  # Start with team schedule by default
        
        while True:
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print("\n[menu_title]Season Schedule[/menu_title]")
            
            # Display current filter status
            filter_status = "[green]Your Team Schedule[/]" if team_only else "[white]Full League Schedule[/]"
            self.console.console.print(f"\nCurrently showing: {filter_status}")
            
            # Display schedule
            schedule_table = self.display_full_schedule(team_only)
            if schedule_table:
                self.console.console.print("\n")
                self.console.console.print(schedule_table)
            
            # Display options
            self.console.console.print("\n[menu_title]Options[/menu_title]")
            table = Table(show_header=False, box=None, padding=(0, 1))
            toggle_text = "Show League Schedule" if team_only else "Show Team Schedule"
            table.add_row("[menu_option]1.[/menu_option]", f"[white]{toggle_text}[/white]")
            table.add_row("[menu_option]2.[/menu_option]", "[white]Return to Dashboard[/white]")
            self.console.console.print(table)
            
            try:
                choice = Prompt.ask(
                    "\nEnter your choice",
                    choices=["1", "2"],
                    show_choices=False
                )
                
                if choice == "1":
                    team_only = not team_only  # Toggle the filter
                elif choice == "2":
                    break
                    
            except KeyboardInterrupt:
                break

    def simulate_map(self, home_rating: int, away_rating: int) -> tuple[int, int]:
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

    def simulate_match(self, match) -> tuple[int, int]:
        """
        Simulate a match and determine the winner
        
        Args:
            match: The match to simulate
            
        Returns:
            Tuple of (maps_won_home, maps_won_away)
        """
        if not self.league_manager:
            return 0, 0
            
        home_rating = self.league_manager.team_ratings[match.home_team].rating
        away_rating = self.league_manager.team_ratings[match.away_team].rating
        
        maps_won_home = 0
        maps_won_away = 0
        match.map_scores = []  # Reset map scores
        
        # Simulate maps until a team wins enough maps
        while maps_won_home < match.maps_needed and maps_won_away < match.maps_needed:
            home_rounds, away_rounds = self.simulate_map(home_rating, away_rating)
            match.map_scores.append((home_rounds, away_rounds))
            
            if home_rounds > away_rounds:
                maps_won_home += 1
            else:
                maps_won_away += 1
                
        logging.info(f'Match simulated: {match.home_team} vs {match.away_team} - Maps: {maps_won_home}-{maps_won_away}')
        for i, (home_rounds, away_rounds) in enumerate(match.map_scores, 1):
            logging.info(f'Map {i}: {home_rounds}-{away_rounds}')
            
        return maps_won_home, maps_won_away

    def simulate_week(self) -> List[Match]:
        """
        Simulate all matches for the current week
        
        Returns:
            List of matches that were simulated
        """
        if not self.league_manager:
            return []
            
        current_week = self.get_current_week()
        
        # Get all matches for the current week
        current_matches = []
        for match in sorted(self.league_manager.schedule, key=lambda x: x.week):
            if match.week == current_week:
                if match.completed:
                    logging.warning(f'Found completed match in current week {current_week}')
                else:
                    current_matches.append(match)
            elif match.week < current_week and not match.completed:
                # This indicates a problem - earlier week has uncompleted matches
                logging.error(f'Found uncompleted match in week {match.week} while simulating week {current_week}')
                return []
        
        if not current_matches:
            logging.warning(f'No matches found for week {current_week}')
            return []
            
        simulated_matches = []
        for match in current_matches:
            # Simulate the match
            home_score, away_score = self.simulate_match(match)
            
            # Update match data
            match.completed = True
            match.home_score = home_score
            match.away_score = away_score
            
            # Update team records
            home_team = self.league_manager.team_ratings[match.home_team]
            away_team = self.league_manager.team_ratings[match.away_team]
            
            if home_score > away_score:
                home_team.wins += 1
                away_team.losses += 1
            else:
                away_team.wins += 1
                home_team.losses += 1
                
            simulated_matches.append(match)
            
        return simulated_matches

    def display_match_results(self, matches: List[Match], title: str = "Match Results"):
        """
        Display the results of simulated matches
        
        Args:
            matches: List of matches to display
            title: Title for the results table
        """
        table = Table(title=title, show_header=True)
        table.add_column("Home Team", justify="right")
        table.add_column("Score", justify="center")
        table.add_column("Away Team", justify="left")
        
        for match in matches:
            home_style = "[green]" if match.home_team == self.selected_team else "[white]"
            away_style = "[green]" if match.away_team == self.selected_team else "[white]"
            
            # Highlight winner
            if match.home_score > match.away_score:
                home_style = home_style.replace("]", " bold]")
            else:
                away_style = away_style.replace("]", " bold]")
                
            table.add_row(
                f"{home_style}{match.home_team}[/]",
                f"{match.home_score} - {match.away_score}",
                f"{away_style}{match.away_team}[/]"
            )
            
        return table

    def display_match_details(self, match: Match):
        """
        Display detailed information about a specific match
        
        Args:
            match: The match to display details for
        """
        self.console.clear_screen()
        self.console.display_header()
        
        # Match header with playoff info if applicable
        title = f"{match.home_team} vs {match.away_team} - Week {match.week}"
        if match.is_playoff:
            title = f"{match.playoff_round.title()} - {title}"
            if match.playoff_round == "final":
                title = f"GRAND {title}"
        self.console.console.print(f"\n[menu_title]{title}[/menu_title]")
        
        # Create match summary table
        summary_table = Table(title="Match Summary", show_header=False)
        summary_table.add_column("Label", style="bold")
        summary_table.add_column("Value")
        
        winner = match.get_winner()
        maps_needed = match.maps_needed
        total_maps = "Best of 5" if maps_needed == 3 else "Best of 3"
        
        summary_table.add_row("Format", total_maps)
        summary_table.add_row("Final Score", f"{match.home_score} - {match.away_score}")
        if winner:
            winner_style = "[green bold]" if winner == self.selected_team else "[white bold]"
            summary_table.add_row("Winner", f"{winner_style}{winner}[/]")
        else:
            summary_table.add_row("Winner", "Not Played")
            
        if match.is_playoff:
            summary_table.add_row("Match Type", f"Playoff {match.playoff_round.title()}")
            # Add seed information
            home_seed = next(t.playoff_seed for t in self.league_manager.playoffs.teams if t.name == match.home_team)
            away_seed = next(t.playoff_seed for t in self.league_manager.playoffs.teams if t.name == match.away_team)
            summary_table.add_row("Seeds", f"#{home_seed} vs #{away_seed}")
        
        # Create map details table
        maps_table = Table(title="Map Details", show_header=True)
        maps_table.add_column("Map", justify="center")
        maps_table.add_column(match.home_team, justify="center")
        maps_table.add_column("Score", justify="center")
        maps_table.add_column(match.away_team, justify="center")
        
        for i, (home_rounds, away_rounds) in enumerate(match.map_scores, 1):
            winner_style = "[green bold]" if home_rounds > away_rounds else "[white]"
            loser_style = "[white]" if home_rounds > away_rounds else "[green bold]"
            
            maps_table.add_row(
                f"Map {i}",
                f"{winner_style if home_rounds > away_rounds else loser_style}{match.home_team}[/]",
                f"{home_rounds} - {away_rounds}",
                f"{loser_style if home_rounds > away_rounds else winner_style}{match.away_team}[/]"
            )
        
        # Display tables
        self.console.console.print("\n")
        self.console.console.print(summary_table)
        self.console.console.print("\n")
        self.console.console.print(maps_table)
        
        self.console.console.print("\n[info]Press Enter to continue...[/info]", end="")
        input()

    def display_table_pair(self, left_table, right_table=None):
        """Display two tables side by side"""
        tables = [left_table]
        if right_table:
            tables.append(right_table)
        self.console.console.print(Columns(tables, equal=True, expand=True))

    def display_history(self):
        """Display the history of all completed seasons"""
        self.console.clear_screen()
        self.console.display_header()
        
        if not self.season_history.seasons:
            self.console.console.print("\n[yellow]No completed seasons yet[/yellow]")
            self.console.console.print("\nPress Enter to return to dashboard...", end="")
            input()
            return
            
        self.console.console.print("\n[menu_title]Season History[/menu_title]")
        
        table = Table(show_header=True)
        table.add_column("Year", justify="center")
        table.add_column("Region")
        table.add_column("Champion")
        table.add_column("Champion Record", justify="center")
        table.add_column("Your Team")
        table.add_column("Your Record", justify="center")
        table.add_column("Position", justify="center")
        
        for season in self.season_history.get_season_history():
            champion_style = "[green bold]" if season.champion == season.player_team else "[white]"
            table.add_row(
                str(season.year),
                season.region,
                f"{champion_style}{season.champion}[/]",
                f"{season.champion_record[0]}-{season.champion_record[1]}",
                season.player_team,
                f"{season.player_record[0]}-{season.player_record[1]}",
                f"#{season.player_position}"
            )
            
        self.console.console.print("\n")
        self.console.console.print(table)
        self.console.console.print("\nPress Enter to return to dashboard...", end="")
        input()

    def play_next_week(self):
        """Handle playing the next week of matches"""
        if not self.league_manager:
            return
            
        current_week = self.get_current_week()
        
        # Check if regular season is complete and playoffs haven't started
        if not self.league_manager.playoffs and all(m.completed for m in self.league_manager.schedule):
            self.league_manager.regular_season_complete = True
            self.league_manager.start_playoffs()
            current_week += 1  # Start playoffs next week
            
            # Show playoff qualification message
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print("\n[menu_title]Playoff Qualification[/menu_title]")
            
            # Get playoff teams and their seeds
            playoff_teams = sorted(
                [t for t in self.league_manager.playoffs.teams],
                key=lambda x: x.playoff_seed
            )
            
            # Create qualification table
            qual_table = Table(show_header=True)
            qual_table.add_column("Seed", justify="center")
            qual_table.add_column("Team")
            qual_table.add_column("Record", justify="center")
            qual_table.add_column("Rating", justify="center")
            
            for team in playoff_teams:
                team_style = "[green]" if team.name == self.selected_team else "[white]"
                qual_table.add_row(
                    f"#{team.playoff_seed}",
                    f"{team_style}{team.name}[/]",
                    f"{team.wins}-{team.losses}",
                    str(team.rating)
                )
            
            self.console.console.print("\n")
            self.console.console.print(qual_table)
            
            if self.selected_team in [t.name for t in playoff_teams]:
                seed = next(t.playoff_seed for t in playoff_teams if t.name == self.selected_team)
                self.console.console.print(f"\n[green]Congratulations! Your team qualified for playoffs as the #{seed} seed![/green]")
            else:
                self.console.console.print("\n[yellow]Your team did not qualify for playoffs[/yellow]")
            
            # Generate first round of playoff matches
            simulated_matches = self.league_manager.playoffs.generate_playoff_matches(current_week)
            
            self.console.console.print("\nPress Enter to continue...", end="")
            input()
            
        # Get matches to be played (not simulated yet)
        matches_to_play = []
        if self.league_manager.playoffs:
            # Get uncompleted matches from current round
            matches_to_play = [m for m in self.league_manager.playoffs.matches if not m.completed]
            
            # If no uncompleted matches, we need to advance to next round
            if not matches_to_play and not self.league_manager.playoffs.completed:
                current_week += 1
                self.league_manager.playoffs.advance_round()
                matches_to_play = self.league_manager.playoffs.generate_playoff_matches(current_week)
                
                if not matches_to_play and self.league_manager.playoffs.completed:
                    # Playoffs are complete
                    champion = self.league_manager.playoffs.champion
                    champion_team = self.league_manager.team_ratings[champion]
                    player_team = self.league_manager.team_ratings[self.selected_team]
                    
                    # Get player's final position
                    sorted_teams = sorted(
                        self.league_manager.team_ratings.values(),
                        key=lambda x: (x.wins, x.rating),
                        reverse=True
                    )
                    player_position = next(i for i, t in enumerate(sorted_teams, 1) if t.name == self.selected_team)
                    
                    # Add season to history
                    self.season_history.add_season(
                        region=self.league_manager.region,
                        champion=champion,
                        champion_record=(champion_team.wins, champion_team.losses),
                        player_team=self.selected_team,
                        player_record=(player_team.wins, player_team.losses),
                        player_position=player_position
                    )
                    
                    # Display season complete message
                    self.console.clear_screen()
                    self.console.display_header()
                    self.console.console.print("\n[menu_title]Season Complete![/menu_title]")
                    
                    champion_style = "[green bold]" if champion == self.selected_team else "[white bold]"
                    self.console.console.print(f"\n🏆 Congratulations to {champion_style}{champion}[/] - {self.league_manager.region} Champions! 🏆")
                    
                    # Start new season with same team and roster
                    self.console.console.print("\nPress Enter to start the next season...", end="")
                    input()
                    
                    # Keep region, team, and roster but reset league
                    current_players = self.players
                    current_coach = self.coach
                    self.league_manager = LeagueManager(
                        region=self.selected_region,
                        teams=REGIONS[self.selected_region],
                        player_team=self.selected_team,
                        players=current_players,
                        coach=current_coach
                    )
                    self.league_manager.generate_schedule()
                    self.last_roster_change_week = 0
                    
                    # Show new season message
                    self.console.clear_screen()
                    self.console.display_header()
                    self.console.console.print(f"\n[green]Starting {self.season_history.current_year} Season with {self.selected_team}![/green]")
                    
                    # Display team members
                    players_table, coach_table = self.display_team_members()
                    self.console.console.print("\n")
                    self.console.console.print(players_table)
                    self.console.console.print("\n")
                    self.console.console.print(coach_table)
                    
                    # Wait for user input before showing league ratings
                    self.console.console.print("\n[info]Press Enter to view league ratings...[/info]", end="")
                    input()
                    
                    # Display league information
                    self.console.clear_screen()
                    self.console.display_header()
                    self.console.console.print("\n[menu_title]League Overview[/menu_title]")
                    ratings_table = self.display_team_ratings()
                    if ratings_table:
                        self.console.console.print("\n")
                        self.console.console.print(ratings_table)
                    
                    # Wait for user input before showing schedule
                    self.console.console.print("\n[info]Press Enter to view upcoming matches...[/info]", end="")
                    input()
                    
                    # Display schedule
                    self.console.clear_screen()
                    self.console.display_header()
                    self.console.console.print("\n[menu_title]Upcoming Matches[/menu_title]")
                    schedule_table = self.display_full_schedule()
                    if schedule_table:
                        self.console.console.print("\n")
                        self.console.console.print(schedule_table)
                    
                    self.console.console.print("\nPress Enter to continue to dashboard...", end="")
                    input()
                    return
        else:
            # Get regular season matches for current week (not simulated yet)
            current_week_matches = []
            for match in sorted(self.league_manager.schedule, key=lambda x: x.week):
                if match.week == current_week:
                    if not match.completed:
                        current_week_matches.append(match)
                elif match.week < current_week and not match.completed:
                    logging.error(f'Found uncompleted match in week {match.week} while simulating week {current_week}')
                    return
            matches_to_play = current_week_matches

        if not matches_to_play:
            self.console.console.print("[error]No matches found for the current week. Check the logs for details.[/error]")
            input("\nPress Enter to continue...")
            return

        # Display upcoming matches and confirm simulation
        self.console.clear_screen()
        self.console.display_header()
        
        # Show playoff round if applicable
        if self.league_manager.playoffs:
            playoff_round = self.league_manager.get_playoff_round_name()
            round_name = playoff_round.title() if playoff_round else "Playoffs"
            self.console.console.print(f"\n[menu_title]{round_name} - Week {current_week}[/menu_title]")
            
            # Show upcoming matches
            matches_table = Table(title="Upcoming Matches", show_header=True)
            matches_table.add_column("Match", justify="center")
            matches_table.add_column("Teams", justify="center")
            matches_table.add_column("Format", justify="center")
            
            for idx, match in enumerate(matches_to_play, 1):
                home_style = "[green]" if match.home_team == self.selected_team else "[white]"
                away_style = "[green]" if match.away_team == self.selected_team else "[white]"
                format_str = "Best of 5" if match.maps_needed == 3 else "Best of 3"
                
                matches_table.add_row(
                    f"Match {idx}",
                    f"{home_style}{match.home_team}[/] vs {away_style}{match.away_team}[/]",
                    format_str
                )
            
            self.console.console.print("\n")
            self.console.console.print(matches_table)
        else:
            self.console.console.print(f"\n[menu_title]Week {current_week} Matches[/menu_title]")
            schedule_table = self.display_full_schedule(team_only=True)
            if schedule_table:
                self.console.console.print("\n")
                self.console.console.print(schedule_table)
        
        # Confirm with user
        if not Prompt.ask(
            "\nReady to play matches?",
            choices=["y", "n"],
            show_choices=False
        ) == "y":
            return

        # Now simulate the matches after confirmation
        simulated_matches = []
        for match in matches_to_play:
            home_score, away_score = self.simulate_match(match)
            match.completed = True
            match.home_score = home_score
            match.away_score = away_score
            simulated_matches.append(match)
            
            # Update eliminated teams in playoffs immediately
            if self.league_manager.playoffs:
                loser = match.get_loser()
                if loser:
                    loser_team = next(t for t in self.league_manager.playoffs.teams if t.name == loser)
                    loser_team.eliminated = True
                    
            # Update team records for regular season
            else:
                home_team = self.league_manager.team_ratings[match.home_team]
                away_team = self.league_manager.team_ratings[match.away_team]
                
                if home_score > away_score:
                    home_team.wins += 1
                    away_team.losses += 1
                else:
                    away_team.wins += 1
                    home_team.losses += 1

        # Display results view
        self.console.clear_screen()
        self.console.display_header()
        
        # Show playoff round if applicable
        if self.league_manager.playoffs:
            playoff_round = self.league_manager.get_playoff_round_name()
            round_name = playoff_round.title() if playoff_round else "Playoffs"
            self.console.console.print(f"\n[menu_title]{round_name} Results - Week {current_week}[/menu_title]")
        else:
            self.console.console.print(f"\n[menu_title]Week {current_week} Results[/menu_title]")
        
        # Your team's matches
        your_matches = [m for m in simulated_matches if self.selected_team in [m.home_team, m.away_team]]
        if your_matches:
            self.console.console.print("\n[bold]Your Team's Results[/bold]")
            self.console.console.print(self.display_match_results(your_matches))
        
        # All other matches
        other_matches = [m for m in simulated_matches if m not in your_matches]
        if other_matches:
            self.console.console.print("\n[bold]Other Results[/bold]")
            self.console.console.print(self.display_match_results(other_matches))

        # Display options for match details
        self.console.console.print("\n[menu_title]Options[/menu_title]")
        table = Table(show_header=False, box=None, padding=(0, 1))
        
        # Reorder matches to put player's match first
        ordered_matches = []
        if your_matches:
            ordered_matches.extend(your_matches)
        ordered_matches.extend(other_matches)
        
        # Add options for viewing match details
        for idx, match in enumerate(ordered_matches, 1):
            is_player_match = self.selected_team in [match.home_team, match.away_team]
            option_style = "[green]" if is_player_match else "[white]"
            match_text = f"{match.home_team} vs {match.away_team}"
            if is_player_match:
                match_text = f"{match_text} (Your Match)"
                
            table.add_row(
                f"[menu_option]{idx}.[/menu_option]",
                f"{option_style}{match_text}[/]"
            )
        table.add_row("[menu_option]s.[/menu_option]", "[white]View Full Schedule[/white]")
        table.add_row("[menu_option]x.[/menu_option]", "[white]Return to Dashboard[/white]")
        self.console.console.print(table)
        
        while True:
            try:
                choices = [str(i) for i in range(1, len(ordered_matches) + 1)] + ["s", "x"]
                choice = Prompt.ask(
                    "\nEnter your choice",
                    choices=choices,
                    show_choices=False
                )
                
                if choice == "x":
                    break
                elif choice == "s":
                    self.display_schedule_menu()
                else:
                    match_idx = int(choice) - 1
                    self.display_match_details(ordered_matches[match_idx])
                    
                    # After viewing match details, redisplay the results and options
                    self.console.clear_screen()
                    self.console.display_header()
                    
                    if self.league_manager.playoffs:
                        playoff_round = self.league_manager.get_playoff_round_name()
                        round_name = playoff_round.title() if playoff_round else "Playoffs"
                        self.console.console.print(f"\n[menu_title]{round_name} Results - Week {current_week}[/menu_title]")
                    else:
                        self.console.console.print(f"\n[menu_title]Week {current_week} Results[/menu_title]")
                    
                    if your_matches:
                        self.console.console.print("\n[bold]Your Team's Results[/bold]")
                        self.console.console.print(self.display_match_results(your_matches))
                    
                    if other_matches:
                        self.console.console.print("\n[bold]Other Results[/bold]")
                        self.console.console.print(self.display_match_results(other_matches))
                        
                    self.console.console.print("\n[menu_title]Options[/menu_title]")
                    self.console.console.print(table)
                    
            except KeyboardInterrupt:
                break
            
        # Show advancing teams after match details if a playoff round is complete
        if self.league_manager.playoffs and all(m.completed for m in simulated_matches):
            remaining = [t for t in self.league_manager.playoffs.teams if not t.eliminated]
            if remaining and len(remaining) < len(self.league_manager.playoffs.teams):
                self.console.clear_screen()
                self.console.display_header()
                
                playoff_round = self.league_manager.get_playoff_round_name()
                round_name = playoff_round.title() if playoff_round else "Playoffs"
                self.console.console.print(f"\n[menu_title]{round_name} Complete![/menu_title]")
                
                self.console.console.print("\n[bold]Teams Advancing:[/bold]")
                
                advance_table = Table(show_header=True)
                advance_table.add_column("Seed", justify="center")
                advance_table.add_column("Team")
                
                remaining.sort(key=lambda x: x.playoff_seed)
                for team in remaining:
                    team_style = "[green]" if team.name == self.selected_team else "[white]"
                    advance_table.add_row(
                        f"#{team.playoff_seed}",
                        f"{team_style}{team.name}[/]"
                    )
                
                self.console.console.print(advance_table)
                
                # Show next round info
                next_round = ""
                if playoff_round == "quarterfinal":
                    next_round = "Semifinals"
                elif playoff_round == "semifinal":
                    next_round = "Finals"
                
                if next_round:
                    self.console.console.print(f"\n[bold]Advancing to {next_round}![/bold]")
                
                self.console.console.print("\nPress Enter to continue...", end="")
                input()
            
        # After matches are complete, update eliminated teams in playoffs
        if self.league_manager.playoffs:
            for match in simulated_matches:
                if match.completed:
                    loser = match.get_loser()
                    if loser:
                        loser_team = next(t for t in self.league_manager.playoffs.teams if t.name == loser)
                        loser_team.eliminated = True
            
        logging.info(f'Completed week {current_week} matches')

    def display_dashboard(self):
        """Display the main game dashboard and handle user input"""
        while True:
            self.console.clear_screen()
            self.console.display_header()
            
            # Display current standings
            standings_table = self.display_standings()
            if standings_table:
                self.console.console.print("\n")
                self.console.console.print(standings_table)
            
            # Display playoff status if applicable
            if self.league_manager.playoffs:
                playoff_round = self.league_manager.get_playoff_round_name()
                if playoff_round:
                    self.console.console.print(f"\n[bold]{playoff_round.title()} Round[/bold]")
                    if self.selected_team in [t.name for t in self.league_manager.playoffs.teams if not t.eliminated]:
                        self.console.console.print("[green]Your team is in the playoffs![/green]")
                    else:
                        self.console.console.print("[yellow]Your team did not qualify for playoffs[/yellow]")
            
            # Display dashboard options
            self.console.console.print("\n[menu_title]Dashboard[/menu_title]")
            table = Table(show_header=False, box=None, padding=(0, 1))
            
            # Check if season is complete
            if self.league_manager.playoffs and self.league_manager.playoffs.completed:
                champion = self.league_manager.playoffs.champion
                champion_style = "[green bold]" if champion == self.selected_team else "[white bold]"
                table.add_row("[menu_option]1.[/menu_option]", "[grey]Season Complete[/grey]")
                table.add_row(
                    "[info]Champion:[/info]",
                    f"{champion_style}{champion}[/] - {self.league_manager.region} Champions"
                )
            elif self.league_manager.playoffs:
                # Determine next round text
                playoff_round = self.league_manager.get_playoff_round_name()
                next_round = ""
                if playoff_round == "quarterfinal":
                    next_round = "Semifinals"
                elif playoff_round == "semifinal":
                    next_round = "Finals"
                elif playoff_round == "final":
                    next_round = "Championship"
                else:
                    next_round = "Next Round"
                    
                table.add_row("[menu_option]1.[/menu_option]", f"[white]Advance to {next_round}[/white]")
            else:
                remaining_matches = [m for m in self.league_manager.schedule if not m.completed]
                if remaining_matches:
                    table.add_row("[menu_option]1.[/menu_option]", "[white]Play Next Week[/white]")
                else:
                    table.add_row("[menu_option]1.[/menu_option]", "[white]Start Playoffs[/white]")
                
            table.add_row("[menu_option]2.[/menu_option]", "[white]Manage Roster[/white]")
            table.add_row("[menu_option]3.[/menu_option]", "[white]View Standings[/white]")
            table.add_row("[menu_option]4.[/menu_option]", "[white]View Schedule[/white]")
            table.add_row("[menu_option]5.[/menu_option]", "[white]View History[/white]")
            table.add_row("[menu_option]6.[/menu_option]", "[white]Return to Main Menu[/white]")
            self.console.console.print(table)
            
            try:
                choice = Prompt.ask(
                    "\nEnter your choice",
                    choices=["1", "2", "3", "4", "5", "6"],
                    show_choices=False
                )
                
                if choice == "1":
                    if not (self.league_manager.playoffs and self.league_manager.playoffs.completed):
                        self.play_next_week()
                    else:
                        self.console.console.print("[yellow]The season is complete![/yellow]")
                        input("\nPress Enter to continue...")
                elif choice == "2":
                    self.display_roster_management()
                elif choice == "3":
                    self.console.clear_screen()
                    self.console.display_header()
                    standings_table = self.display_standings()
                    if standings_table:
                        self.console.console.print("\n")
                        self.console.console.print(standings_table)
                    input("\nPress Enter to continue...")
                elif choice == "4":
                    self.display_schedule_menu()
                elif choice == "5":
                    self.display_history()
                elif choice == "6":
                    break
                    
            except KeyboardInterrupt:
                break

    def create_new_game(self):
        """
        Initialize a new game session with region and team selection.
        """
        logging.info('Creating new game session')
        self.console.clear_screen()
        self.console.display_header()
        
        # Region Selection
        self.console.console.print("\n[menu_title]Select Your Region[/menu_title]")
        self.console.console.print(self.display_region_selection())
        
        try:
            region_choice = Prompt.ask(
                "\nEnter your choice",
                choices=[str(i) for i in range(1, len(REGION_LIST) + 1)],
                show_choices=False
            )
            self.selected_region = REGION_LIST[int(region_choice) - 1]
            logging.info(f'User selected region: {self.selected_region}')
            
            # Team Selection
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print(f"\n[menu_title]Select Your Team from {self.selected_region}[/menu_title]")
            self.console.console.print(self.display_team_selection(self.selected_region))
            
            team_choice = Prompt.ask(
                "\nEnter your choice",
                choices=[str(i) for i in range(1, len(REGIONS[self.selected_region]) + 1)],
                show_choices=False
            )
            self.selected_team = REGIONS[self.selected_region][int(team_choice) - 1]
            logging.info(f'User selected team: {self.selected_team}')
            
            # Generate team members
            self.generate_team_members()
            
            # Initialize league with player data
            self.league_manager = LeagueManager(
                region=self.selected_region,
                teams=REGIONS[self.selected_region],
                player_team=self.selected_team,
                players=self.players,
                coach=self.coach
            )
            self.league_manager.generate_schedule()
            
            # Display team information
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print(f"\n[green]You have selected {self.selected_team} from {self.selected_region}![/green]")
            
            # Display team members
            players_table, coach_table = self.display_team_members()
            self.console.console.print("\n")
            self.console.console.print(players_table)
            self.console.console.print("\n")
            self.console.console.print(coach_table)
            
            # Wait for user input before showing league ratings
            self.console.console.print("\n[info]Press Enter to view league ratings...[/info]", end="")
            input()
            
            # Display league information
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print("\n[menu_title]League Overview[/menu_title]")
            ratings_table = self.display_team_ratings()
            if ratings_table:
                self.console.console.print("\n")
                self.console.console.print(ratings_table)
            
            # Wait for user input before showing schedule
            self.console.console.print("\n[info]Press Enter to view upcoming matches...[/info]", end="")
            input()
            
            # Display schedule
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print("\n[menu_title]Upcoming Matches[/menu_title]")
            schedule_table = self.display_full_schedule()
            if schedule_table:
                self.console.console.print("\n")
                self.console.console.print(schedule_table)
            
            # After displaying schedule, go to dashboard
            self.display_dashboard()
            
        except KeyboardInterrupt:
            logging.info('User interrupted team selection')
            self.console.console.print("\n[warning]Team selection interrupted[/warning]")
            return
        except Exception as e:
            logging.error(f'Error during team creation: {str(e)}')
            self.console.console.print("\n[error]An error occurred during team creation[/error]")
            return

    def load_game(self):
        """
        Load an existing game session.
        """
        logging.info('Attempting to load existing game')
        self.console.clear_screen()
        self.console.display_header()
        self.console.console.print("\n[info]Loading game...[/info]")
        # TODO: Implement game loading
        self.console.console.print("[yellow]Game loading will be implemented soon[/yellow]")

    def main_menu(self):
        """
        Display and handle the main menu options with improved UI.
        Returns False when the user wants to quit, True otherwise.
        """
        self.console.clear_screen()
        self.console.display_header()
        
        # Display menu in a compact format
        self.console.console.print("\n[menu_title]Game Menu[/menu_title]")
        self.console.console.print(self.console.create_menu_table())
        
        try:
            choice = Prompt.ask(
                "\nEnter your choice",
                choices=["1", "2", "3"],
                show_choices=False
            )
            
            if choice == '1':
                logging.info('User selected: New Game')
                self.create_new_game()
                return True
            elif choice == '2':
                logging.info('User selected: Load Game')
                self.load_game()
                return True
            elif choice == '3':
                logging.info('User selected: Quit Game')
                self.console.clear_screen()
                self.console.display_header()
                self.console.console.print("\n[cyan]Thanks for playing![/cyan]")
                return False
                
        except KeyboardInterrupt:
            logging.info('User interrupted the program')
            self.console.console.print("\n[warning]Game interrupted by user[/warning]")
            return False

    def run(self):
        """
        Main game loop.
        """
        try:
            while self.main_menu():
                self.console.console.print("\nPress Enter to continue...", end="")
                input()
        except Exception as e:
            logging.error(f'Unexpected error occurred: {str(e)}', exc_info=True)
            self.console.clear_screen()
            self.console.console.print("[error]An unexpected error occurred. Check the logs for details.[/error]") 