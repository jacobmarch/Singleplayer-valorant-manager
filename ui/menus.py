import logging
from typing import List, Callable, Dict
from .console import Console

class MenuItem:
    def __init__(self, key: str, description: str, action: Callable):
        self.key = key
        self.description = description
        self.action = action

class Menu:
    def __init__(self, title: str, items: List[MenuItem]):
        self.title = title
        self.items = items
        
    def display(self) -> None:
        """Display the menu and handle user input"""
        while True:
            Console.clear_screen()
            Console.print_header(self.title)
            
            # Display menu items
            for item in self.items:
                Console.print(f"[{item.key}] {item.description}")
            
            # Get user input
            choice = Console.input("\nEnter your choice: ").strip().lower()
            
            # Find and execute the chosen action
            for item in self.items:
                if item.key.lower() == choice:
                    logging.info(f"Menu action selected: {item.description}")
                    item.action()
                    return
            
            Console.print("\nInvalid choice. Please try again.")
