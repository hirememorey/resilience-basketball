"""
Canonical mapping of NBA Team IDs to Abbreviations and Conference.
This file serves as the single source of truth for team taxonomy to prevent
inconsistencies across different API endpoints.

Source: Official NBA Team IDs
Last Updated: Dec 2025
"""

# Official NBA Team IDs
TEAMS = {
    1610612737: {'abbrev': 'ATL', 'name': 'Atlanta Hawks', 'conference': 'East'},
    1610612738: {'abbrev': 'BOS', 'name': 'Boston Celtics', 'conference': 'East'},
    1610612739: {'abbrev': 'CLE', 'name': 'Cleveland Cavaliers', 'conference': 'East'},
    1610612740: {'abbrev': 'NOP', 'name': 'New Orleans Pelicans', 'conference': 'West'},
    1610612741: {'abbrev': 'CHI', 'name': 'Chicago Bulls', 'conference': 'East'},
    1610612742: {'abbrev': 'DAL', 'name': 'Dallas Mavericks', 'conference': 'West'},
    1610612743: {'abbrev': 'DEN', 'name': 'Denver Nuggets', 'conference': 'West'},
    1610612744: {'abbrev': 'GSW', 'name': 'Golden State Warriors', 'conference': 'West'},
    1610612745: {'abbrev': 'HOU', 'name': 'Houston Rockets', 'conference': 'West'},
    1610612746: {'abbrev': 'LAC', 'name': 'Los Angeles Clippers', 'conference': 'West'},
    1610612747: {'abbrev': 'LAL', 'name': 'Los Angeles Lakers', 'conference': 'West'},
    1610612748: {'abbrev': 'MIA', 'name': 'Miami Heat', 'conference': 'East'},
    1610612749: {'abbrev': 'MIL', 'name': 'Milwaukee Bucks', 'conference': 'East'},
    1610612750: {'abbrev': 'MIN', 'name': 'Minnesota Timberwolves', 'conference': 'West'},
    1610612751: {'abbrev': 'BKN', 'name': 'Brooklyn Nets', 'conference': 'East'},
    1610612752: {'abbrev': 'NYK', 'name': 'New York Knicks', 'conference': 'East'},
    1610612753: {'abbrev': 'ORL', 'name': 'Orlando Magic', 'conference': 'East'},
    1610612754: {'abbrev': 'IND', 'name': 'Indiana Pacers', 'conference': 'East'},
    1610612755: {'abbrev': 'PHI', 'name': 'Philadelphia 76ers', 'conference': 'East'},
    1610612756: {'abbrev': 'PHX', 'name': 'Phoenix Suns', 'conference': 'West'},
    1610612757: {'abbrev': 'POR', 'name': 'Portland Trail Blazers', 'conference': 'West'},
    1610612758: {'abbrev': 'SAC', 'name': 'Sacramento Kings', 'conference': 'West'},
    1610612759: {'abbrev': 'SAS', 'name': 'San Antonio Spurs', 'conference': 'West'},
    1610612760: {'abbrev': 'OKC', 'name': 'Oklahoma City Thunder', 'conference': 'West'},
    1610612761: {'abbrev': 'TOR', 'name': 'Toronto Raptors', 'conference': 'East'},
    1610612762: {'abbrev': 'UTA', 'name': 'Utah Jazz', 'conference': 'West'},
    1610612763: {'abbrev': 'MEM', 'name': 'Memphis Grizzlies', 'conference': 'West'},
    1610612764: {'abbrev': 'WAS', 'name': 'Washington Wizards', 'conference': 'East'},
    1610612765: {'abbrev': 'DET', 'name': 'Detroit Pistons', 'conference': 'East'},
    1610612766: {'abbrev': 'CHA', 'name': 'Charlotte Hornets', 'conference': 'East'}
}

# Derived Mappings
ID_TO_ABBREV = {k: v['abbrev'] for k, v in TEAMS.items()}
ABBREV_TO_ID = {v['abbrev']: k for k, v in TEAMS.items()}

# Historical Abbreviation handling (for defunct/relocated teams if needed in future)
HISTORICAL_ABBREV_MAP = {
    'NOH': 'NOP', # New Orleans Hornets -> Pelicans
    'NJN': 'BKN', # New Jersey Nets -> Brooklyn Nets
}

def get_team_id(abbrev):
    """Get Team ID from Abbreviation, handling historical cases."""
    cleaned_abbrev = HISTORICAL_ABBREV_MAP.get(abbrev, abbrev)
    return ABBREV_TO_ID.get(cleaned_abbrev)

def get_team_abbrev(team_id):
    """Get Abbreviation from Team ID."""
    return ID_TO_ABBREV.get(team_id)












