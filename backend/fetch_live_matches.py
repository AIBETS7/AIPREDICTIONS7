#!/usr/bin/env python3
"""
Script para obtener partidos en vivo desde la API de football
Usando el endpoint: https://apiv2.apifootball.com/?action=get_events
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configuración de la API
API_BASE_URL = "https://apiv2.apifootball.com/"
API_KEY = os.getenv('FOOTBALL_API_KEY', 'TU_API_KEY')  # Obtener de variable de entorno

# IDs de las principales ligas (estos son ejemplos, necesitas los IDs reales)
LEAGUE_IDS = {
    'champions_league': '3',
    'premier_league': '152',
    'la_liga': '302',
    'serie_a': '207',
    'bundesliga': '175',
    'ligue_1': '168',
    'europa_league': '4',
    'conference_league': '683'
}

def fetch_matches_from_api(league_id: str, from_date: str, to_date: str) -> List[Dict]:
    """
    Obtiene partidos desde la API de football
    
    Args:
        league_id: ID de la liga
        from_date: Fecha inicio (YYYY-MM-DD)
        to_date: Fecha fin (YYYY-MM-DD)
    
    Returns:
        Lista de partidos
    """
    url = API_BASE_URL
    params = {
        'action': 'get_events',
        'APIkey': API_KEY,
        'league_id': league_id,
        'from': from_date,
        'to': to_date
    }
    
    try:
        print(f"🔄 Obteniendo partidos de liga {league_id} desde {from_date} hasta {to_date}...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if isinstance(data, list):
            print(f"✅ {len(data)} partidos obtenidos")
            return data
        elif isinstance(data, dict) and 'error' in data:
            print(f"❌ Error de API: {data['error']}")
            return []
        else:
            print(f"⚠️ Respuesta inesperada: {type(data)}")
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

def fetch_all_matches(days_ahead: int = 7) -> Dict[str, List[Dict]]:
    """
    Obtiene partidos de todas las ligas principales
    
    Args:
        days_ahead: Días hacia adelante para buscar partidos
    
    Returns:
        Diccionario con partidos por liga
    """
    today = datetime.now()
    from_date = today.strftime('%Y-%m-%d')
    to_date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    all_matches = {}
    
    print(f"🌍 OBTENIENDO PARTIDOS DE TODAS LAS LIGAS")
    print(f"📅 Período: {from_date} a {to_date}")
    print("=" * 60)
    
    for league_name, league_id in LEAGUE_IDS.items():
        print(f"\n🏆 {league_name.upper().replace('_', ' ')}")
        matches = fetch_matches_from_api(league_id, from_date, to_date)
        all_matches[league_name] = matches
        
        if matches:
            print(f"📊 Partidos encontrados: {len(matches)}")
            # Mostrar algunos ejemplos
            for i, match in enumerate(matches[:3]):
                home = match.get('match_hometeam_name', 'N/A')
                away = match.get('match_awayteam_name', 'N/A')
                date = match.get('match_date', 'N/A')
                time = match.get('match_time', 'N/A')
                print(f"  {i+1}. {home} vs {away} - {date} {time}")
            
            if len(matches) > 3:
                print(f"  ... y {len(matches) - 3} partidos más")
        else:
            print("📭 No se encontraron partidos")
    
    return all_matches

def format_matches_for_bots(api_matches: List[Dict], league_name: str) -> List[Dict]:
    """
    Convierte partidos de la API al formato que usan los bots
    
    Args:
        api_matches: Partidos desde la API
        league_name: Nombre de la liga
    
    Returns:
        Partidos formateados
    """
    formatted_matches = []
    
    for match in api_matches:
        try:
            formatted_match = {
                'id': match.get('match_id', ''),
                'home_team': match.get('match_hometeam_name', ''),
                'away_team': match.get('match_awayteam_name', ''),
                'home_score': match.get('match_hometeam_score'),
                'away_score': match.get('match_awayteam_score'),
                'status': match.get('match_status', 'scheduled'),
                'time': f"{match.get('match_date', '')} {match.get('match_time', '')}".strip(),
                'competition': league_name.replace('_', ' ').title(),
                'competition_type': league_name,
                'season': match.get('league_season', '2024/2025'),
                'source': 'live_api',
                'is_real': True,
                'match_time': f"{match.get('match_date', '')} {match.get('match_time', '')}".strip(),
                'odds': {}
            }
            
            # Añadir cuotas si están disponibles
            if 'match_hometeam_odds' in match:
                formatted_match['odds']['home_win'] = float(match['match_hometeam_odds'])
            if 'match_drawteam_odds' in match:
                formatted_match['odds']['draw'] = float(match['match_drawteam_odds'])
            if 'match_awayteam_odds' in match:
                formatted_match['odds']['away_win'] = float(match['match_awayteam_odds'])
            
            formatted_matches.append(formatted_match)
            
        except Exception as e:
            print(f"⚠️ Error formateando partido: {e}")
            continue
    
    return formatted_matches

def save_matches_to_file(all_matches: Dict[str, List[Dict]], filename: str = None):
    """
    Guarda los partidos en un archivo JSON
    
    Args:
        all_matches: Diccionario con todos los partidos
        filename: Nombre del archivo (opcional)
    """
    if filename is None:
        today = datetime.now().strftime('%Y%m%d')
        filename = f'live_matches_{today}.json'
    
    # Combinar todos los partidos en una sola lista
    combined_matches = []
    
    for league_name, matches in all_matches.items():
        formatted_matches = format_matches_for_bots(matches, league_name)
        combined_matches.extend(formatted_matches)
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(combined_matches, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 PARTIDOS GUARDADOS")
        print(f"📁 Archivo: {filename}")
        print(f"📊 Total partidos: {len(combined_matches)}")
        
        # Mostrar resumen por competición
        competitions = {}
        for match in combined_matches:
            comp = match['competition']
            competitions[comp] = competitions.get(comp, 0) + 1
        
        print(f"🏆 Distribución por competición:")
        for comp, count in sorted(competitions.items()):
            print(f"  • {comp}: {count} partidos")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error guardando archivo: {e}")
        return None

def test_api_connection():
    """
    Prueba la conexión con la API
    """
    print("🔍 PROBANDO CONEXIÓN CON LA API")
    print("=" * 40)
    
    if API_KEY == 'TU_API_KEY':
        print("⚠️ ADVERTENCIA: API_KEY no configurada")
        print("📝 Configura la variable de entorno FOOTBALL_API_KEY")
        print("💡 Ejemplo: export FOOTBALL_API_KEY='tu_clave_aqui'")
        return False
    
    # Probar con Champions League (ID 3) para hoy
    today = datetime.now().strftime('%Y-%m-%d')
    test_matches = fetch_matches_from_api('3', today, today)
    
    if test_matches:
        print("✅ Conexión exitosa con la API")
        print(f"📊 Partidos de prueba obtenidos: {len(test_matches)}")
        return True
    else:
        print("❌ No se pudieron obtener datos de la API")
        print("🔧 Verifica tu API_KEY y conexión a internet")
        return False

def main():
    """Función principal"""
    print("🚀 OBTENEDOR DE PARTIDOS EN VIVO")
    print("=" * 50)
    
    # Probar conexión
    if not test_api_connection():
        print("\n💡 INSTRUCCIONES:")
        print("1. Obtén tu API key de https://apifootball.com/")
        print("2. Configura: export FOOTBALL_API_KEY='tu_clave'")
        print("3. Ejecuta este script nuevamente")
        return
    
    # Obtener partidos de todas las ligas
    all_matches = fetch_all_matches(days_ahead=10)
    
    # Guardar en archivo
    filename = save_matches_to_file(all_matches)
    
    if filename:
        print(f"\n🎯 SIGUIENTE PASO:")
        print(f"Los bots ahora pueden usar: {filename}")
        print(f"💻 Ejecuta: python3 -c \"from match_data_loader import *; matches = load_real_matches(); print(f'Partidos cargados: {{len(matches)}}')\"")

def get_champions_league_matches():
    """
    Función específica para obtener partidos de Champions League
    """
    print("🏆 OBTENIENDO PARTIDOS DE CHAMPIONS LEAGUE")
    print("=" * 50)
    
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    
    from_date = today.strftime('%Y-%m-%d')
    to_date = (today + timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Champions League ID = 3 (ejemplo, verificar el ID real)
    matches = fetch_matches_from_api('3', from_date, to_date)
    
    if matches:
        print(f"✅ {len(matches)} partidos de Champions League encontrados")
        
        # Formatear y guardar
        formatted = format_matches_for_bots(matches, 'champions_league')
        filename = f"champions_league_matches_{today.strftime('%Y%m%d')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(formatted, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Guardado en: {filename}")
        
        # Mostrar partidos
        for i, match in enumerate(matches, 1):
            home = match.get('match_hometeam_name', 'N/A')
            away = match.get('match_awayteam_name', 'N/A')
            date = match.get('match_date', 'N/A')
            time = match.get('match_time', 'N/A')
            print(f"  {i}. {home} vs {away} - {date} {time}")
        
        return formatted
    else:
        print("❌ No se encontraron partidos de Champions League")
        return []

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--champions':
        get_champions_league_matches()
    else:
        main()