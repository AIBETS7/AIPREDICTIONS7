#!/usr/bin/env python3
"""
Script para obtener el chat_id de un grupo de Telegram
"""

import requests
import time

def get_chat_id(bot_token):
    """Obtener el chat_id del último mensaje recibido"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    print("🔍 Obteniendo updates del bot...")
    print("📝 Para obtener el chat_id de un grupo:")
    print("   1. Añade tu bot al grupo")
    print("   2. Escribe cualquier mensaje en el grupo")
    print("   3. Presiona Enter aquí para continuar...")
    
    input()
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('ok') and data.get('result'):
                updates = data['result']
                
                if updates:
                    print(f"\n📊 Encontrados {len(updates)} updates:")
                    
                    for i, update in enumerate(updates, 1):
                        message = update.get('message', {})
                        chat = message.get('chat', {})
                        
                        chat_id = chat.get('id')
                        chat_type = chat.get('type')
                        chat_title = chat.get('title', 'Chat privado')
                        username = chat.get('username', 'Sin username')
                        
                        print(f"\n{i}. Chat ID: {chat_id}")
                        print(f"   Tipo: {chat_type}")
                        print(f"   Título: {chat_title}")
                        print(f"   Username: @{username}")
                        
                        if chat_type == 'group' or chat_type == 'supergroup':
                            print(f"   ✅ Este es un grupo - Chat ID: {chat_id}")
                
                else:
                    print("❌ No se encontraron updates")
                    print("💡 Asegúrate de:")
                    print("   - Haber añadido el bot al grupo")
                    print("   - Haber escrito un mensaje en el grupo")
                    print("   - Esperar unos segundos y volver a intentar")
            else:
                print(f"❌ Error en la respuesta: {data}")
                
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🤖 OBTENER CHAT_ID DE GRUPO DE TELEGRAM")
    print("=" * 50)
    
    # Token del bot actual
    bot_token = '7582466483:AAHshXjaU0vu2nZsYd8wSY5pR1XJ6EHmZOQ'
    
    print(f"Bot Token: {bot_token}")
    print()
    
    get_chat_id(bot_token)
    
    print("\n" + "=" * 50)
    print("📋 INSTRUCCIONES:")
    print("1. Copia el Chat ID del grupo que quieres usar")
    print("2. Edita el archivo 'daily_pick_automated.py'")
    print("3. Cambia la línea: self.chat_id = '2070545442'")
    print("4. Pega el nuevo chat_id")
    print("5. Guarda el archivo")

if __name__ == "__main__":
    main() 