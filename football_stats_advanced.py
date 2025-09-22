from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import time
import os

def setup_driver():
    """Setup Chrome driver with options to bypass bot detection"""
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Run in headless mode (comment out next line if you want to see the browser)
    # options.add_argument('--headless')
    
    try:
        driver = webdriver.Chrome(options=options)
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure Chrome and ChromeDriver are installed")
        return None

def get_team_stats_selenium():
    """Get Premier League team stats using Selenium"""
    driver = setup_driver()
    if not driver:
        return False
    
    all_teams = []
    
    try:
        print("Fetching Premier League main page with Selenium...")
        driver.get("https://fbref.com/en/comps/9/Premier-League-Stats")
        
        # Wait for the page to load and check if we're blocked
        time.sleep(5)
        
        # Check if we hit Cloudflare protection
        if "Just a moment" in driver.title or "cloudflare" in driver.page_source.lower():
            print("Cloudflare protection detected. Waiting...")
            time.sleep(10)  # Wait longer for Cloudflare to pass
        
        # Get page source after potential Cloudflare check
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        
        # Look for stats tables
        tables = soup.find_all('table', class_="stats_table")
        
        if not tables:
            print("No stats_table found. Looking for alternative table structures...")
            # Check for other possible table classes
            all_tables = soup.find_all('table')
            print(f"Found {len(all_tables)} total tables")
            
            # Look for tables with team data
            for table in all_tables:
                links = table.find_all('a')
                squad_links = [l for l in links if l.get('href') and '/squads/' in l.get('href')]
                if squad_links:
                    tables = [table]
                    break
        
        if not tables:
            print("No suitable tables found")
            return False
            
        table = tables[0]
        links = table.find_all('a')
        links = [l.get("href") for l in links]
        links = [l for l in links if l and "/squads" in l]
        
        if not links:
            print("No team links found")
            return False
            
        team_urls = [f"https://fbref.com{l}" for l in links]
        print(f"Found {len(team_urls)} teams to scrape")
        
        # Scrape each team
        for i, team_url in enumerate(team_urls):
            team_name = team_url.split("/")[-1].replace("-Stats", "").replace("Stats", "")
            print(f"Scraping team {i+1}/{len(team_urls)}: {team_name}")
            
            try:
                driver.get(team_url)
                time.sleep(3)  # Wait for page to load
                
                html = driver.page_source
                soup = BeautifulSoup(html, "lxml")
                stats_tables = soup.find_all("table", class_="stats_table")
                
                if not stats_tables:
                    print(f"No stats_table found for team: {team_name}")
                    continue
                    
                stats = stats_tables[0]
                
                # Convert table to DataFrame
                html_data = StringIO(str(stats))
                team_data = pd.read_html(html_data)[0]
                team_data["Team"] = team_name
                all_teams.append(team_data)
                
                # Random delay to avoid being too aggressive
                time.sleep(2 + (i % 3))  # 2-4 second delay
                
            except Exception as e:
                print(f"Error scraping {team_name}: {e}")
                continue
        
        if all_teams:
            print(f"Successfully scraped {len(all_teams)} teams")
            stat_df = pd.concat(all_teams, ignore_index=True)
            stat_df.to_csv("stats_latest.csv", index=False)
            print("Data saved to stats_latest.csv")
            return True
        else:
            print("No team data collected")
            return False
            
    except Exception as e:
        print(f"Error during scraping: {e}")
        return False
        
    finally:
        driver.quit()

def get_alternative_data():
    """Alternative: Use ESPN or other API for Premier League data"""
    try:
        print("Trying alternative data source (ESPN)...")
        
        # ESPN Premier League standings API (public)
        espn_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/teams"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(espn_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            teams_data = []
            
            for team in data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', []):
                team_info = team.get('team', {})
                teams_data.append({
                    'team_name': team_info.get('displayName', ''),
                    'abbreviation': team_info.get('abbreviation', ''),
                    'location': team_info.get('location', ''),
                    'color': team_info.get('color', ''),
                    'logo': team_info.get('logos', [{}])[0].get('href', '') if team_info.get('logos') else ''
                })
            
            if teams_data:
                df = pd.DataFrame(teams_data)
                df.to_csv("premier_league_teams_latest.csv", index=False)
                print(f"Saved {len(teams_data)} Premier League teams to premier_league_teams_latest.csv")
                return True
        
        return False
        
    except Exception as e:
        print(f"Error with alternative data source: {e}")
        return False

if __name__ == "__main__":
    print("=== Premier League Data Collector ===")
    print("Attempting to collect latest Premier League data...")
    
    # First try Selenium approach
    print("\n1. Trying Selenium approach...")
    success = get_team_stats_selenium()
    
    if not success:
        print("\n2. Trying alternative data sources...")
        get_alternative_data()
    
    print("\nScript completed!")