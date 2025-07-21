#!/usr/bin/env python3
"""
European Filter - Filtro para Solo Competiciones Europeas
=========================================================

Filtra y analiza ÚNICAMENTE ligas y campeonatos europeos.
"""

import sys
from typing import Dict, List

sys.path.append('.')

# Competiciones europeas permitidas
EUROPEAN_COMPETITIONS = {
    # Ligas principales
    'la_liga': ['La Liga', 'Primera División', 'Liga EA Sports'],
    'premier_league': ['Premier League', 'English Premier League'],
    'bundesliga': ['Bundesliga', '1. Bundesliga', 'German Bundesliga'],
    'serie_a': ['Serie A', 'Serie A TIM', 'Italian Serie A'],
    'ligue_1': ['Ligue 1', 'Ligue 1 Uber Eats', 'French Ligue 1'],
    
    # Ligas secundarias importantes
    'eredivisie': ['Eredivisie', 'Dutch Eredivisie'],
    'primeira_liga': ['Primeira Liga', 'Liga Portugal', 'Portuguese Liga'],
    'championship': ['Championship', 'English Championship', 'EFL Championship'],
    'serie_b': ['Serie B', 'Italian Serie B'],
    'segunda_division': ['Segunda División', 'LaLiga SmartBank'],
    
    # Competiciones UEFA
    'champions_league': ['UEFA Champions League', 'Champions League'],
    'europa_league': ['UEFA Europa League', 'Europa League'],
    'conference_league': ['UEFA Europa Conference League', 'Conference League'],
    'nations_league': ['UEFA Nations League', 'Nations League'],
    'euro': ['UEFA Euro', 'European Championship', 'Euro 2024'],
    
    # Copas nacionales principales
    'copa_del_rey': ['Copa del Rey', 'Spanish Cup'],
    'fa_cup': ['FA Cup', 'English FA Cup'],
    'dfb_pokal': ['DFB-Pokal', 'German Cup'],
    'coppa_italia': ['Coppa Italia', 'Italian Cup'],
    'coupe_de_france': ['Coupe de France', 'French Cup'],
    
    # Ligas menores europeas
    'scottish_premiership': ['Scottish Premiership', 'SPFL Premiership'],
    'belgian_pro_league': ['Belgian Pro League', 'Jupiler Pro League'],
    'swiss_super_league': ['Swiss Super League', 'Credit Suisse Super League'],
    'austrian_bundesliga': ['Austrian Bundesliga', 'Admiral Bundesliga'],
    'czech_liga': ['Czech First League', 'Fortuna Liga'],
    'polish_ekstraklasa': ['Ekstraklasa', 'Polish Ekstraklasa']
}

# Países europeos
EUROPEAN_COUNTRIES = {
    'spain', 'england', 'germany', 'italy', 'france', 'netherlands', 'portugal',
    'belgium', 'switzerland', 'austria', 'czech republic', 'poland', 'scotland',
    'denmark', 'sweden', 'norway', 'finland', 'greece', 'turkey', 'croatia',
    'serbia', 'ukraine', 'russia', 'romania', 'bulgaria', 'hungary', 'slovakia',
    'slovenia', 'bosnia', 'montenegro', 'albania', 'north macedonia', 'moldova',
    'estonia', 'latvia', 'lithuania', 'belarus', 'iceland', 'ireland', 'wales',
    'luxembourg', 'malta', 'cyprus', 'andorra', 'monaco', 'san marino', 'vatican'
}

def is_european_competition(competition: str, country: str = None) -> bool:
    """Verifica si una competición es europea"""
    
    if not competition:
        return False
    
    competition_lower = competition.lower().strip()
    
    # Verificar competiciones específicas
    for comp_key, comp_names in EUROPEAN_COMPETITIONS.items():
        for comp_name in comp_names:
            if comp_name.lower() in competition_lower:
                return True
    
    # Verificar por país si está disponible
    if country:
        country_lower = country.lower().strip()
        if country_lower in EUROPEAN_COUNTRIES:
            return True
    
    # Verificar palabras clave europeas
    european_keywords = [
        'uefa', 'european', 'euro', 'champions', 'europa', 'conference',
        'premier', 'bundesliga', 'serie', 'ligue', 'liga', 'eredivisie',
        'primeira', 'championship', 'division', 'cup', 'copa', 'pokal',
        'coppa', 'coupe', 'premiership', 'pro league', 'super league',
        'ekstraklasa', 'fortuna liga'
    ]
    
    for keyword in european_keywords:
        if keyword in competition_lower:
            return True
    
    return False

def filter_european_matches(matches: List[Dict]) -> List[Dict]:
    """Filtra solo partidos de competiciones europeas"""
    
    european_matches = []
    excluded_count = 0
    
    for match in matches:
        competition = match.get('competition', '')
        country = match.get('country', '')
        
        if is_european_competition(competition, country):
            european_matches.append(match)
        else:
            excluded_count += 1
            # Debug: mostrar algunos excluidos
            if excluded_count <= 5:
                print(f"🚫 Excluido (no europeo): {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')} ({competition})")
    
    print(f"🇪🇺 Partidos europeos: {len(european_matches)}")
    print(f"🌍 Partidos excluidos (no europeos): {excluded_count}")
    
    return european_matches

def get_european_competitions_summary(matches: List[Dict]) -> Dict[str, int]:
    """Obtiene resumen de competiciones europeas encontradas"""
    
    competitions_count = {}
    
    for match in matches:
        competition = match.get('competition', 'N/A')
        if competition in competitions_count:
            competitions_count[competition] += 1
        else:
            competitions_count[competition] = 1
    
    # Ordenar por cantidad
    sorted_competitions = dict(sorted(competitions_count.items(), key=lambda x: x[1], reverse=True))
    
    return sorted_competitions

def test_european_filter():
    """Prueba el filtro europeo con datos reales"""
    
    from match_data_loader import get_matches_for_bots
    
    print('🇪🇺 TESTING FILTRO EUROPEO')
    print('=' * 40)
    
    # Cargar todos los partidos
    all_matches = get_matches_for_bots(competitions=None, with_referees=True)
    print(f'📊 Total partidos cargados: {len(all_matches)}')
    
    # Filtrar solo europeos
    european_matches = filter_european_matches(all_matches)
    
    # Resumen de competiciones
    competitions = get_european_competitions_summary(european_matches)
    
    print(f'\n🏆 COMPETICIONES EUROPEAS ENCONTRADAS:')
    print('-' * 40)
    
    for comp, count in list(competitions.items())[:15]:  # Top 15
        print(f'   • {comp}: {count} partidos')
    
    if len(competitions) > 15:
        remaining = sum(list(competitions.values())[15:])
        print(f'   • ... y {len(competitions)-15} competiciones más ({remaining} partidos)')
    
    # Ejemplos de partidos europeos
    print(f'\n⚽ EJEMPLOS DE PARTIDOS EUROPEOS:')
    print('-' * 40)
    
    for i, match in enumerate(european_matches[:10]):
        print(f'   {i+1}. {match.get("home_team")} vs {match.get("away_team")}')
        print(f'      🏆 {match.get("competition")}')
        print(f'      🌍 {match.get("country", "N/A")}')
        print(f'      ⏰ {match.get("match_time", "N/A")}')
        print()
    
    return european_matches

if __name__ == "__main__":
    try:
        european_matches = test_european_filter()
        print(f'\n✅ Filtro europeo funcionando correctamente')
        print(f'🇪🇺 Total partidos europeos: {len(european_matches)}')
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()