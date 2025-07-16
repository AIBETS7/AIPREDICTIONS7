from payment_processor import paypal_bp
from flask import Flask, jsonify
import os
import json

app = Flask(__name__)

app.register_blueprint(paypal_bp)

@app.route('/api/tipster-stats')
def get_tipster_stats():
    stats_path = os.path.join(os.path.dirname(__file__), 'data', 'tipster_stats.json')
    if not os.path.exists(stats_path):
        return jsonify({'success': False, 'error': 'No stats available'}), 404
    with open(stats_path, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    return jsonify({'success': True, 'stats': stats}) 