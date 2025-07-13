import os
import sys
import time
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from loguru import logger
from config.settings import LOGGING_CONFIG
from data_collector import DataCollector
from ai_predictor import AIPredictor
from payment_routes import payment_bp
from payment_processor import payment_processor

# Configure logging
logger.add(
    LOGGING_CONFIG['file'],
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    rotation=LOGGING_CONFIG['rotation'],
    retention=LOGGING_CONFIG['retention']
)

app = Flask(__name__)
CORS(app)

# Register payment blueprint
app.register_blueprint(payment_bp)

# Initialize components
data_collector = DataCollector()
ai_predictor = AIPredictor()

# Initialize payment tables
payment_processor.create_payment_tables()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/collect-data', methods=['POST'])
def collect_data():
    """Trigger data collection from all sources"""
    try:
        days_back = request.json.get('days_back', 7)
        days_forward = request.json.get('days_forward', 7)
        
        logger.info(f"Starting data collection: {days_back} days back, {days_forward} days forward")
        
        data = data_collector.collect_all_data(days_back, days_forward)
        
        return jsonify({
            'success': True,
            'message': 'Data collection completed',
            'data_summary': {
                'matches': len(data.get('matches', [])),
                'teams': len(data.get('teams', {})),
                'h2h_records': len(data.get('h2h_records', {})),
                'odds': len(data.get('odds', {}))
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in data collection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get AI predictions for upcoming matches"""
    try:
        # Get latest data
        data = data_collector.get_latest_data()
        
        # Filter upcoming matches
        upcoming_matches = [
            match for match in data.get('matches', [])
            if match.get('status') == 'scheduled'
        ]
        
        # Limit to next 10 matches
        upcoming_matches = upcoming_matches[:10]
        
        all_predictions = []
        
        for match in upcoming_matches:
            try:
                # Get related data
                team_data = data.get('teams', {})
                h2h_data = data.get('h2h_records', {})
                odds_data = data.get('odds', {}).get(match.get('id', ''), {})
                
                # Make predictions
                predictions = ai_predictor.make_prediction(
                    match, team_data, h2h_data, odds_data
                )
                
                # Add match info to predictions
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
            
            except Exception as e:
                logger.error(f"Error making predictions for match {match.get('id')}: {e}")
                continue
        
        # Sort by confidence
        all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return jsonify({
            'success': True,
            'predictions': all_predictions,
            'total_predictions': len(all_predictions),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/matches', methods=['GET'])
def get_matches():
    """Get matches data"""
    try:
        data = data_collector.get_latest_data()
        
        # Filter and format matches
        matches = []
        for match in data.get('matches', []):
            match_dict = {
                'id': match.get('id'),
                'home_team': match.get('home_team'),
                'away_team': match.get('away_team'),
                'home_score': match.get('home_score'),
                'away_score': match.get('away_score'),
                'status': match.get('status'),
                'time': match.get('time'),
                'competition': match.get('competition'),
                'season': match.get('season')
            }
            matches.append(match_dict)
        
        return jsonify({
            'success': True,
            'matches': matches,
            'total_matches': len(matches),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting matches: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Get teams data"""
    try:
        data = data_collector.get_latest_data()
        
        teams = []
        for team_name, team_data in data.get('teams', {}).items():
            team_dict = {
                'name': team_name,
                'form': team_data.get('form', []),
                'goals_scored_avg': team_data.get('goals_scored_avg'),
                'goals_conceded_avg': team_data.get('goals_conceded_avg'),
                'shots_avg': team_data.get('shots_avg'),
                'possession_avg': team_data.get('possession_avg'),
                'injuries': team_data.get('injuries', []),
                'suspensions': team_data.get('suspensions', [])
            }
            teams.append(team_dict)
        
        return jsonify({
            'success': True,
            'teams': teams,
            'total_teams': len(teams),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status and data source health"""
    try:
        # Get data source status
        source_status = data_collector.get_source_status()
        
        # Get latest data summary
        data = data_collector.get_latest_data()
        
        status = {
            'system_status': 'operational',
            'last_data_update': data.get('last_updated'),
            'data_summary': {
                'matches': len(data.get('matches', [])),
                'teams': len(data.get('teams', {})),
                'h2h_records': len(data.get('h2h_records', {})),
                'odds': len(data.get('odds', {}))
            },
            'data_sources': source_status,
            'ai_model_status': {
                'trained': ai_predictor.is_trained,
                'models_available': list(ai_predictor.models.keys())
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/train-models', methods=['POST'])
def train_models():
    """Train AI models with historical data"""
    try:
        # For now, we'll use sample historical data
        # In a real implementation, you'd load actual historical data
        historical_data = [
            {
                'match_data': {
                    'home_team': 'Real Madrid',
                    'away_team': 'Barcelona'
                },
                'team_data': {
                    'Real Madrid': {'form': ['W', 'W', 'D'], 'goals_scored_avg': 2.1},
                    'Barcelona': {'form': ['W', 'D', 'W'], 'goals_scored_avg': 1.9}
                },
                'h2h_data': {
                    'Real Madrid_Barcelona': {
                        'total_matches': 10,
                        'team1_wins': 4,
                        'team2_wins': 3,
                        'draws': 3
                    }
                },
                'odds_data': {
                    'home_win': 2.1,
                    'draw': 3.2,
                    'away_win': 3.5
                },
                'actual_result': {
                    'winner': 'home',
                    'total_goals': 3,
                    'both_teams_scored': True
                }
            }
            # Add more historical data here
        ]
        
        ai_predictor.train_models(historical_data)
        
        return jsonify({
            'success': True,
            'message': 'Models trained successfully',
            'models_trained': list(ai_predictor.models.keys()),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error training models: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting AI Football Predictions Backend")
    
    # Initialize data collection
    try:
        logger.info("Initializing data collection...")
        # Collect initial data
        data_collector.collect_all_data(days_back=1, days_forward=7)
        logger.info("Initial data collection completed")
    except Exception as e:
        logger.error(f"Error in initial data collection: {e}")
    
    # Start Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
