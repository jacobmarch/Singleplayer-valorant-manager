import logging
import random
from typing import List, Tuple, Optional
from src.game.person import Player, Coach
from rich.prompt import Prompt
from rich.table import Table

class RosterManager:
    def __init__(self, first_names: List[str], last_names: List[str]):
        self.first_names = first_names
        self.last_names = last_names
        self.last_roster_change_week = 0
        self.changes_this_week = False  # Track if a change was made this week
        self.console = None  # Will be set when managing cuts

    def can_make_roster_change(self, current_week: int) -> bool:
        """Check if a roster change is allowed this week"""
        # If we've moved to a new week, reset the changes_this_week flag
        if current_week > self.last_roster_change_week:
            self.changes_this_week = False
            
        # Allow changes if none have been made this week
        return not self.changes_this_week

    def generate_replacement_player(self, position: str) -> Player:
        """Generate a replacement player for a given position"""
        return Player(
            first_name=random.choice(self.first_names).lower().capitalize(),
            last_name=random.choice(self.last_names).lower().capitalize(),
            skill_rating=int(random.gauss(mu=50, sigma=15)),
            position=position
        )

    def generate_replacement_coach(self) -> Coach:
        """Generate a replacement coach"""
        return Coach(
            first_name=random.choice(self.first_names).lower().capitalize(),
            last_name=random.choice(self.last_names).lower().capitalize(),
            skill_rating=int(random.gauss(mu=50, sigma=15))
        )

    def manage_player_cut(self, players: List[Player], console_print, current_week: int) -> Tuple[bool, Optional[Player]]:
        """
        Handle cutting and replacing a player
        Returns (True, new_player) if a change was made, (False, None) otherwise
        """
        if not self.can_make_roster_change(current_week):
            console_print("\n[warning]You have already made a roster change this week.[/warning]")
            return False, None
            
        # Display players with numbers
        console_print("\n[menu_title]Select Player to Cut[/menu_title]")
        table = Table(show_header=True)
        table.add_column("#", justify="center")
        table.add_column("Position")
        table.add_column("Name")
        table.add_column("Rating")
        
        for idx, player in enumerate(players, 1):
            table.add_row(
                str(idx),
                player.position,
                f"{player.first_name} {player.last_name}",
                str(player.skill_rating)
            )
        console_print(table)
        
        try:
            choice = Prompt.ask(
                "\nSelect player number to cut (or 'c' to cancel)",
                choices=[str(i) for i in range(1, len(players) + 1)] + ['c'],
                show_choices=False
            )
            
            if choice == 'c':
                return False, None
                
            # Generate replacement options
            selected_idx = int(choice) - 1
            cut_player = players[selected_idx]
            position = cut_player.position
            
            replacements = [self.generate_replacement_player(position) for _ in range(3)]
            
            # Clear screen and show replacement options
            if self.console:
                self.console.clear_screen()
                self.console.display_header()
            
            console_print(f"\n[menu_title]Select Replacement for {cut_player.first_name} {cut_player.last_name}[/menu_title]")
            console_print("\n[bold]Current Player:[/bold]")
            current_table = Table(show_header=True)
            current_table.add_column("Position")
            current_table.add_column("Name")
            current_table.add_column("Rating")
            current_table.add_row(
                cut_player.position,
                f"{cut_player.first_name} {cut_player.last_name}",
                str(cut_player.skill_rating)
            )
            console_print(current_table)
            
            console_print("\n[bold]Available Replacements:[/bold]")
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
            console_print(table)
            
            choice = Prompt.ask(
                "\nSelect replacement number",
                choices=[str(i) for i in range(1, len(replacements) + 1)],
                show_choices=False
            )
            
            # Get the selected replacement
            replacement_idx = int(choice) - 1
            new_player = replacements[replacement_idx]
            
            # Clear screen and show confirmation
            if self.console:
                self.console.clear_screen()
                self.console.display_header()
            
            console_print("\n[menu_title]Roster Change Complete[/menu_title]")
            console_print("\n[bold]Player Cut:[/bold]")
            cut_table = Table(show_header=True)
            cut_table.add_column("Position")
            cut_table.add_column("Name")
            cut_table.add_column("Rating")
            cut_table.add_row(
                cut_player.position,
                f"{cut_player.first_name} {cut_player.last_name}",
                str(cut_player.skill_rating)
            )
            console_print(cut_table)
            
            console_print("\n[bold]New Player:[/bold]")
            new_table = Table(show_header=True)
            new_table.add_column("Position")
            new_table.add_column("Name")
            new_table.add_column("Rating")
            new_table.add_row(
                new_player.position,
                f"{new_player.first_name} {new_player.last_name}",
                str(new_player.skill_rating)
            )
            console_print(new_table)
            
            logging.info(f'Replaced player {cut_player.first_name} {cut_player.last_name} with {new_player.first_name} {new_player.last_name}')
            self.last_roster_change_week = current_week
            self.changes_this_week = True
            
            console_print("\nPress Enter to continue...", end="")
            input()
            
            return True, new_player
            
        except KeyboardInterrupt:
            return False, None

    def manage_coach_cut(self, coach: Coach, console_print, current_week: int) -> Tuple[bool, Optional[Coach]]:
        """
        Handle cutting and replacing the coach
        Returns (True, new_coach) if a change was made, (False, None) otherwise
        """
        if not self.can_make_roster_change(current_week):
            console_print("\n[warning]You have already made a roster change this week.[/warning]")
            return False, None
            
        # Display current coach
        console_print("\n[menu_title]Current Coach[/menu_title]")
        table = Table(show_header=True)
        table.add_column("Name")
        table.add_column("Rating")
        table.add_row(
            f"{coach.first_name} {coach.last_name}",
            str(coach.skill_rating)
        )
        console_print(table)
        
        try:
            if not Prompt.ask(
                "\nDo you want to cut this coach? (y/n)",
                choices=["y", "n"],
                show_choices=False
            ) == "y":
                return False, None
            
            # Generate replacement options
            replacements = [self.generate_replacement_coach() for _ in range(3)]
            
            # Clear screen and show replacement options
            if self.console:
                self.console.clear_screen()
                self.console.display_header()
            
            console_print(f"\n[menu_title]Select Replacement for {coach.first_name} {coach.last_name}[/menu_title]")
            console_print("\n[bold]Current Coach:[/bold]")
            current_table = Table(show_header=True)
            current_table.add_column("Name")
            current_table.add_column("Rating")
            current_table.add_row(
                f"{coach.first_name} {coach.last_name}",
                str(coach.skill_rating)
            )
            console_print(current_table)
            
            console_print("\n[bold]Available Replacements:[/bold]")
            table = Table(show_header=True)
            table.add_column("#", justify="center")
            table.add_column("Name")
            table.add_column("Rating")
            
            for idx, replacement_coach in enumerate(replacements, 1):
                table.add_row(
                    str(idx),
                    f"{replacement_coach.first_name} {replacement_coach.last_name}",
                    str(replacement_coach.skill_rating)
                )
            console_print(table)
            
            choice = Prompt.ask(
                "\nSelect replacement number",
                choices=[str(i) for i in range(1, len(replacements) + 1)],
                show_choices=False
            )
            
            # Get the selected replacement
            replacement_idx = int(choice) - 1
            new_coach = replacements[replacement_idx]
            
            # Clear screen and show confirmation
            if self.console:
                self.console.clear_screen()
                self.console.display_header()
            
            console_print("\n[menu_title]Coach Change Complete[/menu_title]")
            console_print("\n[bold]Coach Cut:[/bold]")
            cut_table = Table(show_header=True)
            cut_table.add_column("Name")
            cut_table.add_column("Rating")
            cut_table.add_row(
                f"{coach.first_name} {coach.last_name}",
                str(coach.skill_rating)
            )
            console_print(cut_table)
            
            console_print("\n[bold]New Coach:[/bold]")
            new_table = Table(show_header=True)
            new_table.add_column("Name")
            new_table.add_column("Rating")
            new_table.add_row(
                f"{new_coach.first_name} {new_coach.last_name}",
                str(new_coach.skill_rating)
            )
            console_print(new_table)
            
            logging.info(f'Replaced coach {coach.first_name} {coach.last_name} with {new_coach.first_name} {new_coach.last_name}')
            self.last_roster_change_week = current_week
            self.changes_this_week = True
            
            console_print("\nPress Enter to continue...", end="")
            input()
            
            return True, new_coach
            
        except KeyboardInterrupt:
            return False, None 