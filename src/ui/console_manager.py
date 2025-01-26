import os
from rich.console import Console
from rich.text import Text
from rich.theme import Theme
from rich.table import Table

# Custom theme for Rich
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "menu_title": "cyan bold",
    "menu_option": "green",
})

class ConsoleManager:
    def __init__(self):
        self.console = Console(theme=custom_theme, height=None)

    def clear_screen(self):
        """
        Clear the terminal screen in a cross-platform way and move cursor to top.
        """
        if os.name == 'nt':  # for Windows
            os.system('cls')
        else:  # for Unix/Linux/MacOS
            os.system('clear')
        # Move cursor to top-left position
        self.console.clear()

    def display_header(self):
        """
        Display a compact game header.
        """
        self.console.print(
            Text("Valorant Team Manager", justify="center", style="cyan bold"),
            Text("\nA Text-Based Management Simulation", justify="center", style="cyan"),
        )

    def create_menu_table(self):
        """
        Create a compact styled table for the menu options.
        """
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_row("[menu_option]1.[/menu_option]", "[white]New Game[/white]")
        table.add_row("[menu_option]2.[/menu_option]", "[white]Load Game[/white]")
        table.add_row("[menu_option]3.[/menu_option]", "[white]Quit[/white]")
        return table 