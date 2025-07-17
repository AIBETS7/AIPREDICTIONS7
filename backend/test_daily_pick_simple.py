#!/usr/bin/env python3
"""
Test simplified daily pick system
"""

import os
from datetime import datetime, timedelta
from loguru import logger
from ai_predictor import AIPredictor
import requests

# Configure logging
logger.add(
    "logs/football_predictions.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    rotation="1 day",
    retention="30 days"
)

def create_sample_matches():
    """Create sample Conference League matches for testing"""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    sample_matches = [
        {
            'id': 'conf_001',
            'home_team': 'Fiorentina',
            'away_team': 'Molde',
            'time': f"{tomorrow_str} 21:00",
            'competition': 'UEFA Conference League',
            'status': 'scheduled',
            'source': 'sample'
        },
        {
            'id': 'conf_002', 
            'home_team': 'PAOK',
            'away_team': 'Dinamo Zagreb',
            'time': f"{tomorrow_str} 20:00",
            'competition': 'UEFA Conference League',
            'status': 'scheduled',
            'source': 'sample'
        },
        {
            'id': 'conf_003',
            'home_team': 'Slovan Bratislava',
            'away_team': 'Partizan',
            'time': f"{tomorrow_str} 19:00",
            'competition': 'UEFA Conference League',
            'status': 'scheduled',
            'source': 'sample'
        }
    ]
    
    return sample_matches

def send_telegram_message(message: str):
    """Send message to Telegram"""
    TELEGRAM_BOT_TOKEN = '7582466483:AAHshXjaU0vu2nZsYd8wSY5pR1XJ6EHmZOQ'
    TELEGRAM_CHAT_ID = '2070545442'
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    
    try:
        resp = requests.post(url, data=payload)
        if resp.status_code == 200:
            logger.info("Mensaje enviado a Telegram correctamente.")
            print("✅ Mensaje enviado a Telegram")
        else:
            logger.error(f"Error enviando mensaje a Telegram: {resp.text}")
            print(f"❌ Error enviando mensaje: {resp.text}")
    except Exception as e:
        logger.error(f"Excepción enviando mensaje a Telegram: {e}")
        print(f"❌ Excepción: {e}")

def main():
    """Main function to test daily pick system"""
    print("🔍 Testing Daily Pick System for Conference League")
    print("=" * 60)
    
    # Get sample matches
    upcoming_matches = create_sample_matches()
    print(f"📅 Found {len(upcoming_matches)} Conference League matches:")
    
    for i, match in enumerate(upcoming_matches, 1):
        print(f"{i}. {match['home_team']} vs {match['away_team']} - {match['time']}")
    
    # Generate predictions
    ai_predictor = AIPredictor()
    all_predictions = []
    
    print("\n🤖 Generating predictions...")
    
    for match in upcoming_matches:
        try:
            # Create dummy data for prediction
            team_data = {
                match['home_team']: {
                    'goals_scored_avg': 1.8,
                    'goals_conceded_avg': 1.2,
                    'shots_avg': 12.5,
                    'possession_avg': 55.0,
                    'form': ['W', 'W', 'D', 'L', 'W']
                },
                match['away_team']: {
                    'goals_scored_avg': 1.5,
                    'goals_conceded_avg': 1.4,
                    'shots_avg': 10.8,
                    'possession_avg': 48.0,
                    'form': ['L', 'W', 'D', 'W', 'L']
                }
            }
            
            h2h_data = {}
            odds_data = {
                'home_win': 1.85,
                'draw': 3.40,
                'away_win': 4.20,
                'over_2_5': 2.10,
                'under_2_5': 1.75,
                'both_teams_score_yes': 1.90,
                'both_teams_score_no': 1.90
            }
            
            predictions = ai_predictor.make_prediction(match, team_data, h2h_data, odds_data)
            
            for pred in predictions:
                # Filter only picks with odds > 1.50 and probability > 70%
                if pred.odds is not None and pred.odds > 1.50 and pred.confidence > 0.70:
                    pred_dict = {
                        'id': pred.id,
                        'match_id': pred.match_id,
                        'home_team': match['home_team'],
                        'away_team': match['away_team'],
                        'match_time': match['time'],
                        'competition': match['competition'],
                        'prediction_type': pred.prediction_type.value,
                        'prediction': pred.prediction,
                        'confidence': pred.confidence,
                        'odds': pred.odds,
                        'reasoning': pred.reasoning,
                        'tipster': pred.tipster
                    }
                    all_predictions.append(pred_dict)
                    print(f"✅ Generated pick: {pred.prediction} (Confidence: {pred.confidence:.1%}, Odds: {pred.odds:.2f})")
        
        except Exception as e:
            logger.error(f"Error processing match {match['id']}: {e}")
            continue
    
    if not all_predictions:
        print("\n❌ No value picks found (odds > 1.50, prob > 70%)")
        send_telegram_message("Hoy no hay ningún pick estadístico de valor (cuota > 1.50 y probabilidad > 70%) en la Conference League.")
        return
    
    # Select the best pick (highest confidence)
    best_pick = max(all_predictions, key=lambda x: x['confidence'])
    print(f"\n🏆 Best pick selected:")
    print(f"Match: {best_pick['home_team']} vs {best_pick['away_team']}")
    print(f"Pick: {best_pick['prediction']}")
    print(f"Confidence: {best_pick['confidence']:.1%}")
    print(f"Odds: {best_pick['odds']:.2f}")
    
    # Send message to Telegram
    message = (
        f"PICK DIARIO – Conference League\n"
        f"{best_pick['home_team']} vs. {best_pick['away_team']}\n"
        f"🕒 {best_pick['match_time']}\n"
        f"Pick: {best_pick['prediction']}\n"
        f"Cuota: {best_pick['odds']:.2f}\n"
        f"Probabilidad: {best_pick['confidence']*100:.0f}%\n"
        f"Motivo: {best_pick['reasoning'].split('.')[0]}"
    )
    
    print(f"\n📱 Sending to Telegram:")
    print(message)
    
    send_telegram_message(message)
    
    print("\n✅ Daily pick system test completed successfully!")

if __name__ == "__main__":
    main() 