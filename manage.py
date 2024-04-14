from data.connect import connection
from scrapping import Competitive
import psycopg2



competitive_instance = Competitive([], [])


def connectInDB():
    try:
        champions = competitive_instance.get_players()
        con = connection.cursor()
        for champ in champions:
            print(champ['team'])
            # Execute SQL select statement to find championship_id
            con.execute("SELECT id FROM teams WHERE name = %s", (champ['team'],))
            result = con.fetchone()
            
            # Check if result is None
            if result is None:
                print(f"No championship found with the name: {champ['team']}")
                continue  # Skip this iteration
            
            championship_id = result[0]
            print(result[0])
            
            # Execute SQL insert statement
            con.execute("INSERT INTO players (team_id, name, nickname, role, nacionality, contract_date) VALUES (%s, %s, %s,%s, %s, %s)",
                        (championship_id, champ['name'], champ['nickname'], champ['role'], champ['residency'], champ['contract_date']))
            connection.commit()
        print('Connected to the database successfully!')
    except psycopg2.Error as e:
        print(f'Error connecting to the database: {e}')


connectInDB()