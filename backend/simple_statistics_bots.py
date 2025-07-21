#!/usr/bin/env python3
"""
Simple Statistics Bots - Bots Basados en Pura Estadística
=========================================================

Bots simplificados que solo usan medias históricas sin algoritmos complejos.
"""

import sys
import json
import statistics
from typing import Dict, List, Optional
from dataclasses import dataclass

sys.path.append('.')

@dataclass
class SimpleTeamStats:
    """Estadísticas simples de un equipo"""
    team_name: str
    # Córners
    corners_per_match: float = 0.0
    corners_against_per_match: float = 0.0
    # Tarjetas
    cards_per_match: float = 0.0
    # Goles
    goals_for_per_match: float = 0.0
    goals_against_per_match: float = 0.0
    # Empates
    total_matches: int = 0
    draws: int = 0
    matches_without_draw: int = 0
    draw_percentage: float = 0.0

class SimpleStatisticsBots:
    """Bots simplificados basados en estadística pura"""
    
    def __init__(self):
        self.teams_stats = self.load_team_statistics()
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Carga configuración de bots"""
        try:
            with open('data/bots_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def load_team_statistics(self) -> Dict[str, SimpleTeamStats]:
        """Carga estadísticas históricas reales de equipos"""
        
        # Base de datos de estadísticas reales (ejemplo con equipos conocidos)
        # En un sistema real, esto vendría de una base de datos histórica
        real_stats = {
            # La Liga
            'Real Madrid': SimpleTeamStats(
                team_name='Real Madrid',
                corners_per_match=6.2, corners_against_per_match=4.1,
                cards_per_match=2.1, goals_for_per_match=2.3, goals_against_per_match=0.9,
                total_matches=38, draws=8, matches_without_draw=30, draw_percentage=21.1
            ),
            'Barcelona': SimpleTeamStats(
                team_name='Barcelona',
                corners_per_match=7.1, corners_against_per_match=3.8,
                cards_per_match=1.9, goals_for_per_match=2.1, goals_against_per_match=1.0,
                total_matches=38, draws=10, matches_without_draw=28, draw_percentage=26.3
            ),
            'Atletico Madrid': SimpleTeamStats(
                team_name='Atletico Madrid',
                corners_per_match=5.3, corners_against_per_match=4.2,
                cards_per_match=2.4, goals_for_per_match=1.7, goals_against_per_match=0.8,
                total_matches=38, draws=12, matches_without_draw=26, draw_percentage=31.6
            ),
            
            # Premier League
            'Manchester City': SimpleTeamStats(
                team_name='Manchester City',
                corners_per_match=7.8, corners_against_per_match=3.2,
                cards_per_match=1.7, goals_for_per_match=2.4, goals_against_per_match=0.8,
                total_matches=38, draws=6, matches_without_draw=32, draw_percentage=15.8
            ),
            'Liverpool': SimpleTeamStats(
                team_name='Liverpool',
                corners_per_match=6.9, corners_against_per_match=3.9,
                cards_per_match=1.8, goals_for_per_match=2.2, goals_against_per_match=1.1,
                total_matches=38, draws=9, matches_without_draw=29, draw_percentage=23.7
            ),
            'Arsenal': SimpleTeamStats(
                team_name='Arsenal',
                corners_per_match=6.1, corners_against_per_match=4.3,
                cards_per_match=2.0, goals_for_per_match=1.9, goals_against_per_match=1.2,
                total_matches=38, draws=11, matches_without_draw=27, draw_percentage=28.9
            ),
            
            # Equipos genéricos para otros partidos
            'Generic Team A': SimpleTeamStats(
                team_name='Generic Team A',
                corners_per_match=5.5, corners_against_per_match=5.0,
                cards_per_match=2.2, goals_for_per_match=1.5, goals_against_per_match=1.4,
                total_matches=30, draws=8, matches_without_draw=22, draw_percentage=26.7
            ),
            'Generic Team B': SimpleTeamStats(
                team_name='Generic Team B',
                corners_per_match=5.0, corners_against_per_match=5.5,
                cards_per_match=2.3, goals_for_per_match=1.4, goals_against_per_match=1.5,
                total_matches=30, draws=9, matches_without_draw=21, draw_percentage=30.0
            )
        }
        
        return real_stats
    
    def get_team_stats(self, team_name: str) -> SimpleTeamStats:
        """Obtiene estadísticas de un equipo (o genéricas si no existe)"""
        
        # Buscar por nombre exacto
        if team_name in self.teams_stats:
            return self.teams_stats[team_name]
        
        # Buscar por similitud (nombres parciales)
        for stats_name, stats in self.teams_stats.items():
            if any(word.lower() in team_name.lower() for word in stats_name.split()):
                return stats
        
        # Si no se encuentra, usar estadísticas genéricas
        return self.teams_stats.get('Generic Team A', SimpleTeamStats(team_name=team_name))
    
    # ===== BOT CÓRNERS SIMPLIFICADO =====
    def analyze_corners_simple(self, home_team: str, away_team: str) -> Dict:
        """Análisis de córners basado SOLO en medias históricas"""
        
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        
        # PURA ESTADÍSTICA: Solo medias
        home_corners_expected = home_stats.corners_per_match
        away_corners_expected = away_stats.corners_per_match
        total_corners_expected = home_corners_expected + away_corners_expected
        
        # Confianza basada en datos disponibles
        confidence = 70.0  # Base fija
        if home_team in self.teams_stats and away_team in self.teams_stats:
            confidence = 80.0  # Más confianza si tenemos datos reales
        
        # Cuotas estimadas (inversa de probabilidad normalizada)
        probability = min(total_corners_expected / 15.0, 0.9)  # Normalizar a 15 córners máx
        estimated_odds = 1.0 / probability if probability > 0 else 2.0
        estimated_odds = max(1.5, min(estimated_odds, 5.0))  # Limitar rango
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'prediction_type': 'corners',
            'prediction': f"Córners - {total_corners_expected:.1f} esperados",
            'confidence': confidence,
            'total_corners_expected': total_corners_expected,
            'home_corners_expected': home_corners_expected,
            'away_corners_expected': away_corners_expected,
            'odds': estimated_odds,
            'reasoning': f"Media histórica: {home_team} {home_corners_expected:.1f} córners/partido, {away_team} {away_corners_expected:.1f} córners/partido. Total esperado: {total_corners_expected:.1f}"
        }
    
    # ===== BOT TARJETAS SIMPLIFICADO =====
    def analyze_cards_simple(self, home_team: str, away_team: str, referee: str = None) -> Dict:
        """Análisis de tarjetas basado SOLO en medias históricas"""
        
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        
        # PURA ESTADÍSTICA: Solo medias
        home_cards_expected = home_stats.cards_per_match
        away_cards_expected = away_stats.cards_per_match
        total_cards_expected = home_cards_expected + away_cards_expected
        
        # Ajuste mínimo por árbitro (si es conocido como estricto)
        referee_factor = 1.0
        if referee:
            strict_referees = ['Antonio Mateu Lahoz', 'Jesús Gil Manzano', 'Michael Oliver']
            if any(ref in referee for ref in strict_referees):
                referee_factor = 1.2
        
        total_cards_expected *= referee_factor
        
        # Confianza basada en datos disponibles
        confidence = 70.0  # Base fija
        if home_team in self.teams_stats and away_team in self.teams_stats:
            confidence = 80.0
        
        # Cuotas estimadas
        probability = min(total_cards_expected / 8.0, 0.9)  # Normalizar a 8 tarjetas máx
        estimated_odds = 1.0 / probability if probability > 0 else 2.0
        estimated_odds = max(1.5, min(estimated_odds, 4.5))
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'prediction_type': 'cards',
            'prediction': f"Tarjetas - {total_cards_expected:.1f} esperadas",
            'confidence': confidence,
            'total_cards_expected': total_cards_expected,
            'referee': referee,
            'odds': estimated_odds,
            'reasoning': f"Media histórica: {home_team} {home_cards_expected:.1f} tarjetas/partido, {away_team} {away_cards_expected:.1f} tarjetas/partido. Total esperado: {total_cards_expected:.1f}"
        }
    
    # ===== BOT AMBOS MARCAN SIMPLIFICADO =====
    def analyze_btts_simple(self, home_team: str, away_team: str) -> Dict:
        """Análisis BTTS basado SOLO en medias históricas de goles"""
        
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        
        # PURA ESTADÍSTICA: Probabilidad basada en medias de goles
        home_goals_expected = home_stats.goals_for_per_match
        away_goals_expected = away_stats.goals_for_per_match
        
        # Probabilidad BTTS: Si ambos equipos tienen media > 1.0 gol
        btts_probability = 0.0
        if home_goals_expected >= 1.0 and away_goals_expected >= 1.0:
            # Fórmula simple: promedio de capacidad goleadora
            btts_probability = min((home_goals_expected + away_goals_expected) / 3.0 * 100, 85.0)
        else:
            btts_probability = 40.0  # Probabilidad baja si algún equipo marca poco
        
        # Confianza basada en datos disponibles
        confidence = 70.0
        if home_team in self.teams_stats and away_team in self.teams_stats:
            confidence = 80.0
        
        # Cuotas estimadas
        probability_decimal = btts_probability / 100.0
        estimated_odds = 1.0 / probability_decimal if probability_decimal > 0 else 3.0
        estimated_odds = max(1.3, min(estimated_odds, 4.0))
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'prediction_type': 'both_teams_score',
            'btts_probability': btts_probability,
            'confidence': confidence,
            'odds': estimated_odds,
            'reasoning': f"Media de goles: {home_team} {home_goals_expected:.1f} goles/partido, {away_team} {away_goals_expected:.1f} goles/partido. Probabilidad BTTS: {btts_probability:.1f}%"
        }
    
    # ===== BOT EMPATES CON FÓRMULA =====
    def analyze_draws_with_formula(self, home_team: str, away_team: str) -> Dict:
        """Análisis de empates usando la fórmula específica proporcionada"""
        
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        
        # FÓRMULA: P_ajustada = P_media × (1 + α × n_sin_empate/N)
        
        # P_media: probabilidad promedio de empate por partido (histórica)
        # Usar promedio de ambos equipos
        p_media = (home_stats.draw_percentage + away_stats.draw_percentage) / 2.0 / 100.0
        
        # n_sin_empate: partidos seguidos sin empatar (usar el mayor de ambos equipos)
        n_sin_empate = max(home_stats.matches_without_draw, away_stats.matches_without_draw)
        
        # N: total de partidos en la temporada (usar promedio)
        N = (home_stats.total_matches + away_stats.total_matches) / 2.0
        
        # α: coeficiente de sensibilidad (0.8 como en el ejemplo)
        alpha = 0.8
        
        # Aplicar fórmula
        p_ajustada = p_media * (1 + alpha * (n_sin_empate / N))
        
        # Convertir a porcentaje
        draw_probability = min(p_ajustada * 100, 85.0)  # Máximo 85%
        
        # Confianza REDUCIDA (como solicitado)
        confidence = 65.0  # Reducido del 80%
        if home_team in self.teams_stats and away_team in self.teams_stats:
            confidence = 75.0  # Reducido del 80%
        
        # Cuotas estimadas para empates
        estimated_odds = 1.0 / p_ajustada if p_ajustada > 0 else 4.0
        estimated_odds = max(2.5, min(estimated_odds, 6.0))  # Rango típico empates
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'prediction_type': 'draw',
            'draw_probability': draw_probability,
            'confidence': confidence,
            'odds': estimated_odds,
            'p_media': p_media,
            'n_sin_empate': n_sin_empate,
            'N': N,
            'alpha': alpha,
            'reasoning': f"Fórmula aplicada: P_media={p_media:.3f}, n_sin_empate={n_sin_empate}, N={N:.1f}, α={alpha}. Probabilidad ajustada: {draw_probability:.1f}%"
        }

if __name__ == "__main__":
    print("🧮 TESTING BOTS ESTADÍSTICA SIMPLE")
    print("=" * 50)
    
    bots = SimpleStatisticsBots()
    
    # Test con equipos conocidos
    test_matches = [
        ('Real Madrid', 'Barcelona'),
        ('Manchester City', 'Liverpool'),
        ('Arsenal', 'Atletico Madrid')
    ]
    
    for home, away in test_matches:
        print(f"\n🏟️ {home} vs {away}")
        print("-" * 30)
        
        # Test córners
        corners = bots.analyze_corners_simple(home, away)
        print(f"⚽ Córners: {corners['total_corners_expected']:.1f} esperados ({corners['confidence']:.0f}%)")
        
        # Test tarjetas
        cards = bots.analyze_cards_simple(home, away, "Antonio Mateu Lahoz")
        print(f"🟨 Tarjetas: {cards['total_cards_expected']:.1f} esperadas ({cards['confidence']:.0f}%)")
        
        # Test BTTS
        btts = bots.analyze_btts_simple(home, away)
        print(f"🎯 BTTS: {btts['btts_probability']:.1f}% ({btts['confidence']:.0f}%)")
        
        # Test empates
        draws = bots.analyze_draws_with_formula(home, away)
        print(f"🤝 Empate: {draws['draw_probability']:.1f}% ({draws['confidence']:.0f}%)")
        print(f"   📐 Fórmula: P_media={draws['p_media']:.3f}, n_sin_empate={draws['n_sin_empate']}")