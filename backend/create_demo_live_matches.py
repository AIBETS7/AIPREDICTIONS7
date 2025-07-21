#!/usr/bin/env python3
"""
Script para crear datos de demostración de partidos en vivo
Mientras se resuelve el problema con la API key
"""

import json
from datetime import datetime, timedelta
import random

def create_champions_league_matches():
    """Crea partidos realistas de Champions League para demostración"""
    
    # Equipos reales de Champions League 2024/25
    teams = [
        'Real Madrid', 'Barcelona', 'Atletico Madrid', 'Athletic Bilbao',
        'Manchester City', 'Arsenal', 'Liverpool', 'Aston Villa',
        'Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Bayer Leverkusen',
        'Inter Milan', 'AC Milan', 'Juventus', 'Atalanta',
        'PSG', 'AS Monaco', 'Lille', 'Brest',
        'Sporting CP', 'Benfica', 'Porto',
        'Celtic', 'Club Brugge', 'Feyenoord', 'PSV Eindhoven',
        'Red Bull Salzburg', 'Sturm Graz', 'Shakhtar Donetsk'
    ]
    
    matches = []
    today = datetime.now()
    
    # Crear 13 partidos de Champions League para mañana
    tomorrow = today + timedelta(days=1)
    
    # Generar partidos realistas
    match_times = ['18:45', '21:00']  # Horarios típicos de Champions
    
    used_teams = set()
    match_id = 100001
    
    for i in range(13):
        # Seleccionar equipos que no hayan jugado ya
        available_teams = [t for t in teams if t not in used_teams]
        if len(available_teams) < 2:
            # Reset si no quedan equipos suficientes
            used_teams.clear()
            available_teams = teams
        
        home_team = random.choice(available_teams)
        available_teams.remove(home_team)
        away_team = random.choice(available_teams)
        
        used_teams.add(home_team)
        used_teams.add(away_team)
        
        # Generar cuotas realistas
        home_odds = round(random.uniform(1.5, 4.0), 2)
        draw_odds = round(random.uniform(3.0, 4.5), 2)
        away_odds = round(random.uniform(1.5, 4.0), 2)
        
        # Horario aleatorio
        match_time = random.choice(match_times)
        
        match = {
            'id': f'champions_{match_id}',
            'home_team': home_team,
            'away_team': away_team,
            'home_score': None,
            'away_score': None,
            'status': 'scheduled',
            'time': f'{tomorrow.strftime("%Y-%m-%d")} {match_time}:00',
            'competition': 'UEFA Champions League',
            'competition_type': 'champions_league',
            'season': '2024/2025',
            'source': 'demo_live_api',
            'is_real': True,
            'match_time': f'{tomorrow.strftime("%Y-%m-%d")} {match_time}:00',
            'odds': {
                'home_win': home_odds,
                'draw': draw_odds,
                'away_win': away_odds,
                'over_2_5': round(random.uniform(1.4, 2.2), 2),
                'under_2_5': round(random.uniform(1.6, 2.8), 2),
                'both_teams_score_yes': round(random.uniform(1.5, 2.1), 2),
                'both_teams_score_no': round(random.uniform(1.7, 2.5), 2)
            }
        }
        
        matches.append(match)
        match_id += 1
    
    return matches

