#!/usr/bin/env python3
"""
Corrected Odds Integration - Integración de Cuotas Corregida
===========================================================

Integra cuotas reales usando solo los mercados disponibles en OddsAPI.
"""

import sys
import requests
from typing import Dict, List, Optional

sys.path.append('.')

# CONFIGURACIÓN ODDS API CORREGIDA
ODDS_API_CONFIG = {
    'api_key': '714a28a08e610e64f68a0d6d1a928f05',
    'base_url': 'https://api.the-odds-api.com/v4',
    'regions': 'eu,uk',  # Europa y Reino Unido
    'markets': 'h2h',  # Solo Head to Head (1X2) disponible
    'odds_format': 'decimal',
    'date_format': 'iso'
}

def get_real_champions_league_odds():
    """Obtiene cuotas reales de Champions League disponibles"""
    
    print('🏆 OBTENIENDO CUOTAS REALES CHAMPIONS LEAGUE')
    print('=' * 55)
    print('📊 Mercado: H2H (1X2 - Local, Empate, Visitante)')
    print('🌍 Regiones: Europa y Reino Unido')
    print('=' * 55)
    
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
            print(f'✅ Conexión exitosa')
            print(f'📊 Eventos encontrados: {len(events)}')
            
            if events:
                print(f'\n⚽ PARTIDOS CON CUOTAS REALES:')
                print('-' * 50)
                
                for i, event in enumerate(events[:10], 1):
                    home = event.get('home_team', 'N/A')
                    away = event.get('away_team', 'N/A')
                    time = event.get('commence_time', 'N/A')
                    
                    print(f'{i}. {home} vs {away}')
                    print(f'   ⏰ {time}')
                    
                    # Mostrar cuotas H2H
                    if 'bookmakers' in event and event['bookmakers']:
                        bookmaker = event['bookmakers'][0]
                        print(f'   📊 Casa: {bookmaker.get("title", "Unknown")}')
                        
                        for market in bookmaker.get('markets', []):
                            if market.get('key') == 'h2h':
                                outcomes = market.get('outcomes', [])
                                for outcome in outcomes:
                                    name = outcome.get('name')
                                    price = outcome.get('price')
                                    
                                    if name == home:
                                        print(f'   🏠 Local ({name}): {price}')
                                    elif name == away:
                                        print(f'   ✈️ Visitante ({name}): {price}')
                                    elif name == 'Draw':
                                        print(f'   🤝 Empate: {price}')
                    print()
                
                if len(events) > 10:
                    print(f'   ... y {len(events) - 10} partidos más')
                
                return events
            else:
                print('❌ No hay partidos de Champions League disponibles')
                return []
        
        else:
            print(f'❌ Error API: {response.status_code}')
            print(f'📄 Respuesta: {response.text[:300]}...')
            return []
    
    except Exception as e:
        print(f'❌ Error: {e}')
        return []

def update_picks_with_available_odds():
    """Actualiza picks con cuotas reales disponibles (solo H2H)"""
    
    from natural_best_picks_tomorrow import generate_natural_best_picks
    
    print('\n🔄 ACTUALIZANDO PICKS CON CUOTAS DISPONIBLES')
    print('=' * 55)
    
    # Generar picks
    picks = generate_natural_best_picks()
    
    if not picks:
        print('❌ No se pudieron generar picks')
        return
    
    # Obtener cuotas reales
    real_events = get_real_champions_league_odds()
    
    if not real_events:
        print('⚠️ No hay cuotas reales disponibles')
        return picks
    
    print(f'\n💡 ACTUALIZANDO SOLO EMPATES (únicos con cuotas H2H):')
    print('-' * 55)
    
    updated_picks = {}
    
    for bot_type, pick in picks.items():
        updated_pick = pick.copy()
        match_name = pick['match']
        home_team = match_name.split(' vs ')[0]
        away_team = match_name.split(' vs ')[1]
        
        print(f'\n🤖 {bot_type.upper()}: {match_name}')
        
        # Buscar cuotas reales para este partido
        real_odds = None
        bookmaker_name = None
        
        for event in real_events:
            event_home = event.get('home_team', '').lower()
            event_away = event.get('away_team', '').lower()
            
            # Matching por nombres
            if (home_team.lower() in event_home or event_home in home_team.lower()) and \
               (away_team.lower() in event_away or event_away in away_team.lower()):
                
                if 'bookmakers' in event and event['bookmakers']:
                    bookmaker = event['bookmakers'][0]
                    bookmaker_name = bookmaker.get('title')
                    
                    for market in bookmaker.get('markets', []):
                        if market.get('key') == 'h2h':
                            outcomes = market.get('outcomes', [])
                            
                            # Extraer cuota de empate
                            for outcome in outcomes:
                                if outcome.get('name') == 'Draw':
                                    real_odds = outcome.get('price')
                                    break
                            break
                break
        
        # Actualizar solo bots que usan cuotas de empate
        if bot_type == 'draws' and real_odds:
            updated_pick['real_odds'] = real_odds
            updated_pick['bookmaker'] = bookmaker_name
            print(f'✅ Cuota empate real: {real_odds} ({bookmaker_name})')
            print(f'   📊 vs {pick.get("odds", 0):.2f} calculado')
        else:
            updated_pick['real_odds'] = None
            updated_pick['bookmaker'] = None
            if bot_type == 'draws':
                print(f'❌ Cuota empate no encontrada')
            else:
                print(f'💡 {bot_type}: Cuotas no disponibles en H2H')
        
        updated_picks[bot_type] = updated_pick
    
    print(f'\n📋 RESUMEN ACTUALIZACIÓN:')
    print('-' * 30)
    print(f'✅ Solo empates pueden usar cuotas reales')
    print(f'💡 Córners/Tarjetas/BTTS: Sin cuotas API disponibles')
    print(f'🎯 Sistema mantiene análisis estadístico')
    
    return updated_picks

