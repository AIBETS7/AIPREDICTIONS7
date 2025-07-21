#!/usr/bin/env python3
"""
Test Simple Bots Champions - Testing Bots Simplificados en Champions League
===========================================================================

Prueba los nuevos bots basados en pura estadística con partidos de Champions League.
"""

import sys
import json
from typing import Dict, List

sys.path.append('.')

def test_simple_bots_on_champions():
    """Prueba los bots simplificados en partidos de Champions League"""
    
    from simple_statistics_bots import SimpleStatisticsBots
    from match_data_loader import get_matches_for_bots
    
    print('🏆 TESTING BOTS SIMPLIFICADOS - CHAMPIONS LEAGUE')
    print('=' * 60)
    
    # Inicializar bots simplificados
    simple_bots = SimpleStatisticsBots()
    
    # Obtener partidos de Champions League de mañana
    all_matches = get_matches_for_bots(competitions=None, with_referees=True)
    
    champions_matches = []
    for match in all_matches:
        if ('2025-07-22' in match.get('match_time', '') and 
            'champions league' in match.get('competition', '').lower()):
            champions_matches.append(match)
    
    print(f'🏆 Partidos Champions League encontrados: {len(champions_matches)}')
    
    if not champions_matches:
        print('❌ No se encontraron partidos de Champions League')
        return
    
    # Tomar algunos partidos únicos (eliminar duplicados)
    unique_matches = {}
    for match in champions_matches:
        key = f"{match['home_team']} vs {match['away_team']}"
        if key not in unique_matches:
            unique_matches[key] = match
    
    unique_matches_list = list(unique_matches.values())[:5]  # Primeros 5 únicos
    
    print(f'\n📊 ANÁLISIS CON BOTS SIMPLIFICADOS:')
    print('=' * 50)
    
    for i, match in enumerate(unique_matches_list):
        home_team = match['home_team']
        away_team = match['away_team']
        referee = match.get('referee', 'N/A')
        
        print(f'\n{i+1}. 🏟️ {home_team} vs {away_team}')
        print(f'   ⏰ {match.get("match_time", "N/A")}')
        print(f'   👨‍⚖️ {referee}')
        print('-' * 40)
        
        # Test Bot Córners Simplificado
        corners_result = simple_bots.analyze_corners_simple(home_team, away_team)
        print(f'⚽ CÓRNERS:')
        print(f'   📊 Total esperado: {corners_result["total_corners_expected"]:.1f}')
        print(f'   🏠 {home_team}: {corners_result["home_corners_expected"]:.1f}')
        print(f'   ✈️ {away_team}: {corners_result["away_corners_expected"]:.1f}')
        print(f'   📈 Confianza: {corners_result["confidence"]:.0f}%')
        print(f'   💰 Cuotas: {corners_result["odds"]:.2f}')
        
        # Test Bot Tarjetas Simplificado
        cards_result = simple_bots.analyze_cards_simple(home_team, away_team, referee)
        print(f'\n🟨 TARJETAS:')
        print(f'   📊 Total esperado: {cards_result["total_cards_expected"]:.1f}')
        print(f'   📈 Confianza: {cards_result["confidence"]:.0f}%')
        print(f'   💰 Cuotas: {cards_result["odds"]:.2f}')
        print(f'   👨‍⚖️ Factor árbitro aplicado')
        
        # Test Bot BTTS Simplificado
        btts_result = simple_bots.analyze_btts_simple(home_team, away_team)
        print(f'\n🎯 AMBOS MARCAN:')
        print(f'   📊 Probabilidad BTTS: {btts_result["btts_probability"]:.1f}%')
        print(f'   📈 Confianza: {btts_result["confidence"]:.0f}%')
        print(f'   💰 Cuotas: {btts_result["odds"]:.2f}')
        
        # Verificar si cumple criterio ≥70%
        if btts_result["btts_probability"] >= 70.0:
            print(f'   ✅ CUMPLE criterio ≥70%')
        else:
            print(f'   ❌ NO cumple criterio ≥70%')
        
        # Test Bot Empates con Fórmula
        draws_result = simple_bots.analyze_draws_with_formula(home_team, away_team)
        print(f'\n🤝 EMPATES (FÓRMULA):')
        print(f'   📊 Probabilidad: {draws_result["draw_probability"]:.1f}%')
        print(f'   📈 Confianza: {draws_result["confidence"]:.0f}% (REDUCIDA)')
        print(f'   💰 Cuotas: {draws_result["odds"]:.2f}')
        print(f'   📐 P_media: {draws_result["p_media"]:.3f}')
        print(f'   📐 n_sin_empate: {draws_result["n_sin_empate"]}')
        print(f'   📐 α: {draws_result["alpha"]}')
    
    # RESUMEN COMPARATIVO
    print(f'\n📊 RESUMEN COMPARATIVO - BOTS SIMPLIFICADOS:')
    print('=' * 60)
    
    print(f'✅ VENTAJAS:')
    print(f'   • Basados en pura estadística histórica')
    print(f'   • Sin algoritmos complejos innecesarios')
    print(f'   • Fórmula matemática específica para empates')
    print(f'   • Criterios claros y transparentes')
    print(f'   • Confianza reducida en empates (75% → 65%)')
    
    print(f'\n🎯 CRITERIOS APLICADOS:')
    print(f'   • Córners: Media histórica directa')
    print(f'   • Tarjetas: Media + factor árbitro mínimo')
    print(f'   • BTTS: Solo si probabilidad ≥70%')
    print(f'   • Empates: Fórmula P_ajustada = P_media × (1 + α × n_sin_empate/N)')
    
    print(f'\n💡 EJEMPLO REAL:')
    print(f'   Si Real Madrid (6.2 córners/partido) vs Barcelona (7.1 córners/partido)')
    print(f'   → Total esperado: 13.3 córners')
    print(f'   → Sin algoritmos complejos, solo suma de medias')

if __name__ == "__main__":
    try:
        test_simple_bots_on_champions()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()