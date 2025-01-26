import logging
from src.utils.logger import GameLogger
from src.game.game_manager import GameManager

def main():
    """
    Main entry point for the game.
    Sets up logging and initializes the game manager.
    """
    GameLogger.setup_logging()
    logging.info('Game started')
    
    game = GameManager()
    game.run()
    
    logging.info('Game terminated')

if __name__ == "__main__":
    main()
