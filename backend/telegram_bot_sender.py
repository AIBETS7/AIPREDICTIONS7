#!/usr/bin/env python3
"""
Telegram Bot Sender - Envío Automático de Picks por Bot
=======================================================

Sistema para enviar el pick de mayor confianza de cada bot
a su respectivo canal de Telegram.
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from match_data_loader import get_matches_for_bots
from cards_bot import CardsBot
from corners_bot import CornersBot
from draws_bot import DrawsBot
from both_teams_score_bot import BothTeamsScoreBot

# Configuración de Telegram
TELEGRAM_CONFIG = {
    'bot_token': '7582466483:AAHshXjaU0vu2nZsYd8wSY5pR1XJ6EHmZOQ',
    'channels': {
        'tarjetas': {
            'chat_id': '2070545442',  # ACTUALIZAR: Chat ID del grupo de Bot Tarjetas
            'name': '🟨 Bot Tarjetas',
            'emoji': '🟨'
        },
        'corneres': {
            'chat_id': '2070545442',  # ACTUALIZAR: Chat ID del grupo de Bot Córners
            'name': '⚽ Bot Córners',
            'emoji': '⚽'
        },
        'empates': {
            'chat_id': '2070545442',  # ACTUALIZAR: Chat ID del grupo de Bot Empates
            'name': '🤝 Bot Empates',
            'emoji': '🤝'
        },
        'ambos_marcan': {
            'chat_id': '2070545442',  # ACTUALIZAR: Chat ID del grupo de Bot Ambos Marcan
            'name': '🎯 Bot Ambos Marcan',
            'emoji': '🎯'
        }
    }
}

def send_telegram_message(chat_id: str, message: str) -> bool:
    """
    Envía un mensaje a un canal de Telegram
    """
    if chat_id.startswith('CHAT_ID_'):
        print(f"⚠️ Chat ID no configurado: {chat_id}")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['bot_token']}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Mensaje enviado exitosamente a {chat_id}")
            return True
        else:
            print(f"❌ Error enviando mensaje: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def format_pick_message(pick: Dict, bot_info: Dict) -> str:
    """
    Formatea un pick para envío por Telegram
    """
    emoji = bot_info['emoji']
    bot_name = bot_info['name']
    
    # Información básica del partido
    home_team = pick['home_team']
    away_team = pick['away_team']
    competition = pick.get('competition', 'Competición')
    match_time = pick.get('match_time', 'Hora no disponible')
    confidence = pick['confidence']
    odds = pick.get('odds', 'N/A')
    
    # Mensaje base
    message = f"{emoji} *{bot_name}*\n"
    message += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    message += f"🏆 *{competition}*\n"
    message += f"⚽ *{home_team}* vs *{away_team}*\n"
    message += f"📅 {match_time}\n\n"
    
    # Información específica por tipo de bot
    if 'predicted_total' in pick:
        if 'tarjetas' in bot_name.lower():
            message += f"🟨 *Predicción*: {pick['predicted_total']} tarjetas\n"
            if pick.get('referee'):
                message += f"👨‍⚖️ *Árbitro*: {pick['referee']}\n"
        elif 'córner' in bot_name.lower():
            message += f"⚽ *Predicción*: {pick['predicted_total']} córners\n"
    
    if 'draw_probability' in pick:
        message += f"🤝 *Probabilidad de empate*: {pick['draw_probability']:.1f}%\n"
    
    if 'btts_probability' in pick:
        message += f"🎯 *Probabilidad BTTS*: {pick['btts_probability']:.1f}%\n"
    
    # Métricas
    message += f"\n📊 *Confianza*: {confidence}%\n"
    message += f"💰 *Cuota estimada*: {odds}\n\n"
    
    # Análisis (truncado si es muy largo)
    if pick.get('reasoning'):
        analysis = pick['reasoning']
        if len(analysis) > 200:
            analysis = analysis[:200] + "..."
        message += f"📈 *Análisis*: {analysis}\n\n"
    
    # Footer
    message += f"🤖 *AI Predictions 7*\n"
    message += f"⏰ {datetime.now().strftime('%H:%M')} - {datetime.now().strftime('%d/%m/%Y')}"
    
    return message

def get_best_pick_from_bot(bot_name: str, matches: List[Dict]) -> Optional[Dict]:
    """
    Obtiene el pick de mayor confianza de un bot específico
    """
    try:
        if bot_name == 'tarjetas':
            bot = CardsBot()
            picks = bot.get_picks_for_matches(matches)
        elif bot_name == 'corneres':
            bot = CornersBot()
            picks = bot.get_picks_for_matches(matches)
        elif bot_name == 'empates':
            bot = DrawsBot()
            picks = bot.get_picks_for_matches(matches)
        elif bot_name == 'ambos_marcan':
            bot = BothTeamsScoreBot()
            picks = bot.get_picks_for_matches(matches)
        else:
            print(f"❌ Bot desconocido: {bot_name}")
            return None
        
        if picks:
            # Los picks ya vienen ordenados por confianza (descendente)
            best_pick = picks[0]
            print(f"✅ {bot_name}: Mejor pick con {best_pick['confidence']}% confianza")
            return best_pick
        else:
            print(f"⚠️ {bot_name}: No hay picks disponibles")
            return None
            
    except Exception as e:
        print(f"❌ Error obteniendo picks de {bot_name}: {e}")
        return None

def send_all_bot_picks():
    """
    Envía el mejor pick de cada bot a su respectivo canal de Telegram
    """
    print("🚀 INICIANDO ENVÍO DE PICKS A TELEGRAM")
    print("=" * 60)
    
    # Cargar partidos
    print("📊 Cargando partidos...")
    matches = get_matches_for_bots(competitions=None, with_referees=True)
    print(f"✅ {len(matches)} partidos cargados")
    
    if not matches:
        print("❌ No hay partidos disponibles")
        return
    
    results = {
        'sent': 0,
        'failed': 0,
        'no_picks': 0
    }
    
    # Procesar cada bot
    for bot_key, channel_info in TELEGRAM_CONFIG['channels'].items():
        print(f"\n{channel_info['emoji']} Procesando {channel_info['name']}...")
        
        # Obtener mejor pick del bot
        best_pick = get_best_pick_from_bot(bot_key, matches)
        
        if best_pick:
            # Formatear mensaje
            message = format_pick_message(best_pick, channel_info)
            
            # Enviar a Telegram
            chat_id = channel_info['chat_id']
            success = send_telegram_message(chat_id, message)
            
            if success:
                results['sent'] += 1
                print(f"✅ Pick enviado: {best_pick['home_team']} vs {best_pick['away_team']}")
            else:
                results['failed'] += 1
        else:
            results['no_picks'] += 1
    
    # Resumen final
    print(f"\n📊 RESUMEN DE ENVÍOS:")
    print(f"✅ Enviados exitosamente: {results['sent']}")
    print(f"❌ Fallos en envío: {results['failed']}")
    print(f"⚠️ Sin picks disponibles: {results['no_picks']}")
    print(f"🤖 Total bots procesados: {len(TELEGRAM_CONFIG['channels'])}")

def test_telegram_connections():
    """
    Prueba la conexión con todos los canales de Telegram
    """
    print("🔍 PROBANDO CONEXIONES DE TELEGRAM")
    print("=" * 50)
    
    test_message = "🧪 *Mensaje de Prueba*\n\nSistema de bots funcionando correctamente ✅"
    
    for bot_key, channel_info in TELEGRAM_CONFIG['channels'].items():
        print(f"\n{channel_info['emoji']} Probando {channel_info['name']}...")
        
        chat_id = channel_info['chat_id']
        success = send_telegram_message(chat_id, test_message)
        
        if success:
            print(f"✅ Conexión exitosa")
        else:
            print(f"❌ Fallo en conexión")

def show_configuration():
    """
    Muestra la configuración actual de Telegram
    """
    print("⚙️ CONFIGURACIÓN ACTUAL DE TELEGRAM")
    print("=" * 50)
    print(f"🤖 Bot Token: {TELEGRAM_CONFIG['bot_token'][:20]}...")
    print(f"\n📱 Canales configurados:")
    
    for bot_key, channel_info in TELEGRAM_CONFIG['channels'].items():
        chat_id = channel_info['chat_id']
        status = "❌ No configurado" if chat_id.startswith('CHAT_ID_') else "✅ Configurado"
        print(f"  {channel_info['emoji']} {channel_info['name']}: {status}")
        print(f"     Chat ID: {chat_id}")

def update_chat_ids(chat_ids: Dict[str, str]):
    """
    Actualiza los chat IDs de los canales
    """
    for bot_key, chat_id in chat_ids.items():
        if bot_key in TELEGRAM_CONFIG['channels']:
            TELEGRAM_CONFIG['channels'][bot_key]['chat_id'] = chat_id
            print(f"✅ Actualizado {bot_key}: {chat_id}")
        else:
            print(f"❌ Bot desconocido: {bot_key}")

def main():
    """
    Función principal
    """
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'test':
            test_telegram_connections()
        elif command == 'config':
            show_configuration()
        elif command == 'send':
            send_all_bot_picks()
        else:
            print("❌ Comando desconocido. Usa: test, config, o send")
    else:
        # Comportamiento por defecto: enviar picks
        send_all_bot_picks()

if __name__ == "__main__":
    main()