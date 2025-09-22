import requests
import pandas as pd
import json
import time
from datetime import datetime

def get_current_season_data():
    """
    Get the most up-to-date Premier League data for 2025/26 season
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    print("=== CURRENT PREMIER LEAGUE DATA COLLECTOR ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Season: 2025/26")
    
    success = False
    
    # Get Fantasy Premier League data (most reliable for current season)
    try:
        print("\n🔄 Fetching current Fantasy Premier League data...")
        
        fpl_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        response = requests.get(fpl_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            fpl_data = response.json()
            
            # Current gameweek info
            current_gw = None
            for gw in fpl_data['events']:
                if gw['is_current']:
                    current_gw = gw['id']
                    break
            
            if not current_gw:
                current_gw = max([gw['id'] for gw in fpl_data['events'] if gw['finished']])
                
            print(f"📊 Current Gameweek: {current_gw}")
            
            # Extract current players data
            players = fpl_data['elements']
            teams = {team['id']: team['name'] for team in fpl_data['teams']}
            positions = {pos['id']: pos['singular_name_short'] for pos in fpl_data['element_types']}
            
            current_players_data = []
            for player in players:
                # Only include players who have played this season
                if player['total_points'] > 0 or player['minutes'] > 0:
                    current_players_data.append({
                        'player_id': player['id'],
                        'name': f"{player['first_name']} {player['second_name']}",
                        'team': teams.get(player['team'], 'Unknown'),
                        'position': positions.get(player['element_type'], 'Unknown'),
                        'total_points': player['total_points'],
                        'goals': player['goals_scored'],
                        'assists': player['assists'],
                        'clean_sheets': player['clean_sheets'],
                        'minutes_played': player['minutes'],
                        'yellow_cards': player['yellow_cards'],
                        'red_cards': player['red_cards'],
                        'saves': player['saves'],
                        'bonus_points': player['bonus'],
                        'influence': float(player['influence']),
                        'creativity': float(player['creativity']),
                        'threat': float(player['threat']),
                        'selected_by_percent': float(player['selected_by_percent']),
                        'price': player['now_cost'] / 10,
                        'form': float(player['form']),
                        'points_per_game': float(player['points_per_game']) if player['points_per_game'] else 0.0,
                        'dreamteam_count': player['dreamteam_count'],
                        'value_form': float(player['value_form']),
                        'value_season': float(player['value_season']),
                        'news': player['news'],
                        'chance_of_playing_this_round': player['chance_of_playing_this_round'],
                        'chance_of_playing_next_round': player['chance_of_playing_next_round'],
                    })
            
            # Save current season player data
            df_players = pd.DataFrame(current_players_data)
            df_players = df_players.sort_values(['total_points'], ascending=False)
            df_players.to_csv("current_season_players.csv", index=False)
            print(f"✅ Saved {len(current_players_data)} current season players")
            
            # Extract current teams data with more details
            current_teams_data = []
            for team in fpl_data['teams']:
                current_teams_data.append({
                    'team_id': team['id'],
                    'name': team['name'],
                    'short_name': team['short_name'],
                    'code': team['code'],
                    'played': team['played'],
                    'wins': team['win'],
                    'draws': team['draw'],
                    'losses': team['loss'],
                    'goals_for': team['points'],
                    'goals_against': team.get('goals_against', 0),
                    'goal_difference': team.get('goal_difference', 0),
                    'league_points': team.get('points', 0),
                    'position': team.get('position', 0),
                    'form': team.get('form', []),
                    'strength_overall_home': team['strength_overall_home'],
                    'strength_overall_away': team['strength_overall_away'],
                    'strength_attack_home': team['strength_attack_home'],
                    'strength_attack_away': team['strength_attack_away'],
                    'strength_defence_home': team['strength_defence_home'],
                    'strength_defence_away': team['strength_defence_away'],
                    'pulse_id': team['pulse_id'],
                })
            
            df_teams = pd.DataFrame(current_teams_data)
            df_teams = df_teams.sort_values('position')
            df_teams.to_csv("current_season_teams.csv", index=False)
            print(f"✅ Saved {len(current_teams_data)} teams data")
            
            # Create summary statistics
            summary = {
                'data_collection_date': datetime.now().isoformat(),
                'season': '2025/26',
                'current_gameweek': current_gw,
                'total_players': len(current_players_data),
                'total_teams': len(current_teams_data),
                'top_scorer': df_players.iloc[0]['name'] if not df_players.empty else 'N/A',
                'top_scorer_goals': int(df_players.iloc[0]['goals']) if not df_players.empty else 0,
                'most_assists': df_players.nlargest(1, 'assists').iloc[0]['name'] if not df_players.empty else 'N/A',
                'most_assists_count': int(df_players.nlargest(1, 'assists').iloc[0]['assists']) if not df_players.empty else 0,
            }
            
            with open('current_season_summary.json', 'w') as f:
                json.dump(summary, f, indent=2)
            print("✅ Saved season summary")
            
            success = True
            
        else:
            print(f"❌ FPL API returned status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error fetching FPL data: {e}")
    
    return success

def display_current_stats():
    """Display current season highlights"""
    try:
        df_players = pd.read_csv("current_season_players.csv")
        df_teams = pd.read_csv("current_season_teams.csv")
        
        print(f"\n🏆 === CURRENT SEASON HIGHLIGHTS ===")
        print(f"📈 Total Players: {len(df_players)}")
        print(f"⚽ Total Teams: {len(df_teams)}")
        
        print(f"\n🥅 TOP 5 GOALSCORERS:")
        top_scorers = df_players.nlargest(5, 'goals')[['name', 'team', 'goals', 'assists', 'total_points']]
        for idx, player in top_scorers.iterrows():
            print(f"   {player['goals']:2d} goals - {player['name']} ({player['team']})")
        
        print(f"\n🎯 TOP 5 ASSIST PROVIDERS:")
        top_assists = df_players.nlargest(5, 'assists')[['name', 'team', 'assists', 'goals', 'total_points']]
        for idx, player in top_assists.iterrows():
            print(f"   {player['assists']:2d} assists - {player['name']} ({player['team']})")
        
        print(f"\n👑 TOP 5 FANTASY POINTS:")
        top_points = df_players.nlargest(5, 'total_points')[['name', 'team', 'total_points', 'goals', 'assists']]
        for idx, player in top_points.iterrows():
            print(f"   {player['total_points']:3d} points - {player['name']} ({player['team']})")
        
        print(f"\n💰 MOST EXPENSIVE PLAYERS:")
        expensive = df_players.nlargest(5, 'price')[['name', 'team', 'price', 'total_points']]
        for idx, player in expensive.iterrows():
            print(f"   £{player['price']:.1f}m - {player['name']} ({player['team']})")
            
        return True
        
    except Exception as e:
        print(f"Error displaying stats: {e}")
        return False

if __name__ == "__main__":
    success = get_current_season_data()
    
    if success:
        display_current_stats()
        print(f"\n✅ SUCCESS! Current season data collected and saved!")
        print(f"\nFiles created:")
        print(f"  📊 current_season_players.csv - Detailed player statistics")
        print(f"  🏟️  current_season_teams.csv - Team information and standings")
        print(f"  📋 current_season_summary.json - Season summary")
        print(f"\n🔄 This data is from the official Fantasy Premier League API")
        print(f"   and represents the most current 2025/26 season statistics!")
    else:
        print(f"\n❌ Failed to collect current season data")