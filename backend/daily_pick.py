import os
from datetime import datetime
from loguru import logger
from config.settings import LOGGING_CONFIG, DATABASE_URL
from data_collector import DataCollector
from ai_predictor import AIPredictor
from sqlalchemy import create_engine, Table, Column, String, Float, DateTime, MetaData
import requests
import pytz

# Configure logging
logger.add(
    LOGGING_CONFIG['file'],
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    rotation=LOGGING_CONFIG['rotation'],
    retention=LOGGING_CONFIG['retention']
)

def main():
    # Get current date in Spain time
    madrid_tz = pytz.timezone('Europe/Madrid')
    now_madrid = datetime.now(madrid_tz)
    today_str = now_madrid.strftime('%Y-%m-%d')

    # Collect latest data with validation
    collector = DataCollector()
    data = collector.get_latest_data()

    # Generate predictions for real matches today that have not started
    ai_predictor = AIPredictor()
    upcoming_matches = [
        match for match in data.get('matches', [])
        if match.get('status') in ['scheduled', 'not_started']
        and match.get('time', '').startswith(today_str)
    ]
    if not upcoming_matches:
        logger.warning(f"No real matches found for today {today_str}.")
        return
    all_predictions = []
    for match in upcoming_matches:
        team_data = data.get('teams', {})
        h2h_data = data.get('h2h_records', {})
        odds_data = data.get('odds', {}).get(match.get('id', ''), {})
        predictions = ai_predictor.make_prediction(match, team_data, h2h_data, odds_data)
        for pred in predictions:
            pred_dict = {
                'id': pred.id,
                'match_id': pred.match_id,
                'home_team': match.get('home_team'),
                'away_team': match.get('away_team'),
                'match_time': match.get('time'),
                'prediction_type': pred.prediction_type.value,
                'prediction': pred.prediction,
                'confidence': pred.confidence,
                'odds': pred.odds,
                'reasoning': pred.reasoning,
                'tipster': pred.tipster,
                'created_at': now_madrid.isoformat(),
                'expires_at': pred.expires_at.isoformat()
            }
            all_predictions.append(pred_dict)
    if not all_predictions:
        logger.warning(f"No predictions generated for today {today_str}.")
        return
    # Select the best pick (highest confidence)
    best_pick = max(all_predictions, key=lambda x: x['confidence'])
    logger.info(f"Best pick for {today_str}: {best_pick}")

    # Store only one pick for today in the database
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()
    picks_table = Table(
        'daily_picks', metadata,
        Column('id', String, primary_key=True),
        Column('match_id', String),
        Column('home_team', String),
        Column('away_team', String),
        Column('match_time', String),
        Column('prediction_type', String),
        Column('prediction', String),
        Column('confidence', Float),
        Column('odds', Float),
        Column('reasoning', String),
        Column('tipster', String),
        Column('created_at', String),
        Column('expires_at', String)
    )
    metadata.create_all(engine)
    with engine.connect() as conn:
        # Remove any previous pick for today
        conn.execute(
            picks_table.delete().where(picks_table.c.match_time.startswith(today_str))
        )
        # Insert the new pick
        conn.execute(picks_table.insert(), best_pick)
    logger.info(f"Stored new pick for {today_str} in the database.")

if __name__ == "__main__":
    main() 