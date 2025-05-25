from flask import Flask, render_template, request
from wtforms import Form, SelectField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from load_data import POKEMON, MOVES, ABILITIES, TYPES, REGIONS, TEAMS, TRAINERS
import pandas as pd
import pymysql
import os


class MovesForm(Form):
    moves = [('Blank', '')]
    for move in MOVES:
        moves.append((move, move))
    moves = SelectField('Moves', choices=moves)

class LegendaryForm(Form):
    legendary = BooleanField('Legendary')

class AbilitiesForm(Form):
    abilities = [('Blank', '')]
    for a in ABILITIES:
        abilities.append((a, a))
    abilities = SelectField('Abilities', choices=abilities)

class TypesForm(Form):
    types = [('Blank', '')]
    for t in TYPES:
        types.append((t, t))
    types = SelectField('Types', choices=types)

class RegionsForm(Form):
    regs = [('Blank', '')]
    for r in REGIONS:
        regs.append((r, r))
    regions = SelectField('Regions', choices=regs)
    region_submit = SubmitField('Search')

class TeamsForm(Form):
    teams = [('Blank', '')]
    for t in TEAMS:
        teams.append((t, t))
    teams = SelectField('Teams', choices=teams)
    team_submit = SubmitField('Search')

class PokemonsForm(Form):
    pmons = [('Blank', '')]
    for p in POKEMON:
        pmons.append((p, p))
        
    pokemons = SelectField('Regions', choices=pmons)
    pokemon_submit = SubmitField('Search')
    

class NameForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class CombinedTrainerForm(Form):
    
    moves = [('Blank', '')]
    for move in MOVES:
        moves.append((move, move))
    moves = SelectField('Moves', choices=moves)
    
        
    abilities = [('Blank', '')]
    for a in ABILITIES:
        abilities.append((a, a))
    abilities = SelectField('Abilities', choices=abilities)
    
    types = [('Blank', '')]
    for t in TYPES:
        types.append((t, t))
    types = SelectField('Types', choices=types)    
    
    regs = [('Blank', '')]
    for r in REGIONS:
        regs.append((r, r))
    regions = SelectField('Regions', choices=regs)
    
    combined_submit = SubmitField('Search')
    
    
    


def get_pymysql_connection(): # https://www.geeksforgeeks.org/connect-to-mysql-using-pymysql-in-python/
    return pymysql.connect(
        host='localhost',
        user='root',
        password = "PWD", # MODIFY FOR YOUR PASSWORD
        db='Pokemon',
        cursorclass=pymysql.cursors.DictCursor
    )

app = Flask(__name__)
# app.secret_key = 'dev_pokemon_secret_1234'


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/pokemon", methods=['GET', 'POST'])
def pokemon():
    moves = MovesForm(request.form)
    abilities = AbilitiesForm(request.form)
    types1 = TypesForm(request.form)
    regions = RegionsForm(request.form)
    legendaryfm = LegendaryForm(request.form)

    move = 'Blank'
    ability = 'Blank'
    type1 = 'Blank'
    region = 'Blank'
    legendary = False


    df = pd.read_csv('data/pokemon.csv')[["pokemon_name", "is_legendary", "type1", "type2"]]
    
    if request.method == 'POST':
        move = moves.moves.data
        legendary = legendaryfm.legendary.data
        ability = abilities.abilities.data
        type1 = types1.types.data
        region = regions.regions.data
        connection = get_pymysql_connection()

        if all(x == 'Blank' for x in [move, ability, type1, region]):
                    render_template('pokemon.html', moves=moves, abilities=abilities, types1=types1, regions=regions, 
                           ability=ability, type1=type1, region=region, move=move, legendary=legendary, legendaryfm=legendaryfm,
                           tables=[df.to_html(header="true", border=2, justify="center")])

        try: 
            with connection.cursor() as cursor:
                sql = """SELECT DISTINCT p.pokemon_name, r.region_name, p.is_legendary, p.type1, p.type2 \
                        FROM pokemon p \
                        JOIN pokemon_moves pm ON p.pokemon_id = pm.pokemon_id \
                        JOIN moves m ON m.move_id = pm.move_id\
                        JOIN pokemon_abilities pa ON p.pokemon_id = pa.pokemon_id \
                        JOIN regions r ON p.region_id = r.region_id \
                        WHERE 1=1"""
                
                params = []
                if move != 'Blank':
                    sql += " AND m.move_name = %s"
                    params.append(move)
                if ability != 'Blank':
                    sql += " AND pa.ability = %s"
                    params.append(ability)
                if type1 != 'Blank':
                    sql += " AND p.type1 = %s"
                    params.append(type1)
                if region != 'Blank':
                    sql += " AND r.region_name = %s"
                    params.append(region)
                if legendary:
                    sql += " AND p.is_legendary = 1"
                
                cursor.execute(sql, params)
                results = cursor.fetchall()
                df = pd.DataFrame(results)
        finally:
            connection.close()

    df = style_df(df)
    return render_template('pokemon.html', moves=moves, abilities=abilities, types1=types1, regions=regions, legendaryfm=legendaryfm,
                           ability=ability, type1=type1, region=region, move=move, legendary=legendary, tables=[df.to_html(header="true", border=2, justify="center")])

