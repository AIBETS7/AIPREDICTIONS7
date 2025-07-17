import os
from datetime import datetime, timedelta, time
from utils import telegram_utils
from models.data_models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config.database import DATABASE_URL
from flashscore_conference_scraper import get_conference_matches_tomorrow
from flashscore_team_stats import get_team_stats_flashscore
from sofascore_conference_scraper import get_conference_matches_tomorrow_sofa

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# 1. Obtener partidos de Conference League de mañana desde Flashscore o Sofascore
def get_matches():
    partidos = get_conference_matches_tomorrow()
    if not partidos:
        print("No se encontraron partidos de Conference League para mañana en Flashscore. Probando Sofascore...")
        partidos = get_conference_matches_tomorrow_sofa()
        if not partidos:
            print("No se encontraron partidos de Conference League para mañana en Sofascore.")
    return partidos

# 2. Analizar estadísticas y elegir el pick con más valor (mejorado)
def analyze_and_pick(matches):
    best_pick = None
    best_value = -float('inf')
    for match in matches:
        # Buscar equipos en la base de datos local
        home_stats = session.query(Team).filter(Team.name.ilike(f"%{match['home_team']}%")) .first()
        away_stats = session.query(Team).filter(Team.name.ilike(f"%{match['away_team']}%")) .first()
        # Si no está en la base de datos, buscar en Flashscore
        if not home_stats:
            print(f"Buscando estadísticas de {match['home_team']} en Flashscore...")
            home_stats = get_team_stats_flashscore(match['home_team'])
        if not away_stats:
            print(f"Buscando estadísticas de {match['away_team']} en Flashscore...")
            away_stats = get_team_stats_flashscore(match['away_team'])
        if not home_stats or not away_stats:
            continue
        # Unificar acceso a los datos (dict o modelo)
        home_gf = getattr(home_stats, 'goals_scored_avg', None) if hasattr(home_stats, 'goals_scored_avg') else home_stats.get('goals_scored_avg', 0)
        away_gc = getattr(away_stats, 'goals_conceded_avg', None) if hasattr(away_stats, 'goals_conceded_avg') else away_stats.get('goals_conceded_avg', 0)
        home_xg = getattr(home_stats, 'xg', None) if hasattr(home_stats, 'xg') else home_stats.get('xg', 0)
        away_xga = getattr(away_stats, 'xga', None) if hasattr(away_stats, 'xga') else away_stats.get('xga', 0)
        value = (home_gf - away_gc) + (home_xg or 0) - (away_xga or 0)
        if value > best_value:
            best_value = value
            best_pick = {
                'match': match,
                'pick': f"Victoria {match['home_team']}",
                'reason': f"{match['home_team']} promedia {home_gf:.2f} goles a favor y {away_gc:.2f} en contra. xG local: {home_xg if home_xg is not None else 'N/A'}, xGA visitante: {away_xga if away_xga is not None else 'N/A'}",
                'odds': 'N/A',
                'date': match['date'],
                'time': match['time']
            }
    return best_pick

# 3. Generar mensaje y enviar por Telegram
def send_pick_telegram(pick):
    chat_id = telegram_utils.CHAT_ID
    if not pick:
        msg = "No hay partidos de Conference League para mañana o no hay datos suficientes."
    else:
        msg = (f"PICK CONFERENCE LEAGUE\n"
               f"Partido: {pick['match']['home_team']} vs {pick['match']['away_team']}\n"
               f"Fecha: {pick['date']} {pick['time']}\n"
               f"Pick: {pick['pick']}\n"
               f"Cuota: {pick['odds']}\n"
               f"Razonamiento: {pick['reason']}")
    telegram_utils.send_message(chat_id, msg)

if __name__ == "__main__":
    matches = get_matches()
    pick = analyze_and_pick(matches)
    send_pick_telegram(pick) 