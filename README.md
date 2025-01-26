# Valorant Team Manager

A text-based management simulation game where players act as the General Manager of a Valorant team competing in the Valorant Champions Tour.

## Overview

This game is inspired by Football Manager but focuses on the unique aspects of managing a professional Valorant esports team. Players make strategic decisions about team management, player acquisitions, and roster development.

## Technical Stack

- **Language**: Python
- **UI**: Terminal-based using Rich Console
- **Database**: SQLite
- **Mode**: Single-player

## Project Structure
alorant-team-manager/
├── main.py # Application entry point
├── database/ # Database related modules
│ ├── init.py
│ ├── db_manager.py # Database connection and operations
│ └── models.py # SQLite database models
├── entities/ # Game entity classes
│ ├── init.py
│ ├── player.py # Player class and attributes
│ ├── team.py # Team management
│ ├── coach.py # Coach management
├── game/ # Core game logic
│ ├── init.py
│ ├── calendar.py # In-game time management
│ ├── game_state.py # Game state tracking
│ └── events/ # Game events
│ ├── init.py
│ ├── random_events.py
│ ├── team_events.py
│ └── player_events.py
├── ui/ # User interface
│ ├── init.py
│ ├── console.py # Rich console setup
│ ├── displays.py # UI display components
│ └── menus.py # Menu systems
└── utils/ # Utility functions
├── init.py
├── config.py # Configuration settings
└── constants.py # Game constants

## Core Features

### Team Management
- Full roster management
- Player transfers and signings
- Contract negotiations
- Coach hiring and firing
- Team strategy development

### Player Management
- Player attributes and statistics
- Contract management
- Performance tracking
- Development and training

### Game Events
1. **Regular Events**
   - Daily training sessions
   - Match scheduling
   - Transfer windows
   - Contract renewals

2. **Random Events**
   - Player injuries
   - Player suspensions
   - Emergency transfers
   - Team morale events
   - Player retirements

## Game Cycle

The game progresses on a daily cycle where players can:
1. Review team status
2. Make management decisions
3. Handle incoming events
4. Advance to the next day

## Development

### Setup
1. Clone the repository
2. Install dependencies:

```
pip install -r requirements.txt
```

### Running the Game

```
python3 main.py
```

### Logging System
- Development mode: `ENABLE_LOGGING = False`
- Production mode: `ENABLE_LOGGING = True`
- Log files stored in `logs/` directory
- Daily log rotation: `app_YYYYMMDD.log`

### Error Handling
- Comprehensive error logging
- Stack trace capture
- Graceful error recovery

## Project Structure

### Entities Package
The `entities` package contains the core domain entities for the valorant team manager game.

Available Entities:
- `Team`: Represents a valorant team with properties for name, players, coach, region, and fan base
- `Player`: Represents a player with attributes including:
  - Personal details (name, age, nationality, nickname)
  - Role and team affiliation
  - Contract status (expiry, salary, value)
  - Status flags (injured, suspended)
- `Coach`: Represents a team coach with name and team association

Usage:
```python
from entities import Team, Player, Coach

# Create a new player
player = Player(
    first_name="John",
    last_name="Doe",
    age=22,
    role="Duelist",
    nationality="USA",
    nickname="JD"
)

# Create a team
team = Team(
    name="Team Ace",
    players=[],
    coach=None,
    region="NA",
    fans=10000
)


```

## Logging
The application includes comprehensive logging functionality that can be enabled/disabled through the `ENABLE_LOGGING` flag in `main.py`.

### UI Package
The `ui` package provides the terminal-based user interface components for the game.

Components:
- `Console`: Core console I/O operations wrapper
  - Screen clearing
  - Formatted output
  - User input handling
  - Header formatting
- `Menu`: Menu system implementation
  - Menu items with key bindings
  - Action callbacks
  - Input validation
- `GameDisplay`: Game-specific display components
  - New game creation interface
  - Game loading interface
  - (More displays to be added)

Usage Example:
```python
from ui import Console, Menu, MenuItem, GameDisplay

# Create menu items
menu_items = [
    MenuItem("1", "New Game", GameDisplay.create_new_game),
    MenuItem("2", "Load Game", GameDisplay.load_game),
    MenuItem("q", "Quit", exit)
]

# Create and display menu
main_menu = Menu("Main Menu", menu_items)
main_menu.display()
```

---