@app.route("/newtrainer", methods=['GET', 'POST'])
def newtrainer():
    name_form = NameForm(request.form)
    
    trainer_df = pd.read_csv('data/trainers.csv')
    
    if name_form.validate():
        trainer_name = name_form.name.data
        connection = get_pymysql_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT MAX(trainer_ID) as max_id FROM trainers;") # IF NULL (should never be the case) set to 0 
                
                max_id = cursor.fetchone()["max_id"]
                new_id = max_id + 1
                
                sql = "INSERT INTO trainers (trainer_ID, trainer_name) VALUES (%s, %s)"
                cursor.execute(sql, (new_id, trainer_name))
                connection.commit()
                
                sql = """
                    SELECT t.trainer_ID, t.trainer_name
                    FROM trainers as t
                    """
                    
                cursor.execute(sql)
                results = cursor.fetchall()
                trainer_df = pd.DataFrame(results)
        finally:
                connection.close()
                
    
    styled_df = style_df(trainer_df)
    return render_template('newtrainer.html', name_form=name_form, tables=[styled_df.to_html(header="true", border=2, justify="center")])

def style_df(df):
    styled_df = df.style.set_table_styles([
        {'selector': 'th', 'props': [('text-align', 'center'), ('padding', '5px'), ('border', '1px solid black')]}, # Header
        {'selector': 'td', 'props': [('text-align', 'center'), ('padding', '5px'), ('border', '1px solid black')]}, # Data
    ])
    
    return styled_df