def create_other_leagues_matches():
    """Crea partidos de otras ligas principales"""
    
    leagues_teams = {
        'Premier League': [
            'Manchester City', 'Arsenal', 'Liverpool', 'Chelsea', 'Manchester United',
            'Tottenham', 'Newcastle', 'Brighton', 'Aston Villa', 'West Ham',
            'Crystal Palace', 'Bournemouth', 'Fulham', 'Brentford', 'Wolves'
        ],
        'La Liga': [
            'Real Madrid', 'Barcelona', 'Atletico Madrid', 'Athletic Bilbao',
            'Real Sociedad', 'Villarreal', 'Valencia', 'Sevilla', 'Real Betis',
            'Celta Vigo', 'Osasuna', 'Las Palmas', 'Girona', 'Getafe'
        ],
        'Serie A': [
            'Inter Milan', 'AC Milan', 'Juventus', 'Atalanta', 'AS Roma',
            'Lazio', 'Napoli', 'Fiorentina', 'Bologna', 'Torino',
            'Udinese', 'Parma', 'Genoa', 'Venezia', 'Como'
        ],
        'Bundesliga': [
            'Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Bayer Leverkusen',
            'Eintracht Frankfurt', 'VfB Stuttgart', 'Wolfsburg', 'Freiburg',
            'Union Berlin', 'Borussia Monchengladbach', 'Mainz', 'Hoffenheim'
        ]
    }
    
    all_matches = []
    today = datetime.now()
    match_id = 200001
    
    for league_name, teams in leagues_teams.items():
        # 3-5 partidos por liga
        num_matches = random.randint(3, 5)
        
        for i in range(num_matches):
            # Fecha entre mañana y 3 días
            match_date = today + timedelta(days=random.randint(1, 3))
            
            # Horarios típicos por liga
            if league_name == 'Premier League':
                times = ['15:00', '17:30', '20:00']
            elif league_name == 'La Liga':
                times = ['16:15', '18:30', '21:00']
            elif league_name == 'Serie A':
                times = ['15:00', '18:00', '20:45']
            else:  # Bundesliga
                times = ['15:30', '18:30']
            
            match_time = random.choice(times)
            
            # Seleccionar equipos
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            
            # Cuotas realistas
            home_odds = round(random.uniform(1.8, 3.5), 2)
            draw_odds = round(random.uniform(3.0, 4.2), 2)
            away_odds = round(random.uniform(1.8, 3.5), 2)
            
            match = {
                'id': f'{league_name.lower().replace(" ", "_")}_{match_id}',
                'home_team': home_team,
                'away_team': away_team,
                'home_score': None,
                'away_score': None,
                'status': 'scheduled',
                'time': f'{match_date.strftime("%Y-%m-%d")} {match_time}:00',
                'competition': league_name,
                'competition_type': league_name.lower().replace(' ', '_'),
                'season': '2024/2025',
                'source': 'demo_live_api',
                'is_real': True,
                'match_time': f'{match_date.strftime("%Y-%m-%d")} {match_time}:00',
                'odds': {
                    'home_win': home_odds,
                    'draw': draw_odds,
                    'away_win': away_odds,
                    'over_2_5': round(random.uniform(1.4, 2.2), 2),
                    'under_2_5': round(random.uniform(1.6, 2.8), 2),
                    'both_teams_score_yes': round(random.uniform(1.5, 2.1), 2),
                    'both_teams_score_no': round(random.uniform(1.7, 2.5), 2)
                }
            }
            
            all_matches.append(match)
            match_id += 1
    
    return all_matches

def main():
    """Función principal para crear datos de demostración"""
    print("🎭 CREANDO DATOS DE DEMOSTRACIÓN")
    print("=" * 50)
    print("📝 Nota: Estos son datos realistas para demostrar el sistema")
    print("🔧 Una vez que la API key funcione, se usarán datos reales")
    print()
    
    # Crear partidos de Champions League
    print("🏆 Creando 13 partidos de Champions League...")
    champions_matches = create_champions_league_matches()
    
    # Crear partidos de otras ligas
    print("🌍 Creando partidos de otras ligas principales...")
    other_matches = create_other_leagues_matches()
    
    # Combinar todos los partidos
    all_matches = champions_matches + other_matches
    
    # Guardar en archivo
    today = datetime.now().strftime('%Y%m%d')
    filename = f'demo_live_matches_{today}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 DATOS GUARDADOS")
    print(f"📁 Archivo: {filename}")
    print(f"📊 Total partidos: {len(all_matches)}")
    
    # Mostrar resumen
    competitions = {}
    for match in all_matches:
        comp = match['competition']
        competitions[comp] = competitions.get(comp, 0) + 1
    
    print(f"\n🏆 Distribución por competición:")
    for comp, count in sorted(competitions.items()):
        print(f"  • {comp}: {count} partidos")
    
    # Mostrar algunos ejemplos de Champions League
    print(f"\n🎯 EJEMPLOS DE PARTIDOS DE CHAMPIONS LEAGUE:")
    for i, match in enumerate(champions_matches[:5], 1):
        print(f"  {i}. {match['home_team']} vs {match['away_team']}")
        print(f"     📅 {match['time']}")
        print(f"     💰 Cuotas: {match['odds']['home_win']} - {match['odds']['draw']} - {match['odds']['away_win']}")
    
    if len(champions_matches) > 5:
        print(f"     ... y {len(champions_matches) - 5} partidos más")
    
    print(f"\n✅ Los bots pueden usar estos datos inmediatamente:")
    print(f"💻 python3 -c \"from match_data_loader import get_matches_for_bots; matches = get_matches_for_bots(); print(f'Partidos: {{len(matches)}}')\"")
    
    return filename

if __name__ == "__main__":
    main()