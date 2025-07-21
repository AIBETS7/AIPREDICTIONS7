#!/usr/bin/env python3
"""
Pronósticos de Mañana - Predicciones para el 22 de Julio
========================================================

Obtiene todos los pronósticos de cada bot para los partidos de mañana.
"""

import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.append('.')

def filter_tomorrow_matches(matches: List[Dict]) -> List[Dict]:
    """Filtra solo los partidos de mañana (22 de julio)"""
    tomorrow_matches = []
    tomorrow_date = "2025-07-22"
    
    for match in matches:
        match_time = match.get('match_time', '')
        if tomorrow_date in match_time:
            tomorrow_matches.append(match)
    
    return tomorrow_matches

def get_all_bot_predictions():
    """Obtiene pronósticos de todos los bots para mañana"""
    
    from corners_bot import CornersBot
    from cards_bot import CardsBot
    from draws_bot import DrawsBot
    from both_teams_score_bot import BothTeamsScoreBot
    from match_data_loader import get_matches_for_bots
    
    print('🔮 PRONÓSTICOS PARA MAÑANA (22 JULIO 2025)')
    print('=' * 60)
    
    # Cargar todos los partidos
    all_matches = get_matches_for_bots(competitions=None, with_referees=True)
    
    # Filtrar solo partidos de mañana
    tomorrow_matches = filter_tomorrow_matches(all_matches)
    
    print(f'📅 Partidos de mañana encontrados: {len(tomorrow_matches)}')
    
    if not tomorrow_matches:
        print('❌ No se encontraron partidos para mañana')
        return
    
    # Mostrar algunos partidos de ejemplo
    print(f'\n🎯 EJEMPLOS DE PARTIDOS DE MAÑANA:')
    for i, match in enumerate(tomorrow_matches[:5]):
        print(f'   {i+1}. {match.get("home_team")} vs {match.get("away_team")}')
        print(f'      🏆 {match.get("competition", "N/A")}')
        print(f'      ⏰ {match.get("match_time", "N/A")}')
    
    if len(tomorrow_matches) > 5:
        print(f'   ... y {len(tomorrow_matches) - 5} partidos más')
    
    # Obtener pronósticos de cada bot
    bots_predictions = {}
    
    # 1. BOT TARJETAS
    print(f'\n🟨 BOT TARJETAS - PRONÓSTICOS:')
    print('-' * 40)
    try:
        cards_bot = CardsBot()
        cards_picks = cards_bot.get_picks_for_matches(tomorrow_matches)
        
        if cards_picks:
            # Ordenar por confianza
            cards_picks.sort(key=lambda x: x['confidence'], reverse=True)
            
            print(f'📊 Total picks: {len(cards_picks)}')
            print(f'🏆 TOP 5 PICKS:')
            
            for i, pick in enumerate(cards_picks[:5]):
                print(f'   {i+1}. {pick["home_team"]} vs {pick["away_team"]}')
                print(f'      📈 Confianza: {pick["confidence"]}%')
                print(f'      🎯 Predicción: {pick["prediction"]}')
                print(f'      💰 Cuotas: {pick["odds"]:.2f}')
                print(f'      👨‍⚖️ Árbitro: {pick.get("referee", "N/A")}')
                print(f'      ⏰ Hora: {pick["match_time"]}')
                print()
            
            bots_predictions['tarjetas'] = cards_picks
        else:
            print('❌ Sin picks para mañana')
            bots_predictions['tarjetas'] = []
    except Exception as e:
        print(f'❌ Error: {e}')
        bots_predictions['tarjetas'] = []
    
    # 2. BOT CÓRNERS
    print(f'\n⚽ BOT CÓRNERS - PRONÓSTICOS:')
    print('-' * 40)
    try:
        corners_bot = CornersBot()
        corners_picks = corners_bot.get_picks_for_matches(tomorrow_matches)
        
        if corners_picks:
            corners_picks.sort(key=lambda x: x['confidence'], reverse=True)
            
            print(f'📊 Total picks: {len(corners_picks)}')
            print(f'🏆 TOP 5 PICKS:')
            
            for i, pick in enumerate(corners_picks[:5]):
                print(f'   {i+1}. {pick["home_team"]} vs {pick["away_team"]}')
                print(f'      📈 Confianza: {pick["confidence"]:.1f}%')
                print(f'      🎯 Predicción: {pick["prediction"]}')
                print(f'      💰 Cuotas: {pick["odds"]:.2f}')
                print(f'      ⏰ Hora: {pick["match_time"]}')
                print()
            
            bots_predictions['corneres'] = corners_picks
        else:
            print('❌ Sin picks para mañana')
            bots_predictions['corneres'] = []
    except Exception as e:
        print(f'❌ Error: {e}')
        bots_predictions['corneres'] = []
    
    # 3. BOT EMPATES
    print(f'\n🤝 BOT EMPATES - PRONÓSTICOS:')
    print('-' * 40)
    try:
        draws_bot = DrawsBot()
        draws_picks = draws_bot.get_picks_for_matches(tomorrow_matches)
        
        if draws_picks:
            draws_picks.sort(key=lambda x: x['confidence'], reverse=True)
            
            print(f'📊 Total picks: {len(draws_picks)}')
            print(f'🏆 TOP 5 PICKS:')
            
            for i, pick in enumerate(draws_picks[:5]):
                print(f'   {i+1}. {pick["home_team"]} vs {pick["away_team"]}')
                print(f'      📈 Confianza: {pick["confidence"]:.1f}%')
                print(f'      🎯 Probabilidad empate: {pick["draw_probability"]:.1f}%')
                print(f'      💰 Cuotas: {pick["odds"]:.2f}')
                print(f'      ⏰ Hora: {pick["match_time"]}')
                print()
            
            bots_predictions['empates'] = draws_picks
        else:
            print('❌ Sin picks para mañana')
            bots_predictions['empates'] = []
    except Exception as e:
        print(f'❌ Error: {e}')
        bots_predictions['empates'] = []
    
    # 4. BOT AMBOS MARCAN
    print(f'\n🎯 BOT AMBOS MARCAN - PRONÓSTICOS:')
    print('-' * 40)
    try:
        btts_bot = BothTeamsScoreBot()
        btts_picks = btts_bot.get_picks_for_matches(tomorrow_matches)
        
        if btts_picks:
            btts_picks.sort(key=lambda x: x['confidence'], reverse=True)
            
            print(f'📊 Total picks: {len(btts_picks)}')
            print(f'🏆 TOP 5 PICKS:')
            
            for i, pick in enumerate(btts_picks[:5]):
                print(f'   {i+1}. {pick["home_team"]} vs {pick["away_team"]}')
                print(f'      📈 Confianza: {pick["confidence"]:.1f}%')
                print(f'      🎯 Probabilidad BTTS: {pick["btts_probability"]:.1f}%')
                print(f'      💰 Cuotas: {pick["odds"]:.2f}')
                print(f'      ⏰ Hora: {pick["match_time"]}')
                print()
            
            bots_predictions['ambos_marcan'] = btts_picks
        else:
            print('❌ Sin picks para mañana')
            bots_predictions['ambos_marcan'] = []
    except Exception as e:
        print(f'❌ Error: {e}')
        bots_predictions['ambos_marcan'] = []
    
    # RESUMEN FINAL
    print(f'\n📊 RESUMEN DE PRONÓSTICOS PARA MAÑANA:')
    print('=' * 50)
    
    total_picks = 0
    for bot_name, picks in bots_predictions.items():
        count = len(picks)
        total_picks += count
        status = "✅" if count > 0 else "❌"
        print(f'{status} {bot_name.upper()}: {count} picks')
    
    print(f'\n🎯 TOTAL PICKS PARA MAÑANA: {total_picks}')
    
    if total_picks > 0:
        print(f'\n🏆 MEJORES PICKS DE CADA BOT:')
        for bot_name, picks in bots_predictions.items():
            if picks:
                best = picks[0]
                print(f'• {bot_name.upper()}: {best["home_team"]} vs {best["away_team"]} ({best["confidence"]:.1f}%)')
    
    return bots_predictions

if __name__ == "__main__":
    try:
        predictions = get_all_bot_predictions()
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()