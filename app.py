from flask import Flask, jsonify
from flask_cors import CORS
import os
import psycopg
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_db_connection():
    """Create a database connection using the DATABASE_URL environment variable"""
    try:
        # Get DATABASE_URL from environment variable
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("DATABASE_URL environment variable not set")
            return None
            
        if DATABASE_URL.startswith('postgresql://'):
            url = DATABASE_URL.replace('postgresql://', '')
            if '@' in url:
                credentials, rest = url.split('@')
                user, password = credentials.split(':')
                if '/' in rest:
                    host_port, database_with_params = rest.split('/', 1)
                    database = database_with_params.split('?')[0]
                    if ':' in host_port:
                        host, port = host_port.split(':')
                    else:
                        host, port = host_port, '5432'
                    conn = psycopg.connect(
                        host=host,
                        port=port,
                        dbname=database,
                        user=user,
                        password=password,
                        sslmode='require'
                    )
                    return conn
        else:
            print(f"Unsupported database URL format: {DATABASE_URL}")
            return None
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    return jsonify({"message": "Football Predictions API", "status": "running"})

@app.route('/api/daily-picks')
def get_daily_picks():
    """API endpoint to get today's picks"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify([])
        
        cursor = conn.cursor()
        
        # Get picks for today using match_time cast to timestamp
        today = datetime.now().date()
        query = """
        SELECT id, home_team, away_team, prediction, confidence, odds, stake, 
               reasoning, match_time, competition, created_at
        FROM daily_picks 
        WHERE match_time::timestamp::date = %s
        ORDER BY match_time ASC
        """
        cursor.execute(query, (today,))
        picks = cursor.fetchall()
        
        # Convert to list of dictionaries
        picks_list = []
        for pick in picks:
            picks_list.append({
                'id': pick[0],
                'home_team': pick[1],
                'away_team': pick[2],
                'prediction': pick[3],
                'confidence': pick[4],
                'odds': pick[5],
                'stake': pick[6],
                'reasoning': pick[7],
                'match_time': pick[8],
                'competition': pick[9],
                'created_at': pick[10]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(picks_list)
        
    except Exception as e:
        print(f"Error fetching daily picks: {e}")
        return jsonify([])

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port) 