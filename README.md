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
│ │ └── game_manager.py # Core game engine
│ │ └── data.py # Game data
│ │ └── person.py # Player and coach generation
│ │ └── roster.py # League management and scheduling
├── main.py # Entry point
└── README.md


### Core Modules
| Module | Path | Responsibility |
|--------|------|----------------|
| Entry Point | `main.py` | Application bootstrap, no business logic |
| Game Engine | `game_manager.py` | Game loop, state management, event handling |
| UI Manager | `console_manager.py` | Terminal rendering, user input, display formatting |
| Logger | `logger.py` | Error tracking, event logging, debugging support |
| Player and Coach | `person.py` | Classes and functions for player and coach generation |
| League Manager | `roster.py` | Team ratings, match scheduling, league management |

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

- **League Systems**
  - Team ratings (0-100 scale)
  - Round-robin match scheduling
  - Win/loss record tracking
  - League standings
  - Match history

## Dependencies
- **Rich**: Terminal UI framework
- Full list in `requirements.txt`

## About
A text-based Valorant team management simulator inspired by Football Manager, focusing on professional esports team management and strategic decision-making.

## Recent Updates
- Added playoff system with quarterfinals, semifinals, and finals
- Best-of-3 matches for regular season and early playoffs
- Best-of-5 matches for the grand finals
- Playoff seeding based on regular season record
- Updated match simulation to use best-of-3 format with proper round scoring
- Added detailed match view showing map-by-map scores
- Each map is played to 13 rounds with win-by-2 requirement
- Added overtime system for 12-12 maps
- Added main dashboard with roster management and standings view
- Added ability to cut and replace players and coaches
- Each team can make one roster change per week
- Added league standings sorted by wins and team rating
- Added league management system with team ratings and scheduling
- Each team now has a rating from 0-100 (normally distributed)
- Implemented round-robin schedule generation for matches
- Added display of team ratings and upcoming matches
- Added player and coach generation system
- Each team gets 5 players (one for each position) and a coach
- Each person has a randomly generated name and skill rating (1-100)
- Added display of team members in formatted tables

## Features
### Dashboard
- View current league standings
- Manage team roster
- Play next scheduled game
- View season history
- Track multiple seasons with the same team

### Season History
- Track all completed seasons
- View champions and their records
- Track your team's performance across seasons
- Year-by-year progression
- Final standings positions

### Roster Management
- View current team roster with player positions and ratings
- Cut and replace players while maintaining positions
- Cut and replace coach
- Automatic team rating updates after roster changes
- Three replacement options for each cut player/coach

### League System
- Team ratings (0-100 scale)
- Round-robin match scheduling
- Win/loss record tracking
- League standings sorted by wins and rating
- Match history
- Playoff system:
  - Top 8 teams qualify
  - Single elimination bracket
  - Seeded by regular season record (1v8, 4v5, 2v7, 3v6)
  - Best-of-3 matches for quarterfinals and semifinals
  - Best-of-5 grand finals

### Match System
- Best-of-3 match format (regular season and early playoffs)
- Best-of-5 match format (grand finals)
- Each map played to 13 rounds
- Win-by-2 requirement in all maps
- Overtime system when score reaches 12-12
- Detailed match statistics including:
  - Map-by-map scores
  - Round counts for each map
  - Match winner and final score
  - Individual map winners
  - Playoff information and seeding

## Project Structure
- `src/game/person.py`: Contains classes and functions for player and coach generation
- `src/game/game_manager.py`: Main game management logic
- `src/game/roster.py`: League management and scheduling system
- `data/`: Contains name data files for generating random names

## Requirements
- Name data files (`first_names.txt` and `last_names.txt`) in the `data` directory