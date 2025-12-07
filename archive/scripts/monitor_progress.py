#!/usr/bin/env python3
"""
Simple progress monitoring script for historical data population.
Run this anytime to check the current status.
"""

import sqlite3
import subprocess
import sys
from pathlib import Path

def check_processes():
    """Check if any population processes are running."""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=10
        )

        lines = result.stdout.split('\n')
        populate_lines = [line for line in lines if 'populate' in line and 'python' in line and 'grep' not in line]

        if populate_lines:
            print("🔄 ACTIVE PROCESSES:")
            for line in populate_lines:
                parts = line.split()
                pid = parts[1]
                cmd = ' '.join(parts[10:])[:80] + '...' if len(' '.join(parts[10:])) > 80 else ' '.join(parts[10:])
                print(f"  PID {pid}: {cmd}")
            print()
        else:
            print("✅ No population processes currently running\n")

    except Exception as e:
        print(f"❌ Error checking processes: {e}\n")

def check_database():
    """Check database contents."""
    db_path = "data/nba_stats.db"
    if not Path(db_path).exists():
        print(f"❌ Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("📊 DATABASE STATUS:")
        print("=" * 50)

        # Core tables
        tables = [
            ('teams', 'Teams'),
            ('games', 'Games'),
            ('player_season_stats', 'Regular Season Players'),
            ('player_playoff_stats', 'Playoff Players'),
            ('possessions', 'Possessions'),
            ('possession_events', 'Possession Events'),
        ]

        for table_name, display_name in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                print(f"{display_name}: {count:,}")
            except Exception as e:
                print(f"{display_name}: Error - {e}")

        # Season breakdown for players
        print(f"\n📅 PLAYER DATA BY SEASON:")
        try:
            cursor.execute('SELECT season, COUNT(*) FROM player_season_stats GROUP BY season ORDER BY season')
            seasons = cursor.fetchall()
            for season, count in seasons[-5:]:  # Show last 5 seasons
                print(f"  {season}: {count} players")
            if len(seasons) > 5:
                print(f"  ... and {len(seasons) - 5} earlier seasons")
        except Exception as e:
            print(f"Error getting season data: {e}")

        # Recent games
        print(f"\n🏀 RECENT GAMES:")
        try:
            cursor.execute('SELECT season, COUNT(*) FROM games GROUP BY season ORDER BY season DESC LIMIT 3')
            recent_games = cursor.fetchall()
            for season, count in recent_games:
                print(f"  {season}: {count} games")
        except Exception as e:
            print(f"Error getting games data: {e}")

        conn.close()

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

def check_logs():
    """Check recent log activity."""
    log_path = "logs/historical_population.log"
    if not Path(log_path).exists():
        print("📝 No log file found")
        return

    print(f"\n📋 RECENT LOG ACTIVITY:")
    print("-" * 30)

    try:
        result = subprocess.run(
            ["tail", "-10", log_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        for line in result.stdout.split('\n'):
            if line.strip():
                # Color code log levels
                if 'ERROR' in line:
                    print(f"❌ {line}")
                elif 'WARNING' in line:
                    print(f"⚠️  {line}")
                elif 'INFO' in line and '✅' in line:
                    print(f"✅ {line}")
                elif 'INFO' in line:
                    print(f"ℹ️  {line}")
                else:
                    print(f"   {line}")

    except Exception as e:
        print(f"❌ Error reading logs: {e}")

def main():
    """Main monitoring function."""
    print("🔍 NBA DATA POPULATION MONITOR")
    print("=" * 40)

    check_processes()
    check_database()
    check_logs()

    print(f"\n💡 TIP: Run this script anytime with: python monitor_progress.py")

if __name__ == "__main__":
    main()








