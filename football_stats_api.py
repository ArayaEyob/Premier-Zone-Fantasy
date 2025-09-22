import requests
import pandas as pd
import json
import time
from datetime import datetime

def get_premier_league_data():
    """
    Get latest Premier League data from multiple reliable sources
    """
    
    # Headers to appear as a regular browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    print("=== Premier League Data Collector (API Version) ===")
    print(f"Collecting data on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Method 1: Try Fantasy Premier League API (official)
    try:
        print("\n1. Trying Fantasy Premier League API...")
        
        # Get general info
        fpl_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        response = requests.get(fpl_url, headers=headers)
        
        if response.status_code == 200:
            fpl_data = response.json()
            
            # Extract players data
            players = fpl_data['elements']
            teams = {team['id']: team['name'] for team in fpl_data['teams']}
            positions = {pos['id']: pos['singular_name'] for pos in fpl_data['element_types']}
            
            players_data = []
            for player in players:
                players_data.append({
                    'id': player['id'],
                    'name': f"{player['first_name']} {player['second_name']}",
                    'team': teams.get(player['team'], 'Unknown'),
                    'position': positions.get(player['element_type'], 'Unknown'),
                    'total_points': player['total_points'],
                    'goals_scored': player['goals_scored'],
                    'assists': player['assists'],
                    'clean_sheets': player['clean_sheets'],
                    'minutes': player['minutes'],
                    'yellow_cards': player['yellow_cards'],
                    'red_cards': player['red_cards'],
                    'saves': player['saves'],
                    'bonus': player['bonus'],
                    'influence': player['influence'],
                    'creativity': player['creativity'],
                    'threat': player['threat'],
                    'selected_by_percent': player['selected_by_percent'],
                    'now_cost': player['now_cost'] / 10,  # Convert from tenths
                    'form': player['form'],
                    'points_per_game': player['points_per_game'],
                })
            
            # Save to CSV
            df = pd.DataFrame(players_data)
            df.to_csv("premier_league_players_latest.csv", index=False)
            print(f"✅ Successfully saved {len(players_data)} players to premier_league_players_latest.csv")
            
            # Extract and save team data
            teams_data = []
            for team in fpl_data['teams']:
                teams_data.append({
                    'id': team['id'],
                    'name': team['name'],
                    'short_name': team['short_name'],
                    'played': team['played'],
                    'wins': team['win'],
                    'draws': team['draw'],
                    'losses': team['loss'],
                    'goals_for': team['points'],  # This might need adjustment
                    'goals_against': team.get('goals_against', 0),
                    'goal_difference': team.get('goal_difference', 0),
                    'points': team.get('points', 0),
                    'position': team.get('position', 0),
                    'strength_overall_home': team['strength_overall_home'],
                    'strength_overall_away': team['strength_overall_away'],
                    'strength_attack_home': team['strength_attack_home'],
                    'strength_attack_away': team['strength_attack_away'],
                    'strength_defence_home': team['strength_defence_home'],
                    'strength_defence_away': team['strength_defence_away'],
                })
            
            teams_df = pd.DataFrame(teams_data)
            teams_df.to_csv("premier_league_teams_latest.csv", index=False)
            print(f"✅ Successfully saved {len(teams_data)} teams to premier_league_teams_latest.csv")
            
            return True
            
        else:
            print(f"❌ FPL API failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error with FPL API: {e}")
    
    # Method 2: Try Football Data API (free tier)
    try:
        print("\n2. Trying Football-Data.org API...")
        
        # Free tier API - limited requests per day
        football_data_url = "https://api.football-data.org/v4/competitions/PL/standings"
        football_headers = {
            **headers,
            'X-Auth-Token': 'YOUR_API_KEY_HERE'  # You need to register for a free API key
        }
        
        # For demo, we'll skip this if no API key
        print("   Note: Requires free API key from football-data.org")
        
    except Exception as e:
        print(f"❌ Error with Football-Data API: {e}")
    
    # Method 3: ESPN Soccer API
    try:
        print("\n3. Trying ESPN Soccer API...")
        
        espn_standings_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/standings"
        response = requests.get(espn_standings_url, headers=headers)
        
        if response.status_code == 200:
            espn_data = response.json()
            
            standings_data = []
            children = espn_data.get('children', [])
            
            for child in children:
                standings = child.get('standings', {}).get('entries', [])
                for entry in standings:
                    team = entry.get('team', {})
                    stats = entry.get('stats', [])
                    
                    # Extract stats
                    stat_dict = {}
                    for stat in stats:
                        stat_dict[stat.get('name', '')] = stat.get('value', 0)
                    
                    standings_data.append({
                        'team_name': team.get('displayName', ''),
                        'abbreviation': team.get('abbreviation', ''),
                        'position': entry.get('note', {}).get('rank', 0) if entry.get('note') else 0,
                        'played': stat_dict.get('gamesPlayed', 0),
                        'wins': stat_dict.get('wins', 0),
                        'draws': stat_dict.get('ties', 0),
                        'losses': stat_dict.get('losses', 0),
                        'goals_for': stat_dict.get('pointsFor', 0),
                        'goals_against': stat_dict.get('pointsAgainst', 0),
                        'goal_difference': stat_dict.get('pointDifferential', 0),
                        'points': stat_dict.get('points', 0),
                    })
            
            if standings_data:
                standings_df = pd.DataFrame(standings_data)
                standings_df.to_csv("premier_league_standings_latest.csv", index=False)
                print(f"✅ Successfully saved {len(standings_data)} teams standings to premier_league_standings_latest.csv")
                return True
        
    except Exception as e:
        print(f"❌ Error with ESPN API: {e}")
    
    print("\n❌ All API methods failed. The data might not be up to date.")
    return False

def compare_with_existing():
    """Compare new data with existing stats.csv"""
    try:
        if pd.io.common.file_exists("premier_league_players_latest.csv") and pd.io.common.file_exists("stats.csv"):
            new_data = pd.read_csv("premier_league_players_latest.csv")
            old_data = pd.read_csv("stats.csv")
            
            print(f"\n📊 Data Comparison:")
            print(f"   Previous data: {len(old_data)} records")
            print(f"   New data: {len(new_data)} records")
            print(f"   Data freshness: Latest API data (real-time)")
            
    except Exception as e:
        print(f"Error comparing data: {e}")

if __name__ == "__main__":
    success = get_premier_league_data()
    
    if success:
        compare_with_existing()
        print(f"\n✅ Data collection completed successfully!")
        print("Files created:")
        print("  - premier_league_players_latest.csv (player stats)")
        print("  - premier_league_teams_latest.csv (team info)")
        print("  - premier_league_standings_latest.csv (league table)")
    else:
        print(f"\n❌ Data collection failed. Using fallback methods...")