import json
import unicodedata
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import requests

class Competitive:

    def __init__(self, teams, players):
        self.teams = teams
        self.players = players
        self.url = 'https://lol.fandom.com/wiki'
        
    
    def get_championship(self):

        url = "https://lol.fandom.com/wiki/CBLOL/2024_Season/Split_1"
        html = requests.get(url).content

        
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find_all('table','infobox InfoboxTournament')
        
        data = []
        for t in table:
            title = t.find('th','infobox-title').text.strip()
            image = t.find('a','image').get('href','')
            region = t.find('span', 'markup-object-name').text.strip()
            
            rows = t.find_all('tr')
            

            start_date = None
            end_date = None

            for row in rows:
                # Find the <td> tag with class "infobox-label"
                label_cell = row.find('td', class_='infobox-label')
                if label_cell:
                    label_text = label_cell.text.strip()
                    if label_text == "Start Date":
                        start_date_cell = label_cell.find_next_sibling('td')
                        if start_date_cell:
                            start_date = start_date_cell.text.strip()
                    elif label_text == "End Date":
                        end_date_cell = label_cell.find_next_sibling('td')
                        if end_date_cell:
                            end_date = end_date_cell.text.strip()
                            break
            data.append({"title": title, "start_date" : start_date, "end_date" : end_date, "image" : image, 'region': region})
        print(data)
        return data

        
    def get_teams(self):
        championship = self.get_championship()
        options = Options()
        options.add_argument("--headless")  # Executar em modo headless (sem interface gráfica)
        service = Service("chromedriver.exe")  # Substitua pelo caminho do seu driver
        driver = webdriver.Chrome(service=service, options=options)

        url = "https://lol.fandom.com/wiki/CBLOL/2024_Season/Split_1"

        driver.get(url)

        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tournament-rosters"))
        )

        html = driver.page_source

        driver.quit()
        soup = BeautifulSoup(html, "html.parser")
        participants = soup.find_all('div',class_='tournament-rosters maxteams-5')
        champions = []
        
        for p in participants:
            images = p.find_all('img')
            for img in images:
                alt_text = img.get('alt','')
                if alt_text.endswith('square'):
                    champion_name = alt_text.replace('logo square', '').strip()
                    image_link = img.get('data-src', '')
                    for c in championship:
                        champions.append({'championship': c['title'],'team': champion_name, 'image': image_link})
        print(champions)
        
        return champions
        
    def get_players(self):
        teams = self.get_teams()
        players = []
        for team in teams:
            print(team)
            url = f"https://lol.fandom.com/wiki/{team['team']}"
            options = Options()
            options.add_argument("--headless")  # Executar em modo headless (sem interface gráfica)
            service = Service("chromedriver.exe")  # Substitua pelo caminho do seu driver
            driver = webdriver.Chrome(service=service, options=options)

            driver.get(url)

            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "team-members-current"))
            )

            html = driver.page_source

            driver.quit()
            soup = BeautifulSoup(html, "html.parser")
            
            table = soup.find("table",class_='team-members-current')
            rows = table.find_all('tr')

                    # Initialize an empty list to store player information
            role_regex = re.compile(r'title="([^"]+)"')
            date_regex = re.compile(r'\d{4}-\d{2}-\d{2}')

            # Initialize an empty list to store player information
            players_info = []

            # Iterate through each row in the table
            for row in rows:
                # Find the cells in the current row
                cells = row.find_all('td')
                
                # Extract information from each cell
                if len(cells) >= 5:  # Ensure the row has at least the expected number of cells
                    residency = cells[0].text.strip()
                    player_link = cells[2].find('a')
                    player_nickname = player_link.text.strip()
                    get_player_name = cells[3].text.strip()
                    
                    player_name = unicodedata.normalize("NFKD", get_player_name)

                    # Extract role using regular expression
                    role_match = role_regex.search(str(cells[4]))
                    if role_match:
                        role = role_match.group(1)
                    else:
                        role = "Role not found"

                    # Extract contract date using regular expression
                    date_match = date_regex.search(str(cells[5]))
                    if date_match:
                        contract_date = date_match.group()
                    else:
                        contract_date = "Date not found"

                    # Append player information as a dictionary to the list
                    players_info.append({'residency': residency, 'nickname': player_nickname, 'name': player_name, 'role': role, 'contract_date': contract_date})
                    players.append({'residency': residency, 'nickname': player_nickname, 'name': player_name, 'role': role, 'contract_date': contract_date, "team" :team['team']})

    # Print the list of player information
                for player in players_info:
                    print(player)
        with open('players.json', 'w') as json_file:
            json.dump(players, json_file)
        return players