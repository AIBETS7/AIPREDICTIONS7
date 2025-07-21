#!/usr/bin/env python3
"""
Debug Bot Picks - Diagnóstico de Selección de Partidos
======================================================

Analiza por qué los bots están eligiendo los mismos partidos.
"""

import sys
import json
from typing import Dict, List
from collections import defaultdict

sys.path.append('.')

def analyze_bot_picks():
    """Analiza los picks de cada bot en detalle"""
    
    from corners_bot import CornersBot
    from draws_bot import DrawsBot  
    from both_teams_score_bot import BothTeamsScoreBot
    from match_data_loader import get_matches_for_bots
    
    print('🔍 DIAGNÓSTICO DETALLADO DE PICKS')
    print('=' * 60)
    
    # Cargar partidos
    matches = get_matches_for_bots(competitions=None, with_referees=True)
    print(f'📊 Total partidos disponibles: {len(matches)}')
    
    # Analizar cada bot
    bots_data = []
    
    # 1. CORNERS BOT
    print('\n⚽ ANÁLISIS CORNERS BOT:')
    corners_bot = CornersBot()
    corners_picks = corners_bot.get_picks_for_matches(matches)
    
    print(f'   📈 Total picks generados: {len(corners_picks)}')
    print(f'   🎯 Config: min_odds={corners_bot.config.get("min_odds", "N/A")}, confidence_threshold={corners_bot.config.get("confidence_threshold", "N/A")}')
    
    if corners_picks:
        # Top 5 picks
        sorted_corners = sorted(corners_picks, key=lambda x: x['confidence'], reverse=True)
        print(f'   🏆 TOP 5 PICKS:')
        for i, pick in enumerate(sorted_corners[:5]):
            print(f'      {i+1}. {pick["home_team"]} vs {pick["away_team"]} - {pick["confidence"]}% (odds: {pick["odds"]})')
        
        bots_data.append(('Corners', sorted_corners))
    
    # 2. DRAWS BOT
    print('\n🤝 ANÁLISIS DRAWS BOT:')
    draws_bot = DrawsBot()
    draws_picks = draws_bot.get_picks_for_matches(matches)
    
    print(f'   📈 Total picks generados: {len(draws_picks)}')
    print(f'   🎯 Config: min_odds={draws_bot.config.get("min_odds", "N/A")}, confidence_threshold={draws_bot.config.get("confidence_threshold", "N/A")}')
    
    if draws_picks:
        # Top 5 picks
        sorted_draws = sorted(draws_picks, key=lambda x: x['confidence'], reverse=True)
        print(f'   🏆 TOP 5 PICKS:')
        for i, pick in enumerate(sorted_draws[:5]):
            print(f'      {i+1}. {pick["home_team"]} vs {pick["away_team"]} - {pick["confidence"]}% (odds: {pick["odds"]})')
        
        bots_data.append(('Draws', sorted_draws))
    
    # 3. BTTS BOT
    print('\n🎯 ANÁLISIS BTTS BOT:')
    btts_bot = BothTeamsScoreBot()
    btts_picks = btts_bot.get_picks_for_matches(matches)
    
    print(f'   📈 Total picks generados: {len(btts_picks)}')
    print(f'   🎯 Config: min_odds={btts_bot.config.get("min_odds", "N/A")}, confidence_threshold={btts_bot.config.get("confidence_threshold", "N/A")}')
    
    if btts_picks:
        # Top 5 picks
        sorted_btts = sorted(btts_picks, key=lambda x: x['confidence'], reverse=True)
        print(f'   🏆 TOP 5 PICKS:')
        for i, pick in enumerate(sorted_btts[:5]):
            print(f'      {i+1}. {pick["home_team"]} vs {pick["away_team"]} - {pick["confidence"]}% (odds: {pick["odds"]})')
        
        bots_data.append(('BTTS', sorted_btts))
    
    # ANÁLISIS DE COINCIDENCIAS
    print('\n🔍 ANÁLISIS DE COINCIDENCIAS:')
    print('=' * 40)
    
    # Contar qué partidos aparecen en múltiples bots
    match_counter = defaultdict(list)
    
    for bot_name, picks in bots_data:
        if picks:
            best_pick = picks[0]  # El mejor pick de cada bot
            match_key = f"{best_pick['home_team']} vs {best_pick['away_team']}"
            match_counter[match_key].append((bot_name, best_pick['confidence']))
    
    print('🎯 MEJORES PICKS POR BOT:')
    for match, bot_data in match_counter.items():
        print(f'   📍 {match}:')
        for bot_name, confidence in bot_data:
            print(f'      • {bot_name}: {confidence}%')
    
    # Verificar si hay diversidad en los datos
    print('\n📊 ANÁLISIS DE DIVERSIDAD:')
    
    # Verificar si todos los partidos tienen datos similares
    sample_matches = matches[:10]  # Primeros 10 partidos
    print(f'🔬 MUESTRA DE PARTIDOS (primeros 10):')
    
    for i, match in enumerate(sample_matches):
        print(f'   {i+1}. {match.get("home_team", "N/A")} vs {match.get("away_team", "N/A")}')
        print(f'      • Competición: {match.get("competition", "N/A")}')
        print(f'      • País: {match.get("country", "N/A")}')
        print(f'      • Hora: {match.get("match_time", "N/A")}')
    
    # Verificar si hay sesgos en los algoritmos
    print('\n⚠️ POSIBLES PROBLEMAS:')
    
    coincidences = len([match for match, bots in match_counter.items() if len(bots) > 1])
    total_bots = len(bots_data)
    
    if coincidences > 0:
        print(f'   🚨 {coincidences} partidos elegidos por múltiples bots')
        print(f'   💡 Posibles causas:')
        print(f'      • Algoritmos demasiado similares')
        print(f'      • Datos de entrada idénticos')
        print(f'      • Criterios de selección muy restrictivos')
        print(f'      • Falta de diversidad en factores de análisis')
    else:
        print(f'   ✅ Cada bot eligió partidos diferentes')
    
    return bots_data, match_counter

if __name__ == "__main__":
    try:
        analyze_bot_picks()
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()