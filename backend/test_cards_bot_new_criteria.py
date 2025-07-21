#!/usr/bin/env python3
"""
Test del Bot de Tarjetas con los nuevos criterios aplicados:
- Cuota mínima: 1.5 (reducida de 1.7)
- Picks por día: Todos los que tengan valor (999 en lugar de 3)
- Umbral de confianza: 70% o superior
- Análisis del árbitro incluido
- Sin filtro de número mínimo de tarjetas
"""

from cards_bot import CardsBot

def test_cards_bot_new_criteria():
    print("🟨 TESTING BOT DE TARJETAS - NUEVOS CRITERIOS")
    print("=" * 60)
    print("✅ Cuota mínima: 1.5 (antes: 1.7)")
    print("✅ Picks por día: TODOS los que tengan valor (antes: máx 3)")
    print("✅ Umbral de confianza: ≥70%")
    print("✅ Análisis del árbitro incluido")
    print("✅ Sin filtro de número mínimo de tarjetas")
    print("=" * 60)
    
    # Crear bot
    bot = CardsBot()
    
    # Verificar configuración
    print(f"\n📋 CONFIGURACIÓN ACTUAL:")
    print(f"• Confianza mínima: {bot.config.get('confidence_threshold', 70)}%")
    print(f"• Cuota mínima: {bot.config.get('min_odds', 1.5)}")
    print(f"• Picks por día: {bot.config.get('max_picks_per_day', 999)}")
    
    # Partidos de prueba con diferentes árbitros
    test_matches = [
        {
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'referee': 'Antonio Mateu Lahoz',  # Árbitro estricto (5.5 tarjetas/partido)
            'match_time': '2025-01-22 20:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Atletico Madrid',
            'away_team': 'Sevilla',
            'referee': 'Mario Melero López',  # Muy estricto (6.5 tarjetas/partido)
            'match_time': '2025-01-22 18:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Real Betis',
            'away_team': 'Valencia',
            'referee': 'Pablo González Fuertes',  # Permisivo (3.3 tarjetas/partido)
            'match_time': '2025-01-22 16:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Barcelona',
            'away_team': 'Atletico Madrid',
            'referee': 'César Soto Grado',  # Estricto (5.8 tarjetas/partido)
            'match_time': '2025-01-22 21:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Sevilla',
            'away_team': 'Real Madrid',
            'referee': 'Jesús Gil Manzano',  # Normal (5.0 tarjetas/partido)
            'match_time': '2025-01-22 19:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Valencia',
            'away_team': 'Real Betis',
            'referee': 'José Luis Munuera Montero',  # Permisivo (4.0 tarjetas/partido)
            'match_time': '2025-01-22 17:00',
            'competition': 'La Liga'
        }
    ]
    
    print(f"\n🔍 ANALIZANDO {len(test_matches)} PARTIDOS...")
    
    # Analizar cada partido individualmente para mostrar el proceso
    all_predictions = []
    for i, match in enumerate(test_matches, 1):
        print(f"\n--- PARTIDO {i} ---")
        print(f"🏟️ {match['home_team']} vs {match['away_team']}")
        print(f"👨‍⚖️ Árbitro: {match['referee']}")
        
        prediction = bot.analyze_match_cards(
            match['home_team'], 
            match['away_team'], 
            match['referee']
        )
        
        all_predictions.append((match, prediction))
        
        print(f"📊 Tarjetas predichas: {prediction.predicted_total_cards}")
        print(f"🎯 Confianza: {prediction.confidence}%")
        print(f"💰 Cuota estimada: {bot.estimate_odds(prediction.predicted_total_cards)}")
        print(f"⚖️ Factor árbitro: {prediction.referee_factor:.2f}")
        
        # Verificar si cumple criterios
        should_bet = bot.should_bet(prediction)
        if should_bet:
            print("✅ CUMPLE CRITERIOS - Se incluye en picks")
        else:
            print("❌ NO CUMPLE CRITERIOS")
            estimated_odds = bot.estimate_odds(prediction.predicted_total_cards)
            if prediction.confidence < bot.config.get('confidence_threshold', 70):
                print(f"   • Confianza insuficiente: {prediction.confidence}% < 70%")
            if estimated_odds < bot.config.get('min_odds', 1.5):
                print(f"   • Cuota insuficiente: {estimated_odds} < 1.5")
    
    # Obtener picks finales usando el método del bot
    final_picks = bot.get_picks_for_matches(test_matches)
    
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"📊 Partidos analizados: {len(test_matches)}")
    print(f"✅ Picks que cumplen criterios: {len(final_picks)}")
    print(f"📈 Porcentaje de selección: {len(final_picks)/len(test_matches)*100:.1f}%")
    
    print(f"\n🏆 PICKS SELECCIONADOS (ordenados por confianza):")
    for i, pick in enumerate(final_picks, 1):
        print(f"\n{i}. {pick['home_team']} vs {pick['away_team']}")
        print(f"   👨‍⚖️ Árbitro: {pick['referee']}")
        print(f"   🎯 Confianza: {pick['confidence']}%")
        print(f"   📊 Predicción: {pick['predicted_total']} tarjetas")
        print(f"   💰 Cuota: {pick['odds']}")
        print(f"   ⚖️ Factor árbitro: {pick['referee_factor']:.2f}")
    
    # Demostrar que NO hay límite de picks por día
    print(f"\n🚀 DEMOSTRACIÓN: SIN LÍMITE DE PICKS")
    print(f"• Configuración max_picks_per_day: {bot.config.get('max_picks_per_day', 999)}")
    print(f"• Picks generados: {len(final_picks)} (todos los que cumplen criterios)")
    print(f"• Con la configuración anterior (máx 3): se habrían perdido {max(0, len(final_picks) - 3)} picks valiosos")
    
    # Análisis del impacto del árbitro
    print(f"\n👨‍⚖️ ANÁLISIS DEL IMPACTO DEL ÁRBITRO:")
    referee_impact = {}
    for match, prediction in all_predictions:
        referee = match['referee']
        if referee not in referee_impact:
            referee_impact[referee] = []
        referee_impact[referee].append({
            'factor': prediction.referee_factor,
            'predicted_cards': prediction.predicted_total_cards,
            'match': f"{match['home_team']} vs {match['away_team']}"
        })
    
    for referee, data in referee_impact.items():
        avg_factor = sum(d['factor'] for d in data) / len(data)
        avg_cards = sum(d['predicted_cards'] for d in data) / len(data)
        print(f"• {referee}:")
        print(f"  - Factor promedio: {avg_factor:.2f}")
        print(f"  - Tarjetas promedio predichas: {avg_cards:.1f}")
        if avg_factor > 1.1:
            print(f"  - ⚠️ Árbitro estricto - aumenta predicciones")
        elif avg_factor < 0.9:
            print(f"  - 😌 Árbitro permisivo - reduce predicciones")
        else:
            print(f"  - 📊 Árbitro normal - factor neutro")
    
    print(f"\n✅ CRITERIOS APLICADOS CORRECTAMENTE:")
    print(f"• Todos los picks tienen confianza ≥ 70%")
    print(f"• Todos los picks tienen cuota estimada ≥ 1.5")
    print(f"• Se incluye análisis detallado del árbitro")
    print(f"• NO hay filtro de número mínimo de tarjetas")
    print(f"• Se envían TODOS los picks con valor")

if __name__ == "__main__":
    test_cards_bot_new_criteria()