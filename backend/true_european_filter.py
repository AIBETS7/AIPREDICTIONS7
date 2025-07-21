#!/usr/bin/env python3
"""
True European Filter - Filtro Europeo Real
==========================================

Filtro ESTRICTO para SOLO competiciones y equipos europeos REALES.
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
    country = match.get('country', '').lower()
    
    # Verificar equipos no europeos
    for indicator in NON_EUROPEAN_INDICATORS:
        if (indicator in home_team or 
            indicator in away_team or 
            indicator in competition):
            return False
    
    # Competiciones UEFA (100% europeas)
    uefa_competitions = [
        'uefa champions league', 'champions league',
        'uefa europa league', 'europa league', 
        'uefa europa conference league', 'conference league'
    ]
    
    for uefa_comp in uefa_competitions:
        if uefa_comp in competition:
            return True
    
    # Ligas TOP europeas (con verificación adicional)
    european_leagues = {
        'la liga': ['spain', 'españa', 'spanish'],
        'premier league': ['england', 'english', 'inglaterra'],
        'bundesliga': ['germany', 'german', 'alemania'],
        'serie a': ['italy', 'italian', 'italia'],
        'ligue 1': ['france', 'french', 'francia'],
        'eredivisie': ['netherlands', 'dutch', 'holanda'],
        'primeira liga': ['portugal', 'portuguese']
    }
    
    for league, countries in european_leagues.items():
        if league in competition:
            # Verificar que no sea una liga homónima de otro continente
            if any(c in country for c in countries) or country == '':
                return True
    
    # Países europeos conocidos
    european_countries = [
        'spain', 'england', 'germany', 'italy', 'france', 
        'netherlands', 'portugal', 'belgium', 'switzerland',
        'austria', 'czech', 'poland', 'scotland', 'denmark',
        'sweden', 'norway', 'finland', 'greece', 'turkey',
        'croatia', 'serbia', 'ukraine', 'romania', 'bulgaria'
    ]
    
    if any(eu_country in country for eu_country in european_countries):
        return True
    
    return False

def get_real_european_matches_tomorrow():
    """Obtiene SOLO partidos europeos REALES de mañana"""
    
    from match_data_loader import get_matches_for_bots
    
    print('🇪🇺 FILTRO EUROPEO REAL - MAÑANA')
    print('=' * 50)
    
    # Cargar todos los partidos
    all_matches = get_matches_for_bots(competitions=None, with_referees=True)
    
    # Filtrar mañana
    tomorrow_matches = []
    for match in all_matches:
        if '2025-07-22' in match.get('match_time', ''):
            tomorrow_matches.append(match)
    
    print(f'📅 Total partidos mañana: {len(tomorrow_matches)}')
    
    # Filtrar SOLO europeos REALES
    real_european_matches = []
    excluded_matches = []
    
    for match in tomorrow_matches:
        if is_truly_european_match(match):
            real_european_matches.append(match)
        else:
            excluded_matches.append(match)
    
    print(f'🇪🇺 Partidos REALMENTE europeos: {len(real_european_matches)}')
    print(f'🚫 Partidos excluidos (no europeos): {len(excluded_matches)}')
    
    # Mostrar algunos excluidos para verificar
    print(f'\n🚫 EJEMPLOS DE PARTIDOS EXCLUIDOS:')
    for i, match in enumerate(excluded_matches[:10]):
        home = match.get('home_team', 'N/A')
        away = match.get('away_team', 'N/A')
        comp = match.get('competition', 'N/A')
        print(f'   {i+1}. {home} vs {away} ({comp})')
    
    # Mostrar partidos europeos reales
    if real_european_matches:
        print(f'\n✅ PARTIDOS EUROPEOS REALES:')
        competitions = {}
        for match in real_european_matches:
            comp = match.get('competition', 'N/A')
            competitions[comp] = competitions.get(comp, 0) + 1
        
        for comp, count in sorted(competitions.items(), key=lambda x: x[1], reverse=True):
            print(f'   🏆 {comp}: {count} partidos')
        
        print(f'\n⚽ EJEMPLOS DE PARTIDOS EUROPEOS:')
        for i, match in enumerate(real_european_matches[:10]):
            home = match.get('home_team', 'N/A')
            away = match.get('away_team', 'N/A')
            comp = match.get('competition', 'N/A')
            time = match.get('match_time', 'N/A')
            country = match.get('country', 'N/A')
            print(f'   {i+1}. {home} vs {away}')
            print(f'      🏆 {comp}')
            print(f'      🌍 {country}')
            print(f'      ⏰ {time}')
            print()
    else:
        print(f'\n❌ NO HAY PARTIDOS EUROPEOS REALES MAÑANA')
    
    return real_european_matches

if __name__ == "__main__":
    try:
        european_matches = get_real_european_matches_tomorrow()
        print(f'\n📊 RESULTADO FINAL:')
        print(f'🇪🇺 Partidos europeos reales encontrados: {len(european_matches)}')
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()