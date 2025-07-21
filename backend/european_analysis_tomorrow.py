#!/usr/bin/env python3
"""
European Analysis Tomorrow - Análisis Solo Competiciones Europeas Mañana
========================================================================

Análisis estricto de SOLO competiciones europeas reales para mañana.
"""

import sys
from typing import Dict, List

sys.path.append('.')

def is_strictly_european_competition(competition: str, country: str = None) -> bool:
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
        'segunda división'  # España 2ª
    ]
    
    for league in top_european_leagues:
        if league in comp_lower:
            return True
    
    # Copas nacionales principales europeas
    european_cups = [
        'copa del rey',  # España
        'fa cup',  # Inglaterra
        'dfb-pokal',  # Alemania
        'coppa italia',  # Italia
        'coupe de france'  # Francia
    ]
    
    for cup in european_cups:
        if cup in comp_lower:
            return True
    
    return False

def get_european_matches_tomorrow():
    """Obtiene solo partidos europeos de mañana"""
    
    from match_data_loader import get_matches_for_bots
    
    print('🇪🇺 ANÁLISIS SOLO COMPETICIONES EUROPEAS - MAÑANA')
    print('=' * 60)
    
    # Cargar todos los partidos
    all_matches = get_matches_for_bots(competitions=None, with_referees=True)
    
    # Filtrar partidos de mañana
    tomorrow_matches = []
    for match in all_matches:
        if '2025-07-22' in match.get('match_time', ''):
            tomorrow_matches.append(match)
    
    print(f'📅 Total partidos mañana: {len(tomorrow_matches)}')
    
    # Filtrar solo competiciones europeas estrictas
    european_tomorrow = []
    excluded_competitions = set()
    
    for match in tomorrow_matches:
        competition = match.get('competition', '')
        country = match.get('country', '')
        
        if is_strictly_european_competition(competition, country):
            european_tomorrow.append(match)
        else:
            excluded_competitions.add(competition)
    
    print(f'🇪🇺 Partidos europeos mañana: {len(european_tomorrow)}')
    print(f'🌍 Competiciones excluidas: {len(excluded_competitions)}')
    
    # Mostrar competiciones excluidas
    if excluded_competitions:
        print(f'\n🚫 COMPETICIONES NO EUROPEAS EXCLUIDAS:')
        for comp in sorted(excluded_competitions):
            print(f'   • {comp}')
    
    # Resumen de competiciones europeas
    european_competitions = {}
    for match in european_tomorrow:
        comp = match.get('competition', 'N/A')
        european_competitions[comp] = european_competitions.get(comp, 0) + 1
    
    print(f'\n🏆 COMPETICIONES EUROPEAS MAÑANA:')
    print('-' * 40)
    for comp, count in sorted(european_competitions.items(), key=lambda x: x[1], reverse=True):
        print(f'   • {comp}: {count} partidos')
    
    return european_tomorrow

def analyze_european_matches_with_simple_bots():
    """Analiza partidos europeos con bots simplificados"""
    
    from simple_statistics_bots import SimpleStatisticsBots
    
    # Obtener partidos europeos de mañana
    european_matches = get_european_matches_tomorrow()
    
    if not european_matches:
        print('\n❌ No hay partidos europeos mañana')
        return
    
    print(f'\n📊 ANÁLISIS CON BOTS SIMPLIFICADOS (SOLO EUROPA):')
    print('=' * 60)
    
    # Inicializar bots
    simple_bots = SimpleStatisticsBots()
    
    # Analizar cada competición europea
    competitions_analysis = {}
    
    for match in european_matches:
        competition = match.get('competition', 'N/A')
        home_team = match['home_team']
        away_team = match['away_team']
        referee = match.get('referee', 'N/A')
        
        if competition not in competitions_analysis:
            competitions_analysis[competition] = []
        
        # Análisis con bots simplificados
        analysis = {
            'match': f"{home_team} vs {away_team}",
            'time': match.get('match_time', 'N/A'),
            'referee': referee,
            'corners': simple_bots.analyze_corners_simple(home_team, away_team),
            'cards': simple_bots.analyze_cards_simple(home_team, away_team, referee),
            'btts': simple_bots.analyze_btts_simple(home_team, away_team),
            'draws': simple_bots.analyze_draws_with_formula(home_team, away_team)
        }
        
        competitions_analysis[competition].append(analysis)
    
    # Mostrar análisis por competición
    for competition, matches_analysis in competitions_analysis.items():
        print(f'\n🏆 {competition.upper()}:')
        print('=' * 50)
        
        valid_picks = {'corners': 0, 'cards': 0, 'btts': 0, 'draws': 0}
        
        for i, analysis in enumerate(matches_analysis[:3]):  # Primeros 3 de cada competición
            print(f'\n{i+1}. {analysis["match"]}')
            print(f'   ⏰ {analysis["time"]}')
            print(f'   👨‍⚖️ {analysis["referee"]}')
            
            # Córners
            corners = analysis['corners']
            print(f'   ⚽ Córners: {corners["total_corners_expected"]:.1f} esperados ({corners["confidence"]:.0f}%)')
            if corners['confidence'] >= 70:
                valid_picks['corners'] += 1
            
            # Tarjetas  
            cards = analysis['cards']
            print(f'   🟨 Tarjetas: {cards["total_cards_expected"]:.1f} esperadas ({cards["confidence"]:.0f}%)')
            if cards['confidence'] >= 70:
                valid_picks['cards'] += 1
            
            # BTTS
            btts = analysis['btts']
            status = "✅" if btts['btts_probability'] >= 70 else "❌"
            print(f'   🎯 BTTS: {btts["btts_probability"]:.1f}% ({btts["confidence"]:.0f}%) {status}')
            if btts['btts_probability'] >= 70:
                valid_picks['btts'] += 1
            
            # Empates
            draws = analysis['draws']
            print(f'   🤝 Empate: {draws["draw_probability"]:.1f}% ({draws["confidence"]:.0f}%)')
            if draws['confidence'] >= 65:
                valid_picks['draws'] += 1
        
        if len(matches_analysis) > 3:
            print(f'\n   ... y {len(matches_analysis) - 3} partidos más en {competition}')
        
        # Resumen de picks válidos por competición
        print(f'\n   📊 PICKS VÁLIDOS EN {competition}:')
        print(f'      ⚽ Córners: {valid_picks["corners"]}/{len(matches_analysis)}')
        print(f'      🟨 Tarjetas: {valid_picks["cards"]}/{len(matches_analysis)}')
        print(f'      🎯 BTTS: {valid_picks["btts"]}/{len(matches_analysis)}')
        print(f'      🤝 Empates: {valid_picks["draws"]}/{len(matches_analysis)}')
    
    # RESUMEN FINAL
    total_european_matches = len(european_matches)
    print(f'\n🇪🇺 RESUMEN FINAL - SOLO EUROPA:')
    print('=' * 50)
    print(f'📊 Total partidos europeos mañana: {total_european_matches}')
    print(f'🏆 Competiciones europeas: {len(competitions_analysis)}')
    print(f'✅ Sistema enfocado SOLO en fútbol europeo')
    print(f'📈 Bots basados en estadística pura')
    print(f'🎯 Criterios estrictos aplicados')

if __name__ == "__main__":
    try:
        analyze_european_matches_with_simple_bots()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()