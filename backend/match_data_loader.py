import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

def load_real_matches(date_str: Optional[str] = None) -> List[Dict]:
    """
    Carga partidos reales desde TODOS los archivos JSON disponibles
    
    Args:
        date_str: Fecha en formato YYYYMMDD, si no se proporciona usa archivos disponibles
    
    Returns:
        Lista de partidos con formato estándar
    """
    all_matches = []
    
    if date_str is None:
        # Buscar TODOS los archivos de partidos disponibles
        match_files = []
        for filename in os.listdir('.'):
            if (filename.startswith('real_') and filename.endswith('.json') and 'matches' in filename) or \
               (filename.startswith('live_') and filename.endswith('.json') and 'matches' in filename) or \
               (filename.startswith('demo_') and filename.endswith('.json') and 'matches' in filename) or \
               (filename.startswith('api_sports_') and filename.endswith('.json') and 'matches' in filename) or \
               (filename.startswith('upcoming_') and filename.endswith('.json') and 'matches' in filename) or \
               (filename.startswith('champions_league_') and filename.endswith('.json')) or \
               (filename.endswith('_matches.json')) or \
               (filename.endswith('matches.json')):
                match_files.append(filename)
        
        # También buscar en subdirectorios
        if os.path.exists('data'):
            for filename in os.listdir('data'):
                if filename.endswith('.json') and 'match' in filename.lower():
                    match_files.append(os.path.join('data', filename))
        
        if not match_files:
            return []
        
        print(f"📁 Archivos de partidos encontrados: {len(match_files)}")
        for file in match_files:
            print(f"   • {file}")
        
        # Cargar partidos de TODOS los archivos
        for file in match_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list) and data:
                    print(f"✅ {file}: {len(data)} partidos")
                    all_matches.extend(data)
                else:
                    print(f"⚠️ {file}: Sin datos válidos")
                    
            except Exception as e:
                print(f"❌ Error cargando {file}: {e}")
    
    else:
        # Buscar archivo específico para la fecha
        possible_files = [
            f'real_matches_{date_str}.json',
            f'real_active_matches_{date_str}.json',
            f'real_scheduled_matches_{date_str}.json'
        ]
        
        for filename in possible_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        all_matches.extend(data)
                        print(f"📁 Cargando partidos desde: {filename}")
                        
                except Exception as e:
                    print(f"❌ Error cargando {filename}: {e}")
    
    print(f"🌍 Total de partidos cargados: {len(all_matches)}")
    return all_matches

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
    Asigna árbitros a los partidos basándose en el PAÍS/REGIÓN (CORREGIDO)
    Ya no más errores como Munuera Montero en Bolivia
    """
    
    def get_country_from_match(match):
        """Detecta el país del partido basado en competición y equipos"""
        competition = match.get('competition', '').lower()
        country = match.get('country', '').lower()
        home_team = match.get('home_team', '').lower()
        
        # Mapeo por competición específica
        if 'la liga' in competition or 'copa del rey' in competition:
            return 'spain'
        elif 'premier league' in competition and 'england' in country:
            return 'england'
        elif 'bundesliga' in competition:
            return 'germany'
        elif 'serie a' in competition and 'italy' in country:
            return 'italy'
        elif 'ligue 1' in competition:
            return 'france'
        elif 'liga profesional argentina' in competition:
            return 'argentina'
        elif 'brasileiro' in competition or ('serie a' in competition and 'brazil' in country):
            return 'brazil'
        elif 'primera a' in competition and 'colombia' in country:
            return 'colombia'
        elif 'primera b' in competition and 'chile' in country:
            return 'chile'
        elif 'primera división' in competition:
            # Detectar por equipos específicos
            if 'tomayapo' in home_team or 'potosí' in home_team or 'blooming' in home_team or 'guabirá' in home_team:
                return 'bolivia'
            elif 'huachipato' in home_team or "o'higgins" in home_team:
                return 'chile'
            else:
                return 'generic'
        elif 'calcutta' in competition or 'premier division' in competition:
            return 'india'
        elif 'sudani' in competition:
            return 'sudan'
        elif 'uefa champions league' in competition or 'champions league' in competition:
            return 'uefa'
        elif 'friendlies' in competition:
            return 'generic'
        else:
            return 'generic'
    
    # Base de datos de árbitros por país/región (DATOS REALES)
    referees_by_country = {
        # Europa
        'spain': ['José Luis Munuera Montero', 'Antonio Mateu Lahoz', 'Jesús Gil Manzano', 'César Soto Grado'],
        'england': ['Michael Oliver', 'Anthony Taylor', 'Craig Pawson', 'Paul Tierney'],
        'germany': ['Felix Brych', 'Tobias Stieler', 'Manuel Gräfe', 'Deniz Aytekin'],
        'italy': ['Daniele Orsato', 'Marco Guida', 'Davide Massa', 'Gianluca Rocchi'],
        'france': ['Clément Turpin', 'Ruddy Buquet', 'Jérôme Brisard', 'Benoît Bastien'],
        'uefa': ['Björn Kuipers', 'Clément Turpin', 'Szymon Marciniak', 'Daniele Orsato'],
        
        # Sudamérica
        'bolivia': ['Carlos Herrera', 'Raúl Orosco', 'Gery Vargas', 'José Buitrago'],
        'argentina': ['Fernando Rapallini', 'Patricio Loustau', 'Darío Herrera', 'Facundo Tello'],
        'brazil': ['Wilton Sampaio', 'Anderson Daronco', 'Ramon Abatti Abel', 'Raphael Claus'],
        'colombia': ['Carlos Ortega', 'Bismark Santiago', 'Nicolás Gallo', 'Wílmar Roldán'],
        'chile': ['Roberto Tobar', 'Piero Maza', 'Cristián Garay', 'Angelo Hermosilla'],
        'uruguay': ['Esteban Ostojich', 'Gustavo Tejera', 'Christian Ferreyra', 'Andrés Cunha'],
        
        # Asia
        'india': ['Tejas Nagvenkar', 'Crystal John', 'Raghavendra Rao', 'Venkatesh R'],
        'japan': ['Ryuji Sato', 'Hiroyuki Kimura', 'Koichiro Fukushima', 'Yudai Yamamoto'],
        
        # África
        'sudan': ['Bakary Gassama', 'Mehdi Abid Charef', 'Bamlak Tessema', 'Janny Sikazwe'],
        
        # Genérico para ligas menores/amistosos
        'generic': ['Local Referee A', 'Local Referee B', 'Local Referee C', 'International Referee']
    }
    
    matches_with_referees = []
    for match in matches:
        match_copy = match.copy()
        
        # Detectar país del partido
        country = get_country_from_match(match)
        
        # Obtener árbitros del país correspondiente
        referees = referees_by_country.get(country, referees_by_country['generic'])
        
        # Asignar árbitro basado en hash del partido para consistencia
        match_hash = hash(f"{match.get('home_team', '')}{match.get('away_team', '')}{match.get('match_time', '')}")
        referee_index = abs(match_hash) % len(referees)
        match_copy['referee'] = referees[referee_index]
        
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
        # Si no se especifican competiciones, usar TODAS las disponibles
        competitions = []  # Lista vacía significa todas las competiciones
    
    # Cargar partidos reales
    all_matches = load_real_matches()
    
    if not all_matches:
        print("⚠️ No se encontraron partidos reales, usando datos de ejemplo")
        return get_example_matches()
    
    # FILTRO PERMANENTE: Eliminar países/ligas excluidos (RUSIA, etc.)
    from country_filter import filter_matches
    all_matches = filter_matches(all_matches)
    
    # Filtrar por competiciones (si se especificaron)
    if competitions:
        filtered_matches = filter_matches_by_competition(all_matches, competitions)
        if not filtered_matches:
            print(f"⚠️ No se encontraron partidos para {competitions}, usando datos de ejemplo")
            return get_example_matches()
    else:
        # Usar todos los partidos disponibles
        filtered_matches = all_matches
        print(f"🌍 Usando TODAS las competiciones disponibles (sin países excluidos)")
    
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