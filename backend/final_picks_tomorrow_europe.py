#!/usr/bin/env python3
"""
Final Picks Tomorrow Europe - Picks Finales Mañana Solo Europa
==============================================================

Genera los picks finales para mañana usando solo competiciones europeas
y estadística pura según las nuevas especificaciones.
"""

import sys
from typing import Dict, List, Tuple

sys.path.append('.')

def is_strictly_european_competition(competition: str) -> bool:
    """Verifica si es una competición ESTRICTAMENTE europea"""
    
    if not competition:
        return False
    
    comp_lower = competition.lower().strip()
    
    # Competiciones UEFA (100% europeas)
    uefa_competitions = [
        'uefa champions league', 'champions league',
        'uefa europa league', 'europa league', 
        'uefa europa conference league', 'conference league',
        'uefa nations league', 'nations league',
        'uefa euro', 'european championship'
    ]
    
    for uefa_comp in uefa_competitions:
        if uefa_comp in comp_lower:
            return True
    
    # Ligas TOP europeas principales
    top_european_leagues = [
        'la liga', 'primera división',  # España
        'premier league',  # Inglaterra
        'bundesliga', '1. bundesliga',  # Alemania
        'serie a',  # Italia
        'ligue 1',  # Francia
        'eredivisie',  # Holanda
        'primeira liga', 'liga portugal',  # Portugal
        'championship', 'efl championship',  # Inglaterra 2ª
        'serie b',  # Italia 2ª
        'segunda división',  # España 2ª
        'fa cup'  # Copa inglesa
    ]
    
    for league in top_european_leagues:
        if league in comp_lower:
            return True
    
    return False

