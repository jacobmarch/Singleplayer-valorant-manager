"""
UI package initialization.
Exposes the main UI components for easy importing.
"""

from .console import Console
from .menus import Menu, MenuItem
from .displays import GameDisplay

__all__ = [
    'Console',
    'Menu',
    'MenuItem',
    'GameDisplay'
]