@app.route("/trainers", methods=["GET", "POST"])
def trainers():
    pokemons = PokemonsForm(request.form)
    pokemon = 'Blank'
    
    combined_form = CombinedTrainerForm(request.form)
    
    move = 'Blank'
    ability = 'Blank'
    type1 = 'Blank'
    region = 'Blank'

    df = pd.read_csv('data/trainers.csv')

    if request.method == 'POST':
        if pokemons.pokemon_submit.data and pokemons.validate():
            pokemon = pokemons.pokemons.data
            connection = get_pymysql_connection()
            
            if region != "Blank":    
                try:
                    with connection.cursor() as cursor: # https://pymysql.readthedocs.io/en/latest/user/examples.html
                        sql = """
                        SELECT t.trainer_ID, t.trainer_name
                        FROM trainers as t
                        JOIN trainer_pokemon as tp ON t.trainer_ID = tp.trainer_id
                        WHERE tp.pokemon_name = %s
                        """
                        cursor.execute(sql, (region,))
                        results = cursor.fetchall()
                        df = pd.DataFrame(results)
                finally:
                    connection.close()
                    
        elif combined_form.combined_submit.data and combined_form.validate():
            move = combined_form.moves.data
            ability = combined_form.abilities.data
            type1 = combined_form.types.data
            region = combined_form.regions.data
            
            connection = get_pymysql_connection()
            
            if all(x == 'Blank' for x in [move, ability, type1, region]):
                    render_template('trainers.html', pokemons=pokemons, combined=combined_form, 
                           ability=ability, type1=type1, region=region, move=move,
                           tables=[df.to_html(header="true", border=2, justify="center")])

            try: 
                with connection.cursor() as cursor:
                    sql = """SELECT DISTINCT t.trainer_ID, t.trainer_name \
                            FROM trainers as t \
                            JOIN trainer_pokemon as tp ON t.trainer_ID = tp.trainer_id \
                            JOIN pokemon as p ON tp.pokemon_name = p.pokemon_name
                            JOIN pokemon_moves pm ON p.pokemon_id = pm.pokemon_id \
                            JOIN moves m ON m.move_id = pm.move_id\
                            JOIN pokemon_abilities pa ON p.pokemon_id = pa.pokemon_id \
                            JOIN regions r ON p.region_id = r.region_id \
                            WHERE 1=1"""
                    
                    params = []
                    if move != 'Blank':
                        sql += " AND m.move_name = %s"
                        params.append(move)
                    if ability != 'Blank':
                        sql += " AND pa.ability = %s"
                        params.append(ability)
                    if type1 != 'Blank':
                        sql += " AND p.type1 = %s"
                        params.append(type1)
                    if region != 'Blank':
                        sql += " AND r.region_name = %s"
                        params.append(region)
                    
                    cursor.execute(sql, params)
                    results = cursor.fetchall()
                    df = pd.DataFrame(results)
            finally:
                connection.close()
                    
        else:
            df = pd.read_csv('data/trainers.csv')

    styled_df = style_df(df)
    return render_template('trainers.html', pokemons=pokemons, pokemon=pokemon, combined=combined_form, 
                           ability=ability, type1=type1, region=region, move=move,
                           tables=[styled_df.to_html(header="true", border=2, justify="center")])


@app.route("/teams", methods=["GET", "POST"])
def teams():
    teams = TeamsForm(request.form)
    regions = RegionsForm(request.form)

    team = 'Blank'
    region = 'Blank'

    # fetch default table
    connection = get_pymysql_connection()
    with connection.cursor() as cursor: # https://pymysql.readthedocs.io/en/latest/user/examples.html
        sql = """
        SELECT t.team_id, t.team_name, r.region_name
        FROM teams as t
        JOIN regions as r ON t.region_id = r.region_id
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        df = pd.DataFrame(results)
    connection.close()

    if request.method == 'POST':
        if regions.region_submit.data and regions.validate():
            region = regions.regions.data
            connection = get_pymysql_connection()
            
            if region != "Blank":    
                try:
                    with connection.cursor() as cursor: # https://pymysql.readthedocs.io/en/latest/user/examples.html
                        sql = """
                        SELECT t.team_id, t.team_name, r.region_name
                        FROM teams as t
                        JOIN regions as r ON t.region_id = r.region_id
                        WHERE r.region_name = %s
                        """
                        cursor.execute(sql, (region,))
                        results = cursor.fetchall()
                        df = pd.DataFrame(results)
                finally:
                    connection.close()
        elif teams.team_submit.data and teams.validate():
            team = teams.teams.data
            connection = get_pymysql_connection()

            if team != "Blank":    
                try:
                    with connection.cursor() as cursor: # https://pymysql.readthedocs.io/en/latest/user/examples.html
                        sql = """
                        SELECT t.team_name, tr.trainer_name
                        FROM teams as t
                        JOIN trainers as tr ON t.team_id = tr.team_ID
                        WHERE t.team_name = %s
                        """
                        cursor.execute(sql, (team,))
                        results = cursor.fetchall()
                        df = pd.DataFrame(results)
                finally:
                    connection.close()

    df = style_df(df)
    return render_template('teams.html', regions=regions, region=region, teams=teams, team=team, tables=[df.to_html(header="true", border=2, justify="center")])

if __name__ == '__main__':
    app.run(debug=True)