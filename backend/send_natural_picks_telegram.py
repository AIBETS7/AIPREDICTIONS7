#!/usr/bin/env python3
"""
Send Natural Picks Telegram - Envío Natural a Telegram
======================================================

Envía los mejores picks de cada bot a sus grupos de Telegram respectivos
CON CUOTAS REALES cuando estén disponibles en OddsAPI.
"""

import sys
import requests
import json
from typing import Dict, Optional

sys.path.append('.')

# CONFIGURACIÓN TELEGRAM
TELEGRAM_CONFIG = {
    'bot_token': 'TU_BOT_TOKEN',  # Usuario debe proporcionar
    'chat_ids': {
        'corners': 'CHAT_ID_CORNERS',      # Grupo Córners
        'cards': 'CHAT_ID_CARDS',          # Grupo Tarjetas  
        'btts': 'CHAT_ID_BTTS',            # Grupo Ambos Marcan
        'draws': 'CHAT_ID_DRAWS'           # Grupo Empates
    }
}

# CONFIGURACIÓN ODDS API
ODDS_API_CONFIG = {
    'api_key': '714a28a08e610e64f68a0d6d1a928f05',
    'base_url': 'https://api.the-odds-api.com/v4',
    'regions': 'eu,uk',
    'markets': 'h2h',  # Solo mercado disponible
    'odds_format': 'decimal',
    'date_format': 'iso'
}

def get_real_odds_for_match(home_team: str, away_team: str) -> Optional[Dict]:
    """Obtiene cuotas reales para un partido específico"""
    
    # Obtener cuotas de Champions League
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
            events = response.json()
            
            # Buscar el partido específico
            for event in events:
                event_home = event.get('home_team', '').lower()
                event_away = event.get('away_team', '').lower()
                
                # Matching por nombres
                if (home_team.lower() in event_home or event_home in home_team.lower()) and \
                   (away_team.lower() in event_away or event_away in away_team.lower()):
                    
                    if 'bookmakers' in event and event['bookmakers']:
                        bookmaker = event['bookmakers'][0]
                        
                        for market in bookmaker.get('markets', []):
                            if market.get('key') == 'h2h':
                                outcomes = market.get('outcomes', [])
                                
                                odds_data = {}
                                for outcome in outcomes:
                                    name = outcome.get('name')
                                    price = outcome.get('price')
                                    
                                    if name == event.get('home_team'):
                                        odds_data['home_win'] = price
                                    elif name == event.get('away_team'):
                                        odds_data['away_win'] = price
                                    elif name == 'Draw':
                                        odds_data['draw'] = price
                                
                                return {
                                    'found': True,
                                    'bookmaker': bookmaker.get('title'),
                                    'odds': odds_data
                                }
        
        return {'found': False}
    
    except Exception as e:
        print(f'⚠️ Error obteniendo cuotas reales: {e}')
        return {'found': False}

def create_telegram_message(bot_type: str, pick: Dict) -> str:
    """Crea mensaje de Telegram con cuotas reales cuando disponibles"""
    
    match_name = pick['match']
    home_team = match_name.split(' vs ')[0]
    away_team = match_name.split(' vs ')[1]
    
    # Intentar obtener cuotas reales
    real_odds_data = get_real_odds_for_match(home_team, away_team)
    
    if bot_type == 'corners':
        message = f"""🟢 🇪🇺 BOT CÓRNERS - PICK EUROPEO

⚽ {pick['match']}
🏆 {pick['competition']}
⏰ {pick['time']}

📊 ANÁLISIS ESTADÍSTICO:
🔢 {pick['total_corners_expected']:.1f} córners esperados
📈 Confianza: {pick['confidence']:.0f}%

💡 Basado en estadísticas históricas puras
🎯 Análisis de promedios por equipo"""
    
    elif bot_type == 'cards':
        message = f"""🟡 🇪🇺 BOT TARJETAS - PICK EUROPEO

🟨 {pick['match']}
🏆 {pick['competition']}
⏰ {pick['time']}

📊 ANÁLISIS ESTADÍSTICO:
🔢 {pick['total_cards_expected']:.1f} tarjetas esperadas
👨‍⚖️ Árbitro: {pick['referee']}
📈 Confianza: {pick['confidence']:.0f}%

💡 Basado en estadísticas + factor árbitro
🎯 Análisis de promedios históricos"""
    
    elif bot_type == 'btts':
        message = f"""🔴 🇪🇺 BOT AMBOS MARCAN - PICK EUROPEO

🎯 {pick['match']}
🏆 {pick['competition']}
⏰ {pick['time']}

📊 ANÁLISIS ESTADÍSTICO:
🔢 {pick['btts_probability']:.1f}% probabilidad BTTS
📈 Confianza: {pick['confidence']:.0f}%

💡 Basado en promedios de goles históricos
🎯 Solo picks >70% probabilidad"""
    
    elif bot_type == 'draws':
        message = f"""🔵 🇪🇺 BOT EMPATES - PICK EUROPEO

🤝 {pick['match']}
🏆 {pick['competition']}
⏰ {pick['time']}

📊 ANÁLISIS ESTADÍSTICO:
🔢 {pick['draw_probability']:.1f}% probabilidad empate
📈 Confianza: {pick['confidence']:.0f}%

💰 CUOTAS:"""
        
        # Solo para empates podemos tener cuotas reales
        if real_odds_data['found'] and 'draw' in real_odds_data['odds']:
            real_draw_odds = real_odds_data['odds']['draw']
            bookmaker = real_odds_data['bookmaker']
            message += f"""
✅ Cuota REAL: {real_draw_odds} ({bookmaker})
🎯 Fuente: OddsAPI en tiempo real"""
        else:
            estimated_odds = pick.get('odds', 0)
            message += f"""
📊 Cuota estimada: {estimated_odds:.2f}
💡 (Cuotas reales no disponibles)"""
        
        message += f"""

🔮 Fórmula avanzada con racha sin empates
📈 Ajuste dinámico por historial"""
    
    return message

