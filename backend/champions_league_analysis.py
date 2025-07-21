#!/usr/bin/env python3
"""
Champions League Analysis - Análisis Exclusivo Champions League
==============================================================

Analiza SOLO los partidos de Champions League de mañana.
"""

import sys
import json
from typing import Dict, List

sys.path.append('.')

def filter_champions_league_tomorrow(matches: List[Dict]) -> List[Dict]:
    """Filtra SOLO partidos de Champions League de mañana"""
    champions_matches = []
    tomorrow_date = "2025-07-22"
    
    for match in matches:
        match_time = match.get('match_time', '')
        competition = match.get('competition', '').lower()
        
        # Filtrar Champions League de mañana
        if (tomorrow_date in match_time and 
            ('champions league' in competition or 
             'uefa champions league' in competition)):
            champions_matches.append(match)
    
    return champions_matches

def analyze_champions_league():
    """Análisis completo de Champions League para mañana"""
    
    from corners_bot import CornersBot
    from cards_bot import CardsBot
    from draws_bot import DrawsBot
    from both_teams_score_bot import BothTeamsScoreBot
    from match_data_loader import get_matches_for_bots
    
    print('🏆 ANÁLISIS EXCLUSIVO CHAMPIONS LEAGUE - MAÑANA')
    print('=' * 60)
    
    # Cargar todos los partidos
    all_matches = get_matches_for_bots(competitions=None, with_referees=True)
    
    # Filtrar SOLO Champions League de mañana
    champions_matches = filter_champions_league_tomorrow(all_matches)
    
    print(f'🏆 Partidos Champions League mañana: {len(champions_matches)}')
    
    if not champions_matches:
        print('❌ No se encontraron partidos de Champions League para mañana')
        return
    
    # Mostrar todos los partidos de Champions
    print(f'\n⚽ PARTIDOS CHAMPIONS LEAGUE (22 JULIO):')
    print('-' * 50)
    for i, match in enumerate(champions_matches):
        print(f'   {i+1}. {match.get("home_team")} vs {match.get("away_team")}')
        print(f'      🏆 {match.get("competition", "N/A")}')
        print(f'      ⏰ {match.get("match_time", "N/A")}')
        print(f'      👨‍⚖️ Árbitro: {match.get("referee", "N/A")}')
        print(f'      🏟️ Venue: {match.get("venue", "N/A")}')
        print()
    
    # Analizar con cada bot
    all_results = {}
    
    # 1. BOT TARJETAS
    print(f'\n🟨 BOT TARJETAS - CHAMPIONS LEAGUE:')
    print('-' * 40)
    try:
        cards_bot = CardsBot()
        cards_picks = cards_bot.get_picks_for_matches(champions_matches)
        
        if cards_picks:
            cards_picks.sort(key=lambda x: x['confidence'], reverse=True)
            print(f'📊 Picks Champions: {len(cards_picks)}')
            
            for i, pick in enumerate(cards_picks):
                print(f'   {i+1}. {pick["home_team"]} vs {pick["away_team"]}')
                print(f'      📈 Confianza: {pick["confidence"]}%')
                print(f'      🎯 Predicción: {pick["prediction"]}')
                print(f'      💰 Cuotas: {pick["odds"]:.2f}')
                print(f'      👨‍⚖️ Árbitro: {pick.get("referee", "N/A")}')
                print(f'      📝 Análisis: {pick["reasoning"][:100]}...')
                print()
            
            all_results['tarjetas'] = cards_picks
        else:
            print('❌ Sin picks Champions League')
            all_results['tarjetas'] = []
    except Exception as e:
        print(f'❌ Error: {e}')
        all_results['tarjetas'] = []
    
    # 2. BOT CÓRNERS
    print(f'\n⚽ BOT CÓRNERS - CHAMPIONS LEAGUE:')
    print('-' * 40)
    try:
        corners_bot = CornersBot()
        corners_picks = corners_bot.get_picks_for_matches(champions_matches)
        
        if corners_picks:
            corners_picks.sort(key=lambda x: x['confidence'], reverse=True)
            print(f'📊 Picks Champions: {len(corners_picks)}')
            
            for i, pick in enumerate(corners_picks):
                print(f'   {i+1}. {pick["home_team"]} vs {pick["away_team"]}')
                print(f'      📈 Confianza: {pick["confidence"]:.1f}%')
                print(f'      🎯 Predicción: {pick["prediction"]}')
                print(f'      💰 Cuotas: {pick["odds"]:.2f}')
                print(f'      📝 Análisis: {pick["reasoning"][:100]}...')
                print()
            
            all_results['corneres'] = corners_picks
        else:
            print('❌ Sin picks Champions League')
            all_results['corneres'] = []
    except Exception as e:
        print(f'❌ Error: {e}')
        all_results['corneres'] = []
    
    # 3. BOT EMPATES
    print(f'\n🤝 BOT EMPATES - CHAMPIONS LEAGUE:')
    print('-' * 40)
    try:
        draws_bot = DrawsBot()
        draws_picks = draws_bot.get_picks_for_matches(champions_matches)
        
        if draws_picks:
            draws_picks.sort(key=lambda x: x['confidence'], reverse=True)
            print(f'📊 Picks Champions: {len(draws_picks)}')
            
            for i, pick in enumerate(draws_picks):
                print(f'   {i+1}. {pick["home_team"]} vs {pick["away_team"]}')
                print(f'      📈 Confianza: {pick["confidence"]:.1f}%')
                print(f'      🎯 Probabilidad empate: {pick["draw_probability"]:.1f}%')
                print(f'      💰 Cuotas: {pick["odds"]:.2f}')
                print(f'      📝 Análisis: {pick["reasoning"][:100]}...')
                print()
            
            all_results['empates'] = draws_picks
        else:
            print('❌ Sin picks Champions League')
            all_results['empates'] = []
    except Exception as e:
        print(f'❌ Error: {e}')
        all_results['empates'] = []
    
    # 4. BOT AMBOS MARCAN
    print(f'\n🎯 BOT AMBOS MARCAN - CHAMPIONS LEAGUE:')
    print('-' * 40)
    try:
        btts_bot = BothTeamsScoreBot()
        btts_picks = btts_bot.get_picks_for_matches(champions_matches)
        
        if btts_picks:
            btts_picks.sort(key=lambda x: x['btts_probability'], reverse=True)
            print(f'📊 Picks Champions: {len(btts_picks)}')
            
            for i, pick in enumerate(btts_picks):
                print(f'   {i+1}. {pick["home_team"]} vs {pick["away_team"]}')
                print(f'      📈 Confianza: {pick["confidence"]:.1f}%')
                print(f'      🎯 Probabilidad BTTS: {pick["btts_probability"]:.1f}%')
                print(f'      💰 Cuotas: {pick["odds"]:.2f}')
                print(f'      📝 Análisis: {pick["reasoning"][:100]}...')
                print()
            
            all_results['ambos_marcan'] = btts_picks
        else:
            print('❌ Sin picks Champions League (Probabilidad BTTS < 70%)')
            all_results['ambos_marcan'] = []
    except Exception as e:
        print(f'❌ Error: {e}')
        all_results['ambos_marcan'] = []
    
    # RESUMEN CHAMPIONS LEAGUE
    print(f'\n🏆 RESUMEN CHAMPIONS LEAGUE - MAÑANA:')
    print('=' * 50)
    
    total_picks = 0
    for bot_name, picks in all_results.items():
        count = len(picks)
        total_picks += count
        status = "✅" if count > 0 else "❌"
        print(f'{status} {bot_name.upper()}: {count} picks Champions')
    
    print(f'\n🎯 TOTAL PICKS CHAMPIONS LEAGUE: {total_picks}')
    
    if total_picks > 0:
        print(f'\n🏆 MEJORES PICKS CHAMPIONS LEAGUE:')
        for bot_name, picks in all_results.items():
            if picks:
                best = picks[0]
                if bot_name == 'ambos_marcan':
                    prob_text = f"BTTS {best['btts_probability']:.1f}%"
                elif bot_name == 'empates':
                    prob_text = f"Empate {best['draw_probability']:.1f}%"
                else:
                    prob_text = best['prediction']
                
                print(f'• {bot_name.upper()}: {best["home_team"]} vs {best["away_team"]}')
                print(f'   📈 Confianza: {best["confidence"]:.1f}% | 🎯 {prob_text} | 💰 {best["odds"]:.2f}')
    else:
        print(f'\n⚠️ Ningún bot generó picks para Champions League mañana')
        print(f'💡 Posibles razones:')
        print(f'   • Criterios muy estrictos')
        print(f'   • Partidos de muy alto nivel (difíciles de predecir)')
        print(f'   • Datos insuficientes para equipos top')
    
    return all_results

if __name__ == "__main__":
    try:
        results = analyze_champions_league()
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()