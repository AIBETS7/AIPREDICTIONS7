import requests
from bs4 import BeautifulSoup, Tag
import json
import os

NOTBETTING_URL = "https://notbetting.com/tipster/Fut5Tips"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'tipster_stats.json')


def scrape_notbetting_stats():
    response = requests.get(NOTBETTING_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    stats = {
        'unidades_ganadas': '',
        'yield': '',
        'picks': '',
        'cuota_media': '',
        'win_rate': '',
        'stake_medio': '',
        'seguidores': ''
    }

    # Buscar el grid principal de estadísticas (7 columnas)
    grid = soup.find('div', class_='grid')
    if grid and isinstance(grid, Tag):
        stat_blocks = [child for child in grid.children if isinstance(child, Tag)]
        for block in stat_blocks:
            value_tag = block.find('h6')
            label_tag = block.find('p')
            if not value_tag or not label_tag:
                continue
            label = label_tag.get_text(strip=True).lower()
            value = value_tag.get_text(strip=True).replace('\u200b', '')
            if 'beneficio' in label:
                stats['unidades_ganadas'] = value
            elif 'yield' in label:
                stats['yield'] = value
            elif 'picks' in label:
                stats['picks'] = value
            elif 'cuota' in label:
                stats['cuota_media'] = value
            elif 'win rate' in label:
                stats['win_rate'] = value
            elif 'stake medio' in label:
                stats['stake_medio'] = value
            elif 'followers' in label or 'seguidores' in label:
                stats['seguidores'] = value

    return stats

if __name__ == "__main__":
    stats = scrape_notbetting_stats()
    # Guardar en archivo JSON
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"Estadísticas guardadas en {OUTPUT_PATH}")
    print(json.dumps(stats, ensure_ascii=False, indent=2)) 