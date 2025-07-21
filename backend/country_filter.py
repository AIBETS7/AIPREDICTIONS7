#!/usr/bin/env python3
"""
Country Filter - Filtro Permanente de Países
============================================

Sistema para filtrar países/ligas que no queremos analizar.
"""

# Países/ligas excluidos permanentemente
EXCLUDED_COUNTRIES = [
    'Russia',
    'Russian Federation', 
    'Belarus',
    # Agregar más países aquí si es necesario
]

EXCLUDED_LEAGUES = [
    'Premier League',  # Cuando sea de Rusia
    'FNL',  # Liga rusa
    'Russian Premier League',
    'Russian Football National League',
    'Russian Cup',
    'Belarusian Premier League',
    # Agregar más ligas aquí si es necesario
]

def is_match_allowed(match: dict) -> bool:
    """
    Verifica si un partido está permitido según nuestros filtros
    """
    country = match.get('country', '').strip()
    competition = match.get('competition', '').strip()
    
    # Filtrar por país
    if country in EXCLUDED_COUNTRIES:
        return False
    
    # Filtrar por liga específica + país
    if competition in EXCLUDED_LEAGUES and country in EXCLUDED_COUNTRIES:
        return False
    
    # Filtros específicos para Rusia
    if 'Russia' in country or 'Russian' in country:
        return False
    
    if 'Russia' in competition or 'Russian' in competition:
        return False
    
    return True

def filter_matches(matches: list) -> list:
    """
    Filtra una lista de partidos eliminando los no permitidos
    """
    filtered_matches = []
    excluded_count = 0
    
    for match in matches:
        if is_match_allowed(match):
            filtered_matches.append(match)
        else:
            excluded_count += 1
            country = match.get('country', 'N/A')
            competition = match.get('competition', 'N/A')
            home_team = match.get('home_team', 'N/A')
            away_team = match.get('away_team', 'N/A')
            print(f"🚫 Excluido: {home_team} vs {away_team} ({competition}, {country})")
    
    print(f"✅ Filtrados: {len(filtered_matches)} partidos permitidos")
    print(f"🚫 Excluidos: {excluded_count} partidos bloqueados")
    
    return filtered_matches

def get_excluded_summary(matches: list) -> dict:
    """
    Obtiene un resumen de partidos excluidos
    """
    excluded_countries = {}
    excluded_leagues = {}
    
    for match in matches:
        if not is_match_allowed(match):
            country = match.get('country', 'N/A')
            competition = match.get('competition', 'N/A')
            
            excluded_countries[country] = excluded_countries.get(country, 0) + 1
            excluded_leagues[competition] = excluded_leagues.get(competition, 0) + 1
    
    return {
        'countries': excluded_countries,
        'leagues': excluded_leagues
    }

if __name__ == "__main__":
    # Test del filtro
    test_matches = [
        {'country': 'Russia', 'competition': 'Premier League', 'home_team': 'CSKA Moscow', 'away_team': 'Spartak Moscow'},
        {'country': 'Spain', 'competition': 'La Liga', 'home_team': 'Real Madrid', 'away_team': 'Barcelona'},
        {'country': 'England', 'competition': 'Premier League', 'home_team': 'Arsenal', 'away_team': 'Chelsea'},
    ]
    
    print("🧪 TESTING FILTRO DE PAÍSES")
    print("=" * 40)
    
    filtered = filter_matches(test_matches)
    
    print(f"\nResultado: {len(filtered)}/{len(test_matches)} partidos permitidos")