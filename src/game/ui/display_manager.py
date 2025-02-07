from rich.table import Table
from rich.columns import Columns
from src.ui.console_manager import ConsoleManager
from typing import List, Optional, Dict
from src.game.person import Player, Coach
from src.game.roster.league import Match

class DisplayManager:
    def __init__(self, console: ConsoleManager):
        self.console = console

    def display_region_selection(self, region_list: List[str]) -> Table:
        """Display available regions in a table format."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        for idx, region in enumerate(region_list, 1):
            table.add_row(f"[menu_option]{idx}.[/menu_option]", f"[white]{region}[/white]")
        return table

    def display_team_selection(self, teams: List[str]) -> Table:
        """Display teams from the selected region in a table format."""
        table = Table(show_header=False, box=None, padding=(0, 1))
        for idx, team in enumerate(teams, 1):
            table.add_row(f"[menu_option]{idx}.[/menu_option]", f"[white]{team}[/white]")
        return table

    def display_team_members(self, players: List[Player], coach: Coach) -> tuple[Table, Table]:
        """Display the generated team members in a table format"""
        if not players or not coach:
            return None, None

        # Create players table
        players_table = Table(title="Team Players", show_header=True)
        players_table.add_column("Position")
        players_table.add_column("Name")
        players_table.add_column("Skill Rating")

        for player in players:
            players_table.add_row(
                player.position,
                f"{player.first_name} {player.last_name}",
                str(player.skill_rating)
            )

        # Create coach table
        coach_table = Table(title="Team Coach", show_header=True)
        coach_table.add_column("Name")
        coach_table.add_column("Skill Rating")
        coach_table.add_row(
            f"{coach.first_name} {coach.last_name}",
            str(coach.skill_rating)
        )

        return players_table, coach_table

    def display_team_ratings(self, team_ratings: dict, selected_team: str, region: str) -> Table:
        """Display all team ratings in the league in a table format"""
        table = Table(title=f"{region} Team Ratings")
        table.add_column("Team")
        table.add_column("Rating")
        table.add_column("Record")

        # Sort teams by rating for display
        sorted_teams = sorted(
            team_ratings.values(),
            key=lambda x: x.rating,
            reverse=True
        )

        for team in sorted_teams:
            name_style = "[green]" if team.name == selected_team else "[white]"
            table.add_row(
                f"{name_style}{team.name}[/]",
                f"{team.rating}",
                f"{team.wins}-{team.losses}"
            )

        return table

    def display_match_results(self, matches: List[Match], selected_team: str, title: str = "Match Results") -> Table:
        """Display the results of simulated matches"""
        table = Table(title=title, show_header=True)
        table.add_column("Home Team", justify="right")
        table.add_column("Score", justify="center")
        table.add_column("Away Team", justify="left")
        
        for match in matches:
            home_style = "[green]" if match.home_team == selected_team else "[white]"
            away_style = "[green]" if match.away_team == selected_team else "[white]"
            
            # Highlight winner
            if match.home_score > match.away_score:
                home_style = home_style.replace("]", " bold]")
            else:
                away_style = away_style.replace("]", " bold]")
                
            table.add_row(
                f"{home_style}{match.home_team}[/]",
                f"{match.home_score} - {match.away_score}",
                f"{away_style}{match.away_team}[/]"
            )
            
        return table

    def display_standings(self, team_ratings: dict, selected_team: str, region: str) -> Table:
        """Display current league standings in a table format"""
        table = Table(title=f"{region} Standings")
        table.add_column("Position", justify="center")
        table.add_column("Team")
        table.add_column("W", justify="center")
        table.add_column("L", justify="center")
        table.add_column("Rating", justify="center")

        # Sort teams by wins, then rating for tiebreaker
        sorted_teams = sorted(
            team_ratings.values(),
            key=lambda x: (x.wins, x.rating),
            reverse=True
        )

        for pos, team in enumerate(sorted_teams, 1):
            name_style = "[green]" if team.name == selected_team else "[white]"
            table.add_row(
                str(pos),
                f"{name_style}{team.name}[/]",
                str(team.wins),
                str(team.losses),
                str(team.rating)
            )

        return table

    def display_table_pair(self, left_table: Table, right_table: Optional[Table] = None):
        """Display two tables side by side"""
        tables = [left_table]
        if right_table:
            tables.append(right_table)
        self.console.console.print(Columns(tables, equal=True, expand=True))

    def display_full_schedule(self, matches: List[Match], selected_team: str, current_week: int, team_only: bool = False) -> Table:
        """Display the full season schedule in a table format"""
        table = Table(title="Season Schedule")
        table.add_column("Week", justify="center")
        table.add_column("Home Team", justify="right")
        table.add_column("Score", justify="center")
        table.add_column("Away Team", justify="left")
        table.add_column("Status", justify="center")
        table.add_column("Match ID", justify="center")  # Added for reference
        
        # Filter matches if team_only is True
        display_matches = [m for m in matches if selected_team in [m.home_team, m.away_team]] if team_only else matches
            
        # Sort matches by week
        sorted_matches = sorted(display_matches, key=lambda x: x.week)
        
        for idx, match in enumerate(sorted_matches, 1):
            # Determine styles based on team and completion
            home_style = "[green]" if match.home_team == selected_team else "[white]"
            away_style = "[green]" if match.away_team == selected_team else "[white]"
            
            # Format score or status
            if match.completed:
                score = f"{match.home_score} - {match.away_score}"
                status = "[grey]Complete[/]"
                # Highlight winner
                if match.home_score > match.away_score:
                    home_style = home_style.replace("]", " bold]")
                else:
                    away_style = away_style.replace("]", " bold]")
            else:
                score = "vs"
                status = "[yellow]Upcoming[/]" if match.week == current_week else ""
                
            table.add_row(
                str(match.week),
                f"{home_style}{match.home_team}[/]",
                score,
                f"{away_style}{match.away_team}[/]",
                status,
                str(idx)  # Match ID for reference
            )
            
        return table

    def display_match_details(self, match: Match, selected_team: str) -> Table:
        """Display detailed match information including map scores"""
        table = Table(title=f"Match Details: {match.home_team} vs {match.away_team}")
        table.add_column("Map", justify="center")
        table.add_column("Score", justify="center")
        table.add_column("Winner", justify="center")
        
        if not match.completed:
            table.add_row("Match not played yet", "", "")
            return table
            
        # Add overall match score
        home_style = "[green]" if match.home_team == selected_team else "[white]"
        away_style = "[green]" if match.away_team == selected_team else "[white]"
        
        if match.home_score > match.away_score:
            home_style = home_style.replace("]", " bold]")
            winner = match.home_team
        else:
            away_style = away_style.replace("]", " bold]")
            winner = match.away_team
            
        table.add_row(
            "Final",
            f"{home_style}{match.home_score}[/] - {away_style}{match.away_score}[/]",
            f"[bold]{winner}[/]"
        )
        
        # Add separator
        table.add_row("---", "---", "---")
        
        # Add individual map scores
        for i, (home_rounds, away_rounds) in enumerate(match.map_scores, 1):
            map_winner = match.home_team if home_rounds > away_rounds else match.away_team
            winner_style = "[green]" if map_winner == selected_team else "[white]"
            
            table.add_row(
                f"Map {i}",
                f"{home_rounds} - {away_rounds}",
                f"{winner_style}{map_winner}[/]"
            )
            
        return table

    def display_playoff_matches(self, matches: List[Match], selected_team: str) -> Table:
        """Display playoff matches in a table format"""
        table = Table(title="Playoff Matches")
        table.add_column("Round", justify="center")
        table.add_column("Home Team", justify="right")
        table.add_column("Score", justify="center")
        table.add_column("Away Team", justify="left")
        table.add_column("Maps", justify="left")
        
        for match in matches:
            # Determine styles based on team and completion
            home_style = "[green]" if match.home_team == selected_team else "[white]"
            away_style = "[green]" if match.away_team == selected_team else "[white]"
            
            # Format score and map scores
            if match.completed:
                score = f"{match.home_score} - {match.away_score}"
                maps = match.get_map_score_display()
                # Highlight winner
                if match.home_score > match.away_score:
                    home_style = home_style.replace("]", " bold]")
                else:
                    away_style = away_style.replace("]", " bold]")
            else:
                score = "vs"
                maps = f"Best of {match.maps_needed * 2 - 1}"
                
            table.add_row(
                match.playoff_round.title(),
                f"{home_style}{match.home_team}[/]",
                score,
                f"{away_style}{match.away_team}[/]",
                maps
            )
            
        return table

    def display_playoff_qualification(self, teams: List['TeamRating'], selected_team: str) -> Table:
        """Display playoff qualification in a table format"""
        table = Table(title="Playoff Teams")
        table.add_column("Seed", justify="center")
        table.add_column("Team")
        table.add_column("Record", justify="center")
        table.add_column("Rating", justify="center")
        
        for team in teams:
            name_style = "[green]" if team.name == selected_team else "[white]"
            table.add_row(
                str(team.playoff_seed),
                f"{name_style}{team.name}[/]",
                f"{team.wins}-{team.losses}",
                str(team.rating)
            )
            
        return table

    def display_playoff_advancement(self, teams: List['TeamRating'], selected_team: str) -> Table:
        """Display teams advancing in playoffs"""
        table = Table(title="Advancing Teams")
        table.add_column("Seed", justify="center")
        table.add_column("Team")
        table.add_column("Record", justify="center")
        
        for team in teams:
            name_style = "[green]" if team.name == selected_team else "[white]"
            table.add_row(
                str(team.playoff_seed),
                f"{name_style}{team.name}[/]",
                f"{team.wins}-{team.losses}"
            )
            
        return table

    def display_season_history(self, seasons: List[Dict], selected_team: str) -> Table:
        """Display the history of completed seasons"""
        table = Table(show_header=True, title="Season History")
        table.add_column("Year", justify="center")
        table.add_column("Champion", justify="left")
        table.add_column("Champion Record", justify="center")
        table.add_column("Your Record", justify="center")
        table.add_column("Your Position", justify="center")

        for season in seasons:
            # Format position with suffix (1st, 2nd, 3rd, etc.)
            position = season['team_position']
            suffix = 'th'
            if position % 10 == 1 and position != 11:
                suffix = 'st'
            elif position % 10 == 2 and position != 12:
                suffix = 'nd'
            elif position % 10 == 3 and position != 13:
                suffix = 'rd'
            position_str = f"{position}{suffix}"

            # Add row with styling
            table.add_row(
                str(season['number']),
                season['champion'],
                season['champion_record'],
                f"{season['team_wins']}-{season['team_losses']}",
                position_str,
                style="green" if season['champion'] == selected_team else None
            )

        return table 