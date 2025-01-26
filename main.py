import logging
import sys
import os
from datetime import datetime
from ui import Console, Menu, MenuItem, GameDisplay

def setup_logging(enable_logging=False):
    """
    Configure logging with timestamp, level, and message format
    Args:
        enable_logging (bool): Flag to enable/disable all logging
    """
    if enable_logging:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configure logging only if enabled
        logging_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=logging_format,
            handlers=[
                logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log')
            ]
        )
        logging.info("Logging initialized")
    else:
        # Disable all logging
        logging.getLogger().setLevel(logging.CRITICAL + 1)
        logging.disable(logging.CRITICAL)

def create_main_menu() -> Menu:
    """Create the main menu with all options"""
    return Menu("Main Menu", [
        MenuItem("1", "Create New Game", GameDisplay.create_new_game),
        MenuItem("2", "Load Game", GameDisplay.load_game),
        MenuItem("Q", "Quit", sys.exit)
    ])

def main(enable_logging=False):
    """
    Main entry point for the application.
    Args:
        enable_logging (bool): Flag to enable/disable all logging
    """
    # Set up logging first
    setup_logging(enable_logging)
    
    if enable_logging:
        logging.info("Application starting...")
    
    try:
        # Create and display main menu
        main_menu = create_main_menu()
        
        while True:
            main_menu.display()
            
    except Exception as e:
        if enable_logging:
            logging.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)
    
    if enable_logging:
        logging.info("Application completed successfully")

if __name__ == "__main__":
    # You can modify this flag to enable/disable logging
    ENABLE_LOGGING = True
    main(ENABLE_LOGGING)
