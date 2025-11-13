"""
NBA Data Database Schema

Core tables for NBA player analytics focused on playoff resilience.
Based on the NBA Lineup Optimizer schema but simplified for our use case.
"""

import sqlite3
from pathlib import Path
from typing import Optional

class NBADatabaseSchema:
    """Manages the NBA database schema creation and management."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = None

    @property
    def conn(self):
        """Get database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn

    def create_all_tables(self) -> None:
        """Create all necessary database tables."""
        with sqlite3.connect(self.db_path) as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")

            # Create all tables
            self._create_teams_table(conn)
            self._create_games_table(conn)
            self._create_players_table(conn)
            self._create_player_season_stats_table(conn)
            self._create_player_advanced_stats_table(conn)
            self._create_player_tracking_stats_table(conn)
            self._create_player_playoff_stats_table(conn)
            self._create_player_playoff_advanced_stats_table(conn)
            self._create_player_playoff_tracking_stats_table(conn)
            self._create_player_playtype_stats_table(conn)
            self._create_player_playoff_playtype_stats_table(conn)
            self._create_possessions_table(conn)
            self._create_possession_lineups_table(conn)
            self._create_possession_events_table(conn)
            self._create_possession_matchups_table(conn)
            self._create_player_shot_locations_table(conn)
            self._create_league_averages_table(conn)

            print("✅ All database tables created successfully")

    def _create_teams_table(self, conn: sqlite3.Connection) -> None:
        """Create the Teams table."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY,
                team_name TEXT NOT NULL,
                team_abbreviation TEXT NOT NULL,
                team_code TEXT NOT NULL,
                team_city TEXT NOT NULL,
                team_conference TEXT NOT NULL,
                team_division TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index for faster queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_teams_conference_division
            ON teams(team_conference, team_division)
        """)

        # Update trigger
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS teams_updated_at
            AFTER UPDATE ON teams
            BEGIN
                UPDATE teams SET updated_at = CURRENT_TIMESTAMP
                WHERE team_id = NEW.team_id;
            END
        """)

        conn.commit()
        print("✓ Teams table created")

    def _create_games_table(self, conn: sqlite3.Connection) -> None:
        """Create the Games table."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                game_date TEXT,
                home_team_id INTEGER NOT NULL,
                away_team_id INTEGER NOT NULL,
                home_team_score INTEGER,
                away_team_score INTEGER,
                season TEXT NOT NULL,
                season_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
                FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
            )
        """)

        conn.commit()
        print("✓ Games table created")

    def _create_players_table(self, conn: sqlite3.Connection) -> None:
        """Create the Players table."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY,
                player_name TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                birth_date TEXT,
                country TEXT,
                height TEXT,
                weight INTEGER,
                jersey_number INTEGER,
                position TEXT,
                team_id INTEGER,
                wingspan REAL,
                draft_year TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        conn.commit()
        print("✓ Players table created")

    def _create_player_season_stats_table(self, conn: sqlite3.Connection) -> None:
        """Create the PlayerSeasonStats table (traditional box score stats)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_season_stats (
                player_id INTEGER NOT NULL,
                season TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                games_played INTEGER,
                games_started INTEGER,
                minutes_played REAL,
                field_goals_made INTEGER,
                field_goals_attempted INTEGER,
                field_goal_percentage REAL,
                three_pointers_made INTEGER,
                three_pointers_attempted INTEGER,
                three_point_percentage REAL,
                free_throws_made INTEGER,
                free_throws_attempted INTEGER,
                free_throw_percentage REAL,
                offensive_rebounds INTEGER,
                defensive_rebounds INTEGER,
                total_rebounds INTEGER,
                assists INTEGER,
                steals INTEGER,
                blocks INTEGER,
                turnovers INTEGER,
                personal_fouls INTEGER,
                points INTEGER,
                plus_minus REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, season, team_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        conn.commit()
        print("✓ PlayerSeasonStats table created")

    def _create_player_advanced_stats_table(self, conn: sqlite3.Connection) -> None:
        """Create the PlayerAdvancedStats table (advanced analytics)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_advanced_stats (
                player_id INTEGER NOT NULL,
                season TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                age INTEGER,
                games_played INTEGER,
                wins INTEGER,
                losses INTEGER,
                win_percentage REAL,
                minutes_played REAL,
                offensive_rating REAL,
                defensive_rating REAL,
                net_rating REAL,
                assist_percentage REAL,
                assist_to_turnover_ratio REAL,
                assist_ratio REAL,
                offensive_rebound_percentage REAL,
                defensive_rebound_percentage REAL,
                rebound_percentage REAL,
                turnover_percentage REAL,
                effective_field_goal_percentage REAL,
                true_shooting_percentage REAL,
                usage_percentage REAL,
                pace REAL,
                pie REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, season, team_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        conn.commit()
        print("✓ PlayerAdvancedStats table created")

    def _create_player_tracking_stats_table(self, conn: sqlite3.Connection) -> None:
        """Create the PlayerTrackingStats table (advanced tracking metrics)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_tracking_stats (
                player_id INTEGER NOT NULL,
                season TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                minutes_played REAL,

                -- Drive metrics
                drives REAL,
                drive_field_goals_made REAL,
                drive_field_goals_attempted REAL,
                drive_field_goal_percentage REAL,
                drive_free_throws_made REAL,
                drive_free_throws_attempted REAL,
                drive_free_throw_percentage REAL,
                drive_points REAL,
                drive_points_percentage REAL,
                drive_passes REAL,
                drive_passes_percentage REAL,
                drive_assists REAL,
                drive_assists_percentage REAL,
                drive_turnovers REAL,
                drive_turnovers_percentage REAL,
                drive_personal_fouls REAL,
                drive_personal_fouls_percentage REAL,

                -- Catch and shoot metrics
                catch_shoot_field_goals_made REAL,
                catch_shoot_field_goals_attempted REAL,
                catch_shoot_field_goal_percentage REAL,
                catch_shoot_points REAL,
                catch_shoot_three_pointers_made REAL,
                catch_shoot_three_pointers_attempted REAL,
                catch_shoot_three_point_percentage REAL,
                catch_shoot_effective_field_goal_percentage REAL,

                -- Pull up shot metrics
                pull_up_field_goals_made REAL,
                pull_up_field_goals_attempted REAL,
                pull_up_field_goal_percentage REAL,
                pull_up_points REAL,
                pull_up_three_pointers_made REAL,
                pull_up_three_pointers_attempted REAL,
                pull_up_three_point_percentage REAL,
                pull_up_effective_field_goal_percentage REAL,

                -- Paint touch metrics
                touches REAL,
                paint_touches REAL,
                paint_touch_field_goals_made REAL,
                paint_touch_field_goals_attempted REAL,
                paint_touch_field_goal_percentage REAL,
                paint_touch_free_throws_made REAL,
                paint_touch_free_throws_attempted REAL,
                paint_touch_free_throw_percentage REAL,
                paint_touch_points REAL,
                paint_touch_points_percentage REAL,
                paint_touch_passes REAL,
                paint_touch_passes_percentage REAL,
                paint_touch_assists REAL,
                paint_touch_assists_percentage REAL,
                paint_touch_turnovers REAL,
                paint_touch_turnovers_percentage REAL,
                paint_touch_fouls REAL,
                paint_touch_fouls_percentage REAL,

                -- Post touch metrics
                post_touches REAL,
                post_touch_field_goals_made REAL,
                post_touch_field_goals_attempted REAL,
                post_touch_field_goal_percentage REAL,
                post_touch_free_throws_made REAL,
                post_touch_free_throws_attempted REAL,
                post_touch_free_throw_percentage REAL,
                post_touch_points REAL,
                post_touch_points_percentage REAL,
                post_touch_passes REAL,
                post_touch_passes_percentage REAL,
                post_touch_assists REAL,
                post_touch_assists_percentage REAL,
                post_touch_turnovers REAL,
                post_touch_turnovers_percentage REAL,
                post_touch_fouls REAL,
                post_touch_fouls_percentage REAL,

                -- Elbow touch metrics
                elbow_touches REAL,
                elbow_touch_field_goals_made REAL,
                elbow_touch_field_goals_attempted REAL,
                elbow_touch_field_goal_percentage REAL,
                elbow_touch_free_throws_made REAL,
                elbow_touch_free_throws_attempted REAL,
                elbow_touch_free_throw_percentage REAL,
                elbow_touch_points REAL,
                elbow_touch_passes REAL,
                elbow_touch_assists REAL,
                elbow_touch_assists_percentage REAL,
                elbow_touch_turnovers REAL,
                elbow_touch_turnovers_percentage REAL,
                elbow_touch_fouls REAL,
                elbow_touch_passes_percentage REAL,
                elbow_touch_fouls_percentage REAL,
                elbow_touch_points_percentage REAL,

                -- Efficiency metrics (aggregated)
                efficiency_points REAL,
                efficiency_drive_points REAL,
                efficiency_drive_field_goal_percentage REAL,
                efficiency_catch_shoot_points REAL,
                efficiency_catch_shoot_field_goal_percentage REAL,
                efficiency_pull_up_points REAL,
                efficiency_pull_up_field_goal_percentage REAL,
                efficiency_paint_touch_points REAL,
                efficiency_paint_touch_field_goal_percentage REAL,
                efficiency_post_touch_points REAL,
                efficiency_post_touch_field_goal_percentage REAL,
                efficiency_elbow_touch_points REAL,
                efficiency_elbow_touch_field_goal_percentage REAL,
                efficiency_effective_field_goal_percentage REAL,

                -- Speed and Distance metrics
                dist_feet REAL,
                dist_miles REAL,
                dist_miles_off REAL,
                dist_miles_def REAL,
                avg_speed REAL,
                avg_speed_off REAL,
                avg_speed_def REAL,

                -- Passing metrics
                passes_made REAL,
                passes_received REAL,
                ft_ast REAL,
                secondary_ast REAL,
                potential_ast REAL,
                ast_points_created REAL,
                ast_adj REAL,
                ast_to_pass_pct REAL,
                ast_to_pass_pct_adj REAL,

                -- Rebounding metrics
                oreb_contest REAL,
                oreb_uncontest REAL,
                oreb_contest_pct REAL,
                oreb_chances REAL,
                oreb_chance_pct REAL,
                oreb_chance_defer REAL,
                oreb_chance_pct_adj REAL,
                avg_oreb_dist REAL,
                dreb_contest REAL,
                dreb_uncontest REAL,
                dreb_contest_pct REAL,
                dreb_chances REAL,
                dreb_chance_pct REAL,
                dreb_chance_defer REAL,
                dreb_chance_pct_adj REAL,
                avg_dreb_dist REAL,
                reb_contest REAL,
                reb_uncontest REAL,
                reb_contest_pct REAL,
                reb_chances REAL,
                reb_chance_pct REAL,
                reb_chance_defer REAL,
                reb_chance_pct_adj REAL,
                avg_reb_dist REAL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, season, team_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        conn.commit()
        print("✓ PlayerTrackingStats table created")

    def _create_player_playoff_stats_table(self, conn: sqlite3.Connection) -> None:
        """Create the PlayerPlayoffStats table (playoff basic stats)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_playoff_stats (
                player_id INTEGER NOT NULL,
                season TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                games_played INTEGER,
                games_started INTEGER,
                minutes_played REAL,
                field_goals_made INTEGER,
                field_goals_attempted INTEGER,
                field_goal_percentage REAL,
                three_pointers_made INTEGER,
                three_pointers_attempted INTEGER,
                three_point_percentage REAL,
                free_throws_made INTEGER,
                free_throws_attempted INTEGER,
                free_throw_percentage REAL,
                offensive_rebounds INTEGER,
                defensive_rebounds INTEGER,
                total_rebounds INTEGER,
                assists INTEGER,
                steals INTEGER,
                blocks INTEGER,
                turnovers INTEGER,
                personal_fouls INTEGER,
                points INTEGER,
                plus_minus REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, season, team_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        conn.commit()
        print("✓ PlayerPlayoffStats table created")

    def _create_player_playoff_advanced_stats_table(self, conn: sqlite3.Connection) -> None:
        """Create the PlayerPlayoffAdvancedStats table (playoff advanced analytics)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_playoff_advanced_stats (
                player_id INTEGER NOT NULL,
                season TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                age INTEGER,
                games_played INTEGER,
                wins INTEGER,
                losses INTEGER,
                win_percentage REAL,
                minutes_played REAL,
                offensive_rating REAL,
                defensive_rating REAL,
                net_rating REAL,
                assist_percentage REAL,
                assist_to_turnover_ratio REAL,
                assist_ratio REAL,
                offensive_rebound_percentage REAL,
                defensive_rebound_percentage REAL,
                rebound_percentage REAL,
                turnover_percentage REAL,
                effective_field_goal_percentage REAL,
                true_shooting_percentage REAL,
                usage_percentage REAL,
                pace REAL,
                pie REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, season, team_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        conn.commit()
        print("✓ PlayerPlayoffAdvancedStats table created")

    def _create_player_playoff_tracking_stats_table(self, conn: sqlite3.Connection) -> None:
        """Create the PlayerPlayoffTrackingStats table (playoff advanced tracking metrics)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_playoff_tracking_stats (
                player_id INTEGER NOT NULL,
                season TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                minutes_played REAL,

                -- Drive metrics
                drives REAL,
                drive_field_goals_made REAL,
                drive_field_goals_attempted REAL,
                drive_field_goal_percentage REAL,
                drive_free_throws_made REAL,
                drive_free_throws_attempted REAL,
                drive_free_throw_percentage REAL,
                drive_points REAL,
                drive_points_percentage REAL,
                drive_passes REAL,
                drive_passes_percentage REAL,
                drive_assists REAL,
                drive_assists_percentage REAL,
                drive_turnovers REAL,
                drive_turnovers_percentage REAL,
                drive_personal_fouls REAL,
                drive_personal_fouls_percentage REAL,

                -- Catch and shoot metrics
                catch_shoot_field_goals_made REAL,
                catch_shoot_field_goals_attempted REAL,
                catch_shoot_field_goal_percentage REAL,
                catch_shoot_points REAL,
                catch_shoot_three_pointers_made REAL,
                catch_shoot_three_pointers_attempted REAL,
                catch_shoot_three_point_percentage REAL,
                catch_shoot_effective_field_goal_percentage REAL,

                -- Pull up shot metrics
                pull_up_field_goals_made REAL,
                pull_up_field_goals_attempted REAL,
                pull_up_field_goal_percentage REAL,
                pull_up_points REAL,
                pull_up_three_pointers_made REAL,
                pull_up_three_pointers_attempted REAL,
                pull_up_three_point_percentage REAL,
                pull_up_effective_field_goal_percentage REAL,

                -- Paint touch metrics
                touches REAL,
                paint_touches REAL,
                paint_touch_field_goals_made REAL,
                paint_touch_field_goals_attempted REAL,
                paint_touch_field_goal_percentage REAL,
                paint_touch_free_throws_made REAL,
                paint_touch_free_throws_attempted REAL,
                paint_touch_free_throw_percentage REAL,
                paint_touch_points REAL,
                paint_touch_points_percentage REAL,
                paint_touch_passes REAL,
                paint_touch_passes_percentage REAL,
                paint_touch_assists REAL,
                paint_touch_assists_percentage REAL,
                paint_touch_turnovers REAL,
                paint_touch_turnovers_percentage REAL,
                paint_touch_fouls REAL,
                paint_touch_fouls_percentage REAL,

                -- Post touch metrics
                post_touches REAL,
                post_touch_field_goals_made REAL,
                post_touch_field_goals_attempted REAL,
                post_touch_field_goal_percentage REAL,
                post_touch_free_throws_made REAL,
                post_touch_free_throws_attempted REAL,
                post_touch_free_throw_percentage REAL,
                post_touch_points REAL,
                post_touch_points_percentage REAL,
                post_touch_passes REAL,
                post_touch_passes_percentage REAL,
                post_touch_assists REAL,
                post_touch_assists_percentage REAL,
                post_touch_turnovers REAL,
                post_touch_turnovers_percentage REAL,
                post_touch_fouls REAL,
                post_touch_fouls_percentage REAL,

                -- Elbow touch metrics
                elbow_touches REAL,
                elbow_touch_field_goals_made REAL,
                elbow_touch_field_goals_attempted REAL,
                elbow_touch_field_goal_percentage REAL,
                elbow_touch_free_throws_made REAL,
                elbow_touch_free_throws_attempted REAL,
                elbow_touch_free_throw_percentage REAL,
                elbow_touch_points REAL,
                elbow_touch_passes REAL,
                elbow_touch_assists REAL,
                elbow_touch_assists_percentage REAL,
                elbow_touch_turnovers REAL,
                elbow_touch_turnovers_percentage REAL,
                elbow_touch_fouls REAL,
                elbow_touch_passes_percentage REAL,
                elbow_touch_fouls_percentage REAL,
                elbow_touch_points_percentage REAL,

                -- Efficiency metrics (aggregated)
                efficiency_points REAL,
                efficiency_drive_points REAL,
                efficiency_drive_field_goal_percentage REAL,
                efficiency_catch_shoot_points REAL,
                efficiency_catch_shoot_field_goal_percentage REAL,
                efficiency_pull_up_points REAL,
                efficiency_pull_up_field_goal_percentage REAL,
                efficiency_paint_touch_points REAL,
                efficiency_paint_touch_field_goal_percentage REAL,
                efficiency_post_touch_points REAL,
                efficiency_post_touch_field_goal_percentage REAL,
                efficiency_elbow_touch_points REAL,
                efficiency_elbow_touch_field_goal_percentage REAL,
                efficiency_effective_field_goal_percentage REAL,

                -- Speed and Distance metrics
                dist_feet REAL,
                dist_miles REAL,
                dist_miles_off REAL,
                dist_miles_def REAL,
                avg_speed REAL,
                avg_speed_off REAL,
                avg_speed_def REAL,

                -- Passing metrics
                passes_made REAL,
                passes_received REAL,
                ft_ast REAL,
                secondary_ast REAL,
                potential_ast REAL,
                ast_points_created REAL,
                ast_adj REAL,
                ast_to_pass_pct REAL,
                ast_to_pass_pct_adj REAL,

                -- Rebounding metrics
                oreb_contest REAL,
                oreb_uncontest REAL,
                oreb_contest_pct REAL,
                oreb_chances REAL,
                oreb_chance_pct REAL,
                oreb_chance_defer REAL,
                oreb_chance_pct_adj REAL,
                avg_oreb_dist REAL,
                dreb_contest REAL,
                dreb_uncontest REAL,
                dreb_contest_pct REAL,
                dreb_chances REAL,
                dreb_chance_pct REAL,
                dreb_chance_defer REAL,
                dreb_chance_pct_adj REAL,
                avg_dreb_dist REAL,
                reb_contest REAL,
                reb_uncontest REAL,
                reb_contest_pct REAL,
                reb_chances REAL,
                reb_chance_pct REAL,
                reb_chance_defer REAL,
                reb_chance_pct_adj REAL,
                avg_reb_dist REAL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, season, team_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        conn.commit()
        print("✓ PlayerPlayoffTrackingStats table created")

    def _create_player_playtype_stats_table(self, conn: sqlite3.Connection) -> None:
        """Create the PlayerPlaytypeStats table (synergy play type metrics)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_playtype_stats (
                player_id INTEGER NOT NULL,
                season TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                play_type TEXT NOT NULL,
                type_grouping TEXT NOT NULL,

                -- Performance metrics
                percentile REAL,
                games_played INTEGER,
                possession_percentage REAL,
                points_per_possession REAL,
                field_goal_percentage REAL,
                free_throw_possession_percentage REAL,
                turnover_possession_percentage REAL,
                shot_foul_possession_percentage REAL,
                plus_one_possession_percentage REAL,
                score_possession_percentage REAL,
                effective_field_goal_percentage REAL,

                -- Volume metrics
                possessions REAL,
                points REAL,
                field_goals_made REAL,
                field_goals_attempted REAL,
                field_goals_missed REAL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, season, team_id, play_type),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        # Create indexes for performance
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_playtype_stats_player_season
            ON player_playtype_stats(player_id, season)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_playtype_stats_play_type
            ON player_playtype_stats(play_type)
        """)

        # Update trigger
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS player_playtype_stats_updated_at
            AFTER UPDATE ON player_playtype_stats
            BEGIN
                UPDATE player_playtype_stats SET updated_at = CURRENT_TIMESTAMP
                WHERE player_id = NEW.player_id AND season = NEW.season AND team_id = NEW.team_id AND play_type = NEW.play_type;
            END
        """)

        conn.commit()
        print("✓ PlayerPlaytypeStats table created")

    def _create_player_playoff_playtype_stats_table(self, conn: sqlite3.Connection) -> None:
        """Create the PlayerPlayoffPlaytypeStats table (playoff synergy play type metrics)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_playoff_playtype_stats (
                player_id INTEGER NOT NULL,
                season TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                play_type TEXT NOT NULL,
                type_grouping TEXT NOT NULL,

                -- Performance metrics
                percentile REAL,
                games_played INTEGER,
                possession_percentage REAL,
                points_per_possession REAL,
                field_goal_percentage REAL,
                free_throw_possession_percentage REAL,
                turnover_possession_percentage REAL,
                shot_foul_possession_percentage REAL,
                plus_one_possession_percentage REAL,
                score_possession_percentage REAL,
                effective_field_goal_percentage REAL,

                -- Volume metrics
                possessions REAL,
                points REAL,
                field_goals_made REAL,
                field_goals_attempted REAL,
                field_goals_missed REAL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, season, team_id, play_type),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        # Create indexes for performance
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_playoff_playtype_stats_player_season
            ON player_playoff_playtype_stats(player_id, season)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_playoff_playtype_stats_play_type
            ON player_playoff_playtype_stats(play_type)
        """)

        # Update trigger
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS player_playoff_playtype_stats_updated_at
            AFTER UPDATE ON player_playoff_playtype_stats
            BEGIN
                UPDATE player_playoff_playtype_stats SET updated_at = CURRENT_TIMESTAMP
                WHERE player_id = NEW.player_id AND season = NEW.season AND team_id = NEW.team_id AND play_type = NEW.play_type;
            END
        """)

        conn.commit()
        print("✓ PlayerPlayoffPlaytypeStats table created")

    def _create_possessions_table(self, conn: sqlite3.Connection) -> None:
        """Create the Possessions table (for play-by-play analysis)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS possessions (
                possession_id TEXT PRIMARY KEY,
                game_id TEXT NOT NULL,
                period INTEGER,
                clock_time_start TEXT,
                clock_time_end TEXT,
                home_team_id INTEGER NOT NULL,
                away_team_id INTEGER NOT NULL,
                offensive_team_id INTEGER NOT NULL,
                defensive_team_id INTEGER NOT NULL,
                possession_start REAL,
                possession_end REAL,
                duration_seconds REAL,
                points_scored INTEGER DEFAULT 0,
                expected_points REAL,
                possession_type TEXT, -- 'offensive', 'defensive', 'transition', etc.
                start_reason TEXT, -- 'made_shot', 'rebound', 'steal', 'turnover', etc.
                end_reason TEXT, -- 'made_shot', 'missed_shot', 'turnover', 'foul', etc.
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
                FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
                FOREIGN KEY (offensive_team_id) REFERENCES teams(team_id),
                FOREIGN KEY (defensive_team_id) REFERENCES teams(team_id)
            )
        """)

        # Create indexes for performance
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_possessions_game_id
            ON possessions(game_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_possessions_offensive_team
            ON possessions(offensive_team_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_possessions_period
            ON possessions(game_id, period)
        """)

        # Update trigger
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS possessions_updated_at
            AFTER UPDATE ON possessions
            BEGIN
                UPDATE possessions SET updated_at = CURRENT_TIMESTAMP
                WHERE possession_id = NEW.possession_id;
            END
        """)

        conn.commit()
        print("✓ Enhanced Possessions table created")

    def _create_possession_lineups_table(self, conn: sqlite3.Connection) -> None:
        """Create the PossessionLineups table (tracks players on court during possessions)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS possession_lineups (
                possession_id TEXT NOT NULL,
                player_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                position TEXT, -- Point Guard, Shooting Guard, etc. (for context)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (possession_id, player_id),
                FOREIGN KEY (possession_id) REFERENCES possessions(possession_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        # Create indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_possession_lineups_player
            ON possession_lineups(player_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_possession_lineups_team
            ON possession_lineups(team_id)
        """)

        conn.commit()
        print("✓ PossessionLineups table created")

    def _create_possession_events_table(self, conn: sqlite3.Connection) -> None:
        """Create the PossessionEvents table (individual player actions within possessions)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS possession_events (
                event_id TEXT PRIMARY KEY,
                possession_id TEXT NOT NULL,
                event_number INTEGER NOT NULL, -- Sequence within possession
                clock_time TEXT NOT NULL,
                elapsed_seconds REAL NOT NULL,
                player_id INTEGER,
                team_id INTEGER NOT NULL,
                opponent_team_id INTEGER NOT NULL,
                event_type TEXT NOT NULL, -- 'shot', 'pass', 'dribble', 'foul', 'rebound', etc.
                event_subtype TEXT, -- 'made', 'missed', 'assist', 'steal', etc.
                shot_type TEXT, -- '2PT', '3PT', 'FT'
                shot_distance INTEGER,
                shot_result TEXT, -- 'made', 'missed'
                points_scored INTEGER DEFAULT 0,
                assist_player_id INTEGER,
                block_player_id INTEGER,
                steal_player_id INTEGER,
                turnover_type TEXT,
                foul_type TEXT,
                rebound_type TEXT, -- 'offensive', 'defensive'
                location_x REAL, -- Court coordinates (0-94)
                location_y REAL, -- Court coordinates (0-50)
                defender_player_id INTEGER, -- Who was guarding the player
                touches_before_action INTEGER, -- Touches leading to this action
                dribbles_before_action INTEGER, -- Dribbles leading to this action
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (possession_id) REFERENCES possessions(possession_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id),
                FOREIGN KEY (opponent_team_id) REFERENCES teams(team_id),
                FOREIGN KEY (assist_player_id) REFERENCES players(player_id),
                FOREIGN KEY (block_player_id) REFERENCES players(player_id),
                FOREIGN KEY (steal_player_id) REFERENCES players(player_id),
                FOREIGN KEY (defender_player_id) REFERENCES players(player_id)
            )
        """)

        # Create indexes for performance
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_possession_events_possession
            ON possession_events(possession_id, event_number)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_possession_events_player
            ON possession_events(player_id, event_type)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_possession_events_type
            ON possession_events(event_type, event_subtype)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_possession_events_team
            ON possession_events(team_id, event_type)
        """)

        conn.commit()
        print("✓ PossessionEvents table created")

    def _create_possession_matchups_table(self, conn: sqlite3.Connection) -> None:
        """Create the PossessionMatchups table (defensive matchups during possessions)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS possession_matchups (
                possession_id TEXT NOT NULL,
                offensive_player_id INTEGER NOT NULL,
                defensive_player_id INTEGER NOT NULL,
                matchup_start_time TEXT,
                matchup_end_time TEXT,
                duration_seconds REAL,
                switches_during_matchup INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (possession_id, offensive_player_id, defensive_player_id),
                FOREIGN KEY (possession_id) REFERENCES possessions(possession_id),
                FOREIGN KEY (offensive_player_id) REFERENCES players(player_id),
                FOREIGN KEY (defensive_player_id) REFERENCES players(player_id)
            )
        """)

        # Create indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_possession_matchups_offensive
            ON possession_matchups(offensive_player_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_possession_matchups_defensive
            ON possession_matchups(defensive_player_id)
        """)

        conn.commit()
        print("✓ PossessionMatchups table created")

    def _create_player_shot_locations_table(self, conn: sqlite3.Connection) -> None:
        """Create the player_shot_locations table."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player_shot_locations (
                shot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                player_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                season TEXT NOT NULL,
                season_type TEXT NOT NULL,
                period INTEGER,
                minutes_remaining INTEGER,
                seconds_remaining INTEGER,
                event_type TEXT,
                action_type TEXT,
                shot_type TEXT,
                shot_zone_basic TEXT,
                shot_zone_area TEXT,
                shot_zone_range TEXT,
                shot_distance INTEGER,
                loc_x INTEGER,
                loc_y INTEGER,
                shot_attempted_flag INTEGER,
                shot_made_flag INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        # Create indexes for faster queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_shot_locations_player_season
            ON player_shot_locations(player_id, season, season_type)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_shot_locations_game
            ON player_shot_locations(game_id)
        """)

        conn.commit()
        print("✓ player_shot_locations table created")

    def _create_league_averages_table(self, conn: sqlite3.Connection) -> None:
        """Create the league_averages table to store benchmark statistics."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS league_averages (
                season TEXT NOT NULL,
                season_type TEXT NOT NULL,
                metric_type TEXT NOT NULL, -- 'spatial', 'play_type', 'creation'
                metric_name TEXT NOT NULL, -- e.g., 'Restricted Area', 'Isolation', 'Catch & Shoot'
                value REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (season, season_type, metric_type, metric_name)
            )
        """)
        conn.commit()
        print("✓ league_averages table created")

    def verify_schema(self) -> bool:
        """Verify that all required tables exist."""
        required_tables = [
            'teams', 'games', 'players', 'player_season_stats',
            'player_advanced_stats', 'player_tracking_stats',
            'player_playoff_stats', 'player_playoff_advanced_stats', 'player_playoff_tracking_stats',
            'player_playtype_stats', 'player_playoff_playtype_stats',
            'possessions', 'possession_lineups', 'possession_events', 'possession_matchups',
            'player_shot_locations', 'league_averages'
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}

            missing_tables = [table for table in required_tables if table not in existing_tables]

            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                return False
            else:
                print("✅ All required tables exist")
                return True

    def get_table_info(self) -> dict:
        """Get information about all tables in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            table_info = {}
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                table_info[table] = {
                    'columns': len(columns),
                    'column_names': [col[1] for col in columns]
                }

                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                table_info[table]['row_count'] = cursor.fetchone()[0]

            return table_info


def init_database(db_path: str = "data/nba_stats.db") -> NBADatabaseSchema:
    """Initialize the NBA database with all necessary tables."""
    schema = NBADatabaseSchema(db_path)
    schema.create_all_tables()
    return schema


if __name__ == "__main__":
    # Initialize the database
    schema = init_database()

    # Verify schema
    if schema.verify_schema():
        print("\n🎉 Database initialization complete!")
        print("\nTable Summary:")
        for table_name, info in schema.get_table_info().items():
            print(f"  {table_name}: {info['columns']} columns, {info['row_count']} rows")
    else:
        print("\n❌ Database initialization failed!")
