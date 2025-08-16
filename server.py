from flask import Flask, jsonify
import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend funcionando ✅"

@app.route("/api/site-data.json")
def site_data():
    data = {
        "ai_stats": {
            "models_accuracy": 87.3,
            "data_points": 124567,
            "win_rate": 72.1,
            "roi": 13.4,
            "updates_per_hour": 2,
            "last_update": datetime.datetime.utcnow().isoformat()
        },
        "bots": [
            {"name": "CornersMaster", "bot_type": "corners", "description": "Especialista en córners", "win_rate": 71.4, "total_predictions": 1423, "roi": 11.2},
            {"name": "CardsGuard", "bot_type": "cards", "description": "Especialista en tarjetas", "win_rate": 68.9, "total_predictions": 980, "roi": 9.1},
            {"name": "BothScorePro", "bot_type": "both_score", "description": "Hace focus en ambos marcan", "win_rate": 74.2, "total_predictions": 2103, "roi": 15.9}
        ],
        "recent_predictions": [
            {"home_team":"Real Madrid","away_team":"Barcelona","match_date":datetime.datetime.utcnow().isoformat(),"league":"La Liga","bot":{"name":"BothScorePro"},"prediction_value":"Ambos marcan","odds":"2.10","confidence":87},
            {"home_team":"Atletico","away_team":"Valencia","match_date":datetime.datetime.utcnow().isoformat(),"league":"La Liga","bot":{"name":"CornersMaster"},"prediction_value":"Más de 9 córners","odds":"1.85","confidence":79}
        ]
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
