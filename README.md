# Valorant Team Manager

A text-based management simulation game where players act as the General Manager of a Valorant team competing in the Valorant Champions Tour.

## Overview

This game is inspired by Football Manager but focuses on the unique aspects of managing a professional Valorant esports team. Players make strategic decisions about team management, player acquisitions, and roster development.

## Technical Stack

- **Language**: Python
- **UI**: Rich Console for enhanced terminal UI
- **Database**: SQLite
- **Mode**: Single-player

## Project Structure
```
valorant-team-manager/
├── src/
│   ├── ui/
│   │   └── console_manager.py  # UI-related functionality
│   ├── utils/
│   │   └── logger.py          # Logging configuration
│   └── game/
│       └── game_manager.py    # Game logic and flow
├── main.py                    # Application entry point
└── README.md
```

## Code Organization

The project follows a modular structure where:
- `main.py` serves only as the entry point and doesn't contain any function or class definitions
- All game logic is organized into appropriate modules under the `src/` directory
- UI components are separated from game logic
- Utility functions (like logging) are isolated in their own modules

### Module Responsibilities

- **console_manager.py**: Handles all UI-related functionality and terminal display
- **logger.py**: Manages logging configuration and setup
- **game_manager.py**: Contains core game logic and flow control

This modular structure allows for:
- Better code organization and maintainability
- Easier testing and debugging
- Clear separation of concerns
- Simplified future expansions

## Core Features

### User Interface
- Enhanced terminal-based UI using Rich Console
- Styled menus and information panels
- Clear visual hierarchy and navigation
- Color-coded information display

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

### Error Handling
- Comprehensive error logging
- Stack trace capture
- Graceful error recovery

## Setup and Structure

### Main Entry Point
The game can be launched through `main.py`, which provides the following options:
- Create a new game
- Load an existing game
- Quit the game

### Logging
The application includes comprehensive logging functionality:
- Log files are stored in a 'logs' directory
- Logs include timestamps and log levels
- Separate logging for game events and errors
- Console output is focused on user interface only

#### Logging System
- Development mode: `ENABLE_LOGGING = False`
- Production mode: `ENABLE_LOGGING = True`
- Log files stored in `logs/` directory
- Daily log rotation: `app_YYYYMMDD.log`

## Dependencies
- Rich: For enhanced terminal user interface
- Other dependencies listed in requirements.txt
