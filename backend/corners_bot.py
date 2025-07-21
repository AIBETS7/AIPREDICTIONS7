import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics
from dataclasses import dataclass

@dataclass
class TeamCornerStats:
    """Estadísticas de córners de un equipo"""
    team_name: str
    home_corners_for: List[int]  # Córners a favor jugando de local
    home_corners_against: List[int]  # Córners en contra jugando de local
    away_corners_for: List[int]  # Córners a favor jugando de visitante
    away_corners_against: List[int]  # Córners en contra jugando de visitante
    
    @property
    def home_avg_for(self) -> float:
        return statistics.mean(self.home_corners_for) if self.home_corners_for else 0
    
    @property
    def home_avg_against(self) -> float:
        return statistics.mean(self.home_corners_against) if self.home_corners_against else 0
    
    @property
    def away_avg_for(self) -> float:
        return statistics.mean(self.away_corners_for) if self.away_corners_for else 0
    
    @property
    def away_avg_against(self) -> float:
        return statistics.mean(self.away_corners_against) if self.away_corners_against else 0
    
    @property
    def total_home_avg(self) -> float:
        return self.home_avg_for + self.home_avg_against
    
    @property
    def total_away_avg(self) -> float:
        return self.away_avg_for + self.away_avg_against

@dataclass
class CornersPrediction:
    """Predicción de córners para un partido"""
    home_team: str
    away_team: str
    predicted_total_corners: float
    confidence: float
    home_team_corners: float
    away_team_corners: float
    analysis: str
    factors: Dict[str, float]

