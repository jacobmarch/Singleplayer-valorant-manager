import logging
from .console import Console

class GameDisplay:
    @staticmethod
    def create_new_game() -> None:
        """Handle new game creation"""
        Console.clear_screen()
        Console.print_header("Create New Game")
        Console.print("Creating new game...")
        logging.info("New game creation initiated")
        # Add game creation logic here
        Console.input("Press Enter to continue...")

    @staticmethod
    def load_game() -> None:
        """Handle loading an existing game"""
        Console.clear_screen()
        Console.print_header("Load Game")
        Console.print("Loading game...")
        logging.info("Game load initiated")
        # Add game loading logic here
        Console.input("Press Enter to continue...")
