#!/usr/bin/env python3
"""
Real Odds Integration - Integración de Cuotas Reales
====================================================

Integra cuotas reales de OddsAPI para reemplazar las calculadas artificialmente.
"""

import sys
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta

sys.path.append('.')

# CONFIGURACIÓN ODDS API
ODDS_API_CONFIG = {
    'api_key': '714a28a08e610e64f68a0d6d1a928f05',
    'base_url': 'https://api.the-odds-api.com/v4',
    'regions': 'eu,uk',  # Europa y Reino Unido
    'markets': 'h2h,btts,draw',  # Head to Head, Both Teams Score, Draw (corregido)
    'odds_format': 'decimal',
    'date_format': 'iso'
}

def get_real_odds_for_match(home_team: str, away_team: str, match_date: str) -> Dict:
    """Obtiene cuotas reales para un partido específico"""
    
    # Obtener eventos de fútbol
    url = f"{ODDS_API_CONFIG['base_url']}/sports/soccer_uefa_champs_league/odds"
    
    params = {
        'api_key': ODDS_API_CONFIG['api_key'],
        'regions': ODDS_API_CONFIG['regions'],
        'markets': ODDS_API_CONFIG['markets'],
        'oddsFormat': ODDS_API_CONFIG['odds_format'],
        'dateFormat': ODDS_API_CONFIG['date_format']
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Buscar el partido específico
            for event in data:
                event_home = event.get('home_team', '').lower()
                event_away = event.get('away_team', '').lower()
                
                # Matching simple por nombres
                if (home_team.lower() in event_home or event_home in home_team.lower()) and \
                   (away_team.lower() in event_away or event_away in away_team.lower()):
                    
                    # Extraer cuotas
                    odds_data = {
                        'home_win': None,
                        'draw': None,
                        'away_win': None,
                        'btts_yes': None,
                        'btts_no': None
                    }
                    
                    if 'bookmakers' in event and event['bookmakers']:
                        bookmaker = event['bookmakers'][0]  # Primer bookmaker
                        
                        for market in bookmaker.get('markets', []):
                            market_key = market.get('key')
                            
                            if market_key == 'h2h':  # Head to Head (1X2)
                                for outcome in market.get('outcomes', []):
                                    outcome_name = outcome.get('name')
                                    if outcome_name == event.get('home_team'):
                                        odds_data['home_win'] = outcome.get('price')
                                    elif outcome_name == event.get('away_team'):
                                        odds_data['away_win'] = outcome.get('price')
                                    elif outcome_name == 'Draw':
                                        odds_data['draw'] = outcome.get('price')
                            
                            elif market_key == 'btts_yes':  # Both Teams Score
                                for outcome in market.get('outcomes', []):
                                    if outcome.get('name') == 'Yes':
                                        odds_data['btts_yes'] = outcome.get('price')
                                    elif outcome.get('name') == 'No':
                                        odds_data['btts_no'] = outcome.get('price')
                    
                    return {
                        'found': True,
                        'match': f"{event.get('home_team')} vs {event.get('away_team')}",
                        'odds': odds_data,
                        'bookmaker': bookmaker.get('title') if 'bookmakers' in event and event['bookmakers'] else 'Unknown'
                    }
            
            return {'found': False, 'reason': 'Match not found in API'}
        
        else:
            return {'found': False, 'reason': f'API Error: {response.status_code}'}
    
    except requests.exceptions.RequestException as e:
        return {'found': False, 'reason': f'Connection error: {e}'}

def test_odds_api():
    """Prueba la conexión con OddsAPI"""
    
    print('🎯 TESTING ODDS API')
    print('=' * 40)
    
    # Test de conexión básica
    url = f"{ODDS_API_CONFIG['base_url']}/sports"
    params = {'api_key': ODDS_API_CONFIG['api_key']}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            sports = response.json()
            print(f'✅ API conectada correctamente')
            print(f'📊 Deportes disponibles: {len(sports)}')
            
            # Buscar fútbol
            football_sports = [s for s in sports if 'soccer' in s.get('key', '')]
            print(f'⚽ Deportes de fútbol: {len(football_sports)}')
            
            for sport in football_sports[:5]:  # Primeros 5
                print(f'   • {sport.get("title")} ({sport.get("key")})')
            
        else:
            print(f'❌ Error API: {response.status_code}')
            print(f'📄 Respuesta: {response.text}')
    
    except Exception as e:
        print(f'❌ Error de conexión: {e}')

def get_champions_league_odds():
    """Obtiene todas las cuotas de Champions League disponibles"""
    
    print('\n🏆 OBTENIENDO CUOTAS CHAMPIONS LEAGUE')
    print('=' * 50)
    
    url = f"{ODDS_API_CONFIG['base_url']}/sports/soccer_uefa_champs_league/odds"
    
    params = {
        'api_key': ODDS_API_CONFIG['api_key'],
        'regions': ODDS_API_CONFIG['regions'],
        'markets': ODDS_API_CONFIG['markets'],
        'oddsFormat': ODDS_API_CONFIG['odds_format'],
        'dateFormat': ODDS_API_CONFIG['date_format']
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            events = response.json()
            print(f'✅ Eventos obtenidos: {len(events)}')
            
            # Filtrar eventos de mañana
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            
            tomorrow_events = []
            for event in events:
                event_date = event.get('commence_time', '')
                if tomorrow_str in event_date:
                    tomorrow_events.append(event)
            
            print(f'📅 Partidos mañana ({tomorrow_str}): {len(tomorrow_events)}')
            
            if tomorrow_events:
                print(f'\n⚽ PARTIDOS CON CUOTAS REALES:')
                print('-' * 40)
                
                for i, event in enumerate(tomorrow_events[:10], 1):
                    home = event.get('home_team', 'N/A')
                    away = event.get('away_team', 'N/A')
                    time = event.get('commence_time', 'N/A')
                    
                    print(f'{i}. {home} vs {away}')
                    print(f'   ⏰ {time}')
                    
                    # Mostrar cuotas si están disponibles
                    if 'bookmakers' in event and event['bookmakers']:
                        bookmaker = event['bookmakers'][0]
                        print(f'   📊 Casa: {bookmaker.get("title", "Unknown")}')
                        
                        for market in bookmaker.get('markets', []):
                            market_key = market.get('key')
                            if market_key == 'h2h':
                                outcomes = market.get('outcomes', [])
                                for outcome in outcomes:
                                    name = outcome.get('name')
                                    price = outcome.get('price')
                                    if name == home:
                                        print(f'   🏠 {name}: {price}')
                                    elif name == away:
                                        print(f'   ✈️ {name}: {price}')
                                    elif name == 'Draw':
                                        print(f'   🤝 Empate: {price}')
                            elif market_key == 'btts_yes':
                                for outcome in market.get('outcomes', []):
                                    if outcome.get('name') == 'Yes':
                                        print(f'   🎯 BTTS Sí: {outcome.get("price")}')
                    print()
                
                return tomorrow_events
            else:
                print('❌ No hay partidos de Champions League mañana')
                return []
        
        else:
            print(f'❌ Error API: {response.status_code}')
            print(f'📄 Respuesta: {response.text[:500]}...')
            return []
    
    except Exception as e:
        print(f'❌ Error: {e}')
        return []

def integrate_real_odds_with_picks():
    """Integra cuotas reales con los picks generados"""
    
    from natural_best_picks_tomorrow import generate_natural_best_picks
    
    print('🎯 INTEGRANDO CUOTAS REALES CON PICKS')
    print('=' * 50)
    
    # Generar picks
    picks = generate_natural_best_picks()
    
    if not picks:
        print('❌ No se pudieron generar picks')
        return
    
    # Obtener cuotas reales
    real_odds_events = get_champions_league_odds()
    
    if not real_odds_events:
        print('⚠️ No hay cuotas reales disponibles')
        return picks
    
    print(f'\n🔄 ACTUALIZANDO PICKS CON CUOTAS REALES:')
    print('-' * 50)
    
    updated_picks = {}
    
    for bot_type, pick in picks.items():
        updated_pick = pick.copy()
        match_name = pick['match']
        
        print(f'\n🤖 {bot_type.upper()}: {match_name}')
        
        # Buscar cuotas reales para este partido
        odds_result = get_real_odds_for_match(
            match_name.split(' vs ')[0],
            match_name.split(' vs ')[1],
            pick['time']
        )
        
        if odds_result['found']:
            odds_data = odds_result['odds']
            bookmaker = odds_result['bookmaker']
            
            print(f'✅ Cuotas encontradas ({bookmaker}):')
            
            # Actualizar según el tipo de bot
            if bot_type == 'btts' and odds_data['btts_yes']:
                updated_pick['real_odds'] = odds_data['btts_yes']
                updated_pick['bookmaker'] = bookmaker
                print(f'   🎯 BTTS Real: {odds_data["btts_yes"]} (vs {pick["odds"]:.2f} calculado)')
            
            elif bot_type == 'draws' and odds_data['draw']:
                updated_pick['real_odds'] = odds_data['draw']
                updated_pick['bookmaker'] = bookmaker
                print(f'   🤝 Empate Real: {odds_data["draw"]} (vs {pick["odds"]:.2f} calculado)')
            
            else:
                print(f'   ⚠️ Cuotas no disponibles para {bot_type}')
                updated_pick['real_odds'] = None
                updated_pick['bookmaker'] = None
        
        else:
            print(f'❌ No encontrado: {odds_result["reason"]}')
            updated_pick['real_odds'] = None
            updated_pick['bookmaker'] = None
        
        updated_picks[bot_type] = updated_pick
    
    return updated_picks

if __name__ == "__main__":
    try:
        # Test API
        test_odds_api()
        
        # Obtener cuotas Champions League
        champions_odds = get_champions_league_odds()
        
        # Integrar con picks
        if champions_odds:
            updated_picks = integrate_real_odds_with_picks()
            print(f'\n✅ ¡Integración de cuotas reales completada!')
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()