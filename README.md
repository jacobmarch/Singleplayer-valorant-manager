# Valorant Team Manager

## Quick Start

```bash
pip install -r requirements.txt
python3 main.py
```

## Technical Overview
- **Language**: Python
- **UI Engine**: Rich Console
- **Database**: SQLite
- **Architecture**: Modular single-player application

## Project Architecture

### Directory Structure
valorant-team-manager/
├── src/
│ ├── ui/
│ │ └── console_manager.py # Terminal UI & display logic
│ ├── utils/
│ │ └── logger.py # Logging system
│ └── game/
│ └── game_manager.py # Core game engine
├── main.py # Entry point
└── README.md


### Core Modules
| Module | Path | Responsibility |
|--------|------|----------------|
| Entry Point | `main.py` | Application bootstrap, no business logic |
| Game Engine | `game_manager.py` | Game loop, state management, event handling |
| UI Manager | `console_manager.py` | Terminal rendering, user input, display formatting |
| Logger | `logger.py` | Error tracking, event logging, debugging support |

### Design Principles
- Strict separation of concerns (UI/Logic/Utils)
- Modular architecture for testability
- Centralized game state management
- Event-driven gameplay mechanics

## Development Guide

### Logging System
- **Development**: `ENABLE_LOGGING = False`
- **Production**: `ENABLE_LOGGING = True`
- **Location**: `logs/app_YYYYMMDD.log`
- **Format**: `timestamp - level - message`

### Error Handling
1. All exceptions logged with stack traces
2. Graceful degradation implemented
3. User-friendly error messages in UI
4. Automatic error recovery where possible

### Game Systems

#### UI Components
- Rich Console-based interface
- Styled menus & information panels
- Color-coded information hierarchy
- Cross-platform terminal compatibility

#### Core Game Loop
1. State review
2. Management decisions
3. Event processing
4. Day advancement

#### Event System
- **Regular Events**
  - Training sessions
  - Match scheduling
  - Transfer windows
  - Contract management

- **Random Events**
  - Injuries
  - Suspensions
  - Emergency transfers
  - Morale events
  - Retirements

#### Management Systems
- **Team Operations**
  - Roster management
  - Transfer system
  - Contract negotiations
  - Coaching staff
  - Strategy planning

- **Player Systems**
  - Attribute tracking
  - Performance metrics
  - Contract handling
  - Development progression

## Dependencies
- **Rich**: Terminal UI framework
- Full list in `requirements.txt`

## About
A text-based Valorant team management simulator inspired by Football Manager, focusing on professional esports team management and strategic decision-making.