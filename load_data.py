# Reads data from csv to initialize app dropdown options
import pandas as pd
from ast import literal_eval

try:
    pokemon = pd.read_csv('data/pokemon.csv')
    moves = pd.read_csv('data/moves.csv')
    type_eff = pd.read_csv('data/type_effectiveness.csv')
    regions = pd.read_csv('data/regions.csv')
    trainers = pd.read_csv('data/trainers.csv')
    trainer_pokemon = pd.read_csv('data/trainer_pokemon.csv')
    types = pd.read_csv('data/types.csv')
    teams = pd.read_csv('data/teams.csv')
except Exception as e:
    print("Cannot load files:", e)
    exit(1)

def get_pokemon():
    """
    Returns complete list of pokemon
    """
    ret = []
    for _, row in pokemon.iterrows():
        ret.append(row['pokemon_name'])
    return ret

def get_moves():
    """ 
    Returns complete list of moves
    """
    ret = []
    for _, row in moves.iterrows():
        ret.append(row['move_name'])
    return ret

def get_abilities():
    """ 
    Returns complete list of Pokemon abilities
    """
    seen = set()
    pokemon['abilities'] = pokemon['abilities'].apply(literal_eval)
    for _, row in pokemon.iterrows():
        for ability in row['abilities']:
            seen.add(ability)
    return list(seen)

def get_types():
    """ 
    Returns complete list of types
    """
    all_types = set()
    all_types.update(pokemon['type1'].dropna().unique())
    all_types.update(pokemon['type2'].dropna().unique())
    all_types.update(moves['type'].dropna().unique())
    all_types.update(type_eff['atk_move'].dropna().unique())
    all_types.update(type_eff['def_move'].dropna().unique())
    return list(all_types)

def get_regions():
    """ 
    Returns complete list of regions
    """
    ret = []
    for _, row in regions.iterrows():
        ret.append(row['name'])
    return ret

def get_teams():
    """ 
    Returns complete list of teams
    """
    teams['team_name'] = teams['team_name'].str.strip()
    ret = []
    for _, row in teams.iterrows():
        ret.append(row['team_name'])
    return ret
        

def get_trainers():
    """ 
    Returns complete list of trainers
    """
    ret = []
    for _, row in trainers.iterrows():
        ret.append(row['trainer_name'])
    return ret

POKEMON = get_pokemon()
MOVES = get_moves()
ABILITIES = get_abilities()
TYPES = get_types()
REGIONS = get_regions()
TEAMS = get_teams()
TRAINERS = get_trainers()
