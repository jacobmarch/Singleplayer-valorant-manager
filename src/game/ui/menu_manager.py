from rich.prompt import Prompt
from rich.table import Table
from typing import Optional, Callable
from src.ui.console_manager import ConsoleManager

class MenuManager:
    def __init__(self, console: ConsoleManager):
        self.console = console

    def display_main_menu(self) -> str:
        """Display and handle the main menu options"""
        self.console.clear_screen()
        self.console.display_header()
        
        # Display menu in a compact format
        self.console.console.print("\n[menu_title]Game Menu[/menu_title]")
        self.console.console.print(self.console.create_menu_table())
        
        try:
            return Prompt.ask(
                "\nEnter your choice",
                choices=["1", "2", "3"],
                show_choices=False
            )
        except KeyboardInterrupt:
            return "3"  # Return quit option on interrupt

    def display_dashboard_menu(self, is_playoffs: bool, playoffs_completed: bool) -> str:
        """Display the dashboard menu options"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        
        # First option changes based on game state
        if playoffs_completed:
            table.add_row("[menu_option]1.[/menu_option]", "[grey]Season Complete[/grey]")
        elif is_playoffs:
            next_round = self._get_next_playoff_round()
            table.add_row("[menu_option]1.[/menu_option]", f"[white]Advance to {next_round}[/white]")
        else:
            table.add_row("[menu_option]1.[/menu_option]", "[white]Play Next Week[/white]")
            
        # Standard options
        table.add_row("[menu_option]2.[/menu_option]", "[white]Manage Roster[/white]")
        table.add_row("[menu_option]3.[/menu_option]", "[white]View Standings[/white]")
        table.add_row("[menu_option]4.[/menu_option]", "[white]View Schedule[/white]")
        table.add_row("[menu_option]5.[/menu_option]", "[white]View History[/white]")
        table.add_row("[menu_option]6.[/menu_option]", "[white]Return to Main Menu[/white]")
        
        self.console.console.print(table)
        
        try:
            return Prompt.ask(
                "\nEnter your choice",
                choices=["1", "2", "3", "4", "5", "6"],
                show_choices=False
            )
        except KeyboardInterrupt:
            return "6"  # Return to main menu on interrupt

    def display_schedule_menu(self) -> str:
        """Display schedule view menu options"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_row("[menu_option]1.[/menu_option]", "[white]Toggle Schedule View[/white]")
        table.add_row("[menu_option]2.[/menu_option]", "[white]Return to Dashboard[/white]")
        
        self.console.console.print(table)
        
        try:
            return Prompt.ask(
                "\nEnter your choice",
                choices=["1", "2"],
                show_choices=False
            )
        except KeyboardInterrupt:
            return "2"  # Return to dashboard on interrupt

    def display_roster_menu(self) -> str:
        """Display roster management menu options"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_row("[menu_option]1.[/menu_option]", "[white]Cut Player[/white]")
        table.add_row("[menu_option]2.[/menu_option]", "[white]Cut Coach[/white]")
        table.add_row("[menu_option]3.[/menu_option]", "[white]Return to Dashboard[/white]")
        
        self.console.console.print(table)
        
        try:
            return Prompt.ask(
                "\nEnter your choice",
                choices=["1", "2", "3"],
                show_choices=False
            )
        except KeyboardInterrupt:
            return "3"  # Return to dashboard on interrupt

    def confirm_action(self, prompt: str) -> bool:
        """Generic confirmation prompt"""
        try:
            return Prompt.ask(
                prompt,
                choices=["y", "n"],
                show_choices=False
            ) == "y"
        except KeyboardInterrupt:
            return False

    def get_numeric_choice(self, max_value: int, cancel_option: bool = True) -> Optional[int]:
        """Get a numeric choice from the user"""
        choices = [str(i) for i in range(1, max_value + 1)]
        if cancel_option:
            choices.append('c')
            
        try:
            choice = Prompt.ask(
                "\nEnter your choice",
                choices=choices,
                show_choices=False
            )
            return None if choice == 'c' else int(choice)
        except KeyboardInterrupt:
            return None

    def _get_next_playoff_round(self) -> str:
        """Helper method to get the next playoff round name"""
        return {
            "quarterfinal": "Semifinals",
            "semifinal": "Finals",
            "final": "Championship",
        }.get("", "Next Round") 