#!/usr/bin/env python3
"""
Check Odds Markets - Verificar Mercados Disponibles
===================================================

Verifica qué mercados están disponibles en OddsAPI para Champions League.
"""

import requests

API_KEY = '714a28a08e610e64f68a0d6d1a928f05'
BASE_URL = 'https://api.the-odds-api.com/v4'

def check_available_markets():
    """Verifica mercados disponibles"""
    
    print('🔍 VERIFICANDO MERCADOS DISPONIBLES')
    print('=' * 50)
    
    # Primero, obtener solo H2H (básico)
    url = f"{BASE_URL}/sports/soccer_uefa_champs_league/odds"
    
    params = {
        'api_key': API_KEY,
        'regions': 'eu,uk',
        'markets': 'h2h',  # Solo mercado básico
        'oddsFormat': 'decimal',
        'dateFormat': 'iso'
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            events = response.json()
            print(f'✅ Conexión exitosa con mercado H2H')
            print(f'📊 Eventos encontrados: {len(events)}')
            
            if events:
                print(f'\n📋 PRIMER EVENTO EJEMPLO:')
                event = events[0]
                print(f'🏠 Local: {event.get("home_team")}')
                print(f'✈️ Visitante: {event.get("away_team")}')
                print(f'⏰ Fecha: {event.get("commence_time")}')
                
                if 'bookmakers' in event and event['bookmakers']:
                    bookmaker = event['bookmakers'][0]
                    print(f'📊 Casa de apuestas: {bookmaker.get("title")}')
                    
                    for market in bookmaker.get('markets', []):
                        market_key = market.get('key')
                        print(f'📈 Mercado disponible: {market_key}')
                        
                        for outcome in market.get('outcomes', []):
                            name = outcome.get('name')
                            price = outcome.get('price')
                            print(f'   • {name}: {price}')
            
            return True
        
        else:
            print(f'❌ Error: {response.status_code}')
            print(f'📄 Respuesta: {response.text}')
            return False
    
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

def check_specific_markets():
    """Prueba mercados específicos uno por uno"""
    
    print('\n🎯 PROBANDO MERCADOS ESPECÍFICOS')
    print('=' * 50)
    
    markets_to_test = [
        'h2h',           # Head to Head (1X2)
        'spreads',       # Handicap
        'totals',        # Over/Under
        'btts',          # Both Teams to Score
        'draw_no_bet',   # Draw No Bet
    ]
    
    working_markets = []
    
    for market in markets_to_test:
        print(f'\n🔍 Probando mercado: {market}')
        
        url = f"{BASE_URL}/sports/soccer_uefa_champs_league/odds"
        params = {
            'api_key': API_KEY,
            'regions': 'eu,uk',
            'markets': market,
            'oddsFormat': 'decimal',
            'dateFormat': 'iso'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                events = response.json()
                print(f'✅ {market}: FUNCIONA ({len(events)} eventos)')
                working_markets.append(market)
            else:
                print(f'❌ {market}: Error {response.status_code}')
                if response.status_code == 422:
                    error_data = response.json()
                    print(f'   📄 Detalle: {error_data.get("message", "Unknown")}')
        
        except Exception as e:
            print(f'❌ {market}: Error de conexión - {e}')
    
    print(f'\n📊 RESUMEN:')
    print(f'✅ Mercados funcionando: {len(working_markets)}')
    for market in working_markets:
        print(f'   • {market}')
    
    return working_markets

if __name__ == "__main__":
    try:
        # Verificar conexión básica
        if check_available_markets():
            # Probar mercados específicos
            working_markets = check_specific_markets()
            
            if working_markets:
                print(f'\n🎉 ¡Mercados identificados para usar en el sistema!')
            else:
                print(f'\n⚠️ No se encontraron mercados adicionales')
    
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()