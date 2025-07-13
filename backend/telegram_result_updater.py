#!/usr/bin/env python3
"""
Telegram result updater
Sends result updates to Telegram when predictions are completed
"""

import os
import requests
from datetime import datetime
from typing import Dict, List
from loguru import logger
from sqlalchemy import create_engine, text
from config.database import DATABASE_URL

class TelegramResultUpdater:
    """Send result updates to Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '7582466483:AAHshXjaU0vu2nZsYd8wSY5pR1XJ6EHmZOQ')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '2070545442')
        self.engine = create_engine(DATABASE_URL)
        
    def get_completed_predictions(self) -> List[Dict]:
        """Get predictions that have been completed but not yet notified"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT id, home_team, away_team, prediction, prediction_type, 
                           confidence, odds, match_time, competition, reasoning,
                           result_status, actual_result, created_at
                    FROM daily_picks 
                    WHERE result_status IN ('correct', 'incorrect')
                    AND result_updated_at::timestamp > created_at::timestamp
                    ORDER BY result_updated_at DESC
                    LIMIT 10
                """))
                
                predictions = []
                for row in result:
                    predictions.append({
                        'id': row[0],
                        'home_team': row[1],
                        'away_team': row[2],
                        'prediction': row[3],
                        'prediction_type': row[4],
                        'confidence': row[5],
                        'odds': row[6],
                        'match_time': row[7],
                        'competition': row[8],
                        'reasoning': row[9],
                        'result_status': row[10],
                        'actual_result': row[11],
                        'created_at': row[12]
                    })
                
                return predictions
                
        except Exception as e:
            logger.error(f"Error getting completed predictions: {e}")
            return []
    
    def send_result_update(self, prediction: Dict) -> bool:
        """Send result update to Telegram"""
        try:
            # Determine result emoji and color
            if prediction['result_status'] == 'correct':
                result_emoji = "✅"
                result_text = "CORRECT"
                result_color = "🟢"
            else:
                result_emoji = "❌"
                result_text = "INCORRECT"
                result_color = "🔴"
            
            # Get competition emoji
            competition = prediction['competition']
            if 'Women' in competition:
                competition_emoji = "⚽👩‍🦰"
            elif 'La Liga' in competition:
                competition_emoji = "⚽🇪🇸"
            elif 'Champions' in competition:
                competition_emoji = "⚽🏆"
            elif 'Premier' in competition:
                competition_emoji = "⚽🏴󠁧󠁢󠁥󠁮󠁧󠁿"
            else:
                competition_emoji = "⚽"
            
            # Format match time
            match_time = prediction['match_time']
            if isinstance(match_time, str):
                match_time = datetime.fromisoformat(match_time.replace('Z', '+00:00'))
            formatted_time = match_time.strftime('%Y-%m-%d %H:%M UTC')
            
            # Create result message
            message = (
                f"{result_color} **RESULT UPDATE** {result_color}\n\n"
                f"{competition_emoji} **{competition}**\n"
                f"🏟️ **Match**: {prediction['home_team']} vs {prediction['away_team']}\n"
                f"🕐 **Time**: {formatted_time}\n"
                f"📊 **Prediction**: {prediction['prediction_type'].replace('_', ' ').title()} - {prediction['prediction']}\n"
                f"🎯 **Confidence**: {prediction['confidence']}%\n"
                f"💰 **Odds**: {prediction['odds']}\n"
                f"📈 **Result**: {result_emoji} {result_text}\n"
            )
            
            # Add actual result if available
            if prediction['actual_result']:
                message += f"📊 **Final Score**: {prediction['actual_result']}\n"
            
            message += f"\n💡 **Reasoning**: {prediction['reasoning']}\n"
            message += f"🤖 **Tipster**: AI Predictor Pro\n\n"
            message += f"*Result automatically updated from API-Football*"
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                logger.info(f"Result update sent to Telegram: {prediction['result_status']}")
                return True
            else:
                logger.error(f"Failed to send result update: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending result update: {e}")
            return False
    
    def send_daily_summary(self) -> bool:
        """Send daily summary of prediction results"""
        try:
            # Get today's results
            today = datetime.now().date()
            
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_predictions,
                        COUNT(CASE WHEN result_status = 'correct' THEN 1 END) as correct_predictions,
                        COUNT(CASE WHEN result_status = 'incorrect' THEN 1 END) as incorrect_predictions,
                        COUNT(CASE WHEN result_status = 'postponed' THEN 1 END) as postponed_predictions
                    FROM daily_picks 
                    WHERE DATE(created_at) = :today
                """), {'today': today})
                
                row = result.fetchone()
                if not row:
                    return False
                
                total = row[0]
                correct = row[1]
                incorrect = row[2]
                postponed = row[3]
                
                if total == 0:
                    return True  # No predictions today
                
                # Calculate success rate
                success_rate = (correct / (correct + incorrect)) * 100 if (correct + incorrect) > 0 else 0
                
                # Create summary message
                message = (
                    f"📊 **DAILY PREDICTION SUMMARY** 📊\n\n"
                    f"📅 **Date**: {today.strftime('%Y-%m-%d')}\n"
                    f"🎯 **Total Predictions**: {total}\n"
                    f"✅ **Correct**: {correct}\n"
                    f"❌ **Incorrect**: {incorrect}\n"
                    f"⏸️ **Postponed**: {postponed}\n"
                    f"📈 **Success Rate**: {success_rate:.1f}%\n\n"
                )
                
                # Add emoji based on performance
                if success_rate >= 70:
                    message += "🏆 **Excellent performance today!** 🏆"
                elif success_rate >= 50:
                    message += "👍 **Good performance today!** 👍"
                else:
                    message += "📉 **Room for improvement today** 📉"
                
                message += f"\n\n*Summary automatically generated from today's predictions*"
                
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                payload = {
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
                
                response = requests.post(url, data=payload)
                if response.status_code == 200:
                    logger.info("Daily summary sent to Telegram")
                    return True
                else:
                    logger.error(f"Failed to send daily summary: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            return False
    
    def run_updates(self):
        """Run result updates"""
        logger.info("Starting Telegram result updates...")
        
        # Send individual result updates
        completed_predictions = self.get_completed_predictions()
        logger.info(f"Found {len(completed_predictions)} completed predictions to update")
        
        for prediction in completed_predictions:
            if self.send_result_update(prediction):
                logger.info(f"✅ Result update sent for {prediction['home_team']} vs {prediction['away_team']}")
            else:
                logger.error(f"❌ Failed to send result update for {prediction['id']}")
        
        # Send daily summary (only once per day)
        if self.send_daily_summary():
            logger.info("✅ Daily summary sent")
        else:
            logger.info("ℹ️ No daily summary sent (no predictions today or already sent)")
        
        logger.info("Telegram result updates completed")

def main():
    """Main entry point"""
    updater = TelegramResultUpdater()
    updater.run_updates()

if __name__ == "__main__":
    main() 