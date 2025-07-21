#!/usr/bin/env python3
"""
Script de prueba para el Bot de Córners
Demuestra el análisis sofisticado de córners considerando equipos, rivales y estadísticas
"""

from corners_bot import CornersBot, run_corners_bot

def test_individual_analysis():
    """Prueba el análisis individual de partidos"""
    print("🤖 PRUEBA DEL BOT DE CÓRNERS - ANÁLISIS INDIVIDUAL")
    print("=" * 60)
    
    bot = CornersBot()
    
    # Casos de prueba específicos
    test_matches = [
        ("Real Madrid", "Barcelona"),  # Clásico - equipos ofensivos
        ("Atletico Madrid", "Sevilla"),  # Atlético defensivo vs Sevilla ofensivo
        ("Real Betis", "Valencia"),  # Dos equipos de medio nivel
        ("Barcelona", "Atletico Madrid"),  # Ofensivo vs Defensivo
    ]
    
    for i, (home, away) in enumerate(test_matches, 1):
        print(f"\n🏟️ ANÁLISIS #{i}: {home} vs {away}")
        print("-" * 40)
        
        prediction = bot.analyze_match_corners(home, away)
        
        print(f"Predicción total: {prediction.predicted_total_corners} córners")
        print(f"Confianza: {prediction.confidence}%")
        print(f"Córners {home}: {prediction.home_team_corners}")
        print(f"Córners {away}: {prediction.away_team_corners}")
        print(f"¿Apostar?: {'✅ SÍ' if bot.should_bet(prediction) else '❌ NO'}")
        
        print("\n📊 FACTORES:")
        for factor, value in prediction.factors.items():
            print(f"  • {factor}: {value:.3f}")
        
        print(f"\n📝 ANÁLISIS COMPLETO:")
        print(prediction.analysis)
        print("\n" + "="*60)

def test_team_statistics():
    """Muestra las estadísticas de los equipos"""
    print("\n📊 ESTADÍSTICAS DE EQUIPOS")
    print("=" * 60)
    
    bot = CornersBot()
    
    for team_name, stats in bot.teams_stats.items():
        print(f"\n🏆 {team_name}")
        print(f"  Local - Córners a favor: {stats.home_avg_for:.1f} | En contra: {stats.home_avg_against:.1f}")
        print(f"  Visitante - Córners a favor: {stats.away_avg_for:.1f} | En contra: {stats.away_avg_against:.1f}")
        print(f"  Total promedio local: {stats.total_home_avg:.1f}")
        print(f"  Total promedio visitante: {stats.total_away_avg:.1f}")

def test_configuration_impact():
    """Prueba cómo afectan diferentes configuraciones"""
    print("\n⚙️ PRUEBA DE CONFIGURACIONES")
    print("=" * 60)
    
    # Configuración conservadora
    print("\n🔒 CONFIGURACIÓN CONSERVADORA (Umbral 80%, Min 11 córners)")
    bot = CornersBot()
    bot.config['confidence_threshold'] = 80
    bot.config['min_corners'] = 11
    
    picks = bot.get_picks_for_matches([
        {'home_team': 'Real Madrid', 'away_team': 'Barcelona', 'match_time': '20:00', 'competition': 'La Liga'},
        {'home_team': 'Atletico Madrid', 'away_team': 'Sevilla', 'match_time': '18:00', 'competition': 'La Liga'},
        {'home_team': 'Real Betis', 'away_team': 'Valencia', 'match_time': '16:00', 'competition': 'La Liga'},
    ])
    print(f"Picks generados: {len(picks)}")
    for pick in picks:
        print(f"  • {pick['home_team']} vs {pick['away_team']} - {pick['confidence']:.1f}% - {pick['predicted_total']} córners")
    
    # Configuración agresiva
    print("\n🔥 CONFIGURACIÓN AGRESIVA (Umbral 60%, Min 8 córners)")
    bot.config['confidence_threshold'] = 60
    bot.config['min_corners'] = 8
    
    picks = bot.get_picks_for_matches([
        {'home_team': 'Real Madrid', 'away_team': 'Barcelona', 'match_time': '20:00', 'competition': 'La Liga'},
        {'home_team': 'Atletico Madrid', 'away_team': 'Sevilla', 'match_time': '18:00', 'competition': 'La Liga'},
        {'home_team': 'Real Betis', 'away_team': 'Valencia', 'match_time': '16:00', 'competition': 'La Liga'},
    ])
    print(f"Picks generados: {len(picks)}")
    for pick in picks:
        print(f"  • {pick['home_team']} vs {pick['away_team']} - {pick['confidence']:.1f}% - {pick['predicted_total']} córners")

def demonstrate_vs_analysis():
    """Demuestra el análisis de equipos vs rivales específicos"""
    print("\n🆚 ANÁLISIS EQUIPO vs RIVAL")
    print("=" * 60)
    
    bot = CornersBot()
    
    # Real Madrid como local vs diferentes rivales
    rivals = ['Barcelona', 'Atletico Madrid', 'Sevilla', 'Valencia']
    
    print("\n🏠 REAL MADRID (LOCAL) vs DIFERENTES RIVALES:")
    for rival in rivals:
        corners, analysis = bot.calculate_team_vs_opponent_corners('Real Madrid', rival, True)
        print(f"  vs {rival}: {corners:.1f} córners esperados")
        print(f"    → {analysis}")
    
    # Barcelona como visitante vs diferentes rivales
    print("\n✈️ BARCELONA (VISITANTE) vs DIFERENTES RIVALES:")
    for rival in rivals:
        if rival != 'Barcelona':
            corners, analysis = bot.calculate_team_vs_opponent_corners('Barcelona', rival, False)
            print(f"  @ {rival}: {corners:.1f} córners esperados")
            print(f"    → {analysis}")

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL BOT DE CÓRNERS")
    print("Este bot analiza:")
    print("• Media de córners de cada equipo como local/visitante")
    print("• Córners que concede cada equipo")
    print("• Análisis específico del rival")
    print("• Factores de estilo de juego, forma y rivalidad")
    print("• Predicción total con nivel de confianza")
    
    # Ejecutar todas las pruebas
    test_team_statistics()
    test_individual_analysis()
    demonstrate_vs_analysis()
    test_configuration_impact()
    
    print("\n🎯 EJEMPLO COMPLETO CON PICKS FINALES")
    print("=" * 60)
    run_corners_bot()

if __name__ == "__main__":
    main()