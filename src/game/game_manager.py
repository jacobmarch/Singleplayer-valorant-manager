import logging
from datetime import datetime
from typing import List, Optional
from src.ui.console_manager import ConsoleManager
from src.game.data import REGIONS, REGION_LIST
from src.game.person import Player, Coach, generate_team_members
from src.game.roster.league import LeagueManager, Match
from src.game.season_history import SeasonHistory
from src.game.ui.display_manager import DisplayManager
from src.game.ui.menu_manager import MenuManager
from src.game.roster.roster_manager import RosterManager
from src.game.simulation.match_simulator import MatchSimulator

class GameManager:
    def __init__(self):
        self.console = ConsoleManager()
        self.display_manager = DisplayManager(self.console)
        self.menu_manager = MenuManager(self.console)
        self.selected_region = None
        self.selected_team = None
        self.players: Optional[List[Player]] = None
        self.coach: Optional[Coach] = None
        self.league_manager: Optional[LeagueManager] = None
        self.season_history = SeasonHistory()
        
        # Load name data for roster management
        try:
            with open('data/first_names.txt', 'r') as f:
                first_names = [line.strip() for line in f.readlines()]
            with open('data/last_names.txt', 'r') as f:
                last_names = [line.strip() for line in f.readlines()]
            self.roster_manager = RosterManager(first_names, last_names)
            self.roster_manager.console = self.console  # Pass console to roster manager
        except FileNotFoundError as e:
            logging.error(f'Name data files not found: {str(e)}')
            raise
        except Exception as e:
            logging.error(f'Error loading name data: {str(e)}')
            raise

    def get_current_week(self) -> int:
        """Get the current week number based on the first uncompleted week"""
        if not self.league_manager:
            return 1
            
        # Sort matches by week and find first uncompleted week
        sorted_matches = sorted(self.league_manager.schedule, key=lambda x: x.week)
        for match in sorted_matches:
            if not match.completed:
                return match.week
        
        # If all matches completed, return last week + 1
        return sorted_matches[-1].week + 1 if sorted_matches else 1

    def create_new_game(self):
        """Initialize a new game session with region and team selection."""
        logging.info('Creating new game session')
        self.console.clear_screen()
        self.console.display_header()
        
        # Region Selection
        self.console.console.print("\n[menu_title]Select Your Region[/menu_title]")
        self.console.console.print(self.display_manager.display_region_selection(REGION_LIST))
        
        try:
            region_choice = self.menu_manager.get_numeric_choice(len(REGION_LIST), cancel_option=False)
            if not region_choice:
                return
                
            self.selected_region = REGION_LIST[region_choice - 1]
            logging.info(f'User selected region: {self.selected_region}')
            
            # Team Selection
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print(f"\n[menu_title]Select Your Team from {self.selected_region}[/menu_title]")
            self.console.console.print(self.display_manager.display_team_selection(REGIONS[self.selected_region]))
            
            team_choice = self.menu_manager.get_numeric_choice(len(REGIONS[self.selected_region]), cancel_option=False)
            if not team_choice:
                return
                
            self.selected_team = REGIONS[self.selected_region][team_choice - 1]
            logging.info(f'User selected team: {self.selected_team}')
            
            # Generate team members
            self.players, self.coach = generate_team_members(
                self.roster_manager.first_names,
                self.roster_manager.last_names
            )
            
            # Initialize league with player data
            self.league_manager = LeagueManager(
                region=self.selected_region,
                teams=REGIONS[self.selected_region],
                player_team=self.selected_team,
                players=self.players,
                coach=self.coach
            )
            self.league_manager.generate_schedule()
            
            # Display team information
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print(f"\n[green]You have selected {self.selected_team} from {self.selected_region}![/green]")
            
            # Display team members
            players_table, coach_table = self.display_manager.display_team_members(self.players, self.coach)
            self.console.console.print("\n")
            self.console.console.print(players_table)
            self.console.console.print("\n")
            self.console.console.print(coach_table)
            
            # Wait for user input before showing league ratings
            self.console.console.print("\n[info]Press Enter to view league ratings...[/info]", end="")
            input()
            
            # Display league information
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print("\n[menu_title]League Overview[/menu_title]")
            ratings_table = self.display_manager.display_team_ratings(
                self.league_manager.team_ratings,
                self.selected_team,
                self.selected_region
            )
            if ratings_table:
                self.console.console.print("\n")
                self.console.console.print(ratings_table)
            
            # Wait for user input before showing schedule
            self.console.console.print("\n[info]Press Enter to view upcoming matches...[/info]", end="")
            input()
            
            # Display schedule
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print("\n[menu_title]Upcoming Matches[/menu_title]")
            schedule_table = self.display_manager.display_full_schedule(
                self.league_manager.schedule,
                self.selected_team,
                self.get_current_week()
            )
            if schedule_table:
                self.console.console.print("\n")
                self.console.console.print(schedule_table)
            
            # After displaying schedule, go to dashboard
            self.display_dashboard()
            
        except KeyboardInterrupt:
            logging.info('User interrupted team selection')
            self.console.console.print("\n[warning]Team selection interrupted[/warning]")
            return
        except Exception as e:
            logging.error(f'Error during team creation: {str(e)}')
            self.console.console.print("\n[error]An error occurred during team creation[/error]")
            return

    def display_dashboard(self):
        """Display the main game dashboard and handle user input"""
        while True:
            self.console.clear_screen()
            self.console.display_header()
            
            # Display current standings
            standings_table = self.display_manager.display_standings(
                self.league_manager.team_ratings,
                self.selected_team,
                self.selected_region
            )
            if standings_table:
                self.console.console.print("\n")
                self.console.console.print(standings_table)
            
            # Display playoff status if applicable
            if self.league_manager.playoffs:
                playoff_round = self.league_manager.get_playoff_round_name()
                if playoff_round:
                    self.console.console.print(f"\n[bold]{playoff_round.title()} Round[/bold]")
                    if self.selected_team in [t.name for t in self.league_manager.playoffs.teams if not t.eliminated]:
                        self.console.console.print("[green]Your team is in the playoffs![/green]")
                    else:
                        self.console.console.print("[yellow]Your team did not qualify for playoffs[/yellow]")
            
            # Display dashboard options and handle input
            self.console.console.print("\n[menu_title]Dashboard[/menu_title]")
            choice = self.menu_manager.display_dashboard_menu(
                is_playoffs=bool(self.league_manager.playoffs),
                playoffs_completed=bool(self.league_manager.playoffs and self.league_manager.playoffs.completed)
            )
            
            if choice == "1" and not (self.league_manager.playoffs and self.league_manager.playoffs.completed):
                self.play_next_week()
            elif choice == "2":
                self.display_roster_management()
            elif choice == "3":
                self.display_standings_view()
            elif choice == "4":
                self.display_schedule_menu()
            elif choice == "5":
                self.display_history()
            elif choice == "6":
                break

    def display_roster_management(self):
        """Display roster management options and handle user input"""
        while True:
            self.console.clear_screen()
            self.console.display_header()
            
            # Display current roster
            players_table, coach_table = self.display_manager.display_team_members(self.players, self.coach)
            self.console.console.print("\n[menu_title]Current Roster[/menu_title]")
            self.console.console.print("\n")
            self.console.console.print(players_table)
            self.console.console.print("\n")
            self.console.console.print(coach_table)
            
            # Check if roster changes are allowed this week
            current_week = self.get_current_week()
            if not self.roster_manager.can_make_roster_change(current_week):
                self.console.console.print("\n[warning]You have already made a roster change this week. Wait until next week for further changes.[/warning]")
                self.console.console.print("\nPress Enter to return to dashboard...", end="")
                input()
                break
            
            # Display options and handle input
            self.console.console.print("\n[menu_title]Roster Management[/menu_title]")
            choice = self.menu_manager.display_roster_menu()
            
            if choice == "1":
                success, new_player = self.roster_manager.manage_player_cut(
                    self.players,
                    self.console.console.print,
                    current_week
                )
                if success and new_player:
                    # Update the player in the roster
                    selected_idx = next(i for i, p in enumerate(self.players) if p.position == new_player.position)
                    self.players[selected_idx] = new_player
                    # Update team rating
                    if self.league_manager:
                        self.league_manager.team_ratings[self.selected_team].rating = (
                            self.league_manager._calculate_user_team_rating(self.players, self.coach)
                        )
                    break
            elif choice == "2":
                success, new_coach = self.roster_manager.manage_coach_cut(
                    self.coach,
                    self.console.console.print,
                    current_week
                )
                if success and new_coach:
                    self.coach = new_coach
                    # Update team rating
                    if self.league_manager:
                        self.league_manager.team_ratings[self.selected_team].rating = (
                            self.league_manager._calculate_user_team_rating(self.players, self.coach)
                        )
                    break
            elif choice == "3":
                break

    def display_schedule_menu(self):
        """Handle the schedule view menu and options"""
        team_only = True  # Start with team schedule by default
        
        while True:
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print("\n[menu_title]Season Schedule[/menu_title]")
            
            # Display current filter status
            filter_status = "[green]Your Team Schedule[/]" if team_only else "[white]Full League Schedule[/]"
            self.console.console.print(f"\nCurrently showing: {filter_status}")
            
            # Display schedule
            schedule_table = self.display_manager.display_full_schedule(
                self.league_manager.schedule,
                self.selected_team,
                self.get_current_week(),
                team_only
            )
            if schedule_table:
                self.console.console.print("\n")
                self.console.console.print(schedule_table)
            
            # Display options and handle input
            self.console.console.print("\n[menu_title]Options[/menu_title]")
            choice = self.menu_manager.display_schedule_menu()
            
            if choice == "1":
                team_only = not team_only
            elif choice == "2":
                break

    def display_standings_view(self):
        """Display current standings view"""
        self.console.clear_screen()
        self.console.display_header()
        standings_table = self.display_manager.display_standings(
            self.league_manager.team_ratings,
            self.selected_team,
            self.selected_region
        )
        if standings_table:
            self.console.console.print("\n")
            self.console.console.print(standings_table)
        input("\nPress Enter to continue...")

    def display_history(self):
        """Display the history of all completed seasons"""
        self.console.clear_screen()
        self.console.display_header()
        
        if not self.season_history.seasons:
            self.console.console.print("\n[yellow]No completed seasons yet[/yellow]")
            self.console.console.print("\nPress Enter to return to dashboard...", end="")
            input()
            return
            
        self.console.console.print("\n[menu_title]Season History[/menu_title]")
        history_table = self.display_manager.display_season_history(
            self.season_history.get_season_history(),
            self.selected_team
        )
        self.console.console.print("\n")
        self.console.console.print(history_table)
        self.console.console.print("\nPress Enter to return to dashboard...", end="")
        input()

    def play_next_week(self):
        """Handle playing the next week of matches"""
        if not self.league_manager:
            return
            
        current_week = self.get_current_week()
        
        # Check if regular season is complete and playoffs haven't started
        if not self.league_manager.playoffs and all(m.completed for m in self.league_manager.schedule):
            self.league_manager.regular_season_complete = True
            self.league_manager.start_playoffs()
            current_week += 1  # Start playoffs next week
            
            # Show playoff qualification message and handle playoff start
            self._handle_playoff_start()
            return
            
        # Get matches to be played
        matches_to_play = self._get_matches_to_play(current_week)
        if not matches_to_play:
            self.console.console.print("[error]No matches found for the current week. Check the logs for details.[/error]")
            input("\nPress Enter to continue...")
            return

        # Display upcoming matches and confirm simulation
        self._display_upcoming_matches(matches_to_play, current_week)
        
        # Confirm with user
        if not self.menu_manager.confirm_action("\nReady to play matches?"):
            return

        # Simulate matches
        simulated_matches = MatchSimulator.simulate_week(matches_to_play, self.league_manager.team_ratings)
        
        # Display results and handle post-match actions
        self._handle_match_results(simulated_matches, current_week)

    def _handle_playoff_start(self):
        """Handle the start of playoffs"""
        self.console.clear_screen()
        self.console.display_header()
        self.console.console.print("\n[menu_title]Playoff Qualification[/menu_title]")
        
        # Get playoff teams and display qualification
        playoff_teams = sorted(
            [t for t in self.league_manager.playoffs.teams],
            key=lambda x: x.playoff_seed
        )
        
        qual_table = self.display_manager.display_playoff_qualification(
            playoff_teams,
            self.selected_team
        )
        self.console.console.print("\n")
        self.console.console.print(qual_table)
        
        if self.selected_team in [t.name for t in playoff_teams]:
            seed = next(t.playoff_seed for t in playoff_teams if t.name == self.selected_team)
            self.console.console.print(f"\n[green]Congratulations! Your team qualified for playoffs as the #{seed} seed![/green]")
        else:
            self.console.console.print("\n[yellow]Your team did not qualify for playoffs[/yellow]")
        
        self.console.console.print("\nPress Enter to continue...", end="")
        input()

    def _get_matches_to_play(self, current_week: int) -> List[Match]:
        """Get the list of matches to be played"""
        if self.league_manager.playoffs:
            matches = [m for m in self.league_manager.playoffs.matches if not m.completed]
            if not matches and not self.league_manager.playoffs.completed:
                # Handle advancement before generating new matches
                self._handle_playoff_advancement()
                current_week += 1
                self.league_manager.playoffs.advance_round()
                matches = self.league_manager.playoffs.generate_playoff_matches(current_week)
        else:
            matches = [m for m in self.league_manager.schedule if m.week == current_week and not m.completed]
        return matches

    def _display_upcoming_matches(self, matches: List[Match], current_week: int):
        """Display the upcoming matches"""
        self.console.clear_screen()
        self.console.display_header()
        
        if self.league_manager.playoffs:
            playoff_round = self.league_manager.get_playoff_round_name()
            round_name = playoff_round.title() if playoff_round else "Playoffs"
            self.console.console.print(f"\n[menu_title]{round_name} - Week {current_week}[/menu_title]")
            matches_table = self.display_manager.display_playoff_matches(matches, self.selected_team)
        else:
            self.console.console.print(f"\n[menu_title]Week {current_week} Matches[/menu_title]")
            # Show all matches for the week, not just the team's matches
            matches_table = self.display_manager.display_full_schedule(
                matches,
                self.selected_team,
                current_week,
                team_only=False  # Changed to False to show all matches
            )
            
        if matches_table:
            self.console.console.print("\n")
            self.console.console.print(matches_table)
            
        # Add a separator and highlight your team's matches
        your_matches = [m for m in matches if self.selected_team in [m.home_team, m.away_team]]
        if your_matches and not self.league_manager.playoffs:
            self.console.console.print("\n[bold]Your Team's Matches This Week:[/bold]")
            your_matches_table = self.display_manager.display_full_schedule(
                your_matches,
                self.selected_team,
                current_week,
                team_only=True
            )
            self.console.console.print(your_matches_table)

    def _handle_match_results(self, simulated_matches: List[Match], current_week: int):
        """Handle the results of simulated matches"""
        while True:
            self.console.clear_screen()
            self.console.display_header()
            
            # Show results
            if self.league_manager.playoffs:
                playoff_round = self.league_manager.get_playoff_round_name()
                round_name = playoff_round.title() if playoff_round else "Playoffs"
                self.console.console.print(f"\n[menu_title]{round_name} Results - Week {current_week}[/menu_title]")
            else:
                self.console.console.print(f"\n[menu_title]Week {current_week} Results[/menu_title]")
            
            # Split matches into your team's matches and others
            your_matches = [m for m in simulated_matches if self.selected_team in [m.home_team, m.away_team]]
            other_matches = [m for m in simulated_matches if m not in your_matches]
            
            if your_matches:
                self.console.console.print("\n[bold]Your Team's Results[/bold]")
                self.console.console.print(self.display_manager.display_match_results(your_matches, self.selected_team))
            
            if other_matches:
                self.console.console.print("\n[bold]Other Results[/bold]")
                self.console.console.print(self.display_manager.display_match_results(other_matches, self.selected_team))
            
            # Show options for viewing match details
            self.console.console.print("\n[menu_title]Options[/menu_title]")
            self.console.console.print("[menu_option]1.[/menu_option] [white]View Match Details[/white]")
            self.console.console.print("[menu_option]2.[/menu_option] [white]Continue[/white]")
            
            try:
                choice = self.menu_manager.get_numeric_choice(2, cancel_option=False)
                if choice == 1:
                    self._show_match_details(simulated_matches)
                else:
                    break
            except KeyboardInterrupt:
                break
            
        # Handle playoff advancement if needed
        if self.league_manager.playoffs and all(m.completed for m in simulated_matches):
            self._handle_playoff_advancement()

    def _show_match_details(self, matches: List[Match]):
        """Show detailed view of matches"""
        while True:
            self.console.clear_screen()
            self.console.display_header()
            
            # Display all matches with IDs
            self.console.console.print("\n[menu_title]Select Match to View Details[/menu_title]")
            matches_table = self.display_manager.display_full_schedule(
                matches,
                self.selected_team,
                self.get_current_week()
            )
            self.console.console.print("\n")
            self.console.console.print(matches_table)
            
            # Get match selection
            self.console.console.print("\nEnter match ID to view details (or 'c' to cancel)")
            try:
                choice = self.menu_manager.get_numeric_choice(len(matches))
                if not choice:
                    break
                    
                # Display match details
                selected_match = matches[choice - 1]
                details_table = self.display_manager.display_match_details(selected_match, self.selected_team)
                
                self.console.clear_screen()
                self.console.display_header()
                self.console.console.print("\n")
                self.console.console.print(details_table)
                
                self.console.console.print("\nPress Enter to continue...", end="")
                input()
                
            except KeyboardInterrupt:
                break

    def _handle_playoff_advancement(self):
        """Handle playoff advancement and season completion"""
        remaining = [t for t in self.league_manager.playoffs.teams if not t.eliminated]
        if remaining and len(remaining) < len(self.league_manager.playoffs.teams):
            self.console.clear_screen()
            self.console.display_header()
            
            playoff_round = self.league_manager.get_playoff_round_name()
            round_name = playoff_round.title() if playoff_round else "Playoffs"
            self.console.console.print(f"\n[menu_title]{round_name} Complete![/menu_title]")
            
            advance_table = self.display_manager.display_playoff_advancement(remaining, self.selected_team)
            self.console.console.print("\n[bold]Teams Advancing:[/bold]")
            self.console.console.print(advance_table)
            
            # Show next round info
            next_round = ""
            if playoff_round == "quarterfinal":
                next_round = "Semifinals"
            elif playoff_round == "semifinal":
                next_round = "Finals"
            
            if next_round:
                self.console.console.print(f"\n[bold]Advancing to {next_round}![/bold]")
            
            self.console.console.print("\nPress Enter to continue...", end="")
            input()
            
            # If playoffs are complete, handle season transition
            if self.league_manager.playoffs.completed:
                self._handle_season_completion()

    def _handle_season_completion(self):
        """Handle the completion of a season and transition to the next"""
        self.console.clear_screen()
        self.console.display_header()
        
        # Get champion info
        champion = self.league_manager.playoffs.champion
        champion_team = self.league_manager.team_ratings[champion]
        champion_record = (champion_team.wins, champion_team.losses)
        
        # Get player team info
        player_team = self.league_manager.team_ratings[self.selected_team]
        player_record = (player_team.wins, player_team.losses)
        
        # Calculate final standings position
        sorted_teams = sorted(
            self.league_manager.team_ratings.values(),
            key=lambda x: (x.wins, x.rating),
            reverse=True
        )
        player_position = next(i for i, t in enumerate(sorted_teams, 1) if t.name == self.selected_team)
        
        # Add season to history
        self.season_history.add_season(
            champion=champion,
            champion_record=champion_record,
            team_name=self.selected_team,
            team_record=player_record,
            team_position=player_position
        )
        
        # Display season summary
        self.console.console.print("\n[menu_title]Season Complete![/menu_title]")
        self.console.console.print(f"\n[bold]Champion:[/bold] {champion} ({champion_record[0]}-{champion_record[1]})")
        self.console.console.print(f"\n[bold]Your Team:[/bold] {self.selected_team}")
        self.console.console.print(f"Final Position: {player_position}")
        self.console.console.print(f"Record: {player_record[0]}-{player_record[1]}")
        
        self.console.console.print("\nPress Enter to start next season...", end="")
        input()
        
        # Start new season with same roster
        self._start_new_season()

    def _start_new_season(self):
        """Initialize a new season while keeping the same roster"""
        # Create new league manager with same roster
        self.league_manager = LeagueManager(
            region=self.selected_region,
            teams=REGIONS[self.selected_region],
            player_team=self.selected_team,
            players=self.players,
            coach=self.coach
        )
        self.league_manager.generate_schedule()
        
        # Reset roster manager's week tracking
        self.roster_manager.last_roster_change_week = 0
        self.roster_manager.changes_this_week = False
        
        # Display new season info
        self.console.clear_screen()
        self.console.display_header()
        self.console.console.print(f"\n[menu_title]Season {self.season_history.current_year}[/menu_title]")
        
        # Display team ratings
        ratings_table = self.display_manager.display_team_ratings(
            self.league_manager.team_ratings,
            self.selected_team,
            self.selected_region
        )
        if ratings_table:
            self.console.console.print("\n")
            self.console.console.print(ratings_table)
        
        # Display schedule
        self.console.console.print("\n[menu_title]Upcoming Schedule[/menu_title]")
        schedule_table = self.display_manager.display_full_schedule(
            self.league_manager.schedule,
            self.selected_team,
            self.get_current_week()
        )
        if schedule_table:
            self.console.console.print("\n")
            self.console.console.print(schedule_table)
        
        self.console.console.print("\nPress Enter to continue...", end="")
        input()

    def main_menu(self) -> bool:
        """
        Display and handle the main menu options.
        Returns False when the user wants to quit, True otherwise.
        """
        choice = self.menu_manager.display_main_menu()
        
        if choice == '1':
            logging.info('User selected: New Game')
            self.create_new_game()
            return True
        elif choice == '2':
            logging.info('User selected: Load Game')
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print("\n[yellow]Game loading will be implemented soon[/yellow]")
            return True
        else:
            logging.info('User selected: Quit Game')
            self.console.clear_screen()
            self.console.display_header()
            self.console.console.print("\n[cyan]Thanks for playing![/cyan]")
            return False

    def run(self):
        """Main game loop."""
        try:
            while self.main_menu():
                self.console.console.print("\nPress Enter to continue...", end="")
                input()
        except Exception as e:
            logging.error(f'Unexpected error occurred: {str(e)}', exc_info=True)
            self.console.clear_screen()
            self.console.console.print("[error]An unexpected error occurred. Check the logs for details.[/error]") 