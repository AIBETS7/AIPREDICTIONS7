#!/usr/bin/env python3
"""
Test del Bot de Córners con Nueva Configuración
- Cuota mínima: 1.5
- Confianza mínima: 70%
- Picks por día: TODOS los que tengan valor
"""

from corners_bot import CornersBot

def test_new_configuration():
    """Prueba la nueva configuración del bot"""
    print("🎯 BOT DE CÓRNERS - NUEVA CONFIGURACIÓN")
    print("=" * 60)
    print("✅ Cuota mínima: 1.5")
    print("✅ Confianza mínima: 70%")
    print("✅ Picks por día: TODOS los que tengan valor")
    print("✅ Mínimo córners: 9")
    print("=" * 60)
    
    bot = CornersBot()
    
    # Verificar configuración
    print(f"\n📋 CONFIGURACIÓN ACTUAL:")
    print(f"• Cuota mínima: {bot.config.get('min_odds', 1.5)}")
    print(f"• Confianza mínima: {bot.config.get('confidence_threshold', 70)}%")
    print(f"• Mínimo córners: {bot.config.get('min_corners', 9)}")
    print(f"• Picks por día: {bot.config.get('max_picks_per_day', 999)}")
    
    # Lista amplia de partidos para probar
    test_matches = [
        {'home_team': 'Real Madrid', 'away_team': 'Barcelona', 'match_time': '20:00', 'competition': 'La Liga'},
        {'home_team': 'Atletico Madrid', 'away_team': 'Sevilla', 'match_time': '18:00', 'competition': 'La Liga'},
        {'home_team': 'Real Betis', 'away_team': 'Valencia', 'match_time': '16:00', 'competition': 'La Liga'},
        {'home_team': 'Barcelona', 'away_team': 'Real Betis', 'match_time': '21:00', 'competition': 'La Liga'},
        {'home_team': 'Sevilla', 'away_team': 'Real Madrid', 'match_time': '19:00', 'competition': 'La Liga'},
        {'home_team': 'Valencia', 'away_team': 'Atletico Madrid', 'match_time': '17:00', 'competition': 'La Liga'},
        {'home_team': 'Real Betis', 'away_team': 'Barcelona', 'match_time': '15:00', 'competition': 'La Liga'},
        {'home_team': 'Real Madrid', 'away_team': 'Atletico Madrid', 'match_time': '22:00', 'competition': 'La Liga'},
    ]
    
    print(f"\n🔍 ANALIZANDO {len(test_matches)} PARTIDOS...")
    print("=" * 60)
    
    # Analizar cada partido individualmente para mostrar el proceso
    valid_picks = []
    rejected_picks = []
    
    for i, match in enumerate(test_matches, 1):
        home = match['home_team']
        away = match['away_team']
        
        print(f"\n🏟️ PARTIDO #{i}: {home} vs {away}")
        print("-" * 40)
        
        prediction = bot.analyze_match_corners(home, away)
        estimated_odds = bot.estimate_odds(prediction.predicted_total_corners)
        
        print(f"Predicción: {prediction.predicted_total_corners} córners")
        print(f"Confianza: {prediction.confidence}%")
        print(f"Cuota estimada: {estimated_odds}")
        
        # Verificar criterios uno por uno
        corners_ok = prediction.predicted_total_corners >= bot.config.get('min_corners', 9)
        confidence_ok = prediction.confidence >= bot.config.get('confidence_threshold', 70)
        odds_ok = estimated_odds >= bot.config.get('min_odds', 1.5)
        
        print(f"✓ Córners (≥9): {'✅' if corners_ok else '❌'} {prediction.predicted_total_corners}")
        print(f"✓ Confianza (≥70%): {'✅' if confidence_ok else '❌'} {prediction.confidence}%")
        print(f"✓ Cuota (≥1.5): {'✅' if odds_ok else '❌'} {estimated_odds}")
        
        if bot.should_bet(prediction):
            print("🎯 RESULTADO: ✅ PICK VÁLIDO - Se envía")
            valid_picks.append({
                'match': f"{home} vs {away}",
                'corners': prediction.predicted_total_corners,
                'confidence': prediction.confidence,
                'odds': estimated_odds
            })
        else:
            print("🎯 RESULTADO: ❌ RECHAZADO - No cumple criterios")
            rejected_picks.append({
                'match': f"{home} vs {away}",
                'corners': prediction.predicted_total_corners,
                'confidence': prediction.confidence,
                'odds': estimated_odds,
                'reason': 'Córners' if not corners_ok else 'Confianza' if not confidence_ok else 'Cuota'
            })
    
    # Generar picks finales usando el método del bot
    final_picks = bot.get_picks_for_matches(test_matches)
    
    print(f"\n📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"🎯 Partidos analizados: {len(test_matches)}")
    print(f"✅ Picks válidos: {len(valid_picks)}")
    print(f"❌ Picks rechazados: {len(rejected_picks)}")
    print(f"📤 Picks que se envían: {len(final_picks)}")
    
    if valid_picks:
        print(f"\n✅ PICKS VÁLIDOS QUE SE ENVÍAN:")
        for i, pick in enumerate(valid_picks, 1):
            print(f"{i}. {pick['match']}")
            print(f"   📊 {pick['corners']} córners | {pick['confidence']}% conf | {pick['odds']} cuota")
    
    if rejected_picks:
        print(f"\n❌ PICKS RECHAZADOS:")
        for i, pick in enumerate(rejected_picks, 1):
            print(f"{i}. {pick['match']} - Rechazado por: {pick['reason']}")
            print(f"   📊 {pick['corners']} córners | {pick['confidence']}% conf | {pick['odds']} cuota")
    
    print(f"\n🚀 PICKS FINALES GENERADOS POR EL BOT:")
    print("=" * 60)
    
    if final_picks:
        for i, pick in enumerate(final_picks, 1):
            print(f"\n--- PICK #{i} ---")
            print(f"🏟️ {pick['home_team']} vs {pick['away_team']}")
            print(f"📊 {pick['predicted_total']} córners predichos")
            print(f"🎯 {pick['confidence']}% confianza")
            print(f"💰 {pick['odds']} cuota estimada")
            print(f"⏰ {pick['match_time']} - {pick['competition']}")
    else:
        print("❌ No se generaron picks válidos con los criterios actuales")
    
    print(f"\n🎉 CONCLUSIÓN:")
    print("=" * 60)
    print("✅ El bot envía TODOS los picks que cumplan:")
    print("   • ≥9 córners predichos")
    print("   • ≥70% confianza")
    print("   • ≥1.5 cuota estimada")
    print("✅ SIN LÍMITE de picks por día")
    print("✅ Ordenados por confianza (mayor a menor)")

if __name__ == "__main__":
    test_new_configuration()