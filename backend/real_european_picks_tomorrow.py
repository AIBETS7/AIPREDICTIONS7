#!/usr/bin/env python3
"""
Real European Picks Tomorrow - Picks Europeos Reales Mañana
===========================================================

Genera picks SOLO de partidos europeos REALES para mañana.
"""

import sys
from typing import Dict, List

sys.path.append('.')

# Equipos/ciudades claramente NO europeos (para excluir)
NON_EUROPEAN_INDICATORS = {
    # Ciudades asiáticas
    'qingdao', 'beijing', 'guangzhou', 'yunnan', 'shanghai', 'tianjin',
    'vietnam', 'cambodia', 'thailand', 'myanmar', 'malaysia', 'indonesia',
    'philippines', 'brunei', 'singapore', 'hong kong',
    
    # Ciudades africanas
    'motema pembe', 'don bosco', 'al hilal omdurman', 'al merreikh',
    'hay al wadi', 'alamal atbara', 'al-mergheni',
    
    # Ciudades americanas
    'operario-pr', 'atletico goianiense', 'atletico paranaense', 'ferroviária',
    'real tomayapo', 'nacional potosí', 'chacaritas', '22 de julio',
    
    # Palabras clave no europeas
    'u23', 'sudani', 'aff', 'conmebol', 'copa america', 'brasileirao',
    'liga pro', 'primera a', 'primera b', 'primera c'
}

def is_truly_european_match(match: Dict) -> bool:
    """Verifica si un partido es REALMENTE europeo"""
    
    home_team = match.get('home_team', '').lower()
    away_team = match.get('away_team', '').lower()
    competition = match.get('competition', '').lower()
    
    # Verificar equipos no europeos
    for indicator in NON_EUROPEAN_INDICATORS:
        if (indicator in home_team or 
            indicator in away_team or 
            indicator in competition):
            return False
    
    # Solo competiciones UEFA (100% europeas)
    uefa_competitions = [
        'uefa champions league', 'champions league',
        'uefa europa league', 'europa league', 
        'uefa europa conference league', 'conference league'
    ]
    
    for uefa_comp in uefa_competitions:
        if uefa_comp in competition:
            return True
    
    return False

