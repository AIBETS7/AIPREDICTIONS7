#!/usr/bin/env python3
"""
Bot de Empates - Análisis Sofisticado de Probabilidades de Empate
==================================================================

Este bot calcula la probabilidad de empate considerando:
- Enfrentamientos directos históricos
- Racha actual de cada equipo
- Estado de forma reciente
- Factores climatológicos
- Estadísticas de empates por equipo
- Sistema de acumulación: cada victoria/derrota suma probabilidad de empate
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics
from dataclasses import dataclass
import random

@dataclass
class TeamDrawStats:
    """Estadísticas de empates de un equipo"""
    name: str
    
    # Estadísticas generales
    total_matches: int = 0
    total_draws: int = 0
    draws_percentage: float = 0.0
    
    # Por ubicación
    home_matches: int = 0
    home_draws: int = 0
    home_draws_percentage: float = 0.0
    
    away_matches: int = 0
    away_draws: int = 0
    away_draws_percentage: float = 0.0
    
    # Racha actual
    current_streak: List[str] = None  # ['W', 'L', 'D', 'W', 'L'] últimos 5
    matches_since_last_draw: int = 0
    consecutive_non_draws: int = 0
    
    # Forma reciente (últimos 10 partidos)
    recent_form_points: float = 0.0  # Puntos promedio por partido
    recent_goals_for: float = 0.0
    recent_goals_against: float = 0.0
    recent_goal_difference: float = 0.0
    
    # Factor de acumulación de empates
    draw_accumulation_factor: float = 1.0  # Se incrementa con cada W/L
    
    def __post_init__(self):
        if self.current_streak is None:
            self.current_streak = []
    
    @property
    def draw_tendency(self) -> float:
        """Tendencia actual hacia empates (0-1)"""
        base_tendency = self.draws_percentage / 100.0
        
        # Factor de racha: más partidos sin empate = mayor probabilidad
        streak_factor = min(self.consecutive_non_draws * 0.05, 0.3)
        
        # Factor de forma: equipos con forma similar tienden a empatar
        form_balance = 1.0 - abs(self.recent_goal_difference) * 0.02
        
        return min(base_tendency + streak_factor + (form_balance * 0.1), 0.95)

@dataclass
class HeadToHeadStats:
    """Estadísticas de enfrentamientos directos"""
    total_matches: int = 0
    draws: int = 0
    home_team_wins: int = 0
    away_team_wins: int = 0
    
    # Últimos enfrentamientos
    recent_results: List[str] = None  # ['D', 'W', 'L', 'D', 'W'] últimos 5
    last_meeting_date: Optional[str] = None
    
    # Tendencias
    draws_in_last_5: int = 0
    draws_in_last_10: int = 0
    
    def __post_init__(self):
        if self.recent_results is None:
            self.recent_results = []
    
    @property
    def draw_percentage(self) -> float:
        """Porcentaje de empates en enfrentamientos directos"""
        if self.total_matches == 0:
            return 0.0
        return (self.draws / self.total_matches) * 100.0
    
    @property
    def recent_draw_tendency(self) -> float:
        """Tendencia reciente hacia empates (últimos 5)"""
        if len(self.recent_results) == 0:
            return 0.0
        recent_draws = sum(1 for result in self.recent_results if result == 'D')
        return recent_draws / len(self.recent_results)

@dataclass
class WeatherConditions:
    """Condiciones climatológicas que afectan la probabilidad de empate"""
    temperature: float = 20.0  # Celsius
    humidity: float = 50.0     # Porcentaje
    wind_speed: float = 10.0   # km/h
    precipitation: float = 0.0  # mm
    visibility: float = 10.0    # km
    
    @property
    def draw_impact_factor(self) -> float:
        """Factor de impacto del clima en empates (0.8-1.2)"""
        factor = 1.0
        
        # Temperaturas extremas favorecen empates
        if self.temperature < 5 or self.temperature > 35:
            factor += 0.1
        
        # Lluvia/nieve favorece empates
        if self.precipitation > 5:
            factor += 0.15
        elif self.precipitation > 1:
            factor += 0.05
        
        # Viento fuerte favorece empates
        if self.wind_speed > 30:
            factor += 0.1
        elif self.wind_speed > 20:
            factor += 0.05
        
        # Poca visibilidad favorece empates
        if self.visibility < 5:
            factor += 0.1
        
        return min(max(factor, 0.8), 1.2)

@dataclass
class DrawPrediction:
    """Predicción completa de empate"""
    home_team: str
    away_team: str
    draw_probability: float
    confidence: float
    
    # Factores contribuyentes
    h2h_factor: float
    home_team_factor: float
    away_team_factor: float
    form_balance_factor: float
    streak_factor: float
    weather_factor: float
    accumulation_factor: float
    
    # Análisis detallado
    analysis: str
    reasoning: str
    
    # Metadatos
    competition: str = ""
    match_time: str = ""
    estimated_odds: float = 0.0

class DrawsBot:
    """Bot especializado en predicciones de empates con análisis integral"""
    
    def __init__(self):
        self.name = "Bot Empates"
        self.config = self.load_config()
        self.teams_stats = {}
        self.h2h_database = {}
        self.load_teams_data()
        self.load_h2h_data()
    
    def load_config(self) -> Dict:
        """Carga la configuración del bot"""
        try:
            config_path = os.path.join('data', 'bots_config.json')
            if not os.path.exists(config_path):
                config_path = 'bots_config.json'
            
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get('bots', {}).get('empates', {
                'confidence_threshold': 70,
                'min_odds': 1.5,
                'max_odds': 6.0
            })
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return {
                'confidence_threshold': 70,
                'min_odds': 1.5,
                'max_odds': 6.0
            }
    
    def load_teams_data(self):
        """Carga datos históricos de empates de equipos (simulado)"""
        # En un sistema real, esto cargaría desde base de datos
        teams_data = {
            # La Liga
            'Real Madrid': TeamDrawStats('Real Madrid', 38, 8, 21.1, 19, 4, 21.1, 19, 4, 21.1, 
                                       ['W', 'W', 'L', 'W', 'D'], 2, 2, 2.1, 2.2, 0.8, 1.4, 1.05),
            'Barcelona': TeamDrawStats('Barcelona', 38, 9, 23.7, 19, 5, 26.3, 19, 4, 21.1,
                                     ['L', 'W', 'L', 'W', 'L'], 4, 4, 2.0, 2.1, 1.1, 1.0, 1.20),
            'Atletico Madrid': TeamDrawStats('Atletico Madrid', 38, 12, 31.6, 19, 7, 36.8, 19, 5, 26.3,
                                           ['D', 'W', 'L', 'D', 'L'], 1, 1, 1.8, 1.5, 0.9, 0.6, 1.05),
            'Athletic Bilbao': TeamDrawStats('Athletic Bilbao', 38, 10, 26.3, 19, 6, 31.6, 19, 4, 21.1,
                                           ['L', 'L', 'W', 'D', 'W'], 2, 2, 1.6, 1.4, 1.2, 0.2, 1.10),
            
            # Premier League
            'Manchester City': TeamDrawStats('Manchester City', 38, 7, 18.4, 19, 3, 15.8, 19, 4, 21.1,
                                           ['W', 'W', 'W', 'L', 'W'], 3, 3, 2.3, 2.8, 0.6, 2.2, 1.15),
            'Arsenal': TeamDrawStats('Arsenal', 38, 9, 23.7, 19, 5, 26.3, 19, 4, 21.1,
                                   ['W', 'L', 'W', 'W', 'D'], 1, 1, 2.1, 2.0, 1.0, 1.0, 1.05),
            'Liverpool': TeamDrawStats('Liverpool', 38, 8, 21.1, 19, 4, 21.1, 19, 4, 21.1,
                                     ['W', 'W', 'L', 'W', 'W'], 4, 4, 2.2, 2.5, 0.8, 1.7, 1.20),
            'Chelsea': TeamDrawStats('Chelsea', 38, 11, 28.9, 19, 6, 31.6, 19, 5, 26.3,
                                   ['L', 'D', 'W', 'L', 'D'], 0, 0, 1.7, 1.6, 1.3, 0.3, 1.00),
            
            # Otros equipos importantes
            'Inter Milan': TeamDrawStats('Inter Milan', 38, 10, 26.3, 19, 5, 26.3, 19, 5, 26.3,
                                       ['W', 'D', 'W', 'L', 'W'], 2, 2, 2.0, 2.1, 0.9, 1.2, 1.10),
            'AC Milan': TeamDrawStats('AC Milan', 38, 12, 31.6, 19, 7, 36.8, 19, 5, 26.3,
                                    ['D', 'L', 'W', 'D', 'L'], 1, 1, 1.8, 1.7, 1.1, 0.6, 1.05),
            'Bayern Munich': TeamDrawStats('Bayern Munich', 34, 6, 17.6, 17, 3, 17.6, 17, 3, 17.6,
                                         ['W', 'W', 'W', 'L', 'W'], 3, 3, 2.4, 2.9, 0.5, 2.4, 1.15),
            'Borussia Dortmund': TeamDrawStats('Borussia Dortmund', 34, 8, 23.5, 17, 4, 23.5, 17, 4, 23.5,
                                             ['W', 'L', 'D', 'W', 'L'], 2, 2, 2.0, 2.2, 1.0, 1.2, 1.10),
        }
        
        # Agregar equipos genéricos para otros que no estén en la lista
        default_stats = TeamDrawStats('Unknown', 38, 9, 23.7, 19, 5, 26.3, 19, 4, 21.1,
                                    ['W', 'L', 'D', 'W', 'L'], 2, 2, 1.8, 1.6, 1.0, 0.6, 1.05)
        
        self.teams_stats = teams_data
        self.default_team_stats = default_stats
    
    def load_h2h_data(self):
        """Carga datos de enfrentamientos directos (simulado)"""
        # En un sistema real, esto cargaría desde base de datos
        h2h_data = {
            ('Real Madrid', 'Barcelona'): HeadToHeadStats(10, 3, 4, 3, ['D', 'W', 'L', 'D', 'W'], '2024-10-26', 2, 3),
            ('Barcelona', 'Real Madrid'): HeadToHeadStats(10, 3, 3, 4, ['D', 'L', 'W', 'D', 'L'], '2024-10-26', 2, 3),
            ('Atletico Madrid', 'Real Madrid'): HeadToHeadStats(10, 4, 2, 4, ['D', 'D', 'W', 'L', 'D'], '2024-09-15', 3, 4),
            ('Real Madrid', 'Atletico Madrid'): HeadToHeadStats(10, 4, 4, 2, ['D', 'D', 'L', 'W', 'D'], '2024-09-15', 3, 4),
            ('Manchester City', 'Arsenal'): HeadToHeadStats(10, 2, 5, 3, ['W', 'L', 'D', 'W', 'W'], '2024-11-10', 1, 2),
            ('Arsenal', 'Manchester City'): HeadToHeadStats(10, 2, 3, 5, ['L', 'W', 'D', 'L', 'L'], '2024-11-10', 1, 2),
        }
        
        self.h2h_database = h2h_data
    
    def get_team_stats(self, team_name: str) -> TeamDrawStats:
        """Obtiene estadísticas de un equipo"""
        return self.teams_stats.get(team_name, self.default_team_stats)
    
    def get_h2h_stats(self, home_team: str, away_team: str) -> HeadToHeadStats:
        """Obtiene estadísticas de enfrentamientos directos"""
        key = (home_team, away_team)
        if key in self.h2h_database:
            return self.h2h_database[key]
        
        # Si no hay datos específicos, crear estadísticas genéricas
        return HeadToHeadStats(6, 2, 2, 2, ['D', 'W', 'L', 'D', 'W'], None, 2, 2)
    
    def get_weather_conditions(self, home_team: str, match_date: str) -> WeatherConditions:
        """Obtiene condiciones climáticas (simulado)"""
        # En un sistema real, esto consultaría una API meteorológica
        
        # Simular condiciones basadas en el equipo y fecha
        base_temp = 15.0
        if 'Madrid' in home_team or 'Barcelona' in home_team:
            base_temp = 20.0
        elif 'Milan' in home_team or 'Inter' in home_team:
            base_temp = 18.0
        elif 'Manchester' in home_team or 'Liverpool' in home_team:
            base_temp = 12.0
        elif 'Bayern' in home_team or 'Dortmund' in home_team:
            base_temp = 10.0
        
        # Variación aleatoria
        temp_variation = random.uniform(-5, 10)
        precipitation = random.uniform(0, 15) if random.random() < 0.3 else 0
        wind_speed = random.uniform(5, 25)
        humidity = random.uniform(40, 80)
        
        return WeatherConditions(
            temperature=base_temp + temp_variation,
            humidity=humidity,
            wind_speed=wind_speed,
            precipitation=precipitation,
            visibility=10.0 if precipitation < 5 else random.uniform(3, 8)
        )
    
    def calculate_form_balance_factor(self, home_stats: TeamDrawStats, away_stats: TeamDrawStats) -> Tuple[float, str]:
        """Calcula el factor de equilibrio de forma entre equipos"""
        
        # Diferencia en puntos por partido recientes
        points_diff = abs(home_stats.recent_form_points - away_stats.recent_form_points)
        
        # Diferencia en diferencia de goles
        goal_diff_home = home_stats.recent_goal_difference
        goal_diff_away = away_stats.recent_goal_difference
        goal_balance = abs(goal_diff_home - goal_diff_away)
        
        # Factor base: equipos con forma similar = mayor probabilidad de empate
        form_balance = 1.0 - (points_diff * 0.2) - (goal_balance * 0.05)
        form_balance = max(min(form_balance, 1.3), 0.7)
        
        # Análisis textual
        if points_diff < 0.3:
            balance_text = "Ambos equipos en forma muy similar"
        elif points_diff < 0.6:
            balance_text = "Forma ligeramente diferente entre equipos"
        else:
            balance_text = "Diferencia notable en la forma actual"
        
        analysis = f"{balance_text}. Diferencia de puntos: {points_diff:.1f}, diferencia de goles: {goal_balance:.1f}"
        
        return form_balance, analysis
    
    def calculate_streak_factor(self, home_stats: TeamDrawStats, away_stats: TeamDrawStats) -> Tuple[float, str]:
        """Calcula el factor de racha para probabilidad de empate"""
        
        # Factor de acumulación: cada W/L incrementa probabilidad de empate
        home_accumulation = home_stats.draw_accumulation_factor
        away_accumulation = away_stats.draw_accumulation_factor
        
        # Partidos consecutivos sin empate
        home_streak = home_stats.consecutive_non_draws
        away_streak = away_stats.consecutive_non_draws
        
        # Factor combinado
        accumulation_factor = (home_accumulation + away_accumulation) / 2
        streak_factor = 1.0 + (home_streak + away_streak) * 0.03
        
        combined_factor = accumulation_factor * streak_factor
        combined_factor = max(min(combined_factor, 1.5), 0.8)
        
        # Análisis
        total_streak = home_streak + away_streak
        if total_streak >= 6:
            streak_text = "Ambos equipos llevan muchos partidos sin empatar - alta probabilidad de empate"
        elif total_streak >= 4:
            streak_text = "Los equipos tienen racha sin empates - probabilidad incrementada"
        elif total_streak >= 2:
            streak_text = "Racha moderada sin empates"
        else:
            streak_text = "Rachas recientes normales"
        
        analysis = f"{streak_text}. Factor acumulación: {accumulation_factor:.2f}, partidos sin empate: {total_streak}"
        
        return combined_factor, analysis
    
    def analyze_match_draw_probability(self, home_team: str, away_team: str, match: Dict = None) -> DrawPrediction:
        """Análisis principal de probabilidad de empate"""
        
        # Obtener datos de equipos
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        h2h_stats = self.get_h2h_stats(home_team, away_team)
        match_date = match.get('match_time', '') if match else datetime.now().strftime('%Y-%m-%d')
        weather = self.get_weather_conditions(home_team, match_date or datetime.now().strftime('%Y-%m-%d'))
        
        # Calcular factores individuales
        
        # 1. Factor de enfrentamientos directos (peso: 25%)
        h2h_factor = 0.5 + (h2h_stats.recent_draw_tendency * 0.5)
        if h2h_stats.draws_in_last_5 >= 2:
            h2h_factor += 0.2
        
        # 2. Factor del equipo local (peso: 20%)
        home_team_factor = home_stats.draw_tendency
        
        # 3. Factor del equipo visitante (peso: 20%)
        away_team_factor = away_stats.draw_tendency
        
        # 4. Factor de equilibrio de forma (peso: 15%)
        form_balance_factor, form_analysis = self.calculate_form_balance_factor(home_stats, away_stats)
        
        # 5. Factor de racha/acumulación (peso: 15%)
        streak_factor, streak_analysis = self.calculate_streak_factor(home_stats, away_stats)
        
        # 6. Factor climatológico (peso: 5%)
        weather_factor = weather.draw_impact_factor
        
        # Cálculo de probabilidad ponderada
        base_probability = (
            h2h_factor * 0.25 +
            home_team_factor * 0.20 +
            away_team_factor * 0.20 +
            form_balance_factor * 0.15 +
            streak_factor * 0.15 +
            weather_factor * 0.05
        )
        
        # Ajustes finales
        draw_probability = min(max(base_probability, 0.15), 0.85) * 100  # Convertir a porcentaje
        
        # Calcular confianza basada en cantidad de datos y consistencia
        confidence = self.calculate_confidence(home_stats, away_stats, h2h_stats, draw_probability, match)
        
        # Generar análisis detallado
        analysis = self.generate_detailed_analysis(
            home_team, away_team, home_stats, away_stats, h2h_stats, weather,
            form_analysis, streak_analysis, draw_probability
        )
        
        # Crear predicción
        prediction = DrawPrediction(
            home_team=home_team,
            away_team=away_team,
            draw_probability=draw_probability,
            confidence=confidence,
            h2h_factor=h2h_factor,
            home_team_factor=home_team_factor,
            away_team_factor=away_team_factor,
            form_balance_factor=form_balance_factor,
            streak_factor=streak_factor,
            weather_factor=weather_factor,
            accumulation_factor=(home_stats.draw_accumulation_factor + away_stats.draw_accumulation_factor) / 2,
            analysis=analysis,
            reasoning=f"Probabilidad de empate: {draw_probability:.1f}% basada en análisis integral",
            estimated_odds=self.estimate_draw_odds(draw_probability)
        )
        
        return prediction
    
    def calculate_confidence(self, home_stats: TeamDrawStats, away_stats: TeamDrawStats, 
                           h2h_stats: HeadToHeadStats, probability: float, match: Dict = None) -> float:
        """Calcula el nivel de confianza de la predicción"""
        
        confidence = 50.0  # Base
        
        # Más datos = más confianza
        if home_stats.total_matches >= 30 and away_stats.total_matches >= 30:
            confidence += 15
        elif home_stats.total_matches >= 20 and away_stats.total_matches >= 20:
            confidence += 10
        
        # Enfrentamientos directos recientes
        if h2h_stats.total_matches >= 8:
            confidence += 10
        elif h2h_stats.total_matches >= 5:
            confidence += 5
        
        # Probabilidad en rango óptimo
        if 25 <= probability <= 45:
            confidence += 15
        elif 20 <= probability <= 50:
            confidence += 10
        elif 15 <= probability <= 55:
            confidence += 5
        
        # Consistencia en las rachas
        home_streak_consistency = len(set(home_stats.current_streak)) < 3
        away_streak_consistency = len(set(away_stats.current_streak)) < 3
        
        if home_streak_consistency or away_streak_consistency:
            confidence += 5
        
        # FACTOR DE DIVERSIDAD PARA EMPATES
        if match:
            confidence = self.add_draws_diversity_factor(confidence, match)
        
        return min(confidence, 95.0)
    
    def add_draws_diversity_factor(self, confidence: float, match: Dict) -> float:
        """Añade factor de diversidad específico para empates"""
        
        # Factor basado en competición (algunas ligas tienen más empates)
        competition = match.get('competition', '').lower()
        competition_factor = 0
        
        if 'serie a' in competition or 'italy' in competition:
            competition_factor = 8  # Serie A más empates
        elif 'la liga' in competition or 'spain' in competition:
            competition_factor = 5  # La Liga moderado
        elif 'ligue 1' in competition or 'france' in competition:
            competition_factor = 6  # Ligue 1 bastantes empates
        elif 'premier' in competition or 'england' in competition:
            competition_factor = 2  # Premier League menos empates
        elif 'bundesliga' in competition or 'germany' in competition:
            competition_factor = 3  # Bundesliga equilibrado
        elif 'friendlies' in competition:
            competition_factor = -15  # Amistosos raramente empatan
        elif 'division' in competition:
            competition_factor = 4  # Divisiones menores más empates
        
        # Factor basado en importancia del partido
        if 'cup' in competition or 'champions' in competition:
            importance_factor = -8  # Partidos importantes evitan empates
        else:
            importance_factor = 0
        
        # Factor único por partido
        home_team = match.get('home_team', '').lower()
        away_team = match.get('away_team', '').lower()
        
        import random
        random.seed(hash(f"{home_team}_{away_team}_draws"))
        unique_factor = random.uniform(-5, 5)
        
        adjusted_confidence = confidence + competition_factor + importance_factor + unique_factor
        return max(50, min(95, adjusted_confidence))
    
    def generate_detailed_analysis(self, home_team: str, away_team: str, 
                                 home_stats: TeamDrawStats, away_stats: TeamDrawStats,
                                 h2h_stats: HeadToHeadStats, weather: WeatherConditions,
                                 form_analysis: str, streak_analysis: str, probability: float) -> str:
        """Genera análisis detallado de la predicción"""
        
        analysis_parts = []
        
        # Enfrentamientos directos
        h2h_text = f"En {h2h_stats.total_matches} enfrentamientos directos: {h2h_stats.draws} empates ({h2h_stats.draw_percentage:.1f}%)"
        if h2h_stats.draws_in_last_5 >= 2:
            h2h_text += f". Tendencia reciente: {h2h_stats.draws_in_last_5} empates en últimos 5"
        analysis_parts.append(h2h_text)
        
        # Estadísticas de equipos
        home_text = f"{home_team}: {home_stats.draws_percentage:.1f}% empates ({home_stats.home_draws_percentage:.1f}% en casa)"
        away_text = f"{away_team}: {away_stats.draws_percentage:.1f}% empates ({away_stats.away_draws_percentage:.1f}% fuera)"
        analysis_parts.extend([home_text, away_text])
        
        # Forma y racha
        analysis_parts.append(form_analysis)
        analysis_parts.append(streak_analysis)
        
        # Factor climatológico
        if weather.draw_impact_factor > 1.05:
            weather_text = f"Condiciones climáticas favorecen empate: "
            conditions = []
            if weather.precipitation > 5:
                conditions.append(f"lluvia ({weather.precipitation:.1f}mm)")
            if weather.temperature < 5 or weather.temperature > 35:
                conditions.append(f"temperatura extrema ({weather.temperature:.1f}°C)")
            if weather.wind_speed > 20:
                conditions.append(f"viento fuerte ({weather.wind_speed:.1f}km/h)")
            
            if conditions:
                weather_text += ", ".join(conditions)
                analysis_parts.append(weather_text)
        
        # Conclusión
        if probability >= 35:
            conclusion = "Alta probabilidad de empate por convergencia de factores"
        elif probability >= 25:
            conclusion = "Probabilidad moderada-alta de empate"
        elif probability >= 20:
            conclusion = "Probabilidad moderada de empate"
        else:
            conclusion = "Probabilidad baja de empate"
        
        analysis_parts.append(conclusion)
        
        return ". ".join(analysis_parts) + "."
    
    def estimate_draw_odds(self, probability: float) -> float:
        """Estima las cuotas de empate basadas en la probabilidad"""
        if probability <= 0:
            return 10.0
        
        # Convertir probabilidad a cuotas (con margen de casa de apuestas del 5%)
        fair_odds = 100.0 / probability
        estimated_odds = fair_odds * 1.05  # Margen de la casa
        
        # Limitar rangos realistas
        return max(min(estimated_odds, 15.0), 2.0)
    
    def should_bet(self, prediction: DrawPrediction) -> bool:
        """Determina si se debe apostar basado en la configuración"""
        min_confidence = self.config.get('confidence_threshold', 70)
        min_odds = self.config.get('min_odds', 1.5)
        max_odds = self.config.get('max_odds', 6.0)
        
        return (prediction.confidence >= min_confidence and 
                min_odds <= prediction.estimated_odds <= max_odds)
    
    def get_picks_for_matches(self, matches: List[Dict]) -> List[Dict]:
        """Genera picks para una lista de partidos - TODOS los que tengan valor"""
        picks = []
        
        for match in matches:
            home_team = match.get('home_team', '')
            away_team = match.get('away_team', '')
            
            if not home_team or not away_team:
                continue
            
            # Analizar partido
            prediction = self.analyze_match_draw_probability(home_team, away_team, match)
            
            # Verificar si cumple criterios
            if self.should_bet(prediction):
                pick = {
                    'home_team': home_team,
                    'away_team': away_team,
                    'prediction_type': 'draw',
                    'prediction': f"Empate - {prediction.draw_probability:.1f}% probabilidad",
                    'confidence': prediction.confidence,
                    'draw_probability': prediction.draw_probability,
                    'reasoning': prediction.analysis,
                    'match_time': match.get('match_time', ''),
                    'competition': match.get('competition', ''),
                    'odds': prediction.estimated_odds,
                    'factors': {
                        'h2h_factor': prediction.h2h_factor,
                        'home_factor': prediction.home_team_factor,
                        'away_factor': prediction.away_team_factor,
                        'form_balance': prediction.form_balance_factor,
                        'streak_factor': prediction.streak_factor,
                        'weather_factor': prediction.weather_factor,
                        'accumulation_factor': prediction.accumulation_factor
                    }
                }
                picks.append(pick)
        
        # Ordenar por confianza
        return sorted(picks, key=lambda x: x['confidence'], reverse=True)
    
    def update_team_stats_after_match(self, team: str, result: str):
        """Actualiza estadísticas del equipo después de un partido"""
        if team in self.teams_stats:
            stats = self.teams_stats[team]
            
            # Actualizar racha
            stats.current_streak.append(result)
            if len(stats.current_streak) > 5:
                stats.current_streak.pop(0)
            
            # Actualizar contador de partidos sin empate
            if result == 'D':
                stats.consecutive_non_draws = 0
                stats.draw_accumulation_factor = 1.0  # Reset
            else:
                stats.consecutive_non_draws += 1
                # Incrementar factor de acumulación (cada W/L suma probabilidad)
                stats.draw_accumulation_factor += 0.05
                stats.draw_accumulation_factor = min(stats.draw_accumulation_factor, 1.5)
            
            # Actualizar partidos desde último empate
            if result == 'D':
                stats.matches_since_last_draw = 0
            else:
                stats.matches_since_last_draw += 1