import requests
from bs4 import BeautifulSoup
import json
import os
import time

SOFA_URL = 'https://www.sofascore.com/football'
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'sofascore_stats.json')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

# Pool de proxies gratuitos (puedes actualizar la lista periódicamente)
PROXIES = [
    {'http': 'http://51.158.68.68:8811', 'https': 'http://51.158.68.68:8811'},
    {'http': 'http://51.91.144.39:80', 'https': 'http://51.91.144.39:80'},
    {'http': 'http://51.38.191.164:80', 'https': 'http://51.38.191.164:80'},
    {'http': 'http://163.172.182.164:3128', 'https': 'http://163.172.182.164:3128'},
    {'http': 'http://51.75.147.41:3128', 'https': 'http://51.75.147.41:3128'},
]

def try_request_with_proxies(url, headers, proxies_list, timeout=10):
    for idx, proxy in enumerate(proxies_list):
        try:
            print(f"Intentando con proxy {idx+1}/{len(proxies_list)}: {proxy['http']}")
            resp = requests.get(url, headers=headers, proxies=proxy, timeout=timeout)
            resp.raise_for_status()
            print(f"Scraping con proxy {proxy['http']} OK")
            return resp
        except Exception as e:
            print(f"Proxy {proxy['http']} falló: {e}")
            continue
    print("Todos los proxies fallaron. Intentando sin proxy...")
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp

def scrape_sofascore():
    time.sleep(1)  # Pequeño retardo para evitar bloqueos
    resp = try_request_with_proxies(SOFA_URL, headers, PROXIES)
    soup = BeautifulSoup(resp.text, 'html.parser')
    matches = []
    for event in soup.select('a.sc-hLBbgP'):
        href = event.get('href')
        if href and isinstance(href, str):
            match = {
                'url': 'https://www.sofascore.com' + href,
                'teams': event.text.strip() if event.text else ''
            }
            matches.append(match)
    return matches

def main():
    matches = scrape_sofascore()
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    print(f"Estadísticas guardadas en {OUTPUT_PATH}")

if __name__ == "__main__":
    main() 