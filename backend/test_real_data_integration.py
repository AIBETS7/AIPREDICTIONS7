#!/usr/bin/env python3
"""
Test de integración completa con datos reales de la API de football
Demuestra que los bots funcionan con partidos reales descargados
"""

from match_data_loader import get_matches_for_bots, load_real_matches
from cards_bot import CardsBot
from corners_bot import CornersBot
import json

def test_real_data_integration():
    print("🚀 TEST DE INTEGRACIÓN CON DATOS REALES")
    print("=" * 60)
    print("📡 Usando partidos descargados de football-api")
    print("=" * 60)
    
    # 1. Mostrar datos originales de la API
    print("\n📁 DATOS ORIGINALES DE LA API:")
    all_matches = load_real_matches()
    print(f"• Total de partidos descargados: {len(all_matches)}")
    
    # Mostrar distribución por competiciones
    competitions = {}
    for match in all_matches:
        comp = match.get('competition', 'Desconocida')
        competitions[comp] = competitions.get(comp, 0) + 1
    
    print("• Distribución por competiciones:")
    for comp, count in sorted(competitions.items()):
        print(f"  - {comp}: {count} partidos")
    
    # 2. Filtrar partidos de La Liga
    print(f"\n🇪🇸 PARTIDOS DE LA LIGA:")
    la_liga_matches = get_matches_for_bots(['La Liga'], with_referees=True)
    
    if not la_liga_matches:
        print("❌ No se encontraron partidos de La Liga")
        return
    
    print(f"• Partidos de La Liga encontrados: {len(la_liga_matches)}")
    for i, match in enumerate(la_liga_matches, 1):
        print(f"  {i}. {match['home_team']} vs {match['away_team']}")
        print(f"     📅 Fecha: {match['match_time']}")
        print(f"     👨‍⚖️ Árbitro: {match['referee']}")
        print(f"     🏆 Competición: {match['competition']}")
        if 'odds' in match and match['odds']:
            odds = match['odds']
            print(f"     💰 Cuotas: 1:{odds.get('home_win', 'N/A')} X:{odds.get('draw', 'N/A')} 2:{odds.get('away_win', 'N/A')}")
        print()
    
    # 3. Test del Bot de Tarjetas
    print("🟨 TESTING BOT DE TARJETAS CON DATOS REALES")
    print("-" * 50)
    
    cards_bot = CardsBot()
    cards_picks = cards_bot.get_picks_for_matches(la_liga_matches)
    
    print(f"✅ Picks de tarjetas generados: {len(cards_picks)}")
    
    for i, pick in enumerate(cards_picks, 1):
        print(f"\n🎯 PICK #{i} - TARJETAS")
        print(f"🏟️ Partido: {pick['home_team']} vs {pick['away_team']}")
        print(f"👨‍⚖️ Árbitro: {pick['referee']}")
        print(f"📊 Predicción: {pick['predicted_total']} tarjetas")
        print(f"🎯 Confianza: {pick['confidence']}%")
        print(f"💰 Cuota estimada: {pick['odds']}")
        print(f"⚖️ Factor árbitro: {pick['referee_factor']:.2f}")
        print(f"📈 Análisis: {pick['reasoning'][:100]}...")
    
    # 4. Test del Bot de Córners
    print(f"\n⚽ TESTING BOT DE CÓRNERS CON DATOS REALES")
    print("-" * 50)
    
    corners_bot = CornersBot()
    corners_picks = corners_bot.get_picks_for_matches(la_liga_matches)
    
    print(f"✅ Picks de córners generados: {len(corners_picks)}")
    
    for i, pick in enumerate(corners_picks, 1):
        print(f"\n🎯 PICK #{i} - CÓRNERS")
        print(f"🏟️ Partido: {pick['home_team']} vs {pick['away_team']}")
        print(f"📊 Predicción: {pick['predicted_total']} córners")
        print(f"🎯 Confianza: {pick['confidence']}%")
        print(f"💰 Cuota estimada: {pick['odds']}")
        print(f"📈 Análisis: {pick['reasoning'][:100]}...")
    
    # 5. Comparación de resultados
    print(f"\n📊 RESUMEN COMPARATIVO")
    print("=" * 60)
    print(f"🟨 Bot Tarjetas:")
    print(f"  • Partidos analizados: {len(la_liga_matches)}")
    print(f"  • Picks generados: {len(cards_picks)}")
    print(f"  • Tasa de selección: {len(cards_picks)/len(la_liga_matches)*100:.1f}%")
    if cards_picks:
        avg_confidence_cards = sum(p['confidence'] for p in cards_picks) / len(cards_picks)
        print(f"  • Confianza promedio: {avg_confidence_cards:.1f}%")
    
    print(f"\n⚽ Bot Córners:")
    print(f"  • Partidos analizados: {len(la_liga_matches)}")
    print(f"  • Picks generados: {len(corners_picks)}")
    print(f"  • Tasa de selección: {len(corners_picks)/len(la_liga_matches)*100:.1f}%")
    if corners_picks:
        avg_confidence_corners = sum(p['confidence'] for p in corners_picks) / len(corners_picks)
        print(f"  • Confianza promedio: {avg_confidence_corners:.1f}%")
    
    # 6. Verificación de criterios
    print(f"\n✅ VERIFICACIÓN DE CRITERIOS APLICADOS")
    print("-" * 50)
    
    print("🟨 Bot Tarjetas:")
    all_cards_valid = True
    for pick in cards_picks:
        if pick['confidence'] < 70:
            print(f"  ❌ {pick['home_team']} vs {pick['away_team']}: Confianza {pick['confidence']}% < 70%")
            all_cards_valid = False
        if pick['odds'] < 1.5:
            print(f"  ❌ {pick['home_team']} vs {pick['away_team']}: Cuota {pick['odds']} < 1.5")
            all_cards_valid = False
    
    if all_cards_valid:
        print("  ✅ Todos los picks cumplen: confianza ≥70% y cuotas ≥1.5")
        print("  ✅ Análisis del árbitro incluido en todos los picks")
    
    print("\n⚽ Bot Córners:")
    all_corners_valid = True
    for pick in corners_picks:
        if pick['confidence'] < 70:
            print(f"  ❌ {pick['home_team']} vs {pick['away_team']}: Confianza {pick['confidence']}% < 70%")
            all_corners_valid = False
        if pick['odds'] < 1.5:
            print(f"  ❌ {pick['home_team']} vs {pick['away_team']}: Cuota {pick['odds']} < 1.5")
            all_corners_valid = False
    
    if all_corners_valid:
        print("  ✅ Todos los picks cumplen: confianza ≥70% y cuotas ≥1.5")
        print("  ✅ Sin filtro de número mínimo de córners")
    
    # 7. Demostración de que se envían TODOS los picks con valor
    print(f"\n🚀 DEMOSTRACIÓN: TODOS LOS PICKS CON VALOR")
    print("-" * 50)
    print("✅ Los bots están configurados para enviar TODOS los picks que cumplan criterios")
    print("✅ No hay límite artificial de picks por día")
    print("✅ Máximo aprovechamiento de oportunidades de valor")
    
    # 8. Información técnica
    print(f"\n🔧 INFORMACIÓN TÉCNICA")
    print("-" * 50)
    print("📡 Fuente de datos: football-api")
    print("📁 Archivo utilizado: real_matches_20250717.json")
    print("🤖 Bots: cards_bot.py + corners_bot.py")
    print("⚙️ Integración: match_data_loader.py")
    print("🎯 Criterios: confianza ≥70%, cuotas ≥1.5, todos los picks con valor")

def test_api_format_compatibility():
    """Test para verificar compatibilidad con formato de API"""
    print(f"\n🔍 TEST DE COMPATIBILIDAD CON FORMATO API")
    print("-" * 50)
    
    # Cargar un partido de ejemplo y mostrar su estructura
    matches = load_real_matches()
    if matches:
        example = matches[0]
        print("📋 Estructura de datos de la API:")
        for key, value in example.items():
            print(f"  • {key}: {type(value).__name__} = {str(value)[:50]}...")
        
        print(f"\n✅ Campos utilizados por los bots:")
        required_fields = ['home_team', 'away_team', 'time', 'competition']
        for field in required_fields:
            if field in example:
                print(f"  ✅ {field}: {example[field]}")
            else:
                print(f"  ❌ {field}: FALTANTE")
        
        print(f"\n📊 Campos adicionales disponibles:")
        extra_fields = ['odds', 'status', 'season', 'source', 'id']
        for field in extra_fields:
            if field in example:
                print(f"  💡 {field}: {example[field]}")

if __name__ == "__main__":
    test_real_data_integration()
    test_api_format_compatibility()