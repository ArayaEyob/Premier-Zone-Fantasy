from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime, timedelta
import os
import threading
import time
import subprocess
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global variable to store stats data
stats_data = {}
last_update = None

def load_stats_data():
    """Load the latest stats data from CSV files"""
    global stats_data, last_update
    
    try:
        # Load main stats data
        if os.path.exists('stats.csv'):
            df = pd.read_csv('stats.csv')
            
            # Convert to JSON format for API
            players = df.to_dict('records')
            
            # Get top performers
            top_scorers = df.nlargest(10, 'Gls')[['Player', 'Team', 'Gls', 'Ast', 'total_points']].to_dict('records')
            top_assists = df.nlargest(10, 'Ast')[['Player', 'Team', 'Ast', 'Gls', 'total_points']].to_dict('records')
            top_points = df.nlargest(10, 'total_points')[['Player', 'Team', 'total_points', 'Gls', 'Ast']].to_dict('records')
            
            # Team statistics
            team_stats = df.groupby('Team').agg({
                'Gls': 'sum',
                'Ast': 'sum',
                'total_points': 'sum',
                'Player': 'count'
            }).reset_index()
            team_stats.columns = ['Team', 'TotalGoals', 'TotalAssists', 'TotalPoints', 'PlayerCount']
            team_stats = team_stats.to_dict('records')
            
            # Update global stats data
            stats_data = {
                'players': players,
                'top_scorers': top_scorers,
                'top_assists': top_assists,
                'top_points': top_points,
                'team_stats': team_stats,
                'total_players': len(players),
                'total_teams': df['Team'].nunique(),
                'last_updated': datetime.now().isoformat(),
                'status': 'success'
            }
            
            last_update = datetime.now()
            print(f"✅ Stats data loaded: {len(players)} players, {df['Team'].nunique()} teams")
            
        else:
            stats_data = {'error': 'Stats file not found', 'status': 'error'}
            print("❌ stats.csv not found")
            
    except Exception as e:
        stats_data = {'error': str(e), 'status': 'error'}
        print(f"❌ Error loading stats: {e}")

def update_stats_automatically():
    """Run the stats collection script automatically"""
    try:
        print("🔄 Running automatic stats update...")
        result = subprocess.run([
            sys.executable, 'football_stats.py'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ Stats updated successfully")
            load_stats_data()
        else:
            print(f"❌ Stats update failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error updating stats: {e}")

def background_updater():
    """Background thread to update stats every hour"""
    while True:
        time.sleep(3600)  # Wait 1 hour
        update_stats_automatically()

@app.route('/api/stats')
def get_stats():
    """Get all stats data"""
    if not stats_data:
        load_stats_data()
    return jsonify(stats_data)

@app.route('/api/stats/players')
def get_players():
    """Get all players data"""
    if not stats_data:
        load_stats_data()
    return jsonify(stats_data.get('players', []))

@app.route('/api/stats/top-scorers')
def get_top_scorers():
    """Get top scorers"""
    if not stats_data:
        load_stats_data()
    return jsonify(stats_data.get('top_scorers', []))

@app.route('/api/stats/top-assists')
def get_top_assists():
    """Get top assist providers"""
    if not stats_data:
        load_stats_data()
    return jsonify(stats_data.get('top_assists', []))

@app.route('/api/stats/top-points')
def get_top_points():
    """Get top fantasy points"""
    if not stats_data:
        load_stats_data()
    return jsonify(stats_data.get('top_points', []))

@app.route('/api/stats/teams')
def get_team_stats():
    """Get team statistics"""
    if not stats_data:
        load_stats_data()
    return jsonify(stats_data.get('team_stats', []))

@app.route('/api/stats/summary')
def get_summary():
    """Get summary statistics"""
    if not stats_data:
        load_stats_data()
    
    summary = {
        'total_players': stats_data.get('total_players', 0),
        'total_teams': stats_data.get('total_teams', 0),
        'last_updated': stats_data.get('last_updated'),
        'status': stats_data.get('status', 'unknown')
    }
    
    if 'top_scorers' in stats_data and stats_data['top_scorers']:
        summary['leading_scorer'] = stats_data['top_scorers'][0]
    
    if 'top_assists' in stats_data and stats_data['top_assists']:
        summary['leading_assists'] = stats_data['top_assists'][0]
    
    return jsonify(summary)

@app.route('/api/stats/update')
def trigger_update():
    """Manually trigger stats update"""
    try:
        update_stats_automatically()
        return jsonify({'status': 'success', 'message': 'Stats update triggered'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': bool(stats_data),
        'last_update': last_update.isoformat() if last_update else None
    })

if __name__ == '__main__':
    print("🚀 Starting Premier League Stats API Server...")
    
    # Load initial data
    load_stats_data()
    
    # Start background updater thread
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    print("📊 Stats API Server running on http://localhost:5000")
    print("🔄 Automatic updates every hour")
    print("\nAvailable endpoints:")
    print("  📈 /api/stats - All stats data")
    print("  👥 /api/stats/players - All players")
    print("  🥅 /api/stats/top-scorers - Top scorers")
    print("  🎯 /api/stats/top-assists - Top assists")
    print("  👑 /api/stats/top-points - Top fantasy points")
    print("  🏟️ /api/stats/teams - Team statistics")
    print("  📋 /api/stats/summary - Summary stats")
    print("  🔄 /api/stats/update - Manual update trigger")
    print("  💚 /api/health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)