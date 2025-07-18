from payment_processor import paypal_bp
from flask import Flask, jsonify, request, send_file
import os
import json
from scrapers.transfermarkt_scraper import TransfermarktScraper
from sqlalchemy.orm import sessionmaker
from models.data_models import TransfermarktTeam, TransfermarktPlayer, TransfermarktTransfer, Base
from config.database import DATABASE_URL
from sqlalchemy import create_engine
from google_sheets_logger import log_payment

app = Flask(__name__)

app.register_blueprint(paypal_bp)

def load_json_data(filename):
    path = os.path.join(os.path.dirname(__file__), 'data', filename)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/api/odds-realtime')
def api_odds_realtime():
    data = load_json_data('odds_realtime.json')
    return jsonify({'success': bool(data), 'data': data})

@app.route('/api/sportmonks-fixtures')
def api_sportmonks_fixtures():
    data = load_json_data('sportmonks_fixtures.json')
    return jsonify({'success': bool(data), 'data': data})

@app.route('/api/flashscore-fixtures')
def api_flashscore_fixtures():
    data = load_json_data('flashscore_fixtures.json')
    return jsonify({'success': bool(data), 'data': data})

@app.route('/api/sofascore-stats')
def api_sofascore_stats():
    data = load_json_data('sofascore_stats.json')
    return jsonify({'success': bool(data), 'data': data})

@app.route('/api/betexplorer-stats')
def api_betexplorer_stats():
    data = load_json_data('betexplorer_stats.json')
    return jsonify({'success': bool(data), 'data': data})

