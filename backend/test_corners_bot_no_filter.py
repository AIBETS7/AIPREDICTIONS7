#!/usr/bin/env python3
"""
Test del Bot de Córners SIN FILTRO de Córners Mínimos
- Solo confianza ≥ 70%
- Solo cuota ≥ 1.5
- TODOS los picks con valor
"""

from corners_bot import CornersBot

def test_no_corners_filter():
    """Prueba el bot sin filtro de córners mínimos"""
    print("🎯 BOT DE CÓRNERS - SIN FILTRO DE CÓRNERS MÍNIMOS")
    print("=" * 70)
    print("✅ Solo confianza ≥ 70%")
    print("✅ Solo cuota ≥ 1.5")
    print("✅ TODOS los picks con valor (sin importar número de córners)")
    print("✅ Sin límite diario")
    print("=" * 70)
    
    bot = CornersBot()
    
    # Verificar configuración
    print(f"\n📋 CONFIGURACIÓN ACTUAL:")
    print(f"• Cuota mínima: {bot.config.get('min_odds', 1.5)}")
    print(f"• Confianza mínima: {bot.config.get('confidence_threshold', 70)}%")
    print(f"• Filtro córners: ELIMINADO ❌")
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
    print("=" * 70)
    
    # Analizar cada partido individualmente
    valid_picks = []
    rejected_picks = []
    
    for i, match in enumerate(test_matches, 1):
        home = match['home_team']
        away = match['away_team']
        
        print(f"\n🏟️ PARTIDO #{i}: {home} vs {away}")
        print("-" * 50)
        
        prediction = bot.analyze_match_corners(home, away)
        estimated_odds = bot.estimate_odds(prediction.predicted_total_corners)
        
        print(f"Predicción: {prediction.predicted_total_corners} córners")
        print(f"Confianza: {prediction.confidence}%")
        print(f"Cuota estimada: {estimated_odds}")
        
        # Verificar solo los 2 criterios restantes
        confidence_ok = prediction.confidence >= bot.config.get('confidence_threshold', 70)
        odds_ok = estimated_odds >= bot.config.get('min_odds', 1.5)
        
        print(f"✓ Confianza (≥70%): {'✅' if confidence_ok else '❌'} {prediction.confidence}%")
        print(f"✓ Cuota (≥1.5): {'✅' if odds_ok else '❌'} {estimated_odds}")
        print(f"✓ Córners: ✅ {prediction.predicted_total_corners} (SIN FILTRO)")
        
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
                'reason': 'Confianza' if not confidence_ok else 'Cuota'
            })
    
    # Generar picks finales usando el método del bot
    final_picks = bot.get_picks_for_matches(test_matches)
    
    print(f"\n📊 RESUMEN FINAL")
    print("=" * 70)
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
    print("=" * 70)
    
    if final_picks:
        for i, pick in enumerate(final_picks, 1):
            print(f"\n--- PICK #{i} ---")
            print(f"🏟️ {pick['home_team']} vs {pick['away_team']}")
            print(f"📊 Predicción: {pick['prediction']}")
            print(f"🎯 {pick['confidence']}% confianza")
            print(f"💰 {pick['odds']} cuota estimada")
            print(f"⏰ {pick['match_time']} - {pick['competition']}")
    else:
        print("❌ No se generaron picks válidos con los criterios actuales")
    
    # Mostrar comparación con sistema anterior
    print(f"\n📈 COMPARACIÓN CON SISTEMA ANTERIOR:")
    print("=" * 70)
    print("🔴 ANTES (con filtro ≥9 córners):")
    old_valid = [p for p in valid_picks if p['corners'] >= 9]
    print(f"   • Picks válidos: {len(old_valid)}")
    
    print("🟢 AHORA (sin filtro de córners):")
    print(f"   • Picks válidos: {len(valid_picks)}")
    print(f"   • Diferencia: +{len(valid_picks) - len(old_valid)} picks adicionales")
    
    # Mostrar picks que antes se habrían rechazado por córners
    new_picks = [p for p in valid_picks if p['corners'] < 9]
    if new_picks:
        print(f"\n🆕 PICKS NUEVOS (antes rechazados por <9 córners):")
        for pick in new_picks:
            print(f"   • {pick['match']}: {pick['corners']} córners, {pick['confidence']}% conf, {pick['odds']} cuota")
    
    print(f"\n🎉 CONCLUSIÓN:")
    print("=" * 70)
    print("✅ El bot ahora envía TODOS los picks que cumplan:")
    print("   • ≥70% confianza")
    print("   • ≥1.5 cuota estimada")
    print("❌ Ya NO filtra por número de córners")
    print("✅ Más oportunidades de valor")
    print("✅ Sigue manteniendo calidad (confianza + cuota)")

if __name__ == "__main__":
    test_no_corners_filter()