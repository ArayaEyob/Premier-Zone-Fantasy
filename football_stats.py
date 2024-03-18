from bs4 import BeautifulSoup
import pandas as pd 
from io import StringIO
import requests
import time

all_teams = []
url = "https://fbref.com/en/comps/9/Premier-League-Stats"
html = requests.get(url).text
soup = BeautifulSoup(html, "lxml")
table = soup.find('table', class_ = 'stats_table')

for link in table.find_all('a', href=True):
    if "/squads" in link['href']:
        team_url = f"https://fbref.com{link['href']}"
        team_name = link.text.replace(" Stats", "")
        data = requests.get(team_url).text
        soup = BeautifulSoup(data, "lxml")
        stats_table = soup.find('table', class_="stats_table")
        if stats_table:
            team_data = pd.read_html(str(stats_table))[0]
            team_data["Team"] = team_name
            all_teams.append(team_data)
        time.sleep(5)

stat_df = pd.concat(all_teams)
stat_df.to_csv("statss.csv", index=False)
