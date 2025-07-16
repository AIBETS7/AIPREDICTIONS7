from payment_processor import paypal_bp
from flask import Flask, jsonify
import os
import json

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

@app.route('/api/apifootball-fixtures')
def api_apifootball_fixtures():
    data = load_json_data('apifootball_fixtures.json')
    return jsonify({'success': bool(data), 'data': data})

@app.route('/api/footballdata-laliga')
def api_footballdata_laliga():
    data = load_json_data('footballdata_laliga.json')
    return jsonify({'success': bool(data), 'data': data}) 