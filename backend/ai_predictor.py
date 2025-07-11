import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from loguru import logger
from config.settings import AI_CONFIG
from models.data_models import Prediction, PredictionType, Match

class AIPredictor:
    """AI-powered football prediction system"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = AI_CONFIG['features']
        self.prediction_types = AI_CONFIG['prediction_types']
        self.confidence_threshold = AI_CONFIG['confidence_threshold']
        self.training_data = []
        self.is_trained = False
        
    def prepare_features(self, match_data: Dict, team_data: Dict, h2h_data: Dict, odds_data: Dict) -> Dict:
        """Prepare features for prediction"""
        features = {}
        
        try:
            # Team form features
            home_team = match_data.get('home_team', '')
            away_team = match_data.get('away_team', '')
            
            home_stats = team_data.get(home_team, {})
            away_stats = team_data.get(away_team, {})
            
            # Form features (last 5 matches)
            home_form = home_stats.get('form', [])
            away_form = away_stats.get('form', [])
            
            features['home_form_wins'] = home_form.count('W') / max(len(home_form), 1)
            features['home_form_draws'] = home_form.count('D') / max(len(home_form), 1)
            features['home_form_losses'] = home_form.count('L') / max(len(home_form), 1)
            
            features['away_form_wins'] = away_form.count('W') / max(len(away_form), 1)
            features['away_form_draws'] = away_form.count('D') / max(len(away_form), 1)
            features['away_form_losses'] = away_form.count('L') / max(len(away_form), 1)
            
            # Goals features
            features['home_goals_scored_avg'] = home_stats.get('goals_scored_avg', 1.0)
            features['home_goals_conceded_avg'] = home_stats.get('goals_conceded_avg', 1.0)
            features['away_goals_scored_avg'] = away_stats.get('goals_scored_avg', 1.0)
            features['away_goals_conceded_avg'] = away_stats.get('goals_conceded_avg', 1.0)
            
            # Shots features
            features['home_shots_avg'] = home_stats.get('shots_avg', 10.0)
            features['away_shots_avg'] = away_stats.get('shots_avg', 10.0)
            
            # Possession features
            features['home_possession_avg'] = home_stats.get('possession_avg', 50.0)
            features['away_possession_avg'] = away_stats.get('possession_avg', 50.0)
            
            # H2H features
            h2h_key = f"{home_team}_{away_team}"
            h2h_record = h2h_data.get(h2h_key, {})
            
            if h2h_record:
                total_matches = h2h_record.get('total_matches', 1)
                features['h2h_home_wins'] = h2h_record.get('team1_wins', 0) / total_matches
                features['h2h_away_wins'] = h2h_record.get('team2_wins', 0) / total_matches
                features['h2h_draws'] = h2h_record.get('draws', 0) / total_matches
                features['h2h_home_goals_avg'] = h2h_record.get('team1_goals', 0) / total_matches
                features['h2h_away_goals_avg'] = h2h_record.get('team2_goals', 0) / total_matches
            else:
                features['h2h_home_wins'] = 0.33
                features['h2h_away_wins'] = 0.33
                features['h2h_draws'] = 0.34
                features['h2h_home_goals_avg'] = 1.0
                features['h2h_away_goals_avg'] = 1.0
            
            # Odds features
            if odds_data:
                features['odds_home_win'] = odds_data.get('home_win', 2.0)
                features['odds_draw'] = odds_data.get('draw', 3.0)
                features['odds_away_win'] = odds_data.get('away_win', 2.0)
                features['odds_over_2_5'] = odds_data.get('over_2_5', 2.0)
                features['odds_under_2_5'] = odds_data.get('under_2_5', 2.0)
            else:
                features['odds_home_win'] = 2.0
                features['odds_draw'] = 3.0
                features['odds_away_win'] = 2.0
                features['odds_over_2_5'] = 2.0
                features['odds_under_2_5'] = 2.0
            
            # Additional features
            features['home_team_rank'] = home_stats.get('rank', 10)
            features['away_team_rank'] = away_stats.get('rank', 10)
            features['home_injuries_count'] = len(home_stats.get('injuries', []))
            features['away_injuries_count'] = len(away_stats.get('injuries', []))
            features['home_suspensions_count'] = len(home_stats.get('suspensions', []))
            features['away_suspensions_count'] = len(away_stats.get('suspensions', []))
            
            # Weather and other factors (placeholder values)
            features['weather_temperature'] = 20.0
            features['weather_humidity'] = 60.0
            features['crowd_factor'] = 0.8
            features['motivation_factor'] = 0.7
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            # Return default features if error occurs
            features = {col: 0.0 for col in self.feature_columns}
        
        return features
    
    def train_models(self, historical_data: List[Dict]):
        """Train prediction models with historical data"""
        logger.info("Training AI models with historical data")
        
        # Prepare training data
        X = []
        y = {}
        
        for prediction_type in self.prediction_types:
            y[prediction_type] = []
        
        for match in historical_data:
            try:
                features = self.prepare_features(
                    match.get('match_data', {}),
                    match.get('team_data', {}),
                    match.get('h2h_data', {}),
                    match.get('odds_data', {})
                )
                
                # Convert features to array
                feature_array = [features.get(col, 0.0) for col in self.feature_columns]
                X.append(feature_array)
                
                # Prepare labels for each prediction type
                actual_result = match.get('actual_result', {})
                
                # Match winner (0: home win, 1: draw, 2: away win)
                if 'winner' in actual_result:
                    winner = actual_result['winner']
                    if winner == 'home':
                        y['match_winner'].append(0)
                    elif winner == 'draw':
                        y['match_winner'].append(1)
                    else:
                        y['match_winner'].append(2)
                
                # Over/Under (0: under 2.5, 1: over 2.5)
                if 'total_goals' in actual_result:
                    total_goals = actual_result['total_goals']
                    y['over_under'].append(1 if total_goals > 2.5 else 0)
                
                # Both teams score (0: no, 1: yes)
                if 'both_teams_scored' in actual_result:
                    y['both_teams_score'].append(1 if actual_result['both_teams_scored'] else 0)
                
            except Exception as e:
                logger.error(f"Error processing training data: {e}")
                continue
        
        # Train models for each prediction type
        for prediction_type in self.prediction_types:
            if len(y[prediction_type]) > 0 and len(X) > 0:
                try:
                    # Split data
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y[prediction_type], test_size=0.2, random_state=42
                    )
                    
                    # Scale features
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    
                    # Train ensemble model
                    model = RandomForestClassifier(
                        n_estimators=100,
                        max_depth=10,
                        random_state=42
                    )
                    model.fit(X_train_scaled, y_train)
                    
                    # Evaluate model
                    y_pred = model.predict(X_test_scaled)
                    accuracy = accuracy_score(y_test, y_pred)
                    
                    # Store model and scaler
                    self.models[prediction_type] = model
                    self.scalers[prediction_type] = scaler
                    
                    logger.info(f"Trained {prediction_type} model with accuracy: {accuracy:.3f}")
                    
                except Exception as e:
                    logger.error(f"Error training {prediction_type} model: {e}")
        
        self.is_trained = True
        logger.info("Model training completed")
    
    def make_prediction(self, match_data: Dict, team_data: Dict, h2h_data: Dict, odds_data: Dict) -> List[Prediction]:
        """Make predictions for a match"""
        if not self.is_trained:
            logger.warning("Models not trained, using default predictions")
            return self._make_default_predictions(match_data)
        
        predictions = []
        match_id = match_data.get('id', '')
        
        try:
            # Prepare features
            features = self.prepare_features(match_data, team_data, h2h_data, odds_data)
            feature_array = [features.get(col, 0.0) for col in self.feature_columns]
            
            for prediction_type in self.prediction_types:
                if prediction_type in self.models:
                    try:
                        model = self.models[prediction_type]
                        scaler = self.scalers[prediction_type]
                        
                        # Scale features
                        features_scaled = scaler.transform([feature_array])
                        
                        # Make prediction
                        prediction_proba = model.predict_proba(features_scaled)[0]
                        prediction_class = model.predict(features_scaled)[0]
                        
                        # Calculate confidence
                        confidence = max(prediction_proba)
                        
                        # Only make prediction if confidence is above threshold
                        if confidence >= self.confidence_threshold:
                            prediction_value = self._get_prediction_value(prediction_type, prediction_class, match_data)
                            odds = self._get_prediction_odds(prediction_type, prediction_class, odds_data)
                            reasoning = self._generate_reasoning(prediction_type, features, confidence)
                            
                            prediction = Prediction(
                                id=f"{match_id}_{prediction_type}",
                                match_id=match_id,
                                prediction_type=PredictionType(prediction_type),
                                prediction=prediction_value,
                                confidence=confidence,
                                odds=odds,
                                reasoning=reasoning,
                                tipster="AI Predictions Pro",
                                created_at=datetime.now(),
                                expires_at=datetime.now() + timedelta(hours=2),
                                status="pending"
                            )
                            
                            predictions.append(prediction)
                    
                    except Exception as e:
                        logger.error(f"Error making {prediction_type} prediction: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
        
        return predictions
    
    def _get_prediction_value(self, prediction_type: str, prediction_class: int, match_data: Dict) -> str:
        """Convert prediction class to human-readable value"""
        home_team = match_data.get('home_team', '')
        away_team = match_data.get('away_team', '')
        
        if prediction_type == 'match_winner':
            if prediction_class == 0:
                return f"{home_team} Win"
            elif prediction_class == 1:
                return "Draw"
            else:
                return f"{away_team} Win"
        
        elif prediction_type == 'over_under':
            return "Over 2.5 Goals" if prediction_class == 1 else "Under 2.5 Goals"
        
        elif prediction_type == 'both_teams_score':
            return "Both Teams Score" if prediction_class == 1 else "Not Both Teams Score"
        
        elif prediction_type == 'correct_score':
            # This would need more sophisticated logic
            return "1-0" if prediction_class == 0 else "2-1"
        
        else:
            return f"Prediction Class {prediction_class}"
    
    def _get_prediction_odds(self, prediction_type: str, prediction_class: int, odds_data: Dict) -> float:
        """Get odds for the prediction"""
        if prediction_type == 'match_winner':
            if prediction_class == 0:
                return odds_data.get('home_win', 2.0)
            elif prediction_class == 1:
                return odds_data.get('draw', 3.0)
            else:
                return odds_data.get('away_win', 2.0)
        
        elif prediction_type == 'over_under':
            return odds_data.get('over_2_5', 2.0) if prediction_class == 1 else odds_data.get('under_2_5', 2.0)
        
        elif prediction_type == 'both_teams_score':
            return odds_data.get('both_teams_score_yes', 2.0) if prediction_class == 1 else odds_data.get('both_teams_score_no', 2.0)
        
        else:
            return 2.0
    
    def _generate_reasoning(self, prediction_type: str, features: Dict, confidence: float) -> str:
        """Generate reasoning for the prediction"""
        reasoning_parts = []
        
        if prediction_type == 'match_winner':
            home_form_wins = features.get('home_form_wins', 0)
            away_form_wins = features.get('away_form_wins', 0)
            
            if home_form_wins > away_form_wins:
                reasoning_parts.append(f"Home team has better recent form ({home_form_wins:.1%} vs {away_form_wins:.1%})")
            
            h2h_home_wins = features.get('h2h_home_wins', 0)
            if h2h_home_wins > 0.5:
                reasoning_parts.append(f"Home team has good H2H record ({h2h_home_wins:.1%} wins)")
        
        elif prediction_type == 'over_under':
            home_goals_avg = features.get('home_goals_scored_avg', 1.0)
            away_goals_avg = features.get('away_goals_scored_avg', 1.0)
            total_avg = home_goals_avg + away_goals_avg
            
            if total_avg > 2.5:
                reasoning_parts.append(f"Both teams average {total_avg:.1f} goals per game")
        
        elif prediction_type == 'both_teams_score':
            home_goals_avg = features.get('home_goals_scored_avg', 1.0)
            away_goals_avg = features.get('away_goals_scored_avg', 1.0)
            
            if home_goals_avg > 1.0 and away_goals_avg > 1.0:
                reasoning_parts.append(f"Both teams score regularly (home: {home_goals_avg:.1f}, away: {away_goals_avg:.1f} avg)")
        
        reasoning_parts.append(f"AI confidence: {confidence:.1%}")
        
        return ". ".join(reasoning_parts) if reasoning_parts else "Based on AI analysis"
    
    def _make_default_predictions(self, match_data: Dict) -> List[Prediction]:
        """Make default predictions when models are not trained"""
        predictions = []
        match_id = match_data.get('id', '')
        home_team = match_data.get('home_team', '')
        away_team = match_data.get('away_team', '')
        
        # Default predictions with moderate confidence
        default_predictions = [
            {
                'type': 'match_winner',
                'prediction': f"{home_team} Win",
                'confidence': 0.65,
                'odds': 2.0,
                'reasoning': 'Home advantage and recent form analysis'
            },
            {
                'type': 'over_under',
                'prediction': 'Over 2.5 Goals',
                'confidence': 0.70,
                'odds': 1.85,
                'reasoning': 'Both teams have good attacking records'
            },
            {
                'type': 'both_teams_score',
                'prediction': 'Both Teams Score',
                'confidence': 0.75,
                'odds': 1.75,
                'reasoning': 'High scoring teams with good form'
            }
        ]
        
        for pred in default_predictions:
            prediction = Prediction(
                id=f"{match_id}_{pred['type']}",
                match_id=match_id,
                prediction_type=PredictionType(pred['type']),
                prediction=pred['prediction'],
                confidence=pred['confidence'],
                odds=pred['odds'],
                reasoning=pred['reasoning'],
                tipster="AI Predictions Pro",
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=2),
                status="pending"
            )
            predictions.append(prediction)
        
        return predictions
    
    def save_models(self, filepath: str):
        """Save trained models to file"""
        import pickle
        
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Models saved to {filepath}")
    
    def load_models(self, filepath: str):
        """Load trained models from file"""
        import pickle
        
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.feature_columns = model_data['feature_columns']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Models loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")

# Example usage
if __name__ == "__main__":
    predictor = AIPredictor()
    
    # Example match data
    match_data = {
        'id': '12345',
        'home_team': 'Real Madrid',
        'away_team': 'Barcelona',
        'status': 'scheduled'
    }
    
    team_data = {
        'Real Madrid': {
            'form': ['W', 'W', 'D', 'W', 'L'],
            'goals_scored_avg': 2.1,
            'goals_conceded_avg': 0.8,
            'shots_avg': 15.2,
            'possession_avg': 58.5
        },
        'Barcelona': {
            'form': ['W', 'D', 'W', 'L', 'W'],
            'goals_scored_avg': 1.9,
            'goals_conceded_avg': 1.1,
            'shots_avg': 13.8,
            'possession_avg': 62.3
        }
    }
    
    h2h_data = {
        'Real Madrid_Barcelona': {
            'total_matches': 10,
            'team1_wins': 4,
            'team2_wins': 3,
            'draws': 3,
            'team1_goals': 12,
            'team2_goals': 10
        }
    }
    
    odds_data = {
        'home_win': 2.1,
        'draw': 3.2,
        'away_win': 3.5,
        'over_2_5': 1.85,
        'under_2_5': 2.0
    }
    
    # Make predictions
    predictions = predictor.make_prediction(match_data, team_data, h2h_data, odds_data)
    
    for pred in predictions:
        print(f"{pred.prediction_type.value}: {pred.prediction}")
        print(f"Confidence: {pred.confidence:.1%}")
        print(f"Odds: {pred.odds}")
        print(f"Reasoning: {pred.reasoning}")
        print("---")
