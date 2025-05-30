import mysql.connector
import pandas as pd
from ast import literal_eval

# Helper function to convert NaN to None
def convert_to_none(val):
    return None if pd.isna(val) else val

# Connects to the pokemon databse, change to your password
myConnection = mysql.connector.connect(
    user = 'root',
    password = 'password',
    host = 'localhost',
    database = 'Pokemon'
)
cursorObject = myConnection.cursor()

# Loads CSVs, still needs team data
try:
    pokemon = pd.read_csv('data/pokemon.csv')
    moves = pd.read_csv('data/moves.csv')
    type_eff = pd.read_csv('data/type_effectiveness.csv')
    regions = pd.read_csv('data/regions.csv')
    trainers = pd.read_csv('data/trainers.csv')
    trainer_pokemon = pd.read_csv('data/trainer_pokemon.csv')
    teams = pd.read_csv('data/teams.csv')
    pokemon_moves = pd.read_csv('data/pokemon_moves.csv')
    pokemon_moves_1 = pd.read_csv('data/pokemon_moves_1.csv')
    pokemon_moves_2 = pd.read_csv('data/pokemon_moves_2.csv')
    pokemon_moves_3 = pd.read_csv('data/pokemon_moves_3.csv')
    pokemon_moves_4 = pd.read_csv('data/pokemon_moves_4.csv')
    pokemon_moves_5 = pd.read_csv('data/pokemon_moves_5.csv')
except Exception as e:
    print("Cannot load files:", e)
    exit(1)

# Creates tables, needs team table
cursorObject.execute("""
CREATE TABLE IF NOT EXISTS types (
    type_name VARCHAR(20) PRIMARY KEY
);
""")

cursorObject.execute("""
CREATE TABLE IF NOT EXISTS regions (
    region_id INT PRIMARY KEY,
    region_name VARCHAR(50)
);
""")

cursorObject.execute("""
CREATE TABLE IF NOT EXISTS pokemon (
    pokemon_id INT PRIMARY KEY,
    pokemon_name VARCHAR(50),
    type1 VARCHAR(20),
    type2 VARCHAR(20),
    region_id INT,
    is_legendary INT DEFAULT 0,
    FOREIGN KEY (type1) REFERENCES types(type_name),
    FOREIGN KEY (type2) REFERENCES types(type_name),
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);
""")

cursorObject.execute("""
CREATE TABLE IF NOT EXISTS pokemon_abilities (
    pokemon_id INT,
    ability VARCHAR(50),
    PRIMARY KEY (pokemon_id, ability),
    FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id)
);
""")

cursorObject.execute("""
CREATE TABLE IF NOT EXISTS moves (
    move_id INT PRIMARY KEY,
    move_name VARCHAR(100),
    accuracy INT DEFAULT 0,
    power INT DEFAULT 0,
    type VARCHAR(20),
    damage_class VARCHAR(20),
    FOREIGN KEY (type) REFERENCES types(type_name)
);
""")

cursorObject.execute("""
CREATE TABLE IF NOT EXISTS type_effectiveness (
    attacking_type VARCHAR(20),
    defending_type VARCHAR(20),
    multiplier FLOAT,
    PRIMARY KEY (attacking_type, defending_type),
    FOREIGN KEY (attacking_type) REFERENCES types(type_name),
    FOREIGN KEY (defending_type) REFERENCES types(type_name)
);
""")

cursorObject.execute("""
CREATE TABLE IF NOT EXISTS teams (
	team_id INT PRIMARY KEY,
	team_name VARCHAR(20),
    region_id INT,
	FOREIGN KEY (region_id) REFERENCES regions(region_id)
);
""")

cursorObject.execute("""
CREATE TABLE IF NOT EXISTS trainers (
    trainer_ID INT PRIMARY KEY,
    trainer_name VARCHAR(100),
    team_ID INT,
    FOREIGN KEY (team_ID) REFERENCES teams(team_id)
);
""")

cursorObject.execute("""
CREATE TABLE IF NOT EXISTS trainer_pokemon (
    trainer_ID INT,
    pokemon_name VARCHAR(50),
    PRIMARY KEY (trainer_ID, pokemon_name),
    FOREIGN KEY (trainer_ID) REFERENCES trainers(trainer_ID)
);
""")

