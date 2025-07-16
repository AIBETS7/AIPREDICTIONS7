import requests
import json
import os

# Rutas de salida
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'odds_realtime.json')

# === CONFIGURACIÓN ===
# Sustituye por tus claves de API
THE_ODDS_API_KEY = os.getenv('THE_ODDS_API_KEY', 'TU_API_KEY_AQUI')
BETSAPI_KEY = os.getenv('BETSAPI_KEY', 'TU_API_KEY_AQUI')

# === THE ODDS API ===
def get_the_odds_api():
    url = f'https://api.the-odds-api.com/v4/sports/soccer_epl/odds/'
    params = {
        'apiKey': THE_ODDS_API_KEY,
        'regions': 'eu',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'decimal',
        'dateFormat': 'iso'
    }
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return {'source': 'the-odds-api', 'data': resp.json()}
    except Exception as e:
        return {'source': 'the-odds-api', 'error': str(e)}

# === BETSAPI ===
def get_betsapi():
    url = f'https://betsapi.com/api/v1/bet365/inplay'
    params = {'token': BETSAPI_KEY}
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return {'source': 'betsapi', 'data': resp.json()}
    except Exception as e:
        return {'source': 'betsapi', 'error': str(e)}


def main():
    results = []
    results.append(get_the_odds_api())
    results.append(get_betsapi())
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Cuotas guardadas en {OUTPUT_PATH}")

if __name__ == "__main__":
    main() 