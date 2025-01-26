import logging
import os
from datetime import datetime

class GameLogger:
    @staticmethod
    def setup_logging():
        """
        Configure logging for the game with file handler only.
        Creates a 'logs' directory if it doesn't exist.
        """
        if not os.path.exists('logs'):
            os.makedirs('logs')

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f'logs/game_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename)
            ]
        )
        
        logging.info('Logging system initialized') 