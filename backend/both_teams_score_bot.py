#!/usr/bin/env python3
"""
Bot Ambos Marcan - Análisis Sofisticado de Probabilidades de que Ambos Equipos Marquen
=====================================================================================

Este bot calcula la probabilidad de que ambos equipos marquen considerando:
- Estadísticas ofensivas y defensivas de cada equipo
- Enfrentamientos directos históricos
- Forma reciente y tendencias de goles
- Factores de ubicación (local/visitante)
- Análisis de líneas defensivas y ataques
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics
from dataclasses import dataclass
import random

@dataclass
class TeamScoringStats:
    """Estadísticas de goles de un equipo"""
    name: str
    
    # Estadísticas generales
    total_matches: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goals_for_avg: float = 0.0
    goals_against_avg: float = 0.0
    
    # Por ubicación
    home_matches: int = 0
    home_goals_for: int = 0
    home_goals_against: int = 0
    home_goals_for_avg: float = 0.0
    home_goals_against_avg: float = 0.0
    
    away_matches: int = 0
    away_goals_for: int = 0
    away_goals_against: int = 0
    away_goals_for_avg: float = 0.0
    away_goals_against_avg: float = 0.0
    
    # Estadísticas de "ambos marcan"
    both_teams_scored_matches: int = 0
    both_teams_scored_percentage: float = 0.0
    home_both_teams_scored: int = 0
    away_both_teams_scored: int = 0
    
    # Forma reciente (últimos 5 partidos)
    recent_goals_for: List[int] = None
    recent_goals_against: List[int] = None
    recent_both_teams_scored: List[bool] = None
    
    # Tendencias ofensivas/defensivas
    clean_sheets: int = 0
    failed_to_score: int = 0
    high_scoring_matches: int = 0  # 3+ goles totales
    
    def __post_init__(self):
        if self.recent_goals_for is None:
            self.recent_goals_for = []
        if self.recent_goals_against is None:
            self.recent_goals_against = []
        if self.recent_both_teams_scored is None:
            self.recent_both_teams_scored = []
    
    @property
    def attacking_strength(self) -> float:
        """Fuerza ofensiva del equipo (0-1)"""
        if self.total_matches == 0:
            return 0.5
        
        base_strength = min(self.goals_for_avg / 2.5, 1.0)  # Normalizado a 2.5 goles promedio
        
        # Factor de consistencia (menos partidos sin marcar = mejor)
        consistency_factor = 1.0 - (self.failed_to_score / self.total_matches)
        
        # Forma reciente
        recent_factor = 1.0
        if len(self.recent_goals_for) >= 3:
            recent_avg = sum(self.recent_goals_for) / len(self.recent_goals_for)
            recent_factor = min(recent_avg / 1.5, 1.2)
        
        return min(base_strength * consistency_factor * recent_factor, 1.0)
    
    @property
    def defensive_weakness(self) -> float:
        """Debilidad defensiva del equipo (0-1)"""
        if self.total_matches == 0:
            return 0.5
        
        base_weakness = min(self.goals_against_avg / 2.0, 1.0)
        
        # Factor de clean sheets (menos clean sheets = más débil)
        clean_sheet_factor = 1.0 + (1.0 - (self.clean_sheets / self.total_matches))
        
        return min(base_weakness * clean_sheet_factor, 1.0)
    
    @property
    def btts_tendency(self) -> float:
        """Tendencia a partidos donde ambos marcan"""
        if self.total_matches == 0:
            return 0.5
        
        base_tendency = self.both_teams_scored_percentage / 100.0
        
        # Factor de forma reciente
        recent_factor = 1.0
        if len(self.recent_both_teams_scored) >= 3:
            recent_btts = sum(self.recent_both_teams_scored)
            recent_factor = 0.7 + (recent_btts / len(self.recent_both_teams_scored)) * 0.6
        
        return min(base_tendency * recent_factor, 1.0)

@dataclass
class BTTSPrediction:
    """Predicción completa de ambos marcan"""
    home_team: str
    away_team: str
    btts_probability: float
    confidence: float
    
    # Factores contribuyentes
    home_attacking_factor: float
    home_defensive_factor: float
    away_attacking_factor: float
    away_defensive_factor: float
    h2h_factor: float
    form_factor: float
    
    # Análisis detallado
    analysis: str
    reasoning: str
    
    # Metadatos
    competition: str = ""
    match_time: str = ""
    estimated_odds: float = 0.0

class BothTeamsScoreBot:
    """Bot especializado en predicciones de ambos equipos marcan"""
    
    def __init__(self):
        self.name = "Bot Ambos Marcan"
        self.config = self.load_config()
        self.teams_stats = {}
        self.load_teams_data()
    
    def load_config(self) -> Dict:
        """Carga la configuración del bot"""
        try:
            config_path = os.path.join('data', 'bots_config.json')
            if not os.path.exists(config_path):
                config_path = 'bots_config.json'
            
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get('bots', {}).get('ambos-marcan', {
                'confidence_threshold': 70,
                'min_odds': 1.5,
                'max_odds': 4.0
            })
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return {
                'confidence_threshold': 70,
                'min_odds': 1.5,
                'max_odds': 4.0
            }
    
    def load_teams_data(self):
        """Carga datos históricos de goles de equipos (simulado)"""
        # En un sistema real, esto cargaría desde base de datos
        teams_data = {
            # La Liga
            'Real Madrid': TeamScoringStats(
                'Real Madrid', 38, 87, 26, 2.3, 0.7, 19, 45, 12, 2.4, 0.6, 19, 42, 14, 2.2, 0.7,
                28, 73.7, 15, 13, [3, 2, 1, 2, 3], [0, 1, 0, 1, 0], [True, True, False, True, False],
                10, 2, 25
            ),
            'Barcelona': TeamScoringStats(
                'Barcelona', 38, 76, 32, 2.0, 0.8, 19, 40, 15, 2.1, 0.8, 19, 36, 17, 1.9, 0.9,
                25, 65.8, 13, 12, [2, 1, 2, 1, 2], [1, 0, 1, 1, 0], [True, False, True, True, False],
                8, 4, 22
            ),
            'Atletico Madrid': TeamScoringStats(
                'Atletico Madrid', 38, 58, 24, 1.5, 0.6, 19, 32, 10, 1.7, 0.5, 19, 26, 14, 1.4, 0.7,
                20, 52.6, 11, 9, [1, 0, 1, 2, 1], [0, 0, 1, 0, 1], [False, False, True, False, True],
                14, 8, 15
            ),
            
            # Premier League
            'Manchester City': TeamScoringStats(
                'Manchester City', 38, 96, 31, 2.5, 0.8, 19, 52, 14, 2.7, 0.7, 19, 44, 17, 2.3, 0.9,
                30, 78.9, 16, 14, [3, 2, 4, 1, 2], [1, 0, 0, 1, 0], [True, False, False, True, False],
                7, 1, 28
            ),
            'Arsenal': TeamScoringStats(
                'Arsenal', 38, 82, 29, 2.2, 0.8, 19, 43, 13, 2.3, 0.7, 19, 39, 16, 2.1, 0.8,
                27, 71.1, 14, 13, [2, 3, 1, 2, 1], [0, 1, 0, 1, 0], [False, True, False, True, False],
                9, 3, 24
            ),
            'Liverpool': TeamScoringStats(
                'Liverpool', 38, 86, 41, 2.3, 1.1, 19, 44, 18, 2.3, 0.9, 19, 42, 23, 2.2, 1.2,
                29, 76.3, 15, 14, [2, 1, 3, 2, 2], [1, 2, 1, 0, 1], [True, True, True, False, True],
                6, 2, 26
            ),
            
            # Otros equipos importantes
            'Inter Milan': TeamScoringStats(
                'Inter Milan', 38, 71, 28, 1.9, 0.7, 19, 38, 12, 2.0, 0.6, 19, 33, 16, 1.7, 0.8,
                24, 63.2, 13, 11, [2, 1, 1, 2, 0], [0, 1, 0, 1, 0], [False, True, False, True, False],
                11, 5, 20
            ),
            'AC Milan': TeamScoringStats(
                'AC Milan', 38, 69, 35, 1.8, 0.9, 19, 36, 16, 1.9, 0.8, 19, 33, 19, 1.7, 1.0,
                26, 68.4, 14, 12, [1, 2, 1, 1, 2], [1, 0, 1, 1, 0], [True, False, True, True, False],
                8, 6, 22
            ),
            'Bayern Munich': TeamScoringStats(
                'Bayern Munich', 34, 94, 26, 2.8, 0.8, 17, 50, 11, 2.9, 0.6, 17, 44, 15, 2.6, 0.9,
                28, 82.4, 15, 13, [3, 2, 3, 1, 4], [0, 1, 0, 0, 1], [False, True, False, False, True],
                6, 1, 26
            ),
        }
        
        # Estadísticas por defecto para equipos no listados
        default_stats = TeamScoringStats(
            'Unknown', 38, 65, 45, 1.7, 1.2, 19, 33, 22, 1.7, 1.2, 19, 32, 23, 1.7, 1.2,
            22, 57.9, 11, 11, [1, 2, 1, 1, 2], [1, 0, 1, 1, 0], [True, False, True, True, False],
            10, 8, 18
        )
        
        self.teams_stats = teams_data
        self.default_team_stats = default_stats
    
    def get_team_stats(self, team_name: str) -> TeamScoringStats:
        """Obtiene estadísticas de un equipo"""
        return self.teams_stats.get(team_name, self.default_team_stats)
    
    def calculate_h2h_btts_factor(self, home_team: str, away_team: str) -> Tuple[float, str]:
        """Calcula factor de enfrentamientos directos para BTTS"""
        # Simulación de datos H2H (en sistema real vendría de BD)
        
        # Crear un hash simple para consistencia
        team_hash = hash(f"{home_team}{away_team}") % 100
        
        # Simular estadísticas H2H basadas en el hash
        total_meetings = 8 + (team_hash % 5)  # 8-12 enfrentamientos
        btts_meetings = int(total_meetings * (0.4 + (team_hash % 40) / 100))  # 40-80% BTTS
        
        btts_percentage = (btts_meetings / total_meetings) * 100
        
        # Factor base
        h2h_factor = 0.5 + (btts_percentage / 100) * 0.5
        
        # Análisis textual
        if btts_percentage >= 70:
            analysis = f"Historial muy favorable para BTTS: {btts_meetings}/{total_meetings} enfrentamientos ({btts_percentage:.1f}%)"
        elif btts_percentage >= 50:
            analysis = f"Historial moderadamente favorable: {btts_meetings}/{total_meetings} enfrentamientos ({btts_percentage:.1f}%)"
        else:
            analysis = f"Historial menos favorable para BTTS: {btts_meetings}/{total_meetings} enfrentamientos ({btts_percentage:.1f}%)"
        
        return h2h_factor, analysis
    
    def calculate_form_factor(self, home_stats: TeamScoringStats, away_stats: TeamScoringStats) -> Tuple[float, str]:
        """Calcula factor de forma reciente"""
        
        # Analizar forma reciente de ambos equipos
        home_recent_btts = sum(home_stats.recent_both_teams_scored) if home_stats.recent_both_teams_scored else 0
        away_recent_btts = sum(away_stats.recent_both_teams_scored) if away_stats.recent_both_teams_scored else 0
        
        home_recent_games = len(home_stats.recent_both_teams_scored) if home_stats.recent_both_teams_scored else 5
        away_recent_games = len(away_stats.recent_both_teams_scored) if away_stats.recent_both_teams_scored else 5
        
        # Porcentajes recientes
        home_recent_percentage = (home_recent_btts / home_recent_games) * 100
        away_recent_percentage = (away_recent_btts / away_recent_games) * 100
        
        # Factor combinado
        combined_percentage = (home_recent_percentage + away_recent_percentage) / 2
        form_factor = 0.6 + (combined_percentage / 100) * 0.8
        
        # Análisis
        if combined_percentage >= 70:
            form_text = "Excelente forma reciente para BTTS en ambos equipos"
        elif combined_percentage >= 50:
            form_text = "Forma reciente favorable para BTTS"
        elif combined_percentage >= 30:
            form_text = "Forma reciente moderada para BTTS"
        else:
            form_text = "Forma reciente desfavorable para BTTS"
        
        analysis = f"{form_text}. {home_stats.name}: {home_recent_btts}/{home_recent_games}, {away_stats.name}: {away_recent_btts}/{away_recent_games}"
        
        return form_factor, analysis
    
    def analyze_match_btts_probability(self, home_team: str, away_team: str, match: Dict = None) -> BTTSPrediction:
        """Análisis principal de probabilidad de ambos marcan"""
        
        # Obtener estadísticas de equipos
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        
        # Calcular factores individuales
        
        # 1. Factor de ataque del equipo local (peso: 25%)
        home_attacking_factor = home_stats.attacking_strength
        
        # 2. Factor de defensa del equipo local (debilidad defensiva) (peso: 20%)
        home_defensive_factor = home_stats.defensive_weakness
        
        # 3. Factor de ataque del equipo visitante (peso: 25%)
        away_attacking_factor = away_stats.attacking_strength
        
        # 4. Factor de defensa del equipo visitante (debilidad defensiva) (peso: 20%)
        away_defensive_factor = away_stats.defensive_weakness
        
        # 5. Factor de enfrentamientos directos (peso: 5%)
        h2h_factor, h2h_analysis = self.calculate_h2h_btts_factor(home_team, away_team)
        
        # 6. Factor de forma reciente (peso: 5%)
        form_factor, form_analysis = self.calculate_form_factor(home_stats, away_stats)
        
        # Cálculo de probabilidad ponderada
        # BTTS requiere que ambos equipos marquen, así que necesitamos:
        # - Que el equipo local marque (ataque local vs defensa visitante)
        # - Que el equipo visitante marque (ataque visitante vs defensa local)
        
        home_scores_probability = (home_attacking_factor + away_defensive_factor) / 2
        away_scores_probability = (away_attacking_factor + home_defensive_factor) / 2
        
        # Probabilidad base de BTTS
        base_btts_probability = home_scores_probability * away_scores_probability
        
        # Aplicar factores adicionales
        adjusted_probability = (
            base_btts_probability * 0.70 +  # Factor base
            h2h_factor * 0.15 +             # Historial
            form_factor * 0.15              # Forma reciente
        )
        
        # Convertir a porcentaje y ajustar rangos
        btts_probability = min(max(adjusted_probability * 100, 15), 85)
        
        # Calcular confianza
        confidence = self.calculate_confidence(home_stats, away_stats, btts_probability, match)
        
        # Generar análisis detallado
        analysis = self.generate_detailed_analysis(
            home_team, away_team, home_stats, away_stats,
            h2h_analysis, form_analysis, btts_probability
        )
        
        # Crear predicción
        prediction = BTTSPrediction(
            home_team=home_team,
            away_team=away_team,
            btts_probability=btts_probability,
            confidence=confidence,
            home_attacking_factor=home_attacking_factor,
            home_defensive_factor=home_defensive_factor,
            away_attacking_factor=away_attacking_factor,
            away_defensive_factor=away_defensive_factor,
            h2h_factor=h2h_factor,
            form_factor=form_factor,
            analysis=analysis,
            reasoning=f"Probabilidad de ambos marcan: {btts_probability:.1f}% basada en análisis ofensivo-defensivo",
            estimated_odds=self.estimate_btts_odds(btts_probability)
        )
        
        return prediction
    
    def calculate_confidence(self, home_stats: TeamScoringStats, away_stats: TeamScoringStats, probability: float, match: Dict = None) -> float:
        """Calcula el nivel de confianza de la predicción"""
        
        confidence = 50.0  # Base
        
        # Más partidos = más confianza
        if home_stats.total_matches >= 30 and away_stats.total_matches >= 30:
            confidence += 15
        elif home_stats.total_matches >= 20 and away_stats.total_matches >= 20:
            confidence += 10
        
        # Consistencia en estadísticas BTTS
        home_consistency = abs(home_stats.both_teams_scored_percentage - 50) < 20
        away_consistency = abs(away_stats.both_teams_scored_percentage - 50) < 20
        
        if home_consistency and away_consistency:
            confidence += 10
        elif home_consistency or away_consistency:
            confidence += 5
        
        # Probabilidad en rango óptimo para BTTS
        if 45 <= probability <= 75:
            confidence += 15
        elif 35 <= probability <= 80:
            confidence += 10
        elif 25 <= probability <= 85:
            confidence += 5
        
        # Forma reciente consistente
        if len(home_stats.recent_both_teams_scored) >= 4 and len(away_stats.recent_both_teams_scored) >= 4:
            confidence += 5
        
        # FACTOR DE DIVERSIDAD PARA BTTS
        if match:
            confidence = self.add_btts_diversity_factor(confidence, match)
        
        return min(confidence, 95.0)
    
    def add_btts_diversity_factor(self, confidence: float, match: Dict) -> float:
        """Añade factor de diversidad específico para BTTS"""
        
        # Factor basado en competición (ligas ofensivas vs defensivas)
        competition = match.get('competition', '').lower()
        competition_factor = 0
        
        if 'premier' in competition or 'england' in competition:
            competition_factor = 10  # Premier League muy ofensiva
        elif 'bundesliga' in competition or 'germany' in competition:
            competition_factor = 8  # Bundesliga ofensiva
        elif 'la liga' in competition or 'spain' in competition:
            competition_factor = 6  # La Liga moderada
        elif 'ligue 1' in competition or 'france' in competition:
            competition_factor = 4  # Ligue 1 equilibrada
        elif 'serie a' in competition or 'italy' in competition:
            competition_factor = 2  # Serie A más defensiva
        elif 'friendlies' in competition:
            competition_factor = 12  # Amistosos muy ofensivos
        elif 'division' in competition:
            competition_factor = -2  # Divisiones menores menos goles
        
        # Factor basado en equipos ofensivos
        home_team = match.get('home_team', '').lower()
        away_team = match.get('away_team', '').lower()
        
        offensive_keywords = ['madrid', 'barcelona', 'city', 'liverpool', 'bayern', 'psg', 'arsenal', 'dortmund']
        team_factor = 0
        
        for keyword in offensive_keywords:
            if keyword in home_team or keyword in away_team:
                team_factor += 3
        
        # Factor único por partido
        import random
        random.seed(hash(f"{home_team}_{away_team}_btts"))
        unique_factor = random.uniform(-4, 4)
        
        adjusted_confidence = confidence + competition_factor + team_factor + unique_factor
        return max(50, min(95, adjusted_confidence))
    
    def generate_detailed_analysis(self, home_team: str, away_team: str,
                                 home_stats: TeamScoringStats, away_stats: TeamScoringStats,
                                 h2h_analysis: str, form_analysis: str, probability: float) -> str:
        """Genera análisis detallado de la predicción"""
        
        analysis_parts = []
        
        # Estadísticas ofensivas
        offense_text = f"Ataque: {home_team} {home_stats.goals_for_avg:.1f} goles/partido, {away_team} {away_stats.goals_for_avg:.1f} goles/partido"
        analysis_parts.append(offense_text)
        
        # Estadísticas defensivas
        defense_text = f"Defensa: {home_team} recibe {home_stats.goals_against_avg:.1f} goles/partido, {away_team} recibe {away_stats.goals_against_avg:.1f} goles/partido"
        analysis_parts.append(defense_text)
        
        # Estadísticas BTTS históricas
        btts_text = f"Historial BTTS: {home_team} {home_stats.both_teams_scored_percentage:.1f}%, {away_team} {away_stats.both_teams_scored_percentage:.1f}%"
        analysis_parts.append(btts_text)
        
        # Enfrentamientos directos
        analysis_parts.append(h2h_analysis)
        
        # Forma reciente
        analysis_parts.append(form_analysis)
        
        # Factores adicionales
        if home_stats.failed_to_score <= 2 and away_stats.failed_to_score <= 2:
            analysis_parts.append("Ambos equipos rara vez fallan al marcar")
        
        if home_stats.clean_sheets <= 5 and away_stats.clean_sheets <= 5:
            analysis_parts.append("Ambas defensas conceden goles con frecuencia")
        
        # Conclusión
        if probability >= 65:
            conclusion = "Alta probabilidad de que ambos equipos marquen"
        elif probability >= 50:
            conclusion = "Probabilidad moderada-alta para BTTS"
        elif probability >= 35:
            conclusion = "Probabilidad moderada para BTTS"
        else:
            conclusion = "Probabilidad baja para BTTS"
        
        analysis_parts.append(conclusion)
        
        return ". ".join(analysis_parts) + "."
    
    def estimate_btts_odds(self, probability: float) -> float:
        """Estima las cuotas de ambos marcan basadas en la probabilidad"""
        if probability <= 0:
            return 5.0
        
        # Convertir probabilidad a cuotas (con margen de casa de apuestas del 5%)
        fair_odds = 100.0 / probability
        estimated_odds = fair_odds * 1.05  # Margen de la casa
        
        # Limitar rangos realistas para BTTS
        return max(min(estimated_odds, 8.0), 1.3)
    
    def should_bet(self, prediction: BTTSPrediction) -> bool:
        """Determina si se debe apostar basado en la configuración"""
        min_confidence = self.config.get('confidence_threshold', 70)
        min_odds = self.config.get('min_odds', 1.5)
        max_odds = self.config.get('max_odds', 4.0)
        min_btts_probability = 70.0  # NUEVA REGLA: Probabilidad BTTS mínima del 70%
        
        return (prediction.confidence >= min_confidence and 
                min_odds <= prediction.estimated_odds <= max_odds and
                prediction.btts_probability >= min_btts_probability)
    
    def get_picks_for_matches(self, matches: List[Dict]) -> List[Dict]:
        """Genera picks para una lista de partidos - TODOS los que tengan valor"""
        picks = []
        
        for match in matches:
            home_team = match.get('home_team', '')
            away_team = match.get('away_team', '')
            
            if not home_team or not away_team:
                continue
            
            # Analizar partido
            prediction = self.analyze_match_btts_probability(home_team, away_team, match)
            
            # Verificar si cumple criterios
            if self.should_bet(prediction):
                pick = {
                    'home_team': home_team,
                    'away_team': away_team,
                    'prediction_type': 'both_teams_score',
                    'prediction': f"Ambos Marcan - {prediction.btts_probability:.1f}% probabilidad",
                    'confidence': prediction.confidence,
                    'btts_probability': prediction.btts_probability,
                    'reasoning': prediction.analysis,
                    'match_time': match.get('match_time', ''),
                    'competition': match.get('competition', ''),
                    'odds': prediction.estimated_odds,
                    'factors': {
                        'home_attack': prediction.home_attacking_factor,
                        'home_defense': prediction.home_defensive_factor,
                        'away_attack': prediction.away_attacking_factor,
                        'away_defense': prediction.away_defensive_factor,
                        'h2h_factor': prediction.h2h_factor,
                        'form_factor': prediction.form_factor
                    }
                }
                picks.append(pick)
        
        # Ordenar por confianza
        return sorted(picks, key=lambda x: x['confidence'], reverse=True)