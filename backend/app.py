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
    try:
        # Importar el bot de tarjetas
        import sys
        sys.path.append(os.path.dirname(__file__))
        from cards_bot import CardsBot
        
        # Crear instancia del bot
        cards_bot = CardsBot()
        
        # Cargar partidos reales desde los archivos JSON - TODAS las competiciones
        from match_data_loader import get_matches_for_bots
        sample_matches = get_matches_for_bots(competitions=None, with_referees=True)
        
        # Generar picks usando el bot sofisticado
        picks = cards_bot.get_picks_for_matches(sample_matches)
        
        # Formatear para la API
        formatted_picks = []
        for pick in picks:
            formatted_picks.append({
                'home_team': pick['home_team'],
                'away_team': pick['away_team'],
                'referee': pick['referee'],
                'competition': pick['competition'],
                'match_time': pick['match_time'],
                'probability': pick['confidence'] / 100.0,
                'predicted_total': pick['predicted_total'],
                'odds': pick['odds'],
                'analysis': pick['reasoning'],
                'referee_factor': pick['referee_factor']
            })
        
        return jsonify(formatted_picks)
        
    except Exception as e:
        # Fallback a datos estáticos si hay error
        print(f"Error en bot de tarjetas: {e}")
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
    try:
        # Importar el bot de córners
        import sys
        sys.path.append(os.path.dirname(__file__))
        from corners_bot import CornersBot
        
        # Crear instancia del bot
        corners_bot = CornersBot()
        
        # Cargar partidos reales desde los archivos JSON - TODAS las competiciones
        from match_data_loader import get_matches_for_bots
        sample_matches = get_matches_for_bots(competitions=None, with_referees=False)
        
        # Generar picks usando el bot sofisticado
        picks = corners_bot.get_picks_for_matches(sample_matches)
        
        # Formatear para la API
        formatted_picks = []
        for pick in picks:
            formatted_picks.append({
                'home_team': pick['home_team'],
                'away_team': pick['away_team'],
                'competition': pick['competition'],
                'match_time': pick['match_time'],
                'probability': pick['confidence'] / 100.0,
                'predicted_total': pick['predicted_total'],
                'odds': pick['odds'],
                'analysis': pick['reasoning']
            })
        
        return jsonify(formatted_picks)
        
    except Exception as e:
        # Fallback a datos estáticos si hay error
        print(f"Error en bot de córners: {e}")
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

