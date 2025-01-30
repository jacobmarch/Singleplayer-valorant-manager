import logging
from rich.prompt import Prompt
from rich.table import Table
from datetime import datetime
from src.ui.console_manager import ConsoleManager
from src.game.data import REGIONS, REGION_LIST
from src.game.person import Player, Coach, generate_team_members
from src.game.roster import LeagueManager
from typing import List, Optional
import random

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

    def display_schedule(self):
        """Display the complete season schedule in a table format"""
        if not self.league_manager:
            return None

        table = Table(
            title="Season Schedule",
            show_header=True,
            header_style="bold",
            box=None,
            padding=(0, 2)
        )
        table.add_column("Week", justify="center")
        table.add_column("Home Team", justify="right")
        table.add_column("vs", justify="center")
        table.add_column("Away Team", justify="left")

        upcoming_matches = self.league_manager.display_upcoming_matches()
        for match in upcoming_matches:
            home_style = "[green]" if match.home_team == self.selected_team else "[white]"
            away_style = "[green]" if match.away_team == self.selected_team else "[white]"
            
            table.add_row(
                f"Week {match.week}",
                f"{home_style}{match.home_team}[/]",
                "vs",
                f"{away_style}{match.away_team}[/]"
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
        """Get the current week number based on completed matches"""
        if not self.league_manager:
            return 1
        completed_matches = [m for m in self.league_manager.schedule if m.completed]
        return len(completed_matches) + 1

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
            
            # Display dashboard options
            self.console.console.print("\n[menu_title]Dashboard[/menu_title]")
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_row("[menu_option]1.[/menu_option]", "[white]Play Next Game[/white]")
            table.add_row("[menu_option]2.[/menu_option]", "[white]Manage Roster[/white]")
            table.add_row("[menu_option]3.[/menu_option]", "[white]View Standings[/white]")
            table.add_row("[menu_option]4.[/menu_option]", "[white]Return to Main Menu[/white]")
            self.console.console.print(table)
            
            try:
                choice = Prompt.ask(
                    "\nEnter your choice",
                    choices=["1", "2", "3", "4"],
                    show_choices=False
                )
                
                if choice == "1":
                    self.console.console.print("[yellow]Play Next Game feature coming soon![/yellow]")
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
            schedule_table = self.display_schedule()
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