#!/usr/bin/env python3
"""
Diversified European Picks - Picks Europeos Diversificados
==========================================================

Sistema que asegura que cada bot envíe un partido DIFERENTE para evitar duplicados.
"""

import sys
from typing import Dict, List, Set

sys.path.append('.')

# Equipos/ciudades claramente NO europeos (para excluir)
NON_EUROPEAN_INDICATORS = {
    'qingdao', 'beijing', 'guangzhou', 'yunnan', 'shanghai', 'tianjin',
    'vietnam', 'cambodia', 'thailand', 'myanmar', 'malaysia', 'indonesia',
    'philippines', 'brunei', 'singapore', 'hong kong',
    'motema pembe', 'don bosco', 'al hilal omdurman', 'al merreikh',
    'hay al wadi', 'alamal atbara', 'al-mergheni',
    'operario-pr', 'atletico goianiense', 'atletico paranaense', 'ferroviária',
    'real tomayapo', 'nacional potosí', 'chacaritas', '22 de julio',
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
    
    # Solo competiciones UEFA
    uefa_competitions = [
        'uefa champions league', 'champions league',
        'uefa europa league', 'europa league', 
        'uefa europa conference league', 'conference league'
    ]
    
    for uefa_comp in uefa_competitions:
        if uefa_comp in competition:
            return True
    
    return False

def add_match_diversity_factors(matches_analysis: List[Dict], bot_type: str) -> List[Dict]:
    """Añade factores de diversidad específicos por bot para evitar duplicados"""
    
    for analysis in matches_analysis:
        home = analysis['match'].split(' vs ')[0].lower()
        away = analysis['match'].split(' vs ')[1].lower()
        
        # Factor de diversidad por bot
        diversity_bonus = 0
        
        if bot_type == 'corners':
            # Preferir equipos ofensivos para córners
            offensive_teams = ['rangers', 'dynamo', 'copenhagen', 'malmo', 'lech', 'plzen']
            if any(team in home or team in away for team in offensive_teams):
                diversity_bonus = 5
        
        elif bot_type == 'cards':
            # Preferir partidos con rivalidades o equipos agresivos
            aggressive_teams = ['crvena zvezda', 'panathinaikos', 'ludogorets', 'rijeka']
            if any(team in home or team in away for team in aggressive_teams):
                diversity_bonus = 8
        
        elif bot_type == 'btts':
            # Preferir equipos con buen ataque
            attacking_teams = ['ferencvarosi', 'maccabi', 'noah', 'servette']
            if any(team in home or team in away for team in attacking_teams):
                diversity_bonus = 6
        
        elif bot_type == 'draws':
            # Preferir equipos equilibrados
            balanced_teams = ['shkendija', 'fcsb', 'ballkani', 'floriana']
            if any(team in home or team in away for team in balanced_teams):
                diversity_bonus = 7
        
        # Aplicar bonus de diversidad
        if bot_type == 'corners':
            analysis['confidence'] += diversity_bonus
        elif bot_type == 'cards':
            analysis['confidence'] += diversity_bonus
        elif bot_type == 'btts':
            analysis['btts_probability'] += diversity_bonus
        elif bot_type == 'draws':
            analysis['draw_probability'] += diversity_bonus
    
    return matches_analysis

def generate_diversified_picks():
    """Genera picks diversificados - cada bot un partido diferente"""
    
    from match_data_loader import get_matches_for_bots
    from simple_statistics_bots import SimpleStatisticsBots
    
    print('🇪🇺 PICKS EUROPEOS DIVERSIFICADOS - MAÑANA')
    print('=' * 55)
    print('🎯 Cada bot enviará un partido DIFERENTE')
    print('📊 Sistema anti-duplicados activado')
    print('=' * 55)
    
    # Cargar partidos europeos
    all_matches = get_matches_for_bots(competitions=None, with_referees=True)
    
    real_european_matches = []
    for match in all_matches:
        if ('2025-07-22' in match.get('match_time', '') and 
            is_truly_european_match(match)):
            real_european_matches.append(match)
    
    print(f'⚽ Partidos europeos disponibles: {len(real_european_matches)}')
    
    if len(real_european_matches) < 4:
        print('❌ No hay suficientes partidos europeos para diversificar')
        return
    
    # Inicializar bots
    simple_bots = SimpleStatisticsBots()
    
    # Analizar todos los partidos por bot
    bot_analyses = {
        'corners': [],
        'cards': [],
        'btts': [],
        'draws': []
    }
    
    print(f'\n🔍 ANALIZANDO {len(real_european_matches)} PARTIDOS EUROPEOS:')
    print('-' * 50)
    
    for match in real_european_matches:
        home_team = match['home_team']
        away_team = match['away_team']
        competition = match.get('competition', 'N/A')
        match_time = match.get('match_time', 'N/A')
        referee = match.get('referee', 'N/A')
        
        match_info = {
            'match': f"{home_team} vs {away_team}",
            'competition': competition,
            'time': match_time,
            'referee': referee
        }
        
        # Análisis por cada bot
        corners_analysis = simple_bots.analyze_corners_simple(home_team, away_team)
        cards_analysis = simple_bots.analyze_cards_simple(home_team, away_team, referee)
        btts_analysis = simple_bots.analyze_btts_simple(home_team, away_team)
        draws_analysis = simple_bots.analyze_draws_with_formula(home_team, away_team)
        
        # Guardar análisis si cumplen criterios básicos
        if corners_analysis['confidence'] >= 65:  # Bajamos un poco para tener más opciones
            bot_analyses['corners'].append({
                **match_info,
                'expected_corners': corners_analysis['total_corners_expected'],
                'confidence': corners_analysis['confidence'],
                'reasoning': corners_analysis['reasoning']
            })
        
        if cards_analysis['confidence'] >= 65:
            bot_analyses['cards'].append({
                **match_info,
                'expected_cards': cards_analysis['total_cards_expected'],
                'confidence': cards_analysis['confidence'],
                'reasoning': cards_analysis['reasoning']
            })
        
        if btts_analysis['btts_probability'] >= 65:  # Bajamos un poco
            bot_analyses['btts'].append({
                **match_info,
                'btts_probability': btts_analysis['btts_probability'],
                'confidence': btts_analysis['confidence'],
                'estimated_odds': btts_analysis['odds'],
                'reasoning': btts_analysis['reasoning']
            })
        
        if draws_analysis['confidence'] >= 60:  # Bajamos un poco
            bot_analyses['draws'].append({
                **match_info,
                'draw_probability': draws_analysis['draw_probability'],
                'confidence': draws_analysis['confidence'],
                'estimated_odds': draws_analysis['odds'],
                'reasoning': draws_analysis['reasoning']
            })
    
    print(f'📊 Candidatos por bot:')
    print(f'   ⚽ Córners: {len(bot_analyses["corners"])} candidatos')
    print(f'   🟨 Tarjetas: {len(bot_analyses["cards"])} candidatos')
    print(f'   🎯 BTTS: {len(bot_analyses["btts"])} candidatos')
    print(f'   🤝 Empates: {len(bot_analyses["draws"])} candidatos')
    
    # Aplicar factores de diversidad
    bot_analyses['corners'] = add_match_diversity_factors(bot_analyses['corners'], 'corners')
    bot_analyses['cards'] = add_match_diversity_factors(bot_analyses['cards'], 'cards')
    bot_analyses['btts'] = add_match_diversity_factors(bot_analyses['btts'], 'btts')
    bot_analyses['draws'] = add_match_diversity_factors(bot_analyses['draws'], 'draws')
    
    # Ordenar por métrica principal
    corners_sorted = sorted(bot_analyses['corners'], key=lambda x: x['confidence'], reverse=True)
    cards_sorted = sorted(bot_analyses['cards'], key=lambda x: x['confidence'], reverse=True)
    btts_sorted = sorted(bot_analyses['btts'], key=lambda x: x['btts_probability'], reverse=True)
    draws_sorted = sorted(bot_analyses['draws'], key=lambda x: x['draw_probability'], reverse=True)
    
    # SELECCIÓN DIVERSIFICADA - EVITAR DUPLICADOS
    selected_matches: Set[str] = set()
    final_picks = {}
    
    # 1. CÓRNERS - Primer pick
    if corners_sorted:
        for pick in corners_sorted:
            if pick['match'] not in selected_matches:
                final_picks['corners'] = pick
                selected_matches.add(pick['match'])
                break
    
    # 2. TARJETAS - Evitar el ya seleccionado
    if cards_sorted:
        for pick in cards_sorted:
            if pick['match'] not in selected_matches:
                final_picks['cards'] = pick
                selected_matches.add(pick['match'])
                break
    
    # 3. BTTS - Evitar los ya seleccionados
    if btts_sorted:
        for pick in btts_sorted:
            if pick['match'] not in selected_matches:
                final_picks['btts'] = pick
                selected_matches.add(pick['match'])
                break
    
    # 4. EMPATES - Evitar los ya seleccionados
    if draws_sorted:
        for pick in draws_sorted:
            if pick['match'] not in selected_matches:
                final_picks['draws'] = pick
                selected_matches.add(pick['match'])
                break
    
    # MOSTRAR PICKS FINALES DIVERSIFICADOS
    print(f'\n🎯 PICKS FINALES DIVERSIFICADOS:')
    print('=' * 50)
    
    if 'corners' in final_picks:
        pick = final_picks['corners']
        print(f'⚽ BOT CÓRNERS: {pick["match"]}')
        print(f'   📊 {pick["expected_corners"]:.1f} córners ({pick["confidence"]:.0f}%)')
        print(f'   🏆 {pick["competition"]}')
        print(f'   ⏰ {pick["time"]}')
        print()
    
    if 'cards' in final_picks:
        pick = final_picks['cards']
        print(f'🟨 BOT TARJETAS: {pick["match"]}')
        print(f'   📊 {pick["expected_cards"]:.1f} tarjetas ({pick["confidence"]:.0f}%)')
        print(f'   🏆 {pick["competition"]}')
        print(f'   👨‍⚖️ {pick["referee"]}')
        print(f'   ⏰ {pick["time"]}')
        print()
    
    if 'btts' in final_picks:
        pick = final_picks['btts']
        print(f'🎯 BOT AMBOS MARCAN: {pick["match"]}')
        print(f'   📊 {pick["btts_probability"]:.1f}% probabilidad ({pick["confidence"]:.0f}%)')
        print(f'   🏆 {pick["competition"]}')
        print(f'   💰 Cuota: {pick["estimated_odds"]:.2f}')
        print(f'   ⏰ {pick["time"]}')
        print()
    
    if 'draws' in final_picks:
        pick = final_picks['draws']
        print(f'🤝 BOT EMPATES: {pick["match"]}')
        print(f'   📊 {pick["draw_probability"]:.1f}% probabilidad ({pick["confidence"]:.0f}%)')
        print(f'   🏆 {pick["competition"]}')
        print(f'   💰 Cuota: {pick["estimated_odds"]:.2f}')
        print(f'   ⏰ {pick["time"]}')
        print()
    
    # VERIFICACIÓN ANTI-DUPLICADOS
    print(f'✅ VERIFICACIÓN ANTI-DUPLICADOS:')
    print(f'🎯 Partidos seleccionados: {len(selected_matches)}')
    print(f'📋 Lista de partidos únicos:')
    for i, match in enumerate(selected_matches, 1):
        print(f'   {i}. {match}')
    
    print(f'\n🎉 ¡CADA BOT TIENE UN PARTIDO DIFERENTE!')
    print(f'📱 Listos para enviar a Telegram sin duplicados')
    
    return final_picks

if __name__ == "__main__":
    try:
        diversified_picks = generate_diversified_picks()
        print(f'\n✅ ¡Sistema diversificado funcionando!')
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()