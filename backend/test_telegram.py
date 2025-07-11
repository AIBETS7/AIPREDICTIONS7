import os
import requests
from datetime import datetime

def test_telegram():
    bot_token = "7582466483:AAHshXjaU0vu2nZsYd8wSY5pR1XJ6EHmZOQ"
    chat_id = "2070545442"
    
    message = (
        f"\U0001F3C6 Test Football Pick!\n"
        f"Match: Real Madrid vs Barcelona\n"
        f"Time: 2025-07-12 20:00\n"
        f"Prediction: match_winner - Home Win\n"
        f"Confidence: 85.5%\n"
        f"Odds: 2.10\n"
        f"Reasoning: Real Madrid has been in excellent form at home\n"
        f"Tipster: AI Predictor\n"
        f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    
    try:
        resp = requests.post(url, data=payload)
        if resp.status_code == 200:
            print("✅ Test message sent to Telegram successfully!")
            print(f"Response: {resp.json()}")
        else:
            print(f"❌ Failed to send message: {resp.status_code}")
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"❌ Error sending message: {e}")

if __name__ == "__main__":
    test_telegram() 