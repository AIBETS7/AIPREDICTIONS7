import os
from datetime import datetime
from typing import Dict, List

# Base configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    os.makedirs(directory, exist_ok=True)

# Database configuration
DATABASE_URL = "sqlite:///football_predictions.db"

# API Keys and credentials (you'll need to get these)
BETSAPI_KEY = os.getenv('BETSAPI_KEY', 'your_betsapi_key_here')
FLASHSCORE_API_KEY = os.getenv('FLASHSCORE_API_KEY', 'your_flashscore_key_here')
SOFASCORE_API_KEY = os.getenv('SOFASCORE_API_KEY', 'your_sofascore_key_here')

# Web scraping configuration
SCRAPING_CONFIG = {
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'request_delay': 2,  # seconds between requests
    'max_retries': 3,
    'timeout': 30,
    'headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
}

# Data sources configuration
DATA_SOURCES = {
    'flashscore': {
        'base_url': 'https://www.flashscore.com',
        'api_url': 'https://api.flashscore.com',
        'enabled': True,
        'priority': 1,
        'update_frequency': 300,  # 5 minutes
    },
    'sofascore': {
        'base_url': 'https://www.sofascore.com',
        'api_url': 'https://api.sofascore.com',
        'enabled': True,
        'priority': 2,
        'update_frequency': 300,  # 5 minutes
    },
    'betsapi': {
        'base_url': 'https://betsapi.com',
        'api_url': 'https://api.betsapi.com',
        'enabled': True,
        'priority': 3,
        'update_frequency': 600,  # 10 minutes
    },
    'whoscored': {
        'base_url': 'https://www.whoscored.com',
        'enabled': True,
        'priority': 4,
        'update_frequency': 900,  # 15 minutes
    },
    'transfermarkt': {
        'base_url': 'https://www.transfermarkt.com',
        'enabled': True,
        'priority': 5,
        'update_frequency': 1800,  # 30 minutes
    }
}

# La Liga specific configuration
LA_LIGA_CONFIG = {
    'league_id': 'ES1',  # FlashScore league ID for La Liga
    'season': '2024/2025',
    'teams': [
        'Real Madrid', 'Barcelona', 'Atletico Madrid', 'Athletic Bilbao',
        'Girona', 'Real Sociedad', 'Real Betis', 'Las Palmas',
        'Valencia', 'Getafe', 'Rayo Vallecano', 'Osasuna',
        'Villarreal', 'Mallorca', 'Alaves', 'Celta Vigo',
        'Sevilla', 'Granada', 'Cadiz', 'Almeria'
    ],
    'match_types': ['home', 'away', 'h2h'],
    'statistics': [
        'goals_scored', 'goals_conceded', 'shots', 'shots_on_target',
        'possession', 'corners', 'fouls', 'yellow_cards', 'red_cards',
        'form', 'injuries', 'suspensions'
    ]
}

# AI Model configuration
AI_CONFIG = {
    'model_type': 'ensemble',  # ensemble, neural_network, random_forest
    'features': [
        'team_form', 'h2h_record', 'home_away_form', 'goals_scored_avg',
        'goals_conceded_avg', 'shots_avg', 'possession_avg', 'injuries_count',
        'suspensions_count', 'rest_days', 'motivation_factor', 'weather',
        'referee_stats', 'crowd_factor', 'odds_movement'
    ],
    'prediction_types': [
        'match_winner', 'over_under', 'both_teams_score', 'correct_score',
        'first_goalscorer', 'half_time_result', 'double_chance'
    ],
    'confidence_threshold': 0.75,
    'update_frequency': 3600,  # 1 hour
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}',
    'file': os.path.join(BASE_DIR, 'logs', 'football_predictions.log'),
    'rotation': '1 day',
    'retention': '30 days'
}

# Create logs directory
os.makedirs(os.path.dirname(LOGGING_CONFIG['file']), exist_ok=True)

# Rate limiting configuration
RATE_LIMITS = {
    'requests_per_minute': 30,
    'requests_per_hour': 1000,
    'requests_per_day': 10000,
}

# Cache configuration
CACHE_CONFIG = {
    'enabled': True,
    'ttl': 300,  # 5 minutes
    'max_size': 1000,
}

# Notification configuration
NOTIFICATION_CONFIG = {
    'email_enabled': False,
    'telegram_enabled': False,
    'webhook_enabled': False,
    'prediction_alerts': True,
    'error_alerts': True,
}
