#!/usr/bin/env python3
"""
Add Women's Euro matches for Saturday to test the system
"""

import json
from datetime import datetime, timedelta
from loguru import logger
from config.settings import LOGGING_CONFIG

# Configure logging
logger.add(
    LOGGING_CONFIG['file'],
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    rotation=LOGGING_CONFIG['rotation'],
    retention=LOGGING_CONFIG['retention']
)

def add_womens_euro_matches():
    """Add Women's Euro matches for Saturday"""
    
    # Saturday Women's Euro matches (example matches)
    womens_euro_matches = [
        {
            'id': 'weuro_001',
            'home_team': 'Spain Women',
            'away_team': 'Denmark Women',
            'time': '2025-07-12 15:00',
            'status': 'scheduled',
            'competition': 'UEFA Women\'s Euro 2025 Qualifiers',
            'competition_type': 'womens_euro',
            'home_score': None,
            'away_score': None,
            'venue': 'Estadio de La Cartuja',
            'referee': 'TBD'
        },
        {
            'id': 'weuro_002',
            'home_team': 'England Women',
            'away_team': 'France Women',
            'time': '2025-07-12 17:30',
            'status': 'scheduled',
            'competition': 'UEFA Women\'s Euro 2025 Qualifiers',
            'competition_type': 'womens_euro',
            'home_score': None,
            'away_score': None,
            'venue': 'Wembley Stadium',
            'referee': 'TBD'
        },
        {
            'id': 'weuro_003',
            'home_team': 'Germany Women',
            'away_team': 'Netherlands Women',
            'time': '2025-07-12 20:00',
            'status': 'scheduled',
            'competition': 'UEFA Women\'s Euro 2025 Qualifiers',
            'competition_type': 'womens_euro',
            'home_score': None,
            'away_score': None,
            'venue': 'Olympiastadion Berlin',
            'referee': 'TBD'
        }
    ]
    
    # Load existing data
    try:
        with open("backend/data/processed/latest_data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {
            'matches': [],
            'teams': {},
            'h2h_records': {},
            'odds': {},
            'statistics': {},
            'last_updated': datetime.now().isoformat()
        }
    
    # Add Women's Euro matches
    existing_match_ids = {match.get('id') for match in data.get('matches', [])}
    
    for match in womens_euro_matches:
        if match['id'] not in existing_match_ids:
            data['matches'].append(match)
            logger.info(f"Added match: {match['home_team']} vs {match['away_team']}")
    
    # Add team data for Women's Euro teams
    womens_teams = {
        'Spain Women': {
            'form': ['W', 'W', 'D', 'W', 'W'],
            'goals_scored_avg': 2.8,
            'goals_conceded_avg': 0.6,
            'shots_avg': 15.2,
            'possession_avg': 65.0,
            'injuries': [],
            'suspensions': []
        },
        'Denmark Women': {
            'form': ['L', 'W', 'D', 'L', 'W'],
            'goals_scored_avg': 1.4,
            'goals_conceded_avg': 1.2,
            'shots_avg': 12.8,
            'possession_avg': 52.0,
            'injuries': [],
            'suspensions': []
        },
        'England Women': {
            'form': ['W', 'W', 'W', 'D', 'W'],
            'goals_scored_avg': 3.2,
            'goals_conceded_avg': 0.8,
            'shots_avg': 18.5,
            'possession_avg': 68.0,
            'injuries': [],
            'suspensions': []
        },
        'France Women': {
            'form': ['W', 'L', 'W', 'W', 'D'],
            'goals_scored_avg': 2.6,
            'goals_conceded_avg': 1.0,
            'shots_avg': 16.3,
            'possession_avg': 62.0,
            'injuries': [],
            'suspensions': []
        },
        'Germany Women': {
            'form': ['W', 'W', 'L', 'W', 'W'],
            'goals_scored_avg': 2.9,
            'goals_conceded_avg': 0.9,
            'shots_avg': 17.1,
            'possession_avg': 64.0,
            'injuries': [],
            'suspensions': []
        },
        'Netherlands Women': {
            'form': ['D', 'W', 'W', 'L', 'W'],
            'goals_scored_avg': 2.1,
            'goals_conceded_avg': 1.3,
            'shots_avg': 14.7,
            'possession_avg': 58.0,
            'injuries': [],
            'suspensions': []
        }
    }
    
    # Add team data
    for team_name, team_data in womens_teams.items():
        if team_name not in data['teams']:
            data['teams'][team_name] = team_data
            logger.info(f"Added team data for: {team_name}")
    
    # Update timestamp
    data['last_updated'] = datetime.now().isoformat()
    
    # Save updated data
    with open("backend/data/processed/latest_data.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"Added {len(womens_euro_matches)} Women's Euro matches for Saturday")
    print(f"✅ Added {len(womens_euro_matches)} Women's Euro matches for Saturday")
    print("Matches added:")
    for match in womens_euro_matches:
        print(f"  • {match['home_team']} vs {match['away_team']} - {match['time']}")

if __name__ == "__main__":
    add_womens_euro_matches() 