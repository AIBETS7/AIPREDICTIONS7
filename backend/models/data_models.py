from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class MatchStatus(Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

class PredictionType(Enum):
    MATCH_WINNER = "match_winner"
    OVER_UNDER = "over_under"
    BOTH_TEAMS_SCORE = "both_teams_score"
    CORRECT_SCORE = "correct_score"
    FIRST_GOALSCORER = "first_goalscorer"
    HALF_TIME_RESULT = "half_time_result"
    DOUBLE_CHANCE = "double_chance"

@dataclass
class Team:
    id: str
    name: str
    short_name: str
    country: str
    league: str
    form: List[str]  # Last 5 matches: W, D, L
    goals_scored_avg: float
    goals_conceded_avg: float
    shots_avg: float
    possession_avg: float
    injuries: List[str]
    suspensions: List[str]
    last_updated: datetime

@dataclass
class Match:
    id: str
    home_team: Team
    away_team: Team
    date: datetime
    status: MatchStatus
    competition: str
    season: str
    venue: Optional[str]
    referee: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]
    half_time_home: Optional[int]
    half_time_away: Optional[int]
    odds: Dict[str, float]
    statistics: Dict[str, Any]
    last_updated: datetime

@dataclass
class H2HRecord:
    home_team: str
    away_team: str
    total_matches: int
    home_wins: int
    away_wins: int
    draws: int
    home_goals: int
    away_goals: int
    last_5_matches: List[Dict[str, Any]]
    last_updated: datetime

@dataclass
class Player:
    id: str
    name: str
    team: str
    position: str
    goals_scored: int
    assists: int
    yellow_cards: int
    red_cards: int
    minutes_played: int
    form: List[str]
    injuries: List[str]
    last_updated: datetime

@dataclass
class Prediction:
    id: str
    match_id: str
    prediction_type: PredictionType
    prediction: str
    confidence: float
    odds: float
    reasoning: str
    tipster: str
    created_at: datetime
    expires_at: datetime
    status: str  # pending, won, lost, void

@dataclass
class OddsData:
    match_id: str
    bookmaker: str
    home_win: float
    draw: float
    away_win: float
    over_2_5: float
    under_2_5: float
    both_teams_score_yes: float
    both_teams_score_no: float
    last_updated: datetime

@dataclass
class Statistics:
    match_id: str
    home_possession: float
    away_possession: float
    home_shots: int
    away_shots: int
    home_shots_on_target: int
    away_shots_on_target: int
    home_corners: int
    away_corners: int
    home_fouls: int
    away_fouls: int
    home_yellow_cards: int
    away_yellow_cards: int
    home_red_cards: int
    away_red_cards: int
    last_updated: datetime

@dataclass
class WeatherData:
    match_id: str
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float
    conditions: str
    last_updated: datetime

@dataclass
class RefereeData:
    referee_id: str
    name: str
    matches_officiated: int
    avg_yellow_cards: float
    avg_red_cards: float
    avg_fouls: float
    home_team_bias: float  # -1 to 1, negative favors away teams
    last_updated: datetime

@dataclass
class DataSource:
    name: str
    url: str
    last_scraped: datetime
    status: str  # active, error, disabled
    error_count: int
    success_rate: float
    response_time_avg: float
