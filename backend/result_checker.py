#!/usr/bin/env python3
"""
Result checker for daily picks
Automatically checks match results and updates prediction status
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
from sqlalchemy import create_engine, text
from config.database import DATABASE_URL

class ResultChecker:
    """Check match results and update prediction status"""
    
    def __init__(self):
        self.api_key = os.getenv('API_FOOTBALL_KEY')
        self.api_base = 'https://v3.football.api-sports.io'
        self.engine = create_engine(DATABASE_URL)
        
    def get_pending_predictions(self) -> List[Dict]:
        """Get predictions that need result checking"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT id, home_team, away_team, prediction, prediction_type, 
                           match_time, competition, result_status
                    FROM daily_picks 
                    WHERE result_status = 'pending' 
                    AND match_time < NOW()
                    ORDER BY match_time DESC
                """))
                
                predictions = []
                for row in result:
                    predictions.append({
                        'id': row[0],
                        'home_team': row[1],
                        'away_team': row[2],
                        'prediction': row[3],
                        'prediction_type': row[4],
                        'match_time': row[5],
                        'competition': row[6],
                        'result_status': row[7]
                    })
                
                return predictions
                
        except Exception as e:
            logger.error(f"Error getting pending predictions: {e}")
            return []
    
    def get_match_result(self, home_team: str, away_team: str, match_date: datetime) -> Optional[Dict]:
        """Get match result from API-Football"""
        try:
            # Search for the match
            headers = {
                'x-rapidapi-host': 'v3.football.api-sports.io',
                'x-rapidapi-key': self.api_key
            }
            
            # Search for matches on the specific date
            date_str = match_date.strftime('%Y-%m-%d')
            
            url = f"{self.api_base}/fixtures"
            params = {
                'date': date_str,
                'league': '140',  # La Liga
                'season': '2024'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                fixtures = data.get('response', [])
                
                # Find the specific match
                for fixture in fixtures:
                    fixture_data = fixture['fixture']
                    teams = fixture['teams']
                    goals = fixture['goals']
                    
                    # Check if this is our match
                    if (teams['home']['name'].lower() in home_team.lower() or 
                        home_team.lower() in teams['home']['name'].lower()) and \
                       (teams['away']['name'].lower() in away_team.lower() or 
                        away_team.lower() in teams['away']['name'].lower()):
                        
                        # Check if match is finished
                        if fixture_data['status']['short'] == 'FT':
                            return {
                                'home_score': goals['home'],
                                'away_score': goals['away'],
                                'status': 'finished',
                                'fixture_id': fixture_data['id']
                            }
                        elif fixture_data['status']['short'] in ['PST', 'CANC']:
                            return {
                                'status': 'postponed',
                                'fixture_id': fixture_data['id']
                            }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting match result: {e}")
            return None
    
    def determine_prediction_result(self, prediction: str, prediction_type: str, 
                                  home_score: int, away_score: int) -> str:
        """Determine if prediction was correct"""
        try:
            if prediction_type == 'match_winner':
                if prediction == 'home':
                    return 'correct' if home_score > away_score else 'incorrect'
                elif prediction == 'away':
                    return 'correct' if away_score > home_score else 'incorrect'
                elif prediction == 'draw':
                    return 'correct' if home_score == away_score else 'incorrect'
            
            elif prediction_type == 'both_teams_score':
                both_scored = home_score > 0 and away_score > 0
                if prediction == 'yes':
                    return 'correct' if both_scored else 'incorrect'
                elif prediction == 'no':
                    return 'correct' if not both_scored else 'incorrect'
            
            elif prediction_type == 'over_under':
                total_goals = home_score + away_score
                if 'over' in prediction.lower():
                    # Extract number from prediction (e.g., "over 2.5" -> 2.5)
                    import re
                    numbers = re.findall(r'\d+\.?\d*', prediction)
                    if numbers:
                        threshold = float(numbers[0])
                        return 'correct' if total_goals > threshold else 'incorrect'
                elif 'under' in prediction.lower():
                    numbers = re.findall(r'\d+\.?\d*', prediction)
                    if numbers:
                        threshold = float(numbers[0])
                        return 'correct' if total_goals < threshold else 'incorrect'
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error determining prediction result: {e}")
            return 'unknown'
    
    def update_prediction_result(self, prediction_id: str, result_status: str, 
                               actual_result: str = None) -> bool:
        """Update prediction result in database"""
        try:
            with self.engine.connect() as conn:
                if actual_result:
                    conn.execute(text("""
                        UPDATE daily_picks 
                        SET result_status = :status, 
                            actual_result = :result,
                            result_updated_at = NOW()
                        WHERE id = :id
                    """), {
                        'status': result_status,
                        'result': actual_result,
                        'id': prediction_id
                    })
                else:
                    conn.execute(text("""
                        UPDATE daily_picks 
                        SET result_status = :status,
                            result_updated_at = NOW()
                        WHERE id = :id
                    """), {
                        'status': result_status,
                        'id': prediction_id
                    })
                
                return True
                
        except Exception as e:
            logger.error(f"Error updating prediction result: {e}")
            return False
    
    def check_all_pending_results(self):
        """Check all pending predictions and update their results"""
        logger.info("Starting result checking for pending predictions...")
        
        pending_predictions = self.get_pending_predictions()
        logger.info(f"Found {len(pending_predictions)} pending predictions to check")
        
        for prediction in pending_predictions:
            try:
                logger.info(f"Checking result for: {prediction['home_team']} vs {prediction['away_team']}")
                
                # Parse match time
                match_time = prediction['match_time']
                if isinstance(match_time, str):
                    match_time = datetime.fromisoformat(match_time.replace('Z', '+00:00'))
                
                # Get match result
                result = self.get_match_result(
                    prediction['home_team'],
                    prediction['away_team'],
                    match_time
                )
                
                if result:
                    if result['status'] == 'finished':
                        # Determine if prediction was correct
                        prediction_result = self.determine_prediction_result(
                            prediction['prediction'],
                            prediction['prediction_type'],
                            result['home_score'],
                            result['away_score']
                        )
                        
                        actual_result = f"{result['home_score']}-{result['away_score']}"
                        
                        # Update database
                        if self.update_prediction_result(prediction['id'], prediction_result, actual_result):
                            logger.info(f"✅ Updated result: {prediction_result} ({actual_result})")
                        else:
                            logger.error(f"❌ Failed to update result for {prediction['id']}")
                    
                    elif result['status'] == 'postponed':
                        # Mark as postponed
                        if self.update_prediction_result(prediction['id'], 'postponed'):
                            logger.info(f"✅ Marked as postponed")
                        else:
                            logger.error(f"❌ Failed to mark as postponed for {prediction['id']}")
                
                else:
                    logger.warning(f"⚠️ No result found for {prediction['home_team']} vs {prediction['away_team']}")
                
            except Exception as e:
                logger.error(f"Error checking prediction {prediction['id']}: {e}")
        
        logger.info("Result checking completed")

def main():
    """Main entry point"""
    checker = ResultChecker()
    checker.check_all_pending_results()

if __name__ == "__main__":
    main() 