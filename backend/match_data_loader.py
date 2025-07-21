import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

def load_real_matches(date_str: Optional[str] = None) -> List[Dict]:
    """
    Carga partidos reales desde los archivos JSON
    
    Args:
        date_str: Fecha en formato YYYYMMDD, si no se proporciona usa archivos disponibles
    
    Returns:
        Lista de partidos con formato estándar
    """
    if date_str is None:
        # Buscar archivos disponibles
        files = []
        for filename in os.listdir('.'):
            if filename.startswith('real_') and filename.endswith('.json') and 'matches' in filename:
                files.append(filename)
        
        if not files:
            return []
        
        # Usar el archivo más reciente, preferir real_matches_* sobre otros
        matches_files = [f for f in files if f.startswith('real_matches_')]
        if matches_files:
            latest_file = sorted(matches_files)[-1]
        else:
            latest_file = sorted(files)[-1]
    else:
        # Buscar archivo específico para la fecha
        possible_files = [
            f'real_matches_{date_str}.json',
            f'real_active_matches_{date_str}.json',
            f'real_scheduled_matches_{date_str}.json'
        ]
        
        latest_file = None
        for filename in possible_files:
            if os.path.exists(filename):
                latest_file = filename
                break
        
        if not latest_file:
            return []
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📁 Cargando partidos desde: {latest_file}")
        return data if isinstance(data, list) else []
        
    except Exception as e:
        print(f"❌ Error cargando {latest_file}: {e}")
        return []

def filter_matches_by_competition(matches: List[Dict], competitions: List[str]) -> List[Dict]:
    """
    Filtra partidos por competición
    
    Args:
        matches: Lista de partidos
        competitions: Lista de competiciones a incluir
    
    Returns:
        Partidos filtrados
    """
    filtered = []
    for match in matches:
        competition = match.get('competition', '').lower()
        competition_type = match.get('competition_type', '').lower()
        
        for comp in competitions:
            comp_lower = comp.lower()
            if (comp_lower in competition or 
                comp_lower in competition_type or
                competition in comp_lower or
                competition_type in comp_lower):
                filtered.append(match)
                break
    
    return filtered

def get_la_liga_matches(date_str: Optional[str] = None) -> List[Dict]:
    """
    Obtiene específicamente partidos de La Liga
    
    Args:
        date_str: Fecha en formato YYYYMMDD
    
    Returns:
        Lista de partidos de La Liga
    """
    all_matches = load_real_matches(date_str)
    la_liga_matches = filter_matches_by_competition(all_matches, ['La Liga', 'la_liga'])
    
    print(f"🇪🇸 Partidos de La Liga encontrados: {len(la_liga_matches)}")
    for i, match in enumerate(la_liga_matches, 1):
        print(f"   {i}. {match.get('home_team')} vs {match.get('away_team')}")
    
    return la_liga_matches

def assign_referees_to_matches(matches: List[Dict]) -> List[Dict]:
    """
    Asigna árbitros a los partidos (simulado por ahora)
    En un sistema real, esto vendría de la API o base de datos
    """
    # Árbitros de La Liga con sus características
    la_liga_referees = [
        'Antonio Mateu Lahoz',      # Estricto
        'Jesús Gil Manzano',        # Normal  
        'José Luis Munuera Montero', # Permisivo
        'Ricardo de Burgos Bengoetxea', # Normal
        'César Soto Grado',         # Estricto
        'Javier Alberola Rojas',    # Normal
        'Pablo González Fuertes',   # Permisivo
        'Mario Melero López'        # Muy estricto
    ]
    
    matches_with_referees = []
    for match in matches:
        match_copy = match.copy()
        
        # Asignar árbitro basado en hash del partido para consistencia
        match_hash = hash(f"{match.get('home_team', '')}{match.get('away_team', '')}{match.get('time', '')}")
        referee_index = abs(match_hash) % len(la_liga_referees)
        match_copy['referee'] = la_liga_referees[referee_index]
        
        matches_with_referees.append(match_copy)
    
    return matches_with_referees

def format_match_for_bots(match: Dict) -> Dict:
    """
    Formatea un partido para que sea compatible con los bots
    
    Args:
        match: Partido en formato de la API
    
    Returns:
        Partido en formato estándar para bots
    """
    return {
        'home_team': match.get('home_team', ''),
        'away_team': match.get('away_team', ''),
        'referee': match.get('referee', 'Desconocido'),
        'match_time': match.get('time', ''),
        'competition': match.get('competition', ''),
        'competition_type': match.get('competition_type', ''),
        'status': match.get('status', 'scheduled'),
        'odds': match.get('odds', {}),
        'id': match.get('id', ''),
        'season': match.get('season', ''),
        'source': match.get('source', '')
    }

def get_matches_for_bots(competitions: List[str] = None, with_referees: bool = True) -> List[Dict]:
    """
    Obtiene partidos formateados para usar en los bots
    
    Args:
        competitions: Lista de competiciones a incluir (default: La Liga)
        with_referees: Si asignar árbitros a los partidos
    
    Returns:
        Lista de partidos formateados para bots
    """
    if competitions is None:
        competitions = ['La Liga', 'la_liga']
    
    # Cargar partidos reales
    all_matches = load_real_matches()
    
    if not all_matches:
        print("⚠️ No se encontraron partidos reales, usando datos de ejemplo")
        return get_example_matches()
    
    # Filtrar por competiciones
    filtered_matches = filter_matches_by_competition(all_matches, competitions)
    
    if not filtered_matches:
        print(f"⚠️ No se encontraron partidos para {competitions}, usando datos de ejemplo")
        return get_example_matches()
    
    # Asignar árbitros si se solicita
    if with_referees:
        filtered_matches = assign_referees_to_matches(filtered_matches)
    
    # Formatear para bots
    formatted_matches = [format_match_for_bots(match) for match in filtered_matches]
    
    print(f"✅ Cargados {len(formatted_matches)} partidos reales para los bots")
    
    return formatted_matches

def get_example_matches() -> List[Dict]:
    """
    Datos de ejemplo si no hay partidos reales disponibles
    """
    return [
        {
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'referee': 'Antonio Mateu Lahoz',
            'match_time': '2025-01-22 20:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Atletico Madrid',
            'away_team': 'Sevilla',
            'referee': 'Mario Melero López',
            'match_time': '2025-01-22 18:00',
            'competition': 'La Liga'
        },
        {
            'home_team': 'Real Betis',
            'away_team': 'Valencia',
            'referee': 'Pablo González Fuertes',
            'match_time': '2025-01-22 16:00',
            'competition': 'La Liga'
        }
    ]

# Función de conveniencia para testing
def test_match_loader():
    """Función de prueba para verificar que todo funciona"""
    print("🧪 TESTING MATCH DATA LOADER")
    print("=" * 50)
    
    # Cargar todos los partidos
    all_matches = load_real_matches()
    print(f"📊 Total partidos cargados: {len(all_matches)}")
    
    # Obtener partidos de La Liga
    la_liga_matches = get_la_liga_matches()
    print(f"🇪🇸 Partidos de La Liga: {len(la_liga_matches)}")
    
    # Formatear para bots
    bot_matches = get_matches_for_bots()
    print(f"🤖 Partidos formateados para bots: {len(bot_matches)}")
    
    if bot_matches:
        print("\n📋 EJEMPLO DE PARTIDO FORMATEADO:")
        example = bot_matches[0]
        for key, value in example.items():
            print(f"   {key}: {value}")

if __name__ == "__main__":
    test_match_loader()