class CornersBot:
    """Bot especializado en predicciones de córners"""
    
    def __init__(self):
        self.name = "Bot Córners"
        self.config = self.load_config()
        self.teams_stats = {}
        self.load_teams_data()
    
    def load_config(self) -> Dict:
        """Carga la configuración del bot"""
        config_path = os.path.join(os.path.dirname(__file__), 'data', 'bots_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('bots', {}).get('corneres', {})
        except FileNotFoundError:
            return {
                'confidence_threshold': 70,
                'min_odds': 1.5,
                'max_picks_per_day': 999
            }
    
    def load_teams_data(self):
        """Carga datos históricos de equipos (simulados por ahora)"""
        # En un sistema real, esto vendría de tu base de datos
        # Por ahora simulo datos realistas de equipos de La Liga
        self.teams_stats = {
            'Real Madrid': TeamCornerStats(
                'Real Madrid',
                home_corners_for=[6, 8, 7, 9, 5, 7, 8, 6, 9, 7],  # Últimos 10 partidos de local
                home_corners_against=[3, 4, 2, 5, 3, 4, 2, 3, 4, 3],
                away_corners_for=[5, 6, 4, 7, 5, 6, 4, 5, 6, 5],  # Últimos 10 partidos de visitante
                away_corners_against=[4, 5, 3, 6, 4, 5, 3, 4, 5, 4]
            ),
            'Barcelona': TeamCornerStats(
                'Barcelona',
                home_corners_for=[8, 9, 7, 10, 6, 8, 9, 7, 8, 9],
                home_corners_against=[2, 3, 4, 2, 5, 3, 2, 4, 3, 2],
                away_corners_for=[6, 7, 5, 8, 6, 7, 5, 6, 7, 6],
                away_corners_against=[3, 4, 5, 3, 6, 4, 5, 3, 4, 5]
            ),
            'Atletico Madrid': TeamCornerStats(
                'Atletico Madrid',
                home_corners_for=[5, 6, 4, 7, 5, 6, 4, 5, 6, 5],
                home_corners_against=[4, 3, 5, 2, 6, 3, 5, 4, 3, 5],
                away_corners_for=[4, 5, 3, 6, 4, 5, 3, 4, 5, 4],
                away_corners_against=[5, 4, 6, 3, 7, 4, 6, 5, 4, 6]
            ),
            'Sevilla': TeamCornerStats(
                'Sevilla',
                home_corners_for=[6, 7, 5, 8, 6, 7, 5, 6, 7, 6],
                home_corners_against=[4, 3, 5, 2, 6, 3, 5, 4, 3, 5],
                away_corners_for=[5, 6, 4, 7, 5, 6, 4, 5, 6, 5],
                away_corners_against=[5, 4, 6, 3, 7, 4, 6, 5, 4, 6]
            ),
            'Valencia': TeamCornerStats(
                'Valencia',
                home_corners_for=[5, 6, 4, 7, 5, 6, 4, 5, 6, 5],
                home_corners_against=[5, 4, 6, 3, 7, 4, 6, 5, 4, 6],
                away_corners_for=[4, 5, 3, 6, 4, 5, 3, 4, 5, 4],
                away_corners_against=[6, 5, 7, 4, 8, 5, 7, 6, 5, 7]
            ),
            'Real Betis': TeamCornerStats(
                'Real Betis',
                home_corners_for=[7, 8, 6, 9, 7, 8, 6, 7, 8, 7],
                home_corners_against=[3, 4, 5, 2, 6, 4, 5, 3, 4, 5],
                away_corners_for=[5, 6, 4, 7, 5, 6, 4, 5, 6, 5],
                away_corners_against=[5, 4, 6, 3, 7, 4, 6, 5, 4, 6]
            )
        }
    
    def calculate_team_vs_opponent_corners(self, team: str, opponent: str, is_home: bool) -> Tuple[float, str]:
        """Calcula córners esperados considerando el rival específico"""
        if team not in self.teams_stats or opponent not in self.teams_stats:
            return 5.0, "Datos insuficientes para el análisis"
        
        team_stats = self.teams_stats[team]
        opponent_stats = self.teams_stats[opponent]
        
        if is_home:
            # Equipo local: promedio de córners a favor de local + promedio que concede visitante
            team_corners_for = team_stats.home_avg_for
            opponent_corners_against = opponent_stats.away_avg_against
            
            # Factor de ajuste basado en la diferencia de estilos
            attacking_factor = team_corners_for / 6.0  # Normalizado a 6 córners promedio
            defensive_factor = opponent_corners_against / 4.5  # Normalizado a 4.5 córners concedidos
            
            expected_corners = (team_corners_for + opponent_corners_against) / 2
            expected_corners *= (attacking_factor + defensive_factor) / 2
            
            analysis = f"{team} (local): {team_corners_for:.1f} córners/partido, {opponent} concede {opponent_corners_against:.1f} de visitante"
            
        else:
            # Equipo visitante
            team_corners_for = team_stats.away_avg_for
            opponent_corners_against = opponent_stats.home_avg_against
            
            attacking_factor = team_corners_for / 5.0  # Visitantes suelen tener menos córners
            defensive_factor = opponent_corners_against / 3.5
            
            expected_corners = (team_corners_for + opponent_corners_against) / 2
            expected_corners *= (attacking_factor + defensive_factor) / 2
            
            analysis = f"{team} (visitante): {team_corners_for:.1f} córners/partido, {opponent} concede {opponent_corners_against:.1f} de local"
        
        return expected_corners, analysis
    
    def analyze_match_corners(self, home_team: str, away_team: str) -> CornersPrediction:
        """Análisis completo de córners para un partido"""
        
        # Calcular córners esperados para cada equipo
        home_corners, home_analysis = self.calculate_team_vs_opponent_corners(home_team, away_team, True)
        away_corners, away_analysis = self.calculate_team_vs_opponent_corners(away_team, home_team, False)
        
        total_predicted_corners = home_corners + away_corners
        
        # Factores adicionales de análisis
        factors = self.calculate_additional_factors(home_team, away_team)
        
        # Aplicar factores de ajuste
        adjusted_total = total_predicted_corners * factors['style_factor'] * factors['form_factor']
        
        # Calcular confianza basada en consistencia de datos
        confidence = self.calculate_confidence(home_team, away_team, adjusted_total)
        
        # Generar análisis detallado
        detailed_analysis = self.generate_detailed_analysis(
            home_team, away_team, home_corners, away_corners, 
            adjusted_total, factors, home_analysis, away_analysis
        )
        
        return CornersPrediction(
            home_team=home_team,
            away_team=away_team,
            predicted_total_corners=round(adjusted_total, 1),
            confidence=confidence,
            home_team_corners=round(home_corners, 1),
            away_team_corners=round(away_corners, 1),
            analysis=detailed_analysis,
            factors=factors
        )
    
    def calculate_additional_factors(self, home_team: str, away_team: str) -> Dict[str, float]:
        """Calcula factores adicionales que afectan los córners"""
        
        # Factor de estilo de juego (equipos ofensivos vs defensivos)
        style_factor = 1.0
        if home_team in ['Barcelona', 'Real Madrid', 'Real Betis']:
            style_factor += 0.1  # Equipos más ofensivos
        if away_team in ['Barcelona', 'Real Madrid', 'Real Betis']:
            style_factor += 0.1
        if home_team in ['Atletico Madrid']:
            style_factor -= 0.1  # Equipos más defensivos
        if away_team in ['Atletico Madrid']:
            style_factor -= 0.05
        
        # Factor de forma (simulado - en realidad vendría de resultados recientes)
        form_factor = 1.0
        import random
        random.seed(hash(home_team + away_team))  # Consistente para el mismo partido
        form_factor += random.uniform(-0.1, 0.1)
        
        # Factor de rivalidad (derbis suelen tener más córners)
        rivalry_factor = 1.0
        madrid_teams = ['Real Madrid', 'Atletico Madrid']
        if home_team in madrid_teams and away_team in madrid_teams:
            rivalry_factor = 1.15
        
        return {
            'style_factor': style_factor,
            'form_factor': form_factor,
            'rivalry_factor': rivalry_factor,
            'combined_factor': style_factor * form_factor * rivalry_factor
        }
    
    def calculate_confidence(self, home_team: str, away_team: str, predicted_total: float) -> float:
        """Calcula el nivel de confianza de la predicción"""
        base_confidence = 60
        
        # Aumentar confianza si tenemos datos de ambos equipos
        if home_team in self.teams_stats and away_team in self.teams_stats:
            base_confidence += 15
        
        # Aumentar confianza si la predicción está en rango típico de córners
        if 8 <= predicted_total <= 14:
            base_confidence += 10
        elif predicted_total > 12:
            base_confidence += 15  # Más confianza en partidos con muchos córners
        
        # Reducir confianza si la predicción es muy extrema
        if predicted_total < 6 or predicted_total > 18:
            base_confidence -= 20
        
        # Factor de consistencia (basado en variabilidad de datos históricos)
        if home_team in self.teams_stats:
            home_variance = statistics.variance(self.teams_stats[home_team].home_corners_for + 
                                              self.teams_stats[home_team].home_corners_against)
            if home_variance < 4:  # Baja variabilidad = más consistente
                base_confidence += 5
        
        return min(95, max(50, base_confidence))
    
    def generate_detailed_analysis(self, home_team: str, away_team: str, 
                                 home_corners: float, away_corners: float,
                                 total_corners: float, factors: Dict[str, float],
                                 home_analysis: str, away_analysis: str) -> str:
        """Genera un análisis detallado del partido"""
        
        analysis_parts = [
            f"🏟️ ANÁLISIS DE CÓRNERS: {home_team} vs {away_team}",
            "",
            f"📊 PREDICCIÓN TOTAL: {total_corners:.1f} córners",
            f"🏠 {home_team}: {home_corners:.1f} córners esperados",
            f"✈️ {away_team}: {away_corners:.1f} córners esperados",
            "",
            "📈 ANÁLISIS POR EQUIPO:",
            f"• {home_analysis}",
            f"• {away_analysis}",
            "",
            "🔍 FACTORES ADICIONALES:",
            f"• Factor de estilo: {factors['style_factor']:.2f}",
            f"• Factor de forma: {factors['form_factor']:.2f}",
            f"• Factor de rivalidad: {factors['rivalry_factor']:.2f}",
            "",
            "💡 RECOMENDACIÓN:",
        ]
        
        # Añadir recomendación específica
        estimated_odds = self.estimate_odds(total_corners)
        min_odds = self.config.get('min_odds', 1.5)
        
        if estimated_odds >= min_odds:
            analysis_parts.append(f"✅ Predicción favorable para córners")
            analysis_parts.append(f"💰 Cuota estimada: {estimated_odds} (mín: {min_odds})")
            if total_corners >= 12:
                analysis_parts.append("🔥 Partido con alta expectativa de córners")
            elif total_corners >= 10:
                analysis_parts.append("📈 Partido con buena expectativa de córners")
            else:
                analysis_parts.append("📊 Partido con expectativa moderada de córners")
        else:
            analysis_parts.append(f"❌ Cuota demasiado baja: {estimated_odds} < {min_odds} - No cumple criterios de valor")
        
        return "\n".join(analysis_parts)
    
    def should_bet(self, prediction: CornersPrediction) -> bool:
        """Determina si se debe apostar basado en la configuración"""
        min_confidence = self.config.get('confidence_threshold', 70)
        min_odds = self.config.get('min_odds', 1.5)
        
        # Estimar cuota para esta predicción
        estimated_odds = self.estimate_odds(prediction.predicted_total_corners)
        
        return (prediction.confidence >= min_confidence and
                estimated_odds >= min_odds)
    
    def get_picks_for_matches(self, matches: List[Dict]) -> List[Dict]:
        """Genera picks para una lista de partidos - TODOS los que tengan valor"""
        picks = []
        
        for match in matches:
            home_team = match.get('home_team', '')
            away_team = match.get('away_team', '')
            
            if not home_team or not away_team:
                continue
            
            prediction = self.analyze_match_corners(home_team, away_team)
            
            # Enviar TODOS los picks que cumplan los criterios mínimos
            if self.should_bet(prediction):
                pick = {
                    'home_team': home_team,
                    'away_team': away_team,
                    'prediction_type': 'corners',
                    'prediction': f"Córners - {prediction.predicted_total_corners:.1f} esperados",
                    'confidence': prediction.confidence,
                    'predicted_total': prediction.predicted_total_corners,
                    'reasoning': prediction.analysis,
                    'match_time': match.get('match_time', ''),
                    'competition': match.get('competition', ''),
                    'odds': self.estimate_odds(prediction.predicted_total_corners),
                    'factors': prediction.factors
                }
                picks.append(pick)
        
        # Ordenar por confianza (mayor a menor) pero enviar TODOS
        return sorted(picks, key=lambda x: x['confidence'], reverse=True)
    
    def estimate_odds(self, predicted_corners: float) -> float:
        """Estima las cuotas basadas en la predicción"""
        # Cuotas estimadas para Over 9.5 córners basadas en la predicción
        if predicted_corners >= 13:
            return 1.4  # Muy probable
        elif predicted_corners >= 11:
            return 1.6  # Probable
        elif predicted_corners >= 9.5:
            return 1.9  # Moderadamente probable
        else:
            return 2.5  # Menos probable
    
    def update_team_stats(self, team: str, match_data: Dict):
        """Actualiza las estadísticas de un equipo con nuevos datos"""
        if team not in self.teams_stats:
            self.teams_stats[team] = TeamCornerStats(
                team, [], [], [], []
            )
        
        is_home = match_data.get('is_home', True)
        corners_for = match_data.get('corners_for', 0)
        corners_against = match_data.get('corners_against', 0)
        
        if is_home:
            self.teams_stats[team].home_corners_for.append(corners_for)
            self.teams_stats[team].home_corners_against.append(corners_against)
            # Mantener solo los últimos 10 partidos
            if len(self.teams_stats[team].home_corners_for) > 10:
                self.teams_stats[team].home_corners_for.pop(0)
                self.teams_stats[team].home_corners_against.pop(0)
        else:
            self.teams_stats[team].away_corners_for.append(corners_for)
            self.teams_stats[team].away_corners_against.append(corners_against)
            if len(self.teams_stats[team].away_corners_for) > 10:
                self.teams_stats[team].away_corners_for.pop(0)
                self.teams_stats[team].away_corners_against.pop(0)

# Función principal para usar el bot
def run_corners_bot():
    """Ejecuta el bot de córners"""
    bot = CornersBot()
    
    # Ejemplo de partidos (en un sistema real vendrían de tu API)
    sample_matches = [
        {
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'match_time': '2025-01-22 20:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Atletico Madrid',
            'away_team': 'Sevilla',
            'match_time': '2025-01-22 18:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Real Betis',
            'away_team': 'Valencia',
            'match_time': '2025-01-22 16:00',
            'competition': 'La Liga'
        }
    ]
    
    picks = bot.get_picks_for_matches(sample_matches)
    
    print(f"🤖 {bot.name} - Picks generados: {len(picks)}")
    for i, pick in enumerate(picks, 1):
        print(f"\n--- PICK #{i} ---")
        print(f"Partido: {pick['home_team']} vs {pick['away_team']}")
        print(f"Predicción: {pick['prediction']}")
        print(f"Total esperado: {pick['predicted_total']} córners")
        print(f"Confianza: {pick['confidence']}%")
        print(f"Cuota estimada: {pick['odds']}")
        print("Análisis:")
        print(pick['reasoning'])
    
    return picks

if __name__ == "__main__":
    picks = run_corners_bot()