def generate_real_european_picks():
    """Genera picks SOLO de partidos europeos REALES"""
    
    from match_data_loader import get_matches_for_bots
    from simple_statistics_bots import SimpleStatisticsBots
    
    print('🇪🇺 PICKS EUROPEOS REALES - MAÑANA')
    print('=' * 50)
    print('🎯 Solo UEFA Champions League y Conference League')
    print('📊 Estadística pura + Equipos europeos verificados')
    print('=' * 50)
    
    # Cargar partidos
    all_matches = get_matches_for_bots(competitions=None, with_referees=True)
    
    # Filtrar mañana + solo europeos REALES
    real_european_matches = []
    for match in all_matches:
        if ('2025-07-22' in match.get('match_time', '') and 
            is_truly_european_match(match)):
            real_european_matches.append(match)
    
    print(f'⚽ Partidos europeos REALES mañana: {len(real_european_matches)}')
    
    if not real_european_matches:
        print('❌ No hay partidos europeos reales mañana')
        return
    
    # Mostrar partidos encontrados
    print(f'\n✅ PARTIDOS EUROPEOS CONFIRMADOS:')
    competitions = {}
    for match in real_european_matches:
        comp = match.get('competition', 'N/A')
        competitions[comp] = competitions.get(comp, 0) + 1
    
    for comp, count in sorted(competitions.items(), key=lambda x: x[1], reverse=True):
        print(f'   🏆 {comp}: {count} partidos')
    
    # Inicializar bots
    simple_bots = SimpleStatisticsBots()
    
    # Analizar partidos
    all_picks = {
        'corners': [],
        'cards': [], 
        'btts': [],
        'draws': []
    }
    
    print(f'\n🔍 ANALIZANDO PARTIDOS EUROPEOS:')
    print('-' * 40)
    
    for i, match in enumerate(real_european_matches):
        home_team = match['home_team']
        away_team = match['away_team']
        competition = match.get('competition', 'N/A')
        match_time = match.get('match_time', 'N/A')
        referee = match.get('referee', 'N/A')
        
        print(f'{i+1}. {home_team} vs {away_team}')
        print(f'   🏆 {competition}')
        print(f'   ⏰ {match_time}')
        print(f'   👨‍⚖️ {referee}')
        
        # Análisis con bots simplificados
        corners_analysis = simple_bots.analyze_corners_simple(home_team, away_team)
        cards_analysis = simple_bots.analyze_cards_simple(home_team, away_team, referee)
        btts_analysis = simple_bots.analyze_btts_simple(home_team, away_team)
        draws_analysis = simple_bots.analyze_draws_with_formula(home_team, away_team)
        
        match_info = {
            'match': f"{home_team} vs {away_team}",
            'competition': competition,
            'time': match_time,
            'referee': referee
        }
        
        # Evaluar criterios
        corners_valid = corners_analysis['confidence'] >= 70
        cards_valid = cards_analysis['confidence'] >= 70
        btts_valid = btts_analysis['btts_probability'] >= 70
        draws_valid = draws_analysis['confidence'] >= 65
        
        print(f'   ⚽ Córners: {corners_analysis["total_corners_expected"]:.1f} ({corners_analysis["confidence"]:.0f}%) {"✅" if corners_valid else "❌"}')
        print(f'   🟨 Tarjetas: {cards_analysis["total_cards_expected"]:.1f} ({cards_analysis["confidence"]:.0f}%) {"✅" if cards_valid else "❌"}')
        print(f'   🎯 BTTS: {btts_analysis["btts_probability"]:.1f}% ({btts_analysis["confidence"]:.0f}%) {"✅" if btts_valid else "❌"}')
        print(f'   🤝 Empate: {draws_analysis["draw_probability"]:.1f}% ({draws_analysis["confidence"]:.0f}%) {"✅" if draws_valid else "❌"}')
        
        # Guardar picks válidos
        if corners_valid:
            all_picks['corners'].append({
                **match_info,
                'expected_corners': corners_analysis['total_corners_expected'],
                'confidence': corners_analysis['confidence'],
                'reasoning': corners_analysis['reasoning']
            })
        
        if cards_valid:
            all_picks['cards'].append({
                **match_info,
                'expected_cards': cards_analysis['total_cards_expected'],
                'confidence': cards_analysis['confidence'],
                'reasoning': cards_analysis['reasoning']
            })
        
        if btts_valid:
            all_picks['btts'].append({
                **match_info,
                'btts_probability': btts_analysis['btts_probability'],
                'confidence': btts_analysis['confidence'],
                'estimated_odds': btts_analysis['odds'],
                'reasoning': btts_analysis['reasoning']
            })
        
        if draws_valid:
            all_picks['draws'].append({
                **match_info,
                'draw_probability': draws_analysis['draw_probability'],
                'confidence': draws_analysis['confidence'],
                'estimated_odds': draws_analysis['odds'],
                'reasoning': draws_analysis['reasoning']
            })
        
        print()
    
    # RESUMEN DE PICKS
    print(f'📊 RESUMEN DE PICKS EUROPEOS:')
    print('=' * 40)
    print(f'⚽ Picks córners válidos: {len(all_picks["corners"])}')
    print(f'🟨 Picks tarjetas válidos: {len(all_picks["cards"])}')
    print(f'🎯 Picks BTTS válidos: {len(all_picks["btts"])}')
    print(f'🤝 Picks empates válidos: {len(all_picks["draws"])}')
    
    # TOP PICKS POR BOT
    print(f'\n🏆 TOP PICKS PARA TELEGRAM:')
    print('=' * 40)
    
    # Ordenar por confianza/probabilidad
    corners_sorted = sorted(all_picks['corners'], key=lambda x: x['confidence'], reverse=True)
    cards_sorted = sorted(all_picks['cards'], key=lambda x: x['confidence'], reverse=True)
    btts_sorted = sorted(all_picks['btts'], key=lambda x: x['btts_probability'], reverse=True)
    draws_sorted = sorted(all_picks['draws'], key=lambda x: x['draw_probability'], reverse=True)
    
    if corners_sorted:
        top_corner = corners_sorted[0]
        print(f'⚽ CÓRNERS: {top_corner["match"]}')
        print(f'   📊 {top_corner["expected_corners"]:.1f} córners ({top_corner["confidence"]:.0f}%)')
        print(f'   🏆 {top_corner["competition"]}')
        print(f'   ⏰ {top_corner["time"]}')
        print()
    
    if cards_sorted:
        top_cards = cards_sorted[0]
        print(f'🟨 TARJETAS: {top_cards["match"]}')
        print(f'   📊 {top_cards["expected_cards"]:.1f} tarjetas ({top_cards["confidence"]:.0f}%)')
        print(f'   🏆 {top_cards["competition"]}')
        print(f'   👨‍⚖️ {top_cards["referee"]}')
        print(f'   ⏰ {top_cards["time"]}')
        print()
    
    if btts_sorted:
        top_btts = btts_sorted[0]
        print(f'🎯 AMBOS MARCAN: {top_btts["match"]}')
        print(f'   📊 {top_btts["btts_probability"]:.1f}% probabilidad ({top_btts["confidence"]:.0f}%)')
        print(f'   🏆 {top_btts["competition"]}')
        print(f'   💰 Cuota: {top_btts["estimated_odds"]:.2f}')
        print(f'   ⏰ {top_btts["time"]}')
        print()
    
    if draws_sorted:
        top_draw = draws_sorted[0]
        print(f'🤝 EMPATE: {top_draw["match"]}')
        print(f'   📊 {top_draw["draw_probability"]:.1f}% probabilidad ({top_draw["confidence"]:.0f}%)')
        print(f'   🏆 {top_draw["competition"]}')
        print(f'   💰 Cuota: {top_draw["estimated_odds"]:.2f}')
        print(f'   ⏰ {top_draw["time"]}')
        print()
    
    # VERIFICACIÓN FINAL
    total_picks = sum(len(picks) for picks in all_picks.values())
    print(f'✅ VERIFICACIÓN FINAL:')
    print(f'🇪🇺 Solo partidos europeos REALES analizados')
    print(f'🏆 Solo UEFA Champions League y Conference League')
    print(f'📊 Total picks generados: {total_picks}')
    print(f'🚫 Equipos asiáticos/africanos/americanos excluidos')
    print(f'✅ Sistema corregido y funcionando')
    
    return all_picks

if __name__ == "__main__":
    try:
        real_picks = generate_real_european_picks()
        print(f'\n🎉 ¡Picks europeos REALES generados!')
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()