import logging
from typing import Any, Optional

class Console:
    """
    Handles console input/output operations
    """
    @staticmethod
    def print(message: str) -> None:
        """Print a message to the console"""
        print(message)
    
    @staticmethod
    def input(prompt: str = "") -> str:
        """Get input from the user with an optional prompt"""
        return input(prompt)
    
    @staticmethod
    def clear_screen() -> None:
        """Clear the console screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_header(title: str) -> None:
        """Print a formatted header"""
        Console.print("\n" + "=" * 50)
        Console.print(f"{title:^50}")
        Console.print("=" * 50 + "\n")
