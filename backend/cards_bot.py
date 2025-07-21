import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics
from dataclasses import dataclass

@dataclass
class TeamCardStats:
    """Estadísticas de tarjetas de un equipo"""
    team_name: str
    home_cards_for: List[int]  # Tarjetas recibidas jugando de local
    home_cards_against: List[int]  # Tarjetas del rival jugando de local
    away_cards_for: List[int]  # Tarjetas recibidas jugando de visitante
    away_cards_against: List[int]  # Tarjetas del rival jugando de visitante
    
    @property
    def home_avg_for(self) -> float:
        return statistics.mean(self.home_cards_for) if self.home_cards_for else 0
    
    @property
    def home_avg_against(self) -> float:
        return statistics.mean(self.home_cards_against) if self.home_cards_against else 0
    
    @property
    def away_avg_for(self) -> float:
        return statistics.mean(self.away_cards_for) if self.away_cards_for else 0
    
    @property
    def away_avg_against(self) -> float:
        return statistics.mean(self.away_cards_against) if self.away_cards_against else 0
    
    @property
    def total_home_avg(self) -> float:
        return self.home_avg_for + self.home_avg_against
    
    @property
    def total_away_avg(self) -> float:
        return self.away_avg_for + self.away_avg_against

@dataclass
class RefereeStats:
    """Estadísticas de un árbitro"""
    referee_name: str
    matches_officiated: List[int]  # Tarjetas totales en cada partido
    yellow_cards_avg: float
    red_cards_avg: float
    total_cards_avg: float
    strictness_level: str  # "Permisivo", "Normal", "Estricto"

@dataclass
class CardsPrediction:
    """Predicción de tarjetas para un partido"""
    home_team: str
    away_team: str
    referee: str
    predicted_total_cards: float
    confidence: float
    home_team_cards: float
    away_team_cards: float
    referee_factor: float
    analysis: str
    factors: Dict[str, float]

