import os
from datetime import datetime
from loguru import logger
from config.settings import LOGGING_CONFIG, DATABASE_URL
from data_collector import DataCollector
from ai_predictor import AIPredictor
from sqlalchemy import create_engine, Table, Column, String, Float, DateTime, MetaData
import requests

# Configure logging
logger.add(
    LOGGING_CONFIG['file'],
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    rotation=LOGGING_CONFIG['rotation'],
    retention=LOGGING_CONFIG['retention']
)

def main():
    # Collect latest data
    collector = DataCollector()
    data = collector.get_latest_data()

    # Generate predictions
    ai_predictor = AIPredictor()
    upcoming_matches = [
        match for match in data.get('matches', [])
        if match.get('status') == 'scheduled'
    ]
    upcoming_matches = upcoming_matches[:10]
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
                'created_at': pred.created_at.isoformat(),
                'expires_at': pred.expires_at.isoformat()
            }
            all_predictions.append(pred_dict)
    if not all_predictions:
        logger.warning("No predictions generated.")
        return
    # Select the best pick (highest confidence)
    best_pick = max(all_predictions, key=lambda x: x['confidence'])
    logger.info(f"Best pick: {best_pick}")

    # Log/store the pick in the database
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
        # Upsert by id
        conn.execute(picks_table.insert().prefix_with('OR REPLACE'), best_pick)
    logger.info("Best pick stored in the database.")

    # Send the pick to Telegram
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if bot_token and chat_id:
        message = (
            f"\U0001F3C6 Daily Football Pick!\n"
            f"Match: {best_pick['home_team']} vs {best_pick['away_team']}\n"
            f"Time: {best_pick['match_time']}\n"
            f"Prediction: {best_pick['prediction_type']} - {best_pick['prediction']}\n"
            f"Confidence: {best_pick['confidence']*100:.1f}%\n"
            f"Odds: {best_pick['odds']}\n"
            f"Reasoning: {best_pick['reasoning']}\n"
            f"Tipster: {best_pick['tipster']}\n"
        )
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        try:
            resp = requests.post(url, data=payload)
            if resp.status_code == 200:
                logger.info("Best pick sent to Telegram.")
            else:
                logger.error(f"Failed to send Telegram message: {resp.text}")
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
    else:
        logger.warning("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set. Skipping Telegram notification.")

if __name__ == "__main__":
    main() 