@app.route('/api/tipster-stats')
def get_tipster_stats():
    stats_path = os.path.join(os.path.dirname(__file__), 'data', 'tipster_stats.json')
    if not os.path.exists(stats_path):
        return jsonify({'success': False, 'error': 'No stats available'}), 404
    with open(stats_path, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/tipster-stats/fut5tips', methods=['GET'])
def get_fut5tips_stats():
    stats_path = os.path.join(os.path.dirname(__file__), 'data', 'tipster_stats.json')
    if not os.path.exists(stats_path):
        return jsonify({'success': False, 'error': 'No stats found'}), 404
    with open(stats_path, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/apifootball-fixtures')
def api_apifootball_fixtures():
    data = load_json_data('apifootball_fixtures.json')
    return jsonify({'success': bool(data), 'data': data})

@app.route('/api/footballdata-laliga')
def api_footballdata_laliga():
    data = load_json_data('footballdata_laliga.json')
    return jsonify({'success': bool(data), 'data': data})

@app.route('/api/whoscored-laliga')
def api_whoscored_laliga():
    data = load_json_data('whoscored_laliga.json')
    return jsonify({'success': bool(data), 'data': data})

@app.route('/api/transfermarkt/transfers', methods=['GET'])
def get_transfermarkt_transfers():
    """Devuelve los traspasos recientes de LaLiga desde Transfermarkt"""
    season = request.args.get('season', '2024')
    limit = int(request.args.get('limit', 20))
    league_id = request.args.get('league_id', 'ES1')
    scraper = TransfermarktScraper()
    transfers = scraper.scrape_transfers(league_id=league_id, season=season, limit=limit)
    return jsonify({
        'success': True,
        'transfers': transfers,
        'total': len(transfers)
    })

@app.route('/api/transfermarkt/market-values', methods=['GET'])
def get_transfermarkt_market_values():
    """Devuelve los valores de mercado de equipos y jugadores de LaLiga desde Transfermarkt"""
    season = request.args.get('season', '2024')
    league_id = request.args.get('league_id', 'ES1')
    scraper = TransfermarktScraper()
    market_values = scraper.scrape_market_values(league_id=league_id, season=season)
    return jsonify({
        'success': True,
        'market_values': market_values,
        'total_teams': len(market_values)
    })

@app.route('/api/transfermarkt/squads', methods=['GET'])
def get_transfermarkt_squads():
    """Devuelve las plantillas de equipos de LaLiga desde Transfermarkt"""
    season = request.args.get('season', '2024')
    league_id = request.args.get('league_id', 'ES1')
    scraper = TransfermarktScraper()
    squads = scraper.scrape_squads(league_id=league_id, season=season)
    return jsonify({
        'success': True,
        'squads': squads,
        'total_teams': len(squads)
    })

# --- Transfermarkt DB Endpoints ---
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@app.route('/api/transfermarkt/db/teams', methods=['GET'])
def get_transfermarkt_db_teams():
    session = Session()
    teams = session.query(TransfermarktTeam).all()
    result = [
        {
            'id': t.id,
            'name': t.name,
            'league': t.league,
            'season': t.season,
            'market_value': t.market_value,
            'last_updated': t.last_updated.isoformat() if t.last_updated else None
        } for t in teams
    ]
    session.close()
    return jsonify({'success': True, 'teams': result, 'total': len(result)})

@app.route('/api/transfermarkt/db/players', methods=['GET'])
def get_transfermarkt_db_players():
    session = Session()
    team_id = request.args.get('team_id')
    q = session.query(TransfermarktPlayer)
    if team_id:
        q = q.filter_by(team_id=team_id)
    players = q.all()
    result = [
        {
            'id': p.id,
            'name': p.name,
            'position': p.position,
            'age': p.age,
            'nationality': p.nationality,
            'market_value': p.market_value,
            'team_id': p.team_id,
            'last_updated': p.last_updated.isoformat() if p.last_updated else None
        } for p in players
    ]
    session.close()
    return jsonify({'success': True, 'players': result, 'total': len(result)})

@app.route('/api/transfermarkt/db/transfers', methods=['GET'])
def get_transfermarkt_db_transfers():
    session = Session()
    season = request.args.get('season')
    league = request.args.get('league')
    q = session.query(TransfermarktTransfer)
    if season:
        q = q.filter_by(season=season)
    if league:
        q = q.filter_by(league=league)
    transfers = q.all()
    result = [
        {
            'id': t.id,
            'player_name': t.player_name,
            'from_team': t.from_team,
            'to_team': t.to_team,
            'fee': t.fee,
            'transfer_type': t.transfer_type,
            'season': t.season,
            'league': t.league,
            'last_updated': t.last_updated.isoformat() if t.last_updated else None
        } for t in transfers
    ]
    session.close()
    return jsonify({'success': True, 'transfers': result, 'total': len(result)})

@app.route('/api/bot-ambos-marcan')
def api_bot_ambos_marcan():
    data = load_json_data('processed/latest_data.json')
    picks = []
    if data:
        for pick in data.get('recent_picks', []):
            if pick.get('prediction_type', '').lower() in ['both teams score', 'both_teams_score'] and pick.get('confidence', 0) >= 70:
                picks.append({
                    'home_team': pick.get('home_team'),
                    'away_team': pick.get('away_team'),
                    'competition': pick.get('competition'),
                    'match_time': pick.get('match_time'),
                    'probability': pick.get('confidence', 0) / 100.0
                })
    return jsonify(picks)

@app.route('/api/bot-tarjetas')
def api_bot_tarjetas():
    data = load_json_data('processed/latest_data.json')
    picks = []
    if data:
        for pick in data.get('recent_picks', []):
            if pick.get('prediction_type', '').lower() in ['cards', 'tarjetas', 'yellow cards', 'red cards'] and pick.get('confidence', 0) >= 70:
                picks.append({
                    'home_team': pick.get('home_team'),
                    'away_team': pick.get('away_team'),
                    'competition': pick.get('competition'),
                    'match_time': pick.get('match_time'),
                    'probability': pick.get('confidence', 0) / 100.0
                })
    return jsonify(picks)

@app.route('/api/bot-corneres')
def api_bot_corneres():
    data = load_json_data('processed/latest_data.json')
    picks = []
    if data:
        for pick in data.get('recent_picks', []):
            if pick.get('prediction_type', '').lower() in ['corners', 'corneres'] and pick.get('confidence', 0) >= 70:
                picks.append({
                    'home_team': pick.get('home_team'),
                    'away_team': pick.get('away_team'),
                    'competition': pick.get('competition'),
                    'match_time': pick.get('match_time'),
                    'probability': pick.get('confidence', 0) / 100.0
                })
    return jsonify(picks)

@app.route('/api/bot-empates')
def api_bot_empates():
    data = load_json_data('processed/latest_data.json')
    picks = []
    if data:
        for pick in data.get('recent_picks', []):
            if pick.get('prediction_type', '').lower() in ['draw', 'empate'] and pick.get('confidence', 0) >= 70:
                picks.append({
                    'home_team': pick.get('home_team'),
                    'away_team': pick.get('away_team'),
                    'competition': pick.get('competition'),
                    'match_time': pick.get('match_time'),
                    'probability': pick.get('confidence', 0) / 100.0
                })
    return jsonify(picks)

@app.route('/api/paypal-payment-success', methods=['POST'])
def paypal_payment_success():
    data = request.get_json()
    email = data.get('email')
    bot = data.get('bot')
    if not email or not bot:
        return jsonify({'success': False, 'error': 'Faltan datos'}), 400
    try:
        log_payment(email, bot)
        return jsonify({'success': True, 'message': 'Pago registrado en Google Sheets'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 