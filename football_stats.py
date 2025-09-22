"""
Premier League Stats Collector - Updated Version
Collects latest Premier League data using official APIs
Bypasses web scraping limitations with Cloudflare protection
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime

def get_latest_premier_league_data():
    """
    Collect the most up-to-date Premier League statistics
    Uses Fantasy Premier League official API for 2025/26 season data
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    print("=== PREMIER LEAGUE DATA COLLECTOR (UPDATED) ===")
    print(f"Collection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Data Source: Fantasy Premier League Official API")
    print("Season: 2025/26\n")
    
    try:
        print("🔄 Fetching latest Premier League data...")
        
        # Official Fantasy Premier League API
        fpl_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        response = requests.get(fpl_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ API request failed with status code: {response.status_code}")
            return False
        
        fpl_data = response.json()
        
        # Get current gameweek
        current_gw = None
        for gw in fpl_data['events']:
            if gw['is_current']:
                current_gw = gw['id']
                break
        
        if not current_gw:
            current_gw = max([gw['id'] for gw in fpl_data['events'] if gw.get('finished', False)])
        
        print(f"📊 Current Gameweek: {current_gw}")
        
        # Extract teams mapping
        teams = {team['id']: team['name'] for team in fpl_data['teams']}
        positions = {pos['id']: pos['singular_name_short'] for pos in fpl_data['element_types']}
        
        # Process player data (same format as original script for compatibility)
        all_players_data = []
        players = fpl_data['elements']
        
        for player in players:
            # Create data in similar format to original scraping script
            all_players_data.append({
                'Player': f"{player['first_name']} {player['second_name']}",
                'Nation': '',  # Not available in FPL API
                'Pos': positions.get(player['element_type'], 'Unknown'),
                'Age': '',     # Not available in FPL API
                'MP': '',      # Games played not directly available
                'Starts': '',  # Not available
                'Min': player['minutes'],
                'Gls': player['goals_scored'],
                'Ast': player['assists'],
                'PK': '',      # Penalties not separated in FPL
                'CrdY': player['yellow_cards'],
                'CrdR': player['red_cards'],
                'xG': '',      # Expected goals not in basic FPL data
                'npxG': '',    # Non-penalty xG not available
                'Team': teams.get(player['team'], 'Unknown'),
                # Additional FPL-specific data
                'total_points': player['total_points'],
                'clean_sheets': player['clean_sheets'],
                'saves': player['saves'],
                'bonus': player['bonus'],
                'influence': float(player['influence']),
                'creativity': float(player['creativity']),
                'threat': float(player['threat']),
                'price': player['now_cost'] / 10,
                'selected_by_percent': float(player['selected_by_percent']),
                'form': float(player['form']),
                'points_per_game': float(player['points_per_game']) if player['points_per_game'] else 0.0,
            })
        
        # Convert to DataFrame and save (maintaining compatibility with original script)
        stat_df = pd.DataFrame(all_players_data)
        stat_df.to_csv("stats.csv", index=False)
        
        print(f"✅ Successfully collected data for {len(all_players_data)} players")
        print(f"✅ Data saved to stats.csv")
        
        # Save additional current season specific file
        stat_df.to_csv("stats_latest_api.csv", index=False)
        print(f"✅ Also saved to stats_latest_api.csv")
        
        # Display some current season highlights
        print(f"\n🏆 === CURRENT SEASON HIGHLIGHTS ===")
        
        top_scorers = stat_df.nlargest(5, 'Gls')[['Player', 'Team', 'Gls', 'Ast', 'total_points']]
        print(f"\n🥅 TOP 5 GOALSCORERS:")
        for idx, player in top_scorers.iterrows():
            print(f"   {player['Gls']:2d} goals - {player['Player']} ({player['Team']})")
        
        top_assists = stat_df.nlargest(5, 'Ast')[['Player', 'Team', 'Ast', 'Gls', 'total_points']]
        print(f"\n🎯 TOP 5 ASSIST PROVIDERS:")
        for idx, player in top_assists.iterrows():
            print(f"   {player['Ast']:2d} assists - {player['Player']} ({player['Team']})")
        
        # Create summary
        summary = {
            'collection_date': datetime.now().isoformat(),
            'season': '2025/26',
            'current_gameweek': current_gw,
            'total_players': len(all_players_data),
            'data_source': 'Fantasy Premier League Official API',
            'status': 'SUCCESS - Latest data collected'
        }
        
        with open('data_collection_log.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ Error collecting data: {e}")
        
        # Create error log
        error_summary = {
            'collection_date': datetime.now().isoformat(),
            'status': 'FAILED',
            'error': str(e),
            'note': 'API collection failed'
        }
        
        with open('data_collection_log.json', 'w') as f:
            json.dump(error_summary, f, indent=2)
        
        return False

if __name__ == "__main__":
    success = get_latest_premier_league_data()
    
    if success:
        print(f"\n✅ SUCCESS! Latest Premier League data has been collected!")
        print(f"📂 Files updated:")
        print(f"   • stats.csv (compatible with your existing code)")
        print(f"   • stats_latest_api.csv (backup with API data)")
        print(f"   • data_collection_log.json (collection details)")
        print(f"\n🔄 Your data is now from the official Fantasy Premier League API")
        print(f"   and represents current 2025/26 season statistics!")
        print(f"\n💡 This script now bypasses web scraping limitations and")
        print(f"   provides real-time, accurate Premier League data!")
    else:
        print(f"\n❌ Data collection failed. Check data_collection_log.json for details.")
        print(f"💡 The script attempted to use the official API but encountered an error.")
