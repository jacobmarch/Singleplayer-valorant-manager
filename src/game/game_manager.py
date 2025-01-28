import logging
from rich.prompt import Prompt
from rich.table import Table
from src.ui.console_manager import ConsoleManager
from src.game.data import REGIONS, REGION_LIST
from src.game.person import Player, Coach, generate_team_members
from typing import List, Optional

class GameManager:
    def __init__(self):
        self.console = ConsoleManager()
        self.selected_region = None
        self.selected_team = None
        self.players: Optional[List[Player]] = None
        self.coach: Optional[Coach] = None

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
            
            # After team selection
            self.generate_team_members()
            
            # Display team information
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print(f"\n[green]You have selected {self.selected_team} from {self.selected_region}![/green]")
            
            players_table, coach_table = self.display_team_members()
            self.console.console.print("\n")
            self.console.console.print(players_table)
            self.console.console.print("\n")
            self.console.console.print(coach_table)
            
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