from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import requests
import time

all_teams = []
html = requests.get("https://fbref.com/en/comps/9/Premier-League-Stats").text
soup = BeautifulSoup(html, "lxml")
tables = soup.find_all('table', class_="stats_table")
if not tables:
    print("No stats_table found on main page.")
    exit(1)
table = tables[0]

links = table.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if "/squads" in l]

team_urls = [f"https://fbref.com{l}" for l in links]

for team_url in team_urls:
    team_name = team_url.split("/")[-1].replace("Stats", "")
    data = requests.get(team_url).text
    soup = BeautifulSoup(data, "lxml")
    stats_tables = soup.find_all("table", class_="stats_table")
    if not stats_tables:
        print(f"No stats_table found for team: {team_name}")
        continue
    stats = stats_tables[0]

    # Wrap the HTML string in a StringIO object
    html_data = StringIO(str(stats))
    team_data = pd.read_html(html_data)[0]
    team_data["Team"] = team_name
    all_teams.append(team_data)
    time.sleep(5)
    
stat_df = pd.concat(all_teams)
stat_df.to_csv("stats.csv", index=False)
