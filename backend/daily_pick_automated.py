#!/usr/bin/env python3
"""
Automated daily pick generator using REAL scheduled matches
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

from real_tomorrow_matches import RealTomorrowMatchesCollector
from ai_predictor import AIPredictor

class AutomatedDailyPickGenerator:
    """Automated daily pick generator using REAL scheduled matches"""
    
    def __init__(self):
        self.matches_collector = RealTomorrowMatchesCollector()
        self.ai_predictor = AIPredictor()
        
        # Telegram configuration
        self.bot_token = '7582466483:AAHshXjaU0vu2nZsYd8wSY5pR1XJ6EHmZOQ'
        self.chat_id = '2070545442'
        
        # Priority competitions for picks (currently active)
        self.priority_competitions = [
            'mls',              # Major League Soccer (currently active)
            'brasileirao',      # Brazilian Serie A (currently active)
            'argentina_liga',   # Argentine Primera Division (currently active)
            'mexico_liga',      # Mexican Liga MX (currently active)
            'norway_eliteserien', # Norwegian Eliteserien (currently active)
            'sweden_allsvenskan',  # Swedish Allsvenskan (currently active)
            'denmark_superliga',   # Danish Superliga (currently active)
            'finland_veikkausliiga', # Finnish Veikkausliiga (currently active)
            'poland_ekstraklasa',   # Polish Ekstraklasa (currently active)
            'czech_fortuna_liga',   # Czech Fortuna Liga (currently active)
            'austria_bundesliga',   # Austrian Bundesliga (currently active)
            'switzerland_super_league', # Swiss Super League (currently active)
            'belgium_pro_league',   # Belgian Pro League (currently active)
            'netherlands_eredivisie', # Dutch Eredivisie (currently active)
            'portugal_primeira_liga', # Portuguese Primeira Liga (currently active)
            'greece_super_league',   # Greek Super League (currently active)
            'turkey_super_lig',      # Turkish Süper Lig (currently active)
            'ukraine_premier_league', # Ukrainian Premier League (currently active)
            'russia_premier_league',  # Russian Premier League (currently active)
            'japan_j_league',        # Japanese J-League (currently active)
            'south_korea_k_league',  # South Korean K-League (currently active)
            'china_super_league',    # Chinese Super League (currently active)
            'australia_a_league'     # Australian A-League (currently active)
        ]
    
    def generate_daily_pick(self, target_date: datetime = None) -> Dict:
        """Generate the daily pick for a specific date using REAL scheduled matches"""
        if target_date is None:
            target_date = datetime.now() + timedelta(days=1)
        
        logger.info(f"🎯 Generating daily pick for {target_date.strftime('%Y-%m-%d')}")
        
        # Get REAL scheduled matches for the target date
        matches = self.matches_collector.get_real_matches_for_tomorrow()
        
        if not matches:
            logger.warning("❌ No REAL scheduled matches found for the target date")
            return self._create_no_pick_message(target_date)
        
        logger.info(f"📊 Found {len(matches)} REAL scheduled matches to analyze")
        
        # Filter matches by priority competitions
        priority_matches = [m for m in matches if m.get('competition_type') in self.priority_competitions]
        
        if not priority_matches:
            logger.warning("⚠️ No priority competition matches found")
            priority_matches = matches  # Use all matches as fallback
        
        logger.info(f"🎯 Analyzing {len(priority_matches)} priority REAL scheduled matches")
        
        # Analyze each match and generate picks
        picks = []
        for match in priority_matches:
            pick = self._analyze_match(match)
            if pick:
                picks.append(pick)
        
        if not picks:
            logger.warning("❌ No valid picks found")
            return self._create_no_pick_message(target_date)
        
        # Select the best pick
        best_pick = self._select_best_pick(picks)
        
        logger.info(f"✅ Best pick selected: {best_pick['match']['home_team']} vs {best_pick['match']['away_team']}")
        logger.info(f"   Competition: {best_pick['match']['competition']}")
        logger.info(f"   Market: {best_pick['market']}")
        logger.info(f"   Odds: {best_pick['odds']}")
        logger.info(f"   Probability: {best_pick['probability']:.1f}%")
        logger.info(f"   Confidence: {best_pick['confidence']:.1f}%")
        logger.info(f"   Source: {best_pick['match']['source']}")
        
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
                    
                    # STRICT criteria: odds > 1.30, probability >= 70%, confidence >= 70%
                    if odds_value > 1.30 and probability >= 70:
                        confidence = self._calculate_confidence(match, market_key)
                        if confidence >= 70:
                            pick = {
                                'match': match,
                                'market': market_name,
                                'market_key': market_key,
                                'odds': odds_value,
                                'probability': probability,
                                'confidence': confidence
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
        """Calculate confidence score for a pick - MINIMUM 70%"""
        confidence = 70.0  # Base confidence starts at 70%
        
        # Boost confidence for certain competitions
        competition = match.get('competition_type', '')
        if competition in ['europa_league', 'champions_league']:
            confidence += 15
        elif competition in ['premier_league', 'la_liga', 'bundesliga']:
            confidence += 10
        elif competition in ['mls', 'brasileirao', 'argentina_liga']:
            confidence += 8
        
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
        
        # Sort by confidence and probability (both must be >= 70%)
        sorted_picks = sorted(picks, key=lambda x: (x['confidence'], x['probability']), reverse=True)
        
        return sorted_picks[0]
    
    def _create_no_pick_message(self, target_date: datetime) -> Dict:
        """Create a message when no valid picks are found"""
        return {
            'type': 'no_pick',
            'date': target_date.strftime('%Y-%m-%d'),
            'message': f"No se encontraron picks de valor para el {target_date.strftime('%d/%m/%Y')}. Revisa mañana para nuevas oportunidades.",
            'reason': 'No matches meet the strict criteria (odds > 1.30, probability >= 70%, confidence >= 70%)'
        }
    
    def send_telegram_message(self, message: str) -> bool:
        """Send message to Telegram"""
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Message sent to Telegram successfully")
                return True
            else:
                logger.error(f"❌ Failed to send Telegram message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
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
            success = self.send_telegram_message(message)
            
            if success:
                logger.info("✅ Daily pick sent successfully")
                return True
            else:
                logger.error("❌ Failed to send daily pick")
                return False
                
        except Exception as e:
            logger.error(f"Error sending daily pick: {e}")
            return False
    
    def _format_pick_message(self, pick: Dict) -> str:
        """Format the pick as a message"""
        match = pick['match']
        
        message = f"🎯 <b>PICK DEL DÍA - {match['competition']}</b>\n\n"
        message += f"🏆 <b>{match['home_team']} vs {match['away_team']}</b>\n"
        message += f"⏰ {match['time'].strftime('%H:%M')} - {match['time'].strftime('%d/%m/%Y')}\n\n"
        message += f"📊 <b>MERCADO:</b> {pick['market']}\n"
        message += f"💰 <b>CUOTA:</b> {pick['odds']}\n"
        message += f"📈 <b>PROBABILIDAD:</b> {pick['probability']:.1f}%\n"
        message += f"🎯 <b>CONFIANZA:</b> {pick['confidence']:.1f}%\n\n"
        message += f"✅ <b>PARTIDO REAL PROGRAMADO PARA MAÑANA</b>\n\n"
        message += f"#PickDelDia #Futbol #Predicciones"
        
        return message

def main():
    """Main function to run the automated daily pick generator"""
    # Configure logging
    logger.add(
        "logs/daily_pick_automated.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="1 day",
        retention="7 days"
    )
    
    generator = AutomatedDailyPickGenerator()
    
    # Generate pick for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    
    logger.info("🚀 Starting automated daily pick generation...")
    
    # Generate and send the pick
    success = generator.send_daily_pick(tomorrow)
    
    if success:
        logger.info("✅ Automated daily pick completed successfully")
    else:
        logger.error("❌ Automated daily pick failed")
    
    return success

if __name__ == "__main__":
    main() 