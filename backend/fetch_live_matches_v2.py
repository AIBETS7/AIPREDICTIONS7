#!/usr/bin/env python3
"""
Fetch Live Matches V2 - Usando API-Sports.io
============================================

Script mejorado para obtener partidos en vivo usando la API de api-sports.io
que parece más confiable que la anterior.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configuración de la API
API_KEY = "dc7adf0a857be5ca3fd75d79e82c69cb"
BASE_URL = "https://v3.football.api-sports.io"

def get_fixtures_by_date(date_str: str) -> List[Dict]:
    """
    Obtiene partidos para una fecha específica
    """
    url = f"{BASE_URL}/fixtures"
    headers = {
        "x-apisports-key": API_KEY
    }
    params = {
        "date": date_str
    }
    
    try:
        print(f"🔄 Obteniendo partidos para {date_str}...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            fixtures = data.get("response", [])
            print(f"✅ {len(fixtures)} partidos encontrados para {date_str}")
            return fixtures
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return []

def format_fixture_for_bots(fixture: Dict) -> Dict:
    """
    Convierte un fixture de la API al formato usado por los bots
    """
    try:
        # Extraer información básica
        home_team = fixture["teams"]["home"]["name"]
        away_team = fixture["teams"]["away"]["name"]
        league_name = fixture["league"]["name"]
        country = fixture["league"]["country"]
        match_time = fixture["fixture"]["date"]
        status = fixture["fixture"]["status"]["long"]
        
        # Determinar tipo de competición
        competition_type = "other"
        if "Champions League" in league_name:
            competition_type = "champions_league"
        elif "Europa League" in league_name:
            competition_type = "europa_league"
        elif "Conference League" in league_name:
            competition_type = "conference_league"
        elif "Premier League" in league_name:
            competition_type = "premier_league"
        elif "La Liga" in league_name or "Primera División" in league_name:
            competition_type = "la_liga"
        elif "Serie A" in league_name:
            competition_type = "serie_a"
        elif "Bundesliga" in league_name:
            competition_type = "bundesliga"
        elif "Ligue 1" in league_name:
            competition_type = "ligue_1"
        
        # Formatear para los bots
        formatted_match = {
            'id': f'api_sports_{fixture["fixture"]["id"]}',
            'home_team': home_team,
            'away_team': away_team,
            'home_score': fixture["goals"]["home"],
            'away_score': fixture["goals"]["away"],
            'status': status.lower(),
            'time': match_time,
            'competition': league_name,
            'competition_type': competition_type,
            'country': country,
            'season': fixture["league"]["season"],
            'source': 'api_sports_v3',
            'is_real': True,
            'match_time': match_time,
            'venue': fixture["fixture"]["venue"]["name"] if fixture["fixture"]["venue"] else "Unknown",
            'referee': fixture["fixture"]["referee"] if fixture["fixture"]["referee"] else "Unknown"
        }
        
        return formatted_match
        
    except Exception as e:
        print(f"❌ Error formateando fixture: {e}")
        return None

def fetch_matches_for_dates(dates: List[str]) -> List[Dict]:
    """
    Obtiene partidos para múltiples fechas
    """
    all_matches = []
    
    for date in dates:
        fixtures = get_fixtures_by_date(date)
        
        for fixture in fixtures:
            formatted_match = format_fixture_for_bots(fixture)
            if formatted_match:
                all_matches.append(formatted_match)
    
    return all_matches

def save_matches_to_file(matches: List[Dict], filename: str = None):
    """
    Guarda los partidos en un archivo JSON
    """
    if not filename:
        today = datetime.now().strftime('%Y%m%d')
        filename = f'api_sports_matches_{today}.json'
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        print(f"💾 Partidos guardados en: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error guardando archivo: {e}")
        return None

def display_matches_summary(matches: List[Dict]):
    """
    Muestra un resumen de los partidos obtenidos
    """
    if not matches:
        print("❌ No se encontraron partidos")
        return
    
    print(f"\n📊 RESUMEN DE PARTIDOS OBTENIDOS")
    print("=" * 50)
    print(f"📈 Total partidos: {len(matches)}")
    
    # Agrupar por competición
    competitions = {}
    for match in matches:
        comp = match['competition']
        competitions[comp] = competitions.get(comp, 0) + 1
    
    print(f"\n🏆 Por competición:")
    for comp, count in sorted(competitions.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {comp}: {count} partidos")
    
    # Agrupar por país
    countries = {}
    for match in matches:
        country = match.get('country', 'Unknown')
        countries[country] = countries.get(country, 0) + 1
    
    print(f"\n🌍 Por país:")
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  • {country}: {count} partidos")
    
    # Mostrar algunos ejemplos
    print(f"\n🎯 EJEMPLOS DE PARTIDOS:")
    for i, match in enumerate(matches[:10], 1):
        print(f"  {i}. {match['home_team']} vs {match['away_team']}")
        print(f"     🏆 {match['competition']} ({match['country']})")
        print(f"     📅 {match['time']}")
        if match.get('referee') and match['referee'] != 'Unknown':
            print(f"     👨‍⚖️ {match['referee']}")

def test_api_connection():
    """
    Prueba la conexión con la API
    """
    print("🔍 PROBANDO CONEXIÓN CON API-SPORTS.IO")
    print("=" * 50)
    
    # Probar con fecha de hoy
    today = datetime.now().strftime('%Y-%m-%d')
    fixtures = get_fixtures_by_date(today)
    
    if fixtures:
        print(f"✅ API funcionando correctamente")
        print(f"📊 {len(fixtures)} partidos encontrados para hoy")
        return True
    else:
        print(f"❌ No se pudieron obtener datos de la API")
        return False

def main():
    """
    Función principal
    """
    print("🚀 FETCH LIVE MATCHES V2 - API-SPORTS.IO")
    print("=" * 60)
    print("🔑 Usando nueva API más confiable")
    print(f"🗝️ API Key: {API_KEY[:10]}...")
    print()
    
    # Probar conexión
    if not test_api_connection():
        print("❌ No se puede conectar a la API. Verifica la API key.")
        return
    
    # Fechas a consultar: hoy y mañana
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    
    dates = [
        today.strftime('%Y-%m-%d'),
        tomorrow.strftime('%Y-%m-%d')
    ]
    
    print(f"\n📅 Obteniendo partidos para:")
    for date in dates:
        print(f"  • {date}")
    
    # Obtener partidos
    matches = fetch_matches_for_dates(dates)
    
    if matches:
        # Mostrar resumen
        display_matches_summary(matches)
        
        # Guardar en archivo
        filename = save_matches_to_file(matches)
        
        if filename:
            print(f"\n✅ PROCESO COMPLETADO")
            print(f"📁 Archivo generado: {filename}")
            print(f"🤖 Los bots pueden usar estos datos inmediatamente")
            print(f"💻 Comando: python3 -c \"from match_data_loader import get_matches_for_bots; matches = get_matches_for_bots(); print(f'Partidos: {{len(matches)}}')\"")
        
    else:
        print("❌ No se pudieron obtener partidos")

if __name__ == "__main__":
    main()