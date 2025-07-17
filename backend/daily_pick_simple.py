#!/usr/bin/env python3
"""
Daily pick generator using real matches
"""

import os
import sys
import json
from datetime import datetime, timedelta
from loguru import logger
from typing import Dict, List, Any
import random

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_matches_collector import RealMatchesCollector
from ai_predictor import AIPredictor
from telegram_result_updater import TelegramResultUpdater

class DailyPickGenerator:
    """Generate daily picks using real matches"""
    
    def __init__(self):
        self.matches_collector = RealMatchesCollector()
        self.ai_predictor = AIPredictor()
        self.telegram_updater = TelegramResultUpdater()
        
        # Priority competitions for picks
        self.priority_competitions = [
            'conference_league',
            'europa_league', 
            'champions_league',
            'premier_league',
            'la_liga',
            'bundesliga',
            'serie_a',
            'ligue_1'
        ]
    
    def generate_daily_pick(self, target_date: datetime = None) -> Dict:
        """Generate the daily pick for a specific date"""
        if target_date is None:
            target_date = datetime.now() + timedelta(days=1)
        
        print(f"🎯 Generating daily pick for {target_date.strftime('%Y-%m-%d')}")
        
        # Get real matches for the target date
        matches = self.matches_collector.get_matches_for_date(target_date)
        
        if not matches:
            print("❌ No matches found for the target date")
            return self._create_no_pick_message(target_date)
        
        print(f"📊 Found {len(matches)} matches to analyze")
        
        # Filter matches by priority competitions
        priority_matches = [m for m in matches if m.get('competition_type') in self.priority_competitions]
        
        if not priority_matches:
            print("⚠️ No priority competition matches found")
            priority_matches = matches  # Use all matches as fallback
        
        print(f"🎯 Analyzing {len(priority_matches)} priority matches")
        
        # Analyze each match and generate picks
        picks = []
        for match in priority_matches:
            pick = self._analyze_match(match)
            if pick:
                picks.append(pick)
        
        if not picks:
            print("❌ No valid picks found")
            return self._create_no_pick_message(target_date)
        
        # Select the best pick
        best_pick = self._select_best_pick(picks)
        
        print(f"✅ Best pick selected: {best_pick['match']['home_team']} vs {best_pick['match']['away_team']}")
        print(f"   Market: {best_pick['market']}")
        print(f"   Odds: {best_pick['odds']}")
        print(f"   Probability: {best_pick['probability']:.1f}%")
        
        return best_pick
    
    def _analyze_match(self, match: Dict) -> Dict:
        """Analyze a match and generate potential picks"""
        try:
            # Get odds from match data
            odds = match.get('odds', {})
            if not odds:
                return None
            
            # Define markets to analyze
            markets = [
                ('over_2_5', 'Over 2.5 Goals'),
                ('under_2_5', 'Under 2.5 Goals'),
                ('both_teams_score_yes', 'Both Teams to Score - Yes'),
                ('both_teams_score_no', 'Both Teams to Score - No'),
                ('home_win', 'Home Win'),
                ('away_win', 'Away Win'),
                ('draw', 'Draw')
            ]
            
            picks = []
            for market_key, market_name in markets:
                if market_key in odds:
                    odds_value = odds[market_key]
                    
                    # Calculate probability (simplified)
                    probability = self._calculate_probability(odds_value)
                    
                    # More flexible criteria: odds > 1.30 and probability > 60
                    if odds_value > 1.30 and probability > 60:
                        pick = {
                            'match': match,
                            'market': market_name,
                            'market_key': market_key,
                            'odds': odds_value,
                            'probability': probability,
                            'confidence': self._calculate_confidence(match, market_key)
                        }
                        picks.append(pick)
            
            # Return the best pick for this match
            if picks:
                return max(picks, key=lambda x: x['confidence'])
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing match: {e}")
            return None
    
    def _calculate_probability(self, odds: float) -> float:
        """Calculate probability from odds"""
        try:
            # Simplified probability calculation
            probability = (1 / odds) * 100
            return min(probability, 95)  # Cap at 95%
        except:
            return 50.0
    
    def _calculate_confidence(self, match: Dict, market_key: str) -> float:
        """Calculate confidence score for a pick"""
        confidence = 50.0  # Base confidence
        
        # Boost confidence for certain competitions
        competition = match.get('competition_type', '')
        if competition == 'conference_league':
            confidence += 20
        elif competition in ['europa_league', 'champions_league']:
            confidence += 15
        elif competition in ['premier_league', 'la_liga', 'bundesliga']:
            confidence += 10
        
        # Boost confidence for certain markets
        if market_key in ['over_2_5', 'both_teams_score_yes']:
            confidence += 10
        
        # Add some randomness to avoid always picking the same type
        confidence += random.uniform(-5, 5)
        
        return min(confidence, 100)
    
    def _select_best_pick(self, picks: List[Dict]) -> Dict:
        """Select the best pick from the list"""
        if not picks:
            return None
        
        # Sort by confidence and probability
        sorted_picks = sorted(picks, key=lambda x: (x['confidence'], x['probability']), reverse=True)
        
        return sorted_picks[0]
    
    def _create_no_pick_message(self, target_date: datetime) -> Dict:
        """Create a message when no valid picks are found"""
        return {
            'type': 'no_pick',
            'date': target_date.strftime('%Y-%m-%d'),
            'message': f"No se encontraron picks de valor para el {target_date.strftime('%d/%m/%Y')}. Revisa mañana para nuevas oportunidades.",
            'reason': 'No matches meet the criteria (odds > 1.50 and probability > 70%)'
        }
    
    def send_daily_pick(self, target_date: datetime = None) -> bool:
        """Generate and send the daily pick to Telegram"""
        try:
            pick = self.generate_daily_pick(target_date)
            
            if pick.get('type') == 'no_pick':
                message = pick['message']
            else:
                match = pick['match']
                message = self._format_pick_message(pick)
            
            # Send to Telegram
            success = self.telegram_updater.send_message(message)
            
            if success:
                print(f"✅ Daily pick sent successfully")
                return True
            else:
                print(f"❌ Failed to send daily pick")
                return False
                
        except Exception as e:
            logger.error(f"Error sending daily pick: {e}")
            return False
    
    def _format_pick_message(self, pick: Dict) -> str:
        """Format the pick as a message"""
        match = pick['match']
        
        message = f"🎯 PICK DEL DÍA - {match['competition']}\n\n"
        message += f"🏆 {match['home_team']} vs {match['away_team']}\n"
        message += f"⏰ {match['time'].strftime('%H:%M')} - {match['time'].strftime('%d/%m/%Y')}\n\n"
        message += f"📊 MERCADO: {pick['market']}\n"
        message += f"💰 CUOTA: {pick['odds']}\n"
        message += f"📈 PROBABILIDAD: {pick['probability']:.1f}%\n"
        message += f"🎯 CONFIANZA: {pick['confidence']:.1f}%\n\n"
        message += f"#PickDelDia #Futbol #Predicciones"
        
        return message

def main():
    """Main function to run the daily pick generator"""
    generator = DailyPickGenerator()
    
    # Generate pick for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    
    print("🚀 Starting daily pick generation...")
    
    # Generate the pick
    pick = generator.generate_daily_pick(tomorrow)
    
    if pick.get('type') == 'no_pick':
        print(f"📝 {pick['message']}")
    else:
        print(f"✅ Pick generated successfully!")
        print(f"   Match: {pick['match']['home_team']} vs {pick['match']['away_team']}")
        print(f"   Market: {pick['market']}")
        print(f"   Odds: {pick['odds']}")
    
    # Ask if user wants to send to Telegram
    response = input("\n¿Enviar pick a Telegram? (y/n): ")
    if response.lower() in ['y', 'yes', 'sí', 'si']:
        success = generator.send_daily_pick(tomorrow)
        if success:
            print("✅ Pick enviado a Telegram")
        else:
            print("❌ Error al enviar pick")
    else:
        print("📝 Pick no enviado")

if __name__ == "__main__":
    main() 