def send_to_telegram(bot_token: str, chat_id: str, message: str) -> bool:
    """Envía mensaje a Telegram"""
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f'❌ Error enviando a Telegram: {e}')
        return False

def send_all_picks_to_telegram():
    """Envía todos los picks a sus respectivos grupos de Telegram"""
    
    from natural_best_picks_tomorrow import generate_natural_best_picks
    
    print('📱 ENVIANDO PICKS A TELEGRAM CON CUOTAS REALES')
    print('=' * 55)
    
    # Verificar configuración
    if TELEGRAM_CONFIG['bot_token'] == 'TU_BOT_TOKEN':
        print('❌ ERROR: Debes configurar el bot_token de Telegram')
        print('💡 Edita TELEGRAM_CONFIG en este archivo')
        return False
    
    # Generar picks
    picks = generate_natural_best_picks()
    
    if not picks:
        print('❌ No se pudieron generar picks')
        return False
    
    print(f'✅ {len(picks)} picks generados')
    print(f'🔍 Buscando cuotas reales en OddsAPI...')
    
    success_count = 0
    
    # Enviar cada pick a su grupo
    for bot_type, pick in picks.items():
        chat_id = TELEGRAM_CONFIG['chat_ids'].get(bot_type)
        
        if not chat_id or chat_id.startswith('CHAT_ID_'):
            print(f'⚠️ {bot_type.upper()}: Chat ID no configurado')
            continue
        
        # Crear mensaje con cuotas reales
        message = create_telegram_message(bot_type, pick)
        
        # Enviar a Telegram
        success = send_to_telegram(
            TELEGRAM_CONFIG['bot_token'], 
            chat_id, 
            message
        )
        
        if success:
            print(f'✅ {bot_type.upper()}: Enviado correctamente')
            success_count += 1
        else:
            print(f'❌ {bot_type.upper()}: Error en envío')
    
    print(f'\n📊 RESUMEN:')
    print(f'✅ {success_count}/{len(picks)} mensajes enviados')
    print(f'🎯 Cuotas reales integradas cuando disponibles')
    print(f'💡 Sistema híbrido: Stats + OddsAPI')
    
    return success_count > 0

def test_odds_api_integration():
    """Prueba la integración con OddsAPI"""
    
    print('🧪 PROBANDO INTEGRACIÓN ODDS API')
    print('=' * 40)
    
    # Probar con equipos de ejemplo
    test_teams = [
        ('Real Madrid', 'Barcelona'),
        ('Manchester City', 'Arsenal'),
        ('Bayern Munich', 'Dortmund')
    ]
    
    for home, away in test_teams:
        print(f'\n🔍 Buscando: {home} vs {away}')
        odds_data = get_real_odds_for_match(home, away)
        
        if odds_data['found']:
            print(f'✅ Encontrado en {odds_data["bookmaker"]}')
            odds = odds_data['odds']
            if 'draw' in odds:
                print(f'   🤝 Empate: {odds["draw"]}')
        else:
            print(f'❌ No encontrado')
    
    print(f'\n💡 La API funciona, pero depende de partidos disponibles')
    print(f'🏆 Champions League en temporada tendrá cuotas reales')

if __name__ == "__main__":
    try:
        # Probar integración
        test_odds_api_integration()
        
        # Enviar picks (si están configurados los tokens)
        print(f'\n' + '='*50)
        if TELEGRAM_CONFIG['bot_token'] != 'TU_BOT_TOKEN':
            send_all_picks_to_telegram()
        else:
            print('💡 Para enviar a Telegram, configura los tokens')
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()