class CardsBot:
    """Bot especializado en predicciones de tarjetas"""
    
    def __init__(self):
        self.name = "Bot Tarjetas"
        self.config = self.load_config()
        self.teams_stats = {}
        self.referees_stats = {}
        self.load_teams_data()
        self.load_referees_data()
    
    def load_config(self) -> Dict:
        """Carga la configuración del bot"""
        config_path = os.path.join(os.path.dirname(__file__), 'data', 'bots_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('bots', {}).get('tarjetas', {})
        except FileNotFoundError:
            return {
                'confidence_threshold': 70,
                'min_odds': 1.5,
                'max_picks_per_day': 999
            }
    
    def load_teams_data(self):
        """Carga datos históricos de equipos (simulados por ahora)"""
        # Datos realistas de tarjetas de equipos de La Liga
        self.teams_stats = {
            'Real Madrid': TeamCardStats(
                'Real Madrid',
                home_cards_for=[2, 3, 1, 4, 2, 3, 1, 2, 3, 2],  # Últimos 10 partidos de local
                home_cards_against=[2, 1, 3, 2, 4, 1, 3, 2, 1, 3],
                away_cards_for=[3, 4, 2, 5, 3, 4, 2, 3, 4, 3],  # Últimos 10 partidos de visitante
                away_cards_against=[1, 2, 3, 1, 2, 3, 4, 2, 1, 2]
            ),
            'Barcelona': TeamCardStats(
                'Barcelona',
                home_cards_for=[1, 2, 2, 3, 1, 2, 2, 1, 2, 1],
                home_cards_against=[2, 3, 1, 4, 2, 3, 1, 2, 3, 2],
                away_cards_for=[2, 3, 3, 4, 2, 3, 3, 2, 3, 2],
                away_cards_against=[2, 1, 3, 2, 4, 1, 3, 2, 1, 3]
            ),
            'Atletico Madrid': TeamCardStats(
                'Atletico Madrid',
                home_cards_for=[3, 4, 2, 5, 3, 4, 2, 3, 4, 3],
                home_cards_against=[2, 1, 3, 2, 4, 1, 3, 2, 1, 3],
                away_cards_for=[4, 5, 3, 6, 4, 5, 3, 4, 5, 4],
                away_cards_against=[1, 2, 3, 1, 2, 3, 4, 2, 1, 2]
            ),
            'Sevilla': TeamCardStats(
                'Sevilla',
                home_cards_for=[2, 3, 3, 4, 2, 3, 3, 2, 3, 2],
                home_cards_against=[2, 1, 3, 2, 4, 1, 3, 2, 1, 3],
                away_cards_for=[3, 4, 4, 5, 3, 4, 4, 3, 4, 3],
                away_cards_against=[1, 2, 3, 1, 2, 3, 4, 2, 1, 2]
            ),
            'Valencia': TeamCardStats(
                'Valencia',
                home_cards_for=[2, 3, 2, 4, 2, 3, 2, 2, 3, 2],
                home_cards_against=[3, 2, 4, 3, 5, 2, 4, 3, 2, 4],
                away_cards_for=[3, 4, 3, 5, 3, 4, 3, 3, 4, 3],
                away_cards_against=[2, 1, 3, 2, 4, 1, 3, 2, 1, 3]
            ),
            'Real Betis': TeamCardStats(
                'Real Betis',
                home_cards_for=[2, 3, 2, 4, 2, 3, 2, 2, 3, 2],
                home_cards_against=[2, 1, 3, 2, 4, 1, 3, 2, 1, 3],
                away_cards_for=[3, 4, 3, 5, 3, 4, 3, 3, 4, 3],
                away_cards_against=[2, 1, 3, 2, 4, 1, 3, 2, 1, 3]
            )
        }
    
    def load_referees_data(self):
        """Carga datos históricos de árbitros"""
        # Datos realistas de árbitros de La Liga con sus promedios de tarjetas
        self.referees_stats = {
            'Antonio Mateu Lahoz': RefereeStats(
                'Antonio Mateu Lahoz',
                [6, 8, 7, 9, 6, 8, 7, 6, 8, 7],  # Tarjetas totales por partido
                5.2, 0.3, 5.5, "Estricto"
            ),
            'Jesús Gil Manzano': RefereeStats(
                'Jesús Gil Manzano',
                [5, 6, 4, 7, 5, 6, 4, 5, 6, 5],
                4.8, 0.2, 5.0, "Normal"
            ),
            'José Luis Munuera Montero': RefereeStats(
                'José Luis Munuera Montero',
                [4, 5, 3, 6, 4, 5, 3, 4, 5, 4],
                3.9, 0.1, 4.0, "Permisivo"
            ),
            'Ricardo de Burgos Bengoetxea': RefereeStats(
                'Ricardo de Burgos Bengoetxea',
                [5, 7, 6, 8, 5, 7, 6, 5, 7, 6],
                5.0, 0.2, 5.2, "Normal"
            ),
            'César Soto Grado': RefereeStats(
                'César Soto Grado',
                [6, 7, 5, 8, 6, 7, 5, 6, 7, 6],
                5.5, 0.3, 5.8, "Estricto"
            ),
            'Javier Alberola Rojas': RefereeStats(
                'Javier Alberola Rojas',
                [4, 6, 5, 7, 4, 6, 5, 4, 6, 5],
                4.5, 0.2, 4.7, "Normal"
            ),
            'Pablo González Fuertes': RefereeStats(
                'Pablo González Fuertes',
                [3, 4, 2, 5, 3, 4, 2, 3, 4, 3],
                3.2, 0.1, 3.3, "Permisivo"
            ),
            'Mario Melero López': RefereeStats(
                'Mario Melero López',
                [7, 8, 6, 9, 7, 8, 6, 7, 8, 7],
                6.1, 0.4, 6.5, "Estricto"
            )
        }
    
    def calculate_team_vs_opponent_cards(self, team: str, opponent: str, is_home: bool) -> Tuple[float, str]:
        """Calcula tarjetas esperadas considerando el rival específico"""
        if team not in self.teams_stats or opponent not in self.teams_stats:
            return 2.5, "Datos insuficientes para el análisis"
        
        team_stats = self.teams_stats[team]
        opponent_stats = self.teams_stats[opponent]
        
        if is_home:
            # Equipo local: promedio de tarjetas que recibe de local + promedio que provoca al visitante
            team_cards_for = team_stats.home_avg_for
            opponent_cards_against = opponent_stats.away_avg_against
            
            # Factor de ajuste basado en agresividad
            aggression_factor = team_cards_for / 2.5  # Normalizado a 2.5 tarjetas promedio
            provocation_factor = opponent_cards_against / 2.0  # Normalizado a 2.0 tarjetas provocadas
            
            expected_cards = (team_cards_for + opponent_cards_against) / 2
            expected_cards *= (aggression_factor + provocation_factor) / 2
            
            analysis = f"{team} (local): {team_cards_for:.1f} tarjetas/partido, {opponent} provoca {opponent_cards_against:.1f} de visitante"
            
        else:
            # Equipo visitante
            team_cards_for = team_stats.away_avg_for
            opponent_cards_against = opponent_stats.home_avg_against
            
            aggression_factor = team_cards_for / 3.0  # Visitantes suelen tener más tarjetas
            provocation_factor = opponent_cards_against / 2.0
            
            expected_cards = (team_cards_for + opponent_cards_against) / 2
            expected_cards *= (aggression_factor + provocation_factor) / 2
            
            analysis = f"{team} (visitante): {team_cards_for:.1f} tarjetas/partido, {opponent} provoca {opponent_cards_against:.1f} de local"
        
        return expected_cards, analysis
    
    def analyze_referee_impact(self, referee: str) -> Tuple[float, str]:
        """Analiza el impacto del árbitro en las tarjetas"""
        if referee not in self.referees_stats:
            return 1.0, f"Árbitro {referee}: Sin datos históricos, factor neutro aplicado"
        
        ref_stats = self.referees_stats[referee]
        
        # Factor basado en el promedio del árbitro vs promedio general (5.0 tarjetas)
        general_avg = 5.0
        referee_factor = ref_stats.total_cards_avg / general_avg
        
        analysis = f"Árbitro {referee}: {ref_stats.total_cards_avg:.1f} tarjetas/partido (nivel: {ref_stats.strictness_level})"
        
        return referee_factor, analysis
    
    def analyze_match_cards(self, home_team: str, away_team: str, referee: str = "Desconocido") -> CardsPrediction:
        """Análisis completo de tarjetas para un partido"""
        
        # Calcular tarjetas esperadas para cada equipo
        home_cards, home_analysis = self.calculate_team_vs_opponent_cards(home_team, away_team, True)
        away_cards, away_analysis = self.calculate_team_vs_opponent_cards(away_team, home_team, False)
        
        total_predicted_cards = home_cards + away_cards
        
        # Analizar impacto del árbitro
        referee_factor, referee_analysis = self.analyze_referee_impact(referee)
        
        # Factores adicionales de análisis
        factors = self.calculate_additional_factors(home_team, away_team, referee)
        
        # Aplicar factores de ajuste incluyendo el árbitro
        adjusted_total = total_predicted_cards * factors['style_factor'] * factors['form_factor'] * referee_factor
        
        # Calcular confianza basada en consistencia de datos
        confidence = self.calculate_confidence(home_team, away_team, referee, adjusted_total)
        
        # Generar análisis detallado
        detailed_analysis = self.generate_detailed_analysis(
            home_team, away_team, referee, home_cards, away_cards, 
            adjusted_total, factors, referee_factor, home_analysis, away_analysis, referee_analysis
        )
        
        return CardsPrediction(
            home_team=home_team,
            away_team=away_team,
            referee=referee,
            predicted_total_cards=round(adjusted_total, 1),
            confidence=confidence,
            home_team_cards=round(home_cards, 1),
            away_team_cards=round(away_cards, 1),
            referee_factor=referee_factor,
            analysis=detailed_analysis,
            factors=factors
        )
    
    def calculate_additional_factors(self, home_team: str, away_team: str, referee: str) -> Dict[str, float]:
        """Calcula factores adicionales que afectan las tarjetas"""
        
        # Factor de estilo de juego (equipos agresivos vs técnicos)
        style_factor = 1.0
        if home_team in ['Atletico Madrid', 'Valencia']:
            style_factor += 0.15  # Equipos más agresivos
        if away_team in ['Atletico Madrid', 'Valencia']:
            style_factor += 0.15
        if home_team in ['Barcelona', 'Real Madrid']:
            style_factor -= 0.1  # Equipos más técnicos
        if away_team in ['Barcelona', 'Real Madrid']:
            style_factor -= 0.05
        
        # Factor de forma (simulado - en realidad vendría de resultados recientes)
        form_factor = 1.0
        import random
        random.seed(hash(home_team + away_team + referee))  # Consistente para el mismo partido
        form_factor += random.uniform(-0.1, 0.1)
        
        # Factor de rivalidad (derbis suelen tener más tarjetas)
        rivalry_factor = 1.0
        madrid_teams = ['Real Madrid', 'Atletico Madrid']
        if home_team in madrid_teams and away_team in madrid_teams:
            rivalry_factor = 1.25
        
        return {
            'style_factor': style_factor,
            'form_factor': form_factor,
            'rivalry_factor': rivalry_factor,
            'combined_factor': style_factor * form_factor * rivalry_factor
        }
    
    def calculate_confidence(self, home_team: str, away_team: str, referee: str, predicted_total: float) -> float:
        """Calcula el nivel de confianza de la predicción"""
        base_confidence = 60
        
        # Aumentar confianza si tenemos datos de ambos equipos
        if home_team in self.teams_stats and away_team in self.teams_stats:
            base_confidence += 15
        
        # Aumentar confianza si tenemos datos del árbitro
        if referee in self.referees_stats:
            base_confidence += 10
        
        # Aumentar confianza si la predicción está en rango típico de tarjetas
        if 4 <= predicted_total <= 8:
            base_confidence += 10
        elif predicted_total > 6:
            base_confidence += 15  # Más confianza en partidos con muchas tarjetas
        
        # Reducir confianza si la predicción es muy extrema
        if predicted_total < 2 or predicted_total > 12:
            base_confidence -= 20
        
        # Factor de consistencia (basado en variabilidad de datos históricos)
        if home_team in self.teams_stats:
            home_variance = statistics.variance(self.teams_stats[home_team].home_cards_for + 
                                              self.teams_stats[home_team].home_cards_against)
            if home_variance < 2:  # Baja variabilidad = más consistente
                base_confidence += 5
        
        return min(95, max(50, base_confidence))
    
    def generate_detailed_analysis(self, home_team: str, away_team: str, referee: str,
                                 home_cards: float, away_cards: float,
                                 total_cards: float, factors: Dict[str, float],
                                 referee_factor: float, home_analysis: str, away_analysis: str,
                                 referee_analysis: str) -> str:
        """Genera un análisis detallado del partido"""
        
        analysis_parts = [
            f"🟨 ANÁLISIS DE TARJETAS: {home_team} vs {away_team}",
            f"👨‍⚖️ Árbitro: {referee}",
            "",
            f"📊 PREDICCIÓN TOTAL: {total_cards:.1f} tarjetas",
            f"🏠 {home_team}: {home_cards:.1f} tarjetas esperadas",
            f"✈️ {away_team}: {away_cards:.1f} tarjetas esperadas",
            "",
            "📈 ANÁLISIS POR EQUIPO:",
            f"• {home_analysis}",
            f"• {away_analysis}",
            "",
            "👨‍⚖️ ANÁLISIS DEL ÁRBITRO:",
            f"• {referee_analysis}",
            f"• Factor árbitro: {referee_factor:.2f}",
            "",
            "🔍 FACTORES ADICIONALES:",
            f"• Factor de estilo: {factors['style_factor']:.2f}",
            f"• Factor de forma: {factors['form_factor']:.2f}",
            f"• Factor de rivalidad: {factors['rivalry_factor']:.2f}",
            "",
            "💡 RECOMENDACIÓN:",
        ]
        
        # Añadir recomendación específica
        estimated_odds = self.estimate_odds(total_cards)
        min_odds = self.config.get('min_odds', 1.5)
        
        if estimated_odds >= min_odds:
            analysis_parts.append(f"✅ Predicción favorable para tarjetas")
            analysis_parts.append(f"💰 Cuota estimada: {estimated_odds} (mín: {min_odds})")
            if total_cards >= 7:
                analysis_parts.append("🔥 Partido con alta expectativa de tarjetas")
            elif total_cards >= 5:
                analysis_parts.append("📈 Partido con buena expectativa de tarjetas")
            else:
                analysis_parts.append("📊 Partido con expectativa moderada de tarjetas")
        else:
            analysis_parts.append(f"❌ Cuota demasiado baja: {estimated_odds} < {min_odds} - No cumple criterios de valor")
        
        return "\n".join(analysis_parts)
    
    def should_bet(self, prediction: CardsPrediction) -> bool:
        """Determina si se debe apostar basado en la configuración"""
        min_confidence = self.config.get('confidence_threshold', 70)
        min_odds = self.config.get('min_odds', 1.5)
        
        # Estimar cuota para esta predicción
        estimated_odds = self.estimate_odds(prediction.predicted_total_cards)
        
        return (prediction.confidence >= min_confidence and
                estimated_odds >= min_odds)
    
    def get_picks_for_matches(self, matches: List[Dict]) -> List[Dict]:
        """Genera picks para una lista de partidos - TODOS los que tengan valor"""
        picks = []
        
        for match in matches:
            home_team = match.get('home_team', '')
            away_team = match.get('away_team', '')
            referee = match.get('referee', 'Desconocido')
            
            if not home_team or not away_team:
                continue
            
            prediction = self.analyze_match_cards(home_team, away_team, referee)
            
            # Enviar TODOS los picks que cumplan los criterios mínimos
            if self.should_bet(prediction):
                pick = {
                    'home_team': home_team,
                    'away_team': away_team,
                    'referee': referee,
                    'prediction_type': 'cards',
                    'prediction': f"Tarjetas - {prediction.predicted_total_cards:.1f} esperadas",
                    'confidence': prediction.confidence,
                    'predicted_total': prediction.predicted_total_cards,
                    'reasoning': prediction.analysis,
                    'match_time': match.get('match_time', ''),
                    'competition': match.get('competition', ''),
                    'odds': self.estimate_odds(prediction.predicted_total_cards),
                    'factors': prediction.factors,
                    'referee_factor': prediction.referee_factor
                }
                picks.append(pick)
        
        # Ordenar por confianza (mayor a menor) pero enviar TODOS
        return sorted(picks, key=lambda x: x['confidence'], reverse=True)
    
    def estimate_odds(self, predicted_cards: float) -> float:
        """Estima las cuotas basadas en la predicción"""
        # Cuotas estimadas para Over/Under tarjetas basadas en la predicción
        if predicted_cards >= 8:
            return 1.4  # Muy probable muchas tarjetas
        elif predicted_cards >= 6:
            return 1.6  # Probable
        elif predicted_cards >= 4:
            return 1.9  # Moderadamente probable
        else:
            return 2.5  # Menos probable
    
    def update_team_stats(self, team: str, match_data: Dict):
        """Actualiza las estadísticas de un equipo con nuevos datos"""
        if team not in self.teams_stats:
            self.teams_stats[team] = TeamCardStats(
                team, [], [], [], []
            )
        
        is_home = match_data.get('is_home', True)
        cards_for = match_data.get('cards_for', 0)
        cards_against = match_data.get('cards_against', 0)
        
        if is_home:
            self.teams_stats[team].home_cards_for.append(cards_for)
            self.teams_stats[team].home_cards_against.append(cards_against)
            # Mantener solo los últimos 10 partidos
            if len(self.teams_stats[team].home_cards_for) > 10:
                self.teams_stats[team].home_cards_for.pop(0)
                self.teams_stats[team].home_cards_against.pop(0)
        else:
            self.teams_stats[team].away_cards_for.append(cards_for)
            self.teams_stats[team].away_cards_against.append(cards_against)
            if len(self.teams_stats[team].away_cards_for) > 10:
                self.teams_stats[team].away_cards_for.pop(0)
                self.teams_stats[team].away_cards_against.pop(0)
    
    def update_referee_stats(self, referee: str, match_data: Dict):
        """Actualiza las estadísticas de un árbitro con nuevos datos"""
        if referee not in self.referees_stats:
            self.referees_stats[referee] = RefereeStats(
                referee, [], 0.0, 0.0, 0.0, "Normal"
            )
        
        total_cards = match_data.get('total_cards', 0)
        yellow_cards = match_data.get('yellow_cards', 0)
        red_cards = match_data.get('red_cards', 0)
        
        self.referees_stats[referee].matches_officiated.append(total_cards)
        
        # Recalcular promedios
        if len(self.referees_stats[referee].matches_officiated) > 20:
            self.referees_stats[referee].matches_officiated.pop(0)
        
        matches = self.referees_stats[referee].matches_officiated
        self.referees_stats[referee].total_cards_avg = statistics.mean(matches)
        
        # Determinar nivel de severidad
        if self.referees_stats[referee].total_cards_avg >= 6.5:
            self.referees_stats[referee].strictness_level = "Estricto"
        elif self.referees_stats[referee].total_cards_avg <= 4.0:
            self.referees_stats[referee].strictness_level = "Permisivo"
        else:
            self.referees_stats[referee].strictness_level = "Normal"

# Función principal para usar el bot
def run_cards_bot():
    """Ejecuta el bot de tarjetas"""
    bot = CardsBot()
    
    # Ejemplo de partidos con árbitros (en un sistema real vendrían de tu API)
    sample_matches = [
        {
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'referee': 'Antonio Mateu Lahoz',
            'match_time': '2025-01-22 20:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Atletico Madrid',
            'away_team': 'Sevilla',
            'referee': 'Mario Melero López',
            'match_time': '2025-01-22 18:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Real Betis',
            'away_team': 'Valencia',
            'referee': 'Pablo González Fuertes',
            'match_time': '2025-01-22 16:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Barcelona',
            'away_team': 'Atletico Madrid',
            'referee': 'César Soto Grado',
            'match_time': '2025-01-22 21:00',
            'competition': 'La Liga'
        }
    ]
    
    picks = bot.get_picks_for_matches(sample_matches)
    
    print(f"🤖 {bot.name} - Picks generados: {len(picks)}")
    for i, pick in enumerate(picks, 1):
        print(f"\n--- PICK #{i} ---")
        print(f"Partido: {pick['home_team']} vs {pick['away_team']}")
        print(f"Árbitro: {pick['referee']}")
        print(f"Predicción: {pick['prediction']}")
        print(f"Confianza: {pick['confidence']}%")
        print(f"Cuota estimada: {pick['odds']}")
        print("Análisis:")
        print(pick['reasoning'])
    
    return picks

if __name__ == "__main__":
    picks = run_cards_bot()