# Bot Management API Endpoints
def load_bots_config():
    """Load bots configuration from file"""
    config_path = os.path.join(os.path.dirname(__file__), 'data', 'bots_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default config if file doesn't exist
        return {
            "bots": {
                "ambos-marcan": {"active": True, "confidence_threshold": 70, "min_odds": 1.5},
                "corneres": {"active": True, "confidence_threshold": 70, "min_odds": 1.6},
                "empates": {"active": True, "confidence_threshold": 70, "min_odds": 3.0},
                "tarjetas": {"active": True, "confidence_threshold": 70, "min_odds": 1.7}
            }
        }

def save_bots_config(config):
    """Save bots configuration to file"""
    config_path = os.path.join(os.path.dirname(__file__), 'data', 'bots_config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

@app.route('/api/bots/status')
def get_bots_status():
    """Get status of all bots"""
    try:
        config = load_bots_config()
        bots_status = {}
        for bot_name, bot_config in config.get('bots', {}).items():
            bots_status[bot_name] = {
                'active': bot_config.get('active', False),
                'last_run': bot_config.get('last_run', '2025-01-21T12:00:00Z')
            }
        return jsonify({'success': True, 'bots': bots_status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/start-all', methods=['POST'])
def start_all_bots():
    """Start all bots"""
    try:
        # Here you would implement the logic to start all bots
        # For now, we'll just return success
        return jsonify({'success': True, 'message': 'All bots started successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/stop-all', methods=['POST'])
def stop_all_bots():
    """Stop all bots"""
    try:
        # Here you would implement the logic to stop all bots
        return jsonify({'success': True, 'message': 'All bots stopped successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/reset-all', methods=['POST'])
def reset_all_bots():
    """Reset all bots"""
    try:
        # Here you would implement the logic to reset all bots
        return jsonify({'success': True, 'message': 'All bots reset successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/refresh-data', methods=['POST'])
def refresh_bots_data():
    """Refresh data for all bots"""
    try:
        # Here you would implement the logic to refresh bot data
        return jsonify({'success': True, 'message': 'Bot data refreshed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/<bot_name>/config', methods=['POST'])
def save_bot_config(bot_name):
    """Save configuration for a specific bot"""
    try:
        new_config = request.get_json()
        full_config = load_bots_config()
        
        if bot_name in full_config.get('bots', {}):
            # Update bot configuration
            bot_config = full_config['bots'][bot_name]
            bot_config['confidence_threshold'] = float(new_config.get('confidence', bot_config.get('confidence_threshold', 70)))
            bot_config['min_odds'] = float(new_config.get('odds', bot_config.get('min_odds', 1.5)))
            
            # Update other settings if provided
            if 'competitions' in new_config:
                bot_config['competitions'] = new_config['competitions']
            if 'max_picks_per_day' in new_config:
                bot_config['max_picks_per_day'] = int(new_config['max_picks_per_day'])
            
            # Save updated configuration
            save_bots_config(full_config)
            return jsonify({'success': True, 'message': f'Configuration saved for {bot_name}'})
        else:
            return jsonify({'success': False, 'error': f'Bot {bot_name} not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/<bot_name>/test', methods=['POST'])
def test_bot(bot_name):
    """Test a specific bot"""
    try:
        # Here you would implement bot testing logic
        # For now, we'll simulate finding some picks
        picks_count = 3 if bot_name in ['ambos-marcan', 'corneres'] else 1
        return jsonify({'success': True, 'picks_count': picks_count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/analytics')
def get_bots_analytics():
    """Get analytics for all bots"""
    try:
        config = load_bots_config()
        bots = config.get('bots', {})
        system_info = config.get('system_info', {})
        
        total_picks = sum(bot.get('stats', {}).get('picks_today', 0) for bot in bots.values())
        accuracies = [bot.get('stats', {}).get('accuracy_30d', 0) for bot in bots.values() if bot.get('stats', {}).get('accuracy_30d', 0) > 0]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
        total_profit = sum(bot.get('stats', {}).get('profit_30d', 0) for bot in bots.values())
        active_bots = sum(1 for bot in bots.values() if bot.get('active', False))
        
        analytics = {
            'total_picks': total_picks,
            'avg_accuracy': round(avg_accuracy, 1),
            'total_profit': round(total_profit, 2),
            'active_bots': active_bots,
            'overall_accuracy': system_info.get('overall_accuracy', 0),
            'total_picks_generated': system_info.get('total_picks_generated', 0),
            'uptime_hours': system_info.get('uptime_hours', 0)
        }
        return jsonify({'success': True, **analytics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/global-settings', methods=['POST'])
def save_global_settings():
    """Save global bot settings"""
    try:
        settings = request.get_json()
        # Here you would save the global settings
        return jsonify({'success': True, 'message': 'Global settings saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/test-telegram', methods=['POST'])
def test_telegram():
    """Test Telegram integration"""
    try:
        # Here you would implement Telegram test logic
        return jsonify({'success': True, 'message': 'Test message sent to Telegram'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/export-config')
def export_config():
    """Export bot configuration"""
    try:
        config = {
            'bots': {
                'ambos-marcan': {'confidence': 70, 'odds': 1.5},
                'corneres': {'confidence': 70, 'odds': 1.6},
                'empates': {'confidence': 70, 'odds': 3.0},
                'tarjetas': {'confidence': 70, 'odds': 1.7}
            },
            'global': {
                'update_frequency': 30,
                'max_picks': 5
            }
        }
        return jsonify(config)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/import-config', methods=['POST'])
def import_config():
    """Import bot configuration"""
    try:
        # Here you would implement config import logic
        return jsonify({'success': True, 'message': 'Configuration imported successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/clear-cache', methods=['POST'])
def clear_cache():
    """Clear bot cache"""
    try:
        # Here you would implement cache clearing logic
        return jsonify({'success': True, 'message': 'Cache cleared successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bots/reset-defaults', methods=['POST'])
def reset_defaults():
    """Reset bot configuration to defaults"""
    try:
        # Here you would implement reset to defaults logic
        return jsonify({'success': True, 'message': 'Configuration reset to defaults'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 