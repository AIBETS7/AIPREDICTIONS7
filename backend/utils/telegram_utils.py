import os
import requests

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7582466483:AAHshXjaU0vu2nZsYd8wSY5pR1XJ6EHmZOQ')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '2070545442')


def send_message(chat_id, text, parse_mode='Markdown'):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return True
    else:
        print(f"Error enviando mensaje a Telegram: {response.text}")
        return False 