def generate_final_picks_tomorrow():
    """Genera los picks finales para mañana solo Europa"""
    
    from match_data_loader import get_matches_for_bots
    from simple_statistics_bots import SimpleStatisticsBots
    
    print('🇪🇺 PICKS FINALES MAÑANA - SOLO EUROPA')
    print('=' * 60)
    print('📊 Sistema: Estadística pura + Competiciones europeas')
    print('🎯 Criterios: BTTS ≥70%, Empates ≥65%, Córners/Cards ≥70%')
    print('=' * 60)
    
    # Cargar partidos
    all_matches = get_matches_for_bots(competitions=None, with_referees=True)
    
    # Filtrar solo mañana (2025-07-22) y solo Europa
    tomorrow_european_matches = []
    for match in all_matches:
        if '2025-07-22' in match.get('match_time', ''):
            if is_strictly_european_competition(match.get('competition', '')):
                tomorrow_european_matches.append(match)
    
    print(f'⚽ Total partidos europeos mañana: {len(tomorrow_european_matches)}')
    
    if not tomorrow_european_matches:
        print('❌ No hay partidos europeos mañana')
        return
    
    # Inicializar bots
    simple_bots = SimpleStatisticsBots()
    
    # Analizar todos los partidos
    all_picks = {
        'corners': [],
        'cards': [], 
        'btts': [],
        'draws': []
    }
    
    for match in tomorrow_european_matches:
        home_team = match['home_team']
        away_team = match['away_team']
        competition = match.get('competition', 'N/A')
        match_time = match.get('match_time', 'N/A')
        referee = match.get('referee', 'N/A')
        
        # Análisis con bots simplificados
        corners_analysis = simple_bots.analyze_corners_simple(home_team, away_team)
        cards_analysis = simple_bots.analyze_cards_simple(home_team, away_team, referee)
        btts_analysis = simple_bots.analyze_btts_simple(home_team, away_team)
        draws_analysis = simple_bots.analyze_draws_with_formula(home_team, away_team)
        
        # Evaluar si cumplen criterios
        match_info = {
            'match': f"{home_team} vs {away_team}",
            'competition': competition,
            'time': match_time,
            'referee': referee
        }
        
        # CÓRNERS: ≥70% confianza
        if corners_analysis['confidence'] >= 70:
            all_picks['corners'].append({
                **match_info,
                'expected_corners': corners_analysis['total_corners_expected'],
                'confidence': corners_analysis['confidence'],
                'reasoning': corners_analysis['reasoning']
            })
        
        # TARJETAS: ≥70% confianza  
        if cards_analysis['confidence'] >= 70:
            all_picks['cards'].append({
                **match_info,
                'expected_cards': cards_analysis['total_cards_expected'],
                'confidence': cards_analysis['confidence'],
                'reasoning': cards_analysis['reasoning']
            })
        
        # BTTS: ≥70% probabilidad
        if btts_analysis['btts_probability'] >= 70:
            all_picks['btts'].append({
                **match_info,
                'btts_probability': btts_analysis['btts_probability'],
                'confidence': btts_analysis['confidence'],
                'estimated_odds': btts_analysis['odds'],
                'reasoning': btts_analysis['reasoning']
            })
        
        # EMPATES: ≥65% confianza
        if draws_analysis['confidence'] >= 65:
            all_picks['draws'].append({
                **match_info,
                'draw_probability': draws_analysis['draw_probability'],
                'confidence': draws_analysis['confidence'],
                'estimated_odds': draws_analysis['odds'],
                'reasoning': draws_analysis['reasoning']
            })
    
    # MOSTRAR PICKS POR BOT
    print(f'\n🎯 PICKS FINALES POR BOT:')
    print('=' * 50)
    
    # BOT CÓRNERS
    print(f'\n⚽ BOT CÓRNERS ({len(all_picks["corners"])} picks):')
    print('-' * 40)
    
    # Ordenar por confianza
    corners_sorted = sorted(all_picks['corners'], key=lambda x: x['confidence'], reverse=True)
    
    for i, pick in enumerate(corners_sorted[:5]):  # Top 5
        print(f'{i+1}. {pick["match"]}')
        print(f'   🏆 {pick["competition"]}')
        print(f'   ⏰ {pick["time"]}')
        print(f'   📊 {pick["expected_corners"]:.1f} córners esperados')
        print(f'   📈 Confianza: {pick["confidence"]:.0f}%')
        print(f'   💡 {pick["reasoning"]}')
        print()
    
    if len(corners_sorted) > 5:
        print(f'   ... y {len(corners_sorted) - 5} picks más de córners')
    
    # BOT TARJETAS
    print(f'\n🟨 BOT TARJETAS ({len(all_picks["cards"])} picks):')
    print('-' * 40)
    
    cards_sorted = sorted(all_picks['cards'], key=lambda x: x['confidence'], reverse=True)
    
    for i, pick in enumerate(cards_sorted[:5]):  # Top 5
        print(f'{i+1}. {pick["match"]}')
        print(f'   🏆 {pick["competition"]}')
        print(f'   ⏰ {pick["time"]}')
        print(f'   👨‍⚖️ {pick["referee"]}')
        print(f'   📊 {pick["expected_cards"]:.1f} tarjetas esperadas')
        print(f'   📈 Confianza: {pick["confidence"]:.0f}%')
        print(f'   💡 {pick["reasoning"]}')
        print()
    
    if len(cards_sorted) > 5:
        print(f'   ... y {len(cards_sorted) - 5} picks más de tarjetas')
    
    # BOT BTTS (AMBOS MARCAN)
    print(f'\n🎯 BOT AMBOS MARCAN ({len(all_picks["btts"])} picks):')
    print('-' * 40)
    
    btts_sorted = sorted(all_picks['btts'], key=lambda x: x['btts_probability'], reverse=True)
    
    for i, pick in enumerate(btts_sorted[:5]):  # Top 5
        print(f'{i+1}. {pick["match"]}')
        print(f'   🏆 {pick["competition"]}')
        print(f'   ⏰ {pick["time"]}')
        print(f'   🎯 Probabilidad BTTS: {pick["btts_probability"]:.1f}%')
        print(f'   📈 Confianza: {pick["confidence"]:.0f}%')
        print(f'   💰 Cuota estimada: {pick["estimated_odds"]:.2f}')
        print(f'   💡 {pick["reasoning"]}')
        print()
    
    if len(btts_sorted) > 5:
        print(f'   ... y {len(btts_sorted) - 5} picks más de BTTS')
    
    # BOT EMPATES
    print(f'\n🤝 BOT EMPATES ({len(all_picks["draws"])} picks):')
    print('-' * 40)
    
    draws_sorted = sorted(all_picks['draws'], key=lambda x: x['draw_probability'], reverse=True)
    
    for i, pick in enumerate(draws_sorted[:5]):  # Top 5
        print(f'{i+1}. {pick["match"]}')
        print(f'   🏆 {pick["competition"]}')
        print(f'   ⏰ {pick["time"]}')
        print(f'   🤝 Probabilidad empate: {pick["draw_probability"]:.1f}%')
        print(f'   📈 Confianza: {pick["confidence"]:.0f}%')
        print(f'   💰 Cuota estimada: {pick["estimated_odds"]:.2f}')
        print(f'   💡 {pick["reasoning"]}')
        print()
    
    if len(draws_sorted) > 5:
        print(f'   ... y {len(draws_sorted) - 5} picks más de empates')
    
    # PICKS TOP POR BOT (para Telegram)
    print(f'\n📱 TOP PICK POR BOT (PARA TELEGRAM):')
    print('=' * 50)
    
    if corners_sorted:
        top_corner = corners_sorted[0]
        print(f'⚽ CÓRNERS: {top_corner["match"]}')
        print(f'   📊 {top_corner["expected_corners"]:.1f} córners ({top_corner["confidence"]:.0f}%)')
        print(f'   🏆 {top_corner["competition"]}')
    
    if cards_sorted:
        top_cards = cards_sorted[0]
        print(f'🟨 TARJETAS: {top_cards["match"]}')
        print(f'   📊 {top_cards["expected_cards"]:.1f} tarjetas ({top_cards["confidence"]:.0f}%)')
        print(f'   🏆 {top_cards["competition"]}')
    
    if btts_sorted:
        top_btts = btts_sorted[0]
        print(f'🎯 AMBOS MARCAN: {top_btts["match"]}')
        print(f'   📊 {top_btts["btts_probability"]:.1f}% probabilidad ({top_btts["confidence"]:.0f}%)')
        print(f'   🏆 {top_btts["competition"]}')
        print(f'   💰 Cuota: {top_btts["estimated_odds"]:.2f}')
    
    if draws_sorted:
        top_draw = draws_sorted[0]
        print(f'🤝 EMPATE: {top_draw["match"]}')
        print(f'   📊 {top_draw["draw_probability"]:.1f}% probabilidad ({top_draw["confidence"]:.0f}%)')
        print(f'   🏆 {top_draw["competition"]}')
        print(f'   💰 Cuota: {top_draw["estimated_odds"]:.2f}')
    
    # RESUMEN FINAL
    total_picks = sum(len(picks) for picks in all_picks.values())
    print(f'\n📊 RESUMEN FINAL:')
    print('=' * 30)
    print(f'🇪🇺 Partidos europeos analizados: {len(tomorrow_european_matches)}')
    print(f'📈 Total picks generados: {total_picks}')
    print(f'⚽ Picks córners: {len(all_picks["corners"])}')
    print(f'🟨 Picks tarjetas: {len(all_picks["cards"])}')
    print(f'🎯 Picks BTTS: {len(all_picks["btts"])}')
    print(f'🤝 Picks empates: {len(all_picks["draws"])}')
    print(f'✅ Sistema: Estadística pura + Solo Europa')
    
    return all_picks

if __name__ == "__main__":
    try:
        final_picks = generate_final_picks_tomorrow()
        print(f'\n🎉 ¡Picks finales generados exitosamente!')
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()