def create_final_telegram_messages_with_real_odds():
    """Crea mensajes finales para Telegram con cuotas reales cuando disponibles"""
    
    updated_picks = update_picks_with_available_odds()
    
    if not updated_picks:
        print('❌ No se pudieron actualizar picks')
        return
    
    print(f'\n📱 MENSAJES FINALES PARA TELEGRAM:')
    print('=' * 50)
    
    # Mensaje Córners (sin cuotas reales)
    if 'corners' in updated_picks:
        pick = updated_picks['corners']
        print(f'\n🟢 GRUPO CÓRNERS:')
        print(f'🇪🇺 BOT CÓRNERS - PICK EUROPEO')
        print(f'⚽ {pick["match"]}')
        print(f'🏆 {pick["competition"]}')
        print(f'📊 {pick["total_corners_expected"]:.1f} córners esperados')
        print(f'📈 Confianza: {pick["confidence"]:.0f}%')
        print(f'💡 Estadística pura (sin cuotas API disponibles)')
    
    # Mensaje Tarjetas (sin cuotas reales)
    if 'cards' in updated_picks:
        pick = updated_picks['cards']
        print(f'\n🟡 GRUPO TARJETAS:')
        print(f'🇪🇺 BOT TARJETAS - PICK EUROPEO')
        print(f'🟨 {pick["match"]}')
        print(f'🏆 {pick["competition"]}')
        print(f'👨‍⚖️ {pick["referee"]}')
        print(f'📊 {pick["total_cards_expected"]:.1f} tarjetas esperadas')
        print(f'📈 Confianza: {pick["confidence"]:.0f}%')
        print(f'💡 Estadística pura (sin cuotas API disponibles)')
    
    # Mensaje BTTS (sin cuotas reales)
    if 'btts' in updated_picks:
        pick = updated_picks['btts']
        print(f'\n🔴 GRUPO AMBOS MARCAN:')
        print(f'🇪🇺 BOT AMBOS MARCAN - PICK EUROPEO')
        print(f'🎯 {pick["match"]}')
        print(f'🏆 {pick["competition"]}')
        print(f'📊 {pick["btts_probability"]:.1f}% probabilidad')
        print(f'📈 Confianza: {pick["confidence"]:.0f}%')
        print(f'💡 Estadística pura (sin cuotas BTTS en API)')
    
    # Mensaje Empates (CON cuotas reales si disponibles)
    if 'draws' in updated_picks:
        pick = updated_picks['draws']
        print(f'\n🔵 GRUPO EMPATES:')
        print(f'🇪🇺 BOT EMPATES - PICK EUROPEO')
        print(f'🤝 {pick["match"]}')
        print(f'🏆 {pick["competition"]}')
        print(f'📊 {pick["draw_probability"]:.1f}% probabilidad')
        print(f'📈 Confianza: {pick["confidence"]:.0f}%')
        
        if pick.get('real_odds'):
            print(f'💰 Cuota REAL: {pick["real_odds"]} ({pick["bookmaker"]})')
        else:
            print(f'💰 Cuota estimada: {pick["odds"]:.2f}')
    
    print(f'\n✅ SISTEMA CORREGIDO:')
    print(f'📊 Solo usa mercados disponibles en API')
    print(f'🎯 Empates con cuotas reales cuando disponibles')
    print(f'💡 Otros bots mantienen análisis estadístico')
    
    return updated_picks

if __name__ == "__main__":
    try:
        # Obtener cuotas Champions League
        champions_odds = get_real_champions_league_odds()
        
        if champions_odds:
            # Crear mensajes finales
            final_messages = create_final_telegram_messages_with_real_odds()
            print(f'\n🎉 ¡Sistema corregido funcionando!')
        else:
            print(f'\n⚠️ No hay cuotas disponibles ahora')
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()