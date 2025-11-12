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
            self._create_possessions_table(conn)

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
                game_date TEXT NOT NULL,
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
                drives REAL,
                drive_field_goals_made REAL,
                drive_field_goals_attempted REAL,
                drive_field_goal_percentage REAL,
                front_court_touches REAL,
                elbow_touches REAL,
                post_ups REAL,
                post_up_field_goals_made REAL,
                post_up_field_goals_attempted REAL,
                post_up_field_goal_percentage REAL,
                paint_touches REAL,
                catch_shoot_field_goals_made REAL,
                catch_shoot_field_goals_attempted REAL,
                catch_shoot_field_goal_percentage REAL,
                pull_up_field_goals_made REAL,
                pull_up_field_goals_attempted REAL,
                pull_up_field_goal_percentage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, season, team_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)

        conn.commit()
        print("✓ PlayerTrackingStats table created")

    def _create_possessions_table(self, conn: sqlite3.Connection) -> None:
        """Create the Possessions table (for play-by-play analysis)."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS possessions (
                possession_id TEXT PRIMARY KEY,
                game_id TEXT NOT NULL,
                period INTEGER,
                clock_time TEXT,
                home_team_id INTEGER NOT NULL,
                away_team_id INTEGER NOT NULL,
                offensive_team_id INTEGER NOT NULL,
                defensive_team_id INTEGER NOT NULL,
                possession_start REAL,
                possession_end REAL,
                points_scored INTEGER DEFAULT 0,
                expected_points REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

        conn.commit()
        print("✓ Possessions table created")

    def verify_schema(self) -> bool:
        """Verify that all required tables exist."""
        required_tables = [
            'teams', 'games', 'players', 'player_season_stats',
            'player_advanced_stats', 'player_tracking_stats', 'possessions'
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
