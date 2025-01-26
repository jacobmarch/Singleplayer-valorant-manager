import logging
from rich.prompt import Prompt
from src.ui.console_manager import ConsoleManager

class GameManager:
    def __init__(self):
        self.console = ConsoleManager()

    def create_new_game(self):
        """
        Initialize a new game session.
        """
        logging.info('Creating new game session')
        self.console.clear_screen()
        self.console.display_header()
        self.console.console.print("\n[info]Starting new game...[/info]")
        # TODO: Implement new game creation
        self.console.console.print("[yellow]New game creation will be implemented soon[/yellow]")

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