cursorObject.execute("""
CREATE TABLE IF NOT EXISTS pokemon_moves (
	move_id INT,
	pokemon_id INT,
    PRIMARY KEY (move_id, pokemon_id),
    FOREIGN KEY (move_id) REFERENCES moves(move_id),
    FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id)            
);
""")

# Populates the types table with unique type names from all columns
all_types = set()
all_types.update(pokemon['type1'].dropna().unique())
all_types.update(pokemon['type2'].dropna().unique())
all_types.update(moves['type'].dropna().unique())
all_types.update(type_eff['atk_move'].dropna().unique())
all_types.update(type_eff['def_move'].dropna().unique())

for type_name in all_types:
    if pd.notnull(type_name):
        cursorObject.execute(
            "INSERT IGNORE INTO types (type_name) VALUES (%s);",
            (convert_to_none(type_name),)
        )
myConnection.commit()

# Inserts other data
for _, row in regions.iterrows():
    cursorObject.execute(
        "INSERT INTO regions (region_id, region_name) VALUES (%s, %s);",
        (convert_to_none(row['region_id']), convert_to_none(row['name']))
    )
myConnection.commit()

for _, row in pokemon.iterrows():
    cursorObject.execute("""
        INSERT INTO pokemon
        (pokemon_id, pokemon_name, type1, type2, region_id, is_legendary)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (
        convert_to_none(row['pokemon_id']),
        convert_to_none(row['pokemon_name']),
        convert_to_none(row['type1']),
        convert_to_none(row['type2']),
        convert_to_none(row['region_id']),
        convert_to_none(row['is_legendary'])
    ))
myConnection.commit()

pokemon['abilities'] = pokemon['abilities'].apply(literal_eval)
for _, row in pokemon.iterrows():
    for ability in row['abilities']:
        cursorObject.execute("""
            INSERT IGNORE INTO pokemon_abilities (pokemon_id, ability)
            VALUES (%s, %s);
        """, (convert_to_none(row['pokemon_id']), convert_to_none(ability)))
myConnection.commit()

for i, row in moves.iterrows():
    cursorObject.execute("""
        INSERT INTO moves
        (move_id, move_name, accuracy, power, type, damage_class)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (
        i,
        convert_to_none(row['move_name']),
        convert_to_none(row['accuracy']),
        convert_to_none(row['power']),
        convert_to_none(row['type']),
        convert_to_none(row['damage_class'])
    ))
myConnection.commit()

for _, row in type_eff.iterrows():
    cursorObject.execute("""
        INSERT INTO type_effectiveness
        (attacking_type, defending_type, multiplier)
        VALUES (%s, %s, %s);
    """, (
        convert_to_none(row['atk_move']),
        convert_to_none(row['def_move']),
        convert_to_none(row['multiplier'])
    ))
myConnection.commit()

teams['team_name'] = teams['team_name'].str.strip()
for _, row in teams.iterrows():
    cursorObject.execute(
        "INSERT INTO teams (team_id, team_name, region_id) VALUES (%s, %s, %s);", 
        (convert_to_none(row['team_id']), convert_to_none(row['team_name']), convert_to_none(row['region_id']))
    )
myConnection.commit()

for _, row in trainers.iterrows():
    cursorObject.execute(
        "INSERT INTO trainers (trainer_ID, trainer_name, team_ID) VALUES (%s, %s, %s);",
        (convert_to_none(row['trainer_ID']), convert_to_none(row['trainer_name']), (row['trainer_ID'] % 25)+1)
    )
myConnection.commit()

trainer_pokemon.drop_duplicates(inplace=True)
for _, row in trainer_pokemon.iterrows():
    cursorObject.execute(
        "INSERT INTO trainer_pokemon (trainer_ID, pokemon_name) VALUES (%s, %s);",
        (convert_to_none(row['trainer_ID']), convert_to_none(row['pokemon_name']))
    )

pokemon_moves_1 = pd.concat([pokemon_moves_1, pokemon_moves_2, pokemon_moves_3, pokemon_moves_4, pokemon_moves_5]).drop_duplicates().reset_index(drop=True)
for _, row in pokemon_moves_1.iterrows():
    cursorObject.execute(
        "INSERT INTO pokemon_moves (move_id, pokemon_id) VALUES (%s, %s);", 
        (int(row['move_id']), int(row['pokemon_id']))
    )

myConnection.commit()

# Closes connections
cursorObject.close()
myConnection.close()
