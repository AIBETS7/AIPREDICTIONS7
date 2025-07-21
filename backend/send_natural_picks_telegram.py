#!/usr/bin/env python3
"""
Send Natural Picks to Telegram - Enviar Picks Naturales a Telegram
==================================================================

Envía los mejores picks naturales a sus respectivos grupos de Telegram.
"""

import sys
import requests
from datetime import datetime

sys.path.append('.')

# CONFIGURACIÓN TELEGRAM
TELEGRAM_CONFIG = {
    'bot_token': 'TU_BOT_TOKEN_AQUI',  # Token del bot principal
    'groups': {
        'corners': 'CHAT_ID_CORNERES',      # Chat ID grupo córners
        'cards': 'CHAT_ID_TARJETAS',        # Chat ID grupo tarjetas  
        'btts': 'CHAT_ID_AMBOS_MARCAN',     # Chat ID grupo ambos marcan
        'draws': 'CHAT_ID_EMPATES'          # Chat ID grupo empates
    }
}

def send_telegram_message(chat_id: str, message: str, bot_token: str) -> bool:
    """Envía un mensaje a un grupo de Telegram"""
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                return True
            else:
                print(f"❌ Error Telegram API: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def format_corners_message(pick: dict) -> str:
    """Formatea mensaje para el bot de córners"""
    
    match = pick['match']
    corners = pick['total_corners_expected']
    confidence = pick['confidence']
    competition = pick['competition']
    time = pick['time']
    
    # Extraer hora
    try:
        match_time = datetime.fromisoformat(time.replace('Z', '+00:00'))
        hour = match_time.strftime('%H:%M')
    except:
        hour = time
    
    message = f"""🇪🇺 <b>BOT CÓRNERS - PICK EUROPEO</b>

⚽ <b>{match}</b>
🏆 {competition}
⏰ <b>{hour}</b> (hora española)

📊 <b>ANÁLISIS:</b>
• Córners esperados: <b>{corners:.1f}</b>
• Confianza: <b>{confidence:.0f}%</b>

💡 <b>ESTADÍSTICA PURA</b>
Basado en medias históricas reales de ambos equipos.

✅ <b>SOLO EUROPA - UEFA CHAMPIONS LEAGUE</b>
🎯 #CornersBot #Europa #ChampionsLeague"""
    
    return message

def format_cards_message(pick: dict) -> str:
    """Formatea mensaje para el bot de tarjetas"""
    
    match = pick['match']
    cards = pick['total_cards_expected']
    confidence = pick['confidence']
    competition = pick['competition']
    referee = pick['referee']
    time = pick['time']
    
    # Extraer hora
    try:
        match_time = datetime.fromisoformat(time.replace('Z', '+00:00'))
        hour = match_time.strftime('%H:%M')
    except:
        hour = time
    
    message = f"""🇪🇺 <b>BOT TARJETAS - PICK EUROPEO</b>

🟨 <b>{match}</b>
🏆 {competition}
⏰ <b>{hour}</b> (hora española)
👨‍⚖️ <b>{referee}</b>

📊 <b>ANÁLISIS:</b>
• Tarjetas esperadas: <b>{cards:.1f}</b>
• Confianza: <b>{confidence:.0f}%</b>

💡 <b>ESTADÍSTICA PURA + FACTOR ÁRBITRO</b>
Equipos agresivos con árbitro conocido.

✅ <b>SOLO EUROPA - UEFA CHAMPIONS LEAGUE</b>
🎯 #TarjetasBot #Europa #ChampionsLeague"""
    
    return message

def format_btts_message(pick: dict) -> str:
    """Formatea mensaje para el bot ambos marcan"""
    
    match = pick['match']
    probability = pick['btts_probability']
    confidence = pick['confidence']
    odds = pick['odds']
    competition = pick['competition']
    time = pick['time']
    
    # Extraer hora
    try:
        match_time = datetime.fromisoformat(time.replace('Z', '+00:00'))
        hour = match_time.strftime('%H:%M')
    except:
        hour = time
    
    message = f"""🇪🇺 <b>BOT AMBOS MARCAN - PICK EUROPEO</b>

🎯 <b>{match}</b>
🏆 {competition}
⏰ <b>{hour}</b> (hora española)

📊 <b>ANÁLISIS:</b>
• Probabilidad BTTS: <b>{probability:.1f}%</b>
• Confianza: <b>{confidence:.0f}%</b>
• Cuota estimada: <b>{odds:.2f}</b>

💡 <b>ESTADÍSTICA PURA OFENSIVA</b>
Equipos con alta media de goles por partido.

✅ <b>CRITERIO: ≥70% PROBABILIDAD CUMPLIDO</b>
🔥 <b>IDEAL PARA COMBINADAS</b>
🎯 #AmbosMarcaN #Europa #ChampionsLeague"""
    
    return message

def format_draws_message(pick: dict) -> str:
    """Formatea mensaje para el bot empates"""
    
    match = pick['match']
    probability = pick['draw_probability']
    confidence = pick['confidence']
    odds = pick['odds']
    competition = pick['competition']
    time = pick['time']
    
    # Extraer hora
    try:
        match_time = datetime.fromisoformat(time.replace('Z', '+00:00'))
        hour = match_time.strftime('%H:%M')
    except:
        hour = time
    
    message = f"""🇪🇺 <b>BOT EMPATES - PICK EUROPEO</b>

🤝 <b>{match}</b>
🏆 {competition}
⏰ <b>{hour}</b> (hora española)

📊 <b>ANÁLISIS:</b>
• Probabilidad empate: <b>{probability:.1f}%</b>
• Confianza: <b>{confidence:.0f}%</b>
• Cuota estimada: <b>{odds:.2f}</b>

💡 <b>FÓRMULA ESPECÍFICA APLICADA</b>
Equipos equilibrados con mismo balance ofensivo/defensivo.

✅ <b>ESTADÍSTICA PURA - SOLO EUROPA</b>
🎯 #EmpatesBot #Europa #ChampionsLeague"""
    
    return message

def send_natural_picks_to_telegram():
    """Envía los picks naturales a Telegram"""
    
    from natural_best_picks_tomorrow import generate_natural_best_picks
    
    print('📱 ENVIANDO PICKS NATURALES A TELEGRAM')
    print('=' * 50)
    
    # Generar picks naturales
    print('🔍 Generando picks naturales...')
    picks = generate_natural_best_picks()
    
    if not picks:
        print('❌ No se pudieron generar picks')
        return
    
    print(f'\n📤 ENVIANDO A GRUPOS DE TELEGRAM:')
    print('-' * 40)
    
    # Verificar configuración
    if TELEGRAM_CONFIG['bot_token'] == 'TU_BOT_TOKEN_AQUI':
        print('⚠️ MODO DEMO - Configuración de Telegram pendiente')
        print('📋 Los mensajes se mostrarán aquí en lugar de enviarse:')
        print()
        
        # Mostrar mensajes que se enviarían
        if 'corners' in picks:
            print('🟢 GRUPO CÓRNERS:')
            print(format_corners_message(picks['corners']))
            print('\n' + '='*60 + '\n')
        
        if 'cards' in picks:
            print('🟡 GRUPO TARJETAS:')
            print(format_cards_message(picks['cards']))
            print('\n' + '='*60 + '\n')
        
        if 'btts' in picks:
            print('🔴 GRUPO AMBOS MARCAN:')
            print(format_btts_message(picks['btts']))
            print('\n' + '='*60 + '\n')
        
        if 'draws' in picks:
            print('🔵 GRUPO EMPATES:')
            print(format_draws_message(picks['draws']))
            print('\n' + '='*60 + '\n')
        
        print('📝 PARA ACTIVAR EL ENVÍO REAL:')
        print('   1. Configura TELEGRAM_CONFIG con tu bot token')
        print('   2. Añade los chat IDs de los 4 grupos')
        print('   3. Ejecuta el script nuevamente')
        
        return
    
    # Envío real a Telegram
    success_count = 0
    total_sends = 0
    
    # Enviar córners
    if 'corners' in picks:
        total_sends += 1
        message = format_corners_message(picks['corners'])
        if send_telegram_message(TELEGRAM_CONFIG['groups']['corners'], message, TELEGRAM_CONFIG['bot_token']):
            print(f'✅ Córners enviado: {picks["corners"]["match"]}')
            success_count += 1
        else:
            print(f'❌ Error enviando córners')
    
    # Enviar tarjetas
    if 'cards' in picks:
        total_sends += 1
        message = format_cards_message(picks['cards'])
        if send_telegram_message(TELEGRAM_CONFIG['groups']['cards'], message, TELEGRAM_CONFIG['bot_token']):
            print(f'✅ Tarjetas enviado: {picks["cards"]["match"]}')
            success_count += 1
        else:
            print(f'❌ Error enviando tarjetas')
    
    # Enviar BTTS
    if 'btts' in picks:
        total_sends += 1
        message = format_btts_message(picks['btts'])
        if send_telegram_message(TELEGRAM_CONFIG['groups']['btts'], message, TELEGRAM_CONFIG['bot_token']):
            print(f'✅ BTTS enviado: {picks["btts"]["match"]}')
            success_count += 1
        else:
            print(f'❌ Error enviando BTTS')
    
    # Enviar empates
    if 'draws' in picks:
        total_sends += 1
        message = format_draws_message(picks['draws'])
        if send_telegram_message(TELEGRAM_CONFIG['groups']['draws'], message, TELEGRAM_CONFIG['bot_token']):
            print(f'✅ Empates enviado: {picks["draws"]["match"]}')
            success_count += 1
        else:
            print(f'❌ Error enviando empates')
    
    # Resumen final
    print(f'\n📊 RESUMEN DE ENVÍO:')
    print(f'✅ Enviados exitosamente: {success_count}/{total_sends}')
    print(f'📱 Grupos notificados: {success_count}')
    
    if success_count == total_sends:
        print(f'🎉 ¡Todos los picks enviados correctamente!')
    else:
        print(f'⚠️ Algunos envíos fallaron - revisar configuración')

if __name__ == "__main__":
    try:
        send_natural_picks_to_telegram()
        print(f'\n✅ ¡Proceso de envío completado!')
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()