from utils.transfermarkt_utils import get_team_market_value
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from config.database import DATABASE_URL
from models.data_models import Match
from datetime import datetime, timedelta

def get_transfermarkt_summary(home_team, away_team, season='2024', league='LaLiga'):
    home_value = get_team_market_value(home_team, season, league)
    away_value = get_team_market_value(away_team, season, league)
    if home_value or away_value:
        return f"[Transfermarkt] Valor de mercado: {home_team}: {home_value or 'N/D'} | {away_team}: {away_value or 'N/D'}"
    return ''

def get_odds_summary(odds_data):
    if not odds_data:
        return ''
    # odds_data: dict con claves como 'home_win', 'draw', 'away_win', 'over_2_5', 'under_2_5'
    parts = []
    if 'home_win' in odds_data and 'draw' in odds_data and 'away_win' in odds_data:
        parts.append(f"1X2: {odds_data['home_win']} / {odds_data['draw']} / {odds_data['away_win']}")
    if 'over_2_5' in odds_data and 'under_2_5' in odds_data:
        parts.append(f"Más/Menos 2.5: {odds_data['over_2_5']} / {odds_data['under_2_5']}")
    return '[Cuotas] ' + ' | '.join(parts) if parts else ''

def get_stats_summary(stats):
    if not stats:
        return ''
    # stats: dict con claves como 'goals_scored', 'goals_conceded', 'shots', 'possession', etc.
    parts = []
    if 'goals_scored' in stats and 'goals_conceded' in stats:
        parts.append(f"Goles promedios: {stats['goals_scored']} a favor, {stats['goals_conceded']} en contra")
    if 'shots' in stats:
        parts.append(f"Tiros: {stats['shots']}")
    if 'possession' in stats:
        parts.append(f"Posesión: {stats['possession']}%")
    return '[Estadísticas] ' + ' | '.join(parts) if parts else ''

def get_team_stats_last_5_years(team_name, stat_keys=None):
    """
    Calcula la media de estadísticas (goles, corners, tarjetas, victorias) de los últimos 5 años para un equipo.
    stat_keys: lista de claves a calcular (por defecto: goles, corners, tarjetas, victorias)
    """
    if stat_keys is None:
        stat_keys = ['goals_scored', 'goals_conceded', 'corners', 'yellow_cards', 'red_cards', 'win']
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    five_years_ago = datetime.now() - timedelta(days=5*365)
    # Buscar partidos donde el equipo fue local o visitante
    matches = session.query(Match).filter(
        ((Match.home_team == team_name) | (Match.away_team == team_name)) &
        (Match.date >= five_years_ago)
    ).all()
    stats = {k: [] for k in stat_keys}
    for m in matches:
        # Goles
        if 'goals_scored' in stat_keys:
            if m.home_team == team_name:
                stats['goals_scored'].append(m.home_score or 0)
            elif m.away_team == team_name:
                stats['goals_scored'].append(m.away_score or 0)
        if 'goals_conceded' in stat_keys:
            if m.home_team == team_name:
                stats['goals_conceded'].append(m.away_score or 0)
            elif m.away_team == team_name:
                stats['goals_conceded'].append(m.home_score or 0)
        # Corners
        if 'corners' in stat_keys and m.statistics:
            if m.home_team == team_name:
                stats['corners'].append(m.statistics.get('home_corners', 0))
            elif m.away_team == team_name:
                stats['corners'].append(m.statistics.get('away_corners', 0))
        # Tarjetas
        if 'yellow_cards' in stat_keys and m.statistics:
            if m.home_team == team_name:
                stats['yellow_cards'].append(m.statistics.get('home_yellow_cards', 0))
            elif m.away_team == team_name:
                stats['yellow_cards'].append(m.statistics.get('away_yellow_cards', 0))
        if 'red_cards' in stat_keys and m.statistics:
            if m.home_team == team_name:
                stats['red_cards'].append(m.statistics.get('home_red_cards', 0))
            elif m.away_team == team_name:
                stats['red_cards'].append(m.statistics.get('away_red_cards', 0))
        # Victorias
        if 'win' in stat_keys:
            if m.home_team == team_name and (m.home_score or 0) > (m.away_score or 0):
                stats['win'].append(1)
            elif m.away_team == team_name and (m.away_score or 0) > (m.home_score or 0):
                stats['win'].append(1)
            else:
                stats['win'].append(0)
    # Calcular medias
    medias = {k: (sum(v)/len(v) if v else 0) for k, v in stats.items()}
    session.close()
    return medias 