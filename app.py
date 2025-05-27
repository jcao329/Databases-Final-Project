from flask import Flask, render_template, request
from wtforms import Form, SelectField, StringField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Optional
from load_data import POKEMON, MOVES, ABILITIES, TYPES, REGIONS, TEAMS, TRAINERS
import pandas as pd
import pymysql
import os


class MoveSpecForm(Form):
    power = IntegerField('Power greater than:', validators=[Optional()])
    accuracy = IntegerField('Accuracy greater than:',validators=[Optional()])
    submit = SubmitField('Search')


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
    trainer_teams = SelectField('Trainer Teams', choices=teams)
    trainer_submit = SubmitField('Search')

class PokemonTeamsForm(Form):
    teams = [('Blank', '')]
    for t in TEAMS:
        teams.append((t, t))
    pokemon_teams = SelectField('Pokemon Teams', choices=teams)
    pokemon_submit = SubmitField('Search')

class PokemonsForm(Form):
    pmons = [('Blank', '')]
    for p in POKEMON:
        pmons.append((p, p))
        
    pokemons = SelectField('Regions', choices=pmons)
    pokemon_submit = SubmitField('Search')

class PokemonsOppForm(Form):
    pmons = [('Blank', '')]
    for p in POKEMON:
        pmons.append((p, p))
        
    pokemons_opp = SelectField('Regions', choices=pmons)
    pokemon_submit_opp = SubmitField('Search')

class NameForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    pmons = [('Blank', '')]
    for p in POKEMON:
        pmons.append((p, p))

    p1 = SelectField('Pokemon', choices=pmons)
    p2 = SelectField('Pokemon', choices=pmons)
    p3 = SelectField('Pokemon', choices=pmons)
    p4 = SelectField('Pokemon', choices=pmons)
    p5 = SelectField('Pokemon', choices=pmons)
    p6 = SelectField('Pokemon', choices=pmons)
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
        password = "password", # MODIFY FOR YOUR PASSWORD
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
    pkmns = PokemonsForm(request.form)
    pkmns2 = PokemonsOppForm(request.form)
    move_spec = MoveSpecForm(request.form)

    move = 'Blank'
    ability = 'Blank'
    type1 = 'Blank'
    region = 'Blank'
    legendary = False
    # move_spec = 'Blank'
    opponent = 'Blank'
    opp2 = 'Blank'


    df = pd.read_csv('data/pokemon.csv')[["pokemon_name", "is_legendary", "type1", "type2"]]
    
    if request.method == 'POST':
        if move_spec.submit.data and move_spec.validate():
            power = move_spec.power.data
            accuracy = move_spec.accuracy.data
            connection = get_pymysql_connection()

            try:
                with connection.cursor() as cursor:
                    sql =  """
                    SELECT p.pokemon_name, m.move_name, m.power, m.accuracy
                    FROM pokemon p 
                    JOIN pokemon_moves pm ON p.pokemon_id = pm.pokemon_id
                    JOIN moves m ON m.move_id = pm.move_id
                    WHERE 1 = 1"""
                    
                    params = []
                    if power is not None:
                        sql += " AND m.power >= %s"
                        params.append(power)
                    elif accuracy is not None:
                        sql += " AND m.accuracy >= %s"
                        params.append(accuracy)

                    cursor.execute(sql, params)
                    results = cursor.fetchall()
                    df = pd.DataFrame(results)
                    df = df.dropna(subset=['power', 'accuracy'])
            finally:
                connection.close()
        elif pkmns.pokemon_submit.data and pkmns.validate():
            # print("query 2")
            # print(request.form)
            opponent = pkmns.pokemons.data
            connection = get_pymysql_connection()

            if opponent != 'Blank':
                try: 
                    with connection.cursor() as cursor:
                        # get the opponent type(s)
                        sql = """SELECT DISTINCT p.pokemon_name, p.type1, p.type2 \
                                FROM pokemon p \
                                WHERE p.pokemon_name = %s"""
                        
                        cursor.execute(sql, (opponent))
                        results = cursor.fetchall()
                        t1 = results[0]['type1']
                        t2 = results[0]['type2']

                        if t2:
                            sql = """SELECT DISTINCT p.pokemon_name, m.move_name, m.type, m.power, exp(sum(ln(te.multiplier))) AS effectiveness \
                                    FROM pokemon AS p \
                                    JOIN pokemon_moves AS pm ON p.pokemon_id = pm.pokemon_id \
                                    JOIN moves AS m ON m.move_id = pm.move_id \
                                    JOIN type_effectiveness AS te ON te.attacking_type = m.type \
                                    WHERE te.defending_type = %s OR te.defending_type = %s\
                                    GROUP BY m.move_name, p.pokemon_name, m.type, m.power \
                                    ORDER BY effectiveness DESC, m.power DESC"""
                            cursor.execute(sql, (t1, t2))
                            results = cursor.fetchall()
                        else: 
                            sql = """SELECT DISTINCT p.pokemon_name, m.move_name, m.type, m.power, te.multiplier \
                                    FROM pokemon AS p \
                                    JOIN pokemon_moves AS pm ON p.pokemon_id = pm.pokemon_id \
                                    JOIN moves AS m ON m.move_id = pm.move_id \
                                    JOIN type_effectiveness AS te ON te.attacking_type = m.type \
                                    WHERE te.defending_type = %s \
                                    ORDER BY te.multiplier DESC, m.power DESC"""
                            cursor.execute(sql, (t1))
                            results = cursor.fetchall()
                        df = pd.DataFrame(results)
                finally:
                    connection.close()
        elif pkmns2.pokemon_submit_opp.data and pkmns2.validate():
            print("query 3")
            opp2 = pkmns2.pokemons_opp.data
            connection = get_pymysql_connection()

            if opp2 != 'Blank':
                try: 
                    with connection.cursor() as cursor:
                        # get the opponent type(s)
                        sql = """SELECT DISTINCT p.pokemon_name, p.type1, p.type2 \
                                FROM pokemon p \
                                WHERE p.pokemon_name = %s"""
                        cursor.execute(sql, (opp2))
                        results = cursor.fetchall()
                        t1 = results[0]['type1']
                        t2 = results[0]['type2']

                        # type effectiveness chart with double types
                        sql = """CREATE TABLE IF NOT EXISTS all_type_effectiveness AS 
                                    SELECT t1.attacking_type as attack_type_1, t2.attacking_type as attack_type_2, t1.defending_type as defend_type_1, t2.defending_type as defend_type_2, (t1.multiplier*t2.multiplier) as combined_multiplier
                                    FROM type_effectiveness AS t1 
                                    CROSS JOIN type_effectiveness AS t2 
                                    """
                        cursor.execute(sql)

                        sql = """ALTER TABLE all_type_effectiveness MODIFY attack_type_2 varchar(20)
                                    """
                        cursor.execute(sql)

                        sql = """ALTER TABLE all_type_effectiveness MODIFY defend_type_2 varchar(20)
                                    """
                        cursor.execute(sql)

                        sql = """UPDATE all_type_effectiveness
                                    SET attack_type_2 = NULL
                                    WHERE attack_type_1 = attack_type_2
                                    """
                        cursor.execute(sql)
                        sql = """UPDATE all_type_effectiveness
                                    SET defend_type_2 = NULL
                                    WHERE defend_type_1 = defend_type_2
                                    """
                        cursor.execute(sql)

                        if t2:
                            sql = """SELECT p.pokemon_name, p.type1, p.type2, ate.combined_multiplier \
                                    FROM pokemon AS p \
                                    JOIN all_type_effectiveness AS ate ON ate.defend_type_1 = p.type1 AND ate.defend_type_2 = p.type2 \
                                    WHERE ate.attack_type_1 = %s AND ate.attack_type_2 = %s\
                                    ORDER BY ate.combined_multiplier DESC\
                                    LIMIT 10
                                    """
                        else:
                            sql = """SELECT p.pokemon_name, p.type1, p.type2, ate.combined_multiplier \
                                    FROM pokemon AS p \
                                    JOIN all_type_effectiveness AS ate ON ate.defend_type_1 = p.type1 AND ate.defend_type_2 = p.type2 \
                                    WHERE ate.attack_type_1 = %s AND ate.attack_type_2 is %s\
                                    ORDER BY ate.combined_multiplier DESC\
                                    LIMIT 10
                                    """

                        cursor.execute(sql, (t1, t2))
                        results = cursor.fetchall()
                        df = pd.DataFrame(results)
                finally:
                    connection.close()
        else: 
            move = moves.moves.data
            legendary = legendaryfm.legendary.data
            ability = abilities.abilities.data
            type1 = types1.types.data
            region = regions.regions.data
            connection = get_pymysql_connection()

            if all(x == 'Blank' for x in [move, ability, type1, region]):
                        render_template('pokemon.html', moves=moves, abilities=abilities, types1=types1, regions=regions, legendaryfm=legendaryfm, pkmns=pkmns, opp=opponent, pkmns2=pkmns2, opp2=opp2,
                           move_spec=move_spec, ability=ability, type1=type1, region=region, move=move, legendary=legendary, tables=[df.to_html(header="true", border=2, justify="center")])

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
    return render_template('pokemon.html', moves=moves, abilities=abilities, types1=types1, regions=regions, legendaryfm=legendaryfm, pkmns=pkmns, opp=opponent, pkmns2=pkmns2, opp2=opp2,
                           move_spec=move_spec, ability=ability, type1=type1, region=region, move=move, legendary=legendary, tables=[df.to_html(header="true", border=2, justify="center")])

@app.route("/newtrainer", methods=['GET', 'POST'])
def newtrainer():
    name_form = NameForm(request.form)
    
    trainer_df = pd.read_csv('data/trainers.csv')
    tables=[]
    
    if name_form.validate():
        trainer_name = name_form.name.data
        p1 = name_form.p1.data
        p2 = name_form.p2.data
        p3 = name_form.p3.data
        p4 = name_form.p4.data
        p5 = name_form.p5.data
        p6 = name_form.p6.data
        add_pkmn = set([p1, p2, p3, p4, p5, p6])
        add_pkmn.discard('Blank')
        connection = get_pymysql_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT MAX(trainer_ID) as max_id FROM trainers;") # IF NULL (should never be the case) set to 0 
                
                max_id = cursor.fetchone()["max_id"]
                new_id = max_id + 1
                
                sql = "INSERT INTO trainers (trainer_ID, trainer_name) VALUES (%s, %s)"
                cursor.execute(sql, (new_id, trainer_name))
                connection.commit()

                for pkmn in add_pkmn:
                    sql = "INSERT INTO trainer_pokemon (trainer_ID, pokemon_name) VALUES (%s, %s)"
                    cursor.execute(sql, (new_id, pkmn))
                    connection.commit()
                
                sql = """
                    SELECT t.trainer_ID, t.trainer_name
                    FROM trainers as t
                    """
                cursor.execute(sql)
                results = cursor.fetchall()
                trainer_df = pd.DataFrame(results)

                sql = """
                    SELECT t.trainer_name, tp.pokemon_name
                    FROM trainer_pokemon as tp
                    JOIN trainers as t ON t.trainer_ID = tp.trainer_ID
                    WHERE t.trainer_ID = %s
                    """
                cursor.execute(sql, (new_id))
                results = cursor.fetchall()
                new_df = style_df(pd.DataFrame(results))
                tables.append(new_df.to_html(header="true", border=2, justify="center"))
        finally:
                connection.close()
                
    
    styled_df = style_df(trainer_df)
    tables.append(styled_df.to_html(header="true", border=2, justify="center"))
    return render_template('newtrainer.html', name_form=name_form, tables=tables)

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
    
    move_spec_form = MoveSpecForm(request.form)

    df = pd.read_csv('data/trainers.csv')

    if request.method == 'POST':
        if pokemons.pokemon_submit.data and pokemons.validate():
            pokemon = pokemons.pokemons.data
            
            connection = get_pymysql_connection()
            
            if pokemon != "Blank":    
                try:
                    with connection.cursor() as cursor: # https://pymysql.readthedocs.io/en/latest/user/examples.html
                        sql = """
                        SELECT t.trainer_ID, t.trainer_name
                        FROM trainers as t
                        JOIN trainer_pokemon as tp ON t.trainer_ID = tp.trainer_id
                        WHERE tp.pokemon_name = %s
                        """
                        cursor.execute(sql, (pokemon,))
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
                           ability=ability, type1=type1, region=region, move=move, move_spec=move_spec_form,
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
        elif move_spec_form.submit.data and move_spec_form.validate():
            power = move_spec_form.power.data
            accuracy = move_spec_form.accuracy.data
            connection = get_pymysql_connection()

            try:
                with connection.cursor() as cursor:
                    sql =  """
                    SELECT DISTINCT t.trainer_name, tp.pokemon_name, m.move_name, m.accuracy, m.power
                    FROM trainers t
                    JOIN trainer_pokemon tp ON t.trainer_ID = tp.trainer_ID
                    JOIN pokemon p ON tp.pokemon_name = p.pokemon_name
                    JOIN pokemon_moves pm ON p.pokemon_id = pm.pokemon_id
                    JOIN moves m ON pm.move_id = m.move_id
                    WHERE 1=1"""
                    
                    params = []
                    if power is not None:
                        sql += " AND m.power >= %s"
                        params.append(power)
                    if accuracy is not None:
                        sql += " AND m.accuracy >= %s"
                        params.append(accuracy)
                    
                    cursor.execute(sql, params)
                    results = cursor.fetchall()
                    df = pd.DataFrame(results)
                    
                    if not accuracy:
                        df = df.drop('accuracy', axis=1)
                    if not power:
                        df = df.drop('power', axis=1)
            finally:
                connection.close()        
        else:
            df = pd.read_csv('data/trainers.csv')

    styled_df = style_df(df)
    return render_template('trainers.html', pokemons=pokemons, pokemon=pokemon, combined=combined_form, 
                           ability=ability, type1=type1, region=region, move=move, move_spec=move_spec_form,
                           tables=[styled_df.to_html(header="true", border=2, justify="center")])


@app.route("/teams", methods=["GET", "POST"])
def teams():
    teams = TeamsForm(request.form)
    pkmn_teams = PokemonTeamsForm(request.form)
    regions = RegionsForm(request.form)

    team = 'Blank'
    region = 'Blank'
    pkmn_team = 'Blank'

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
        elif teams.trainer_submit.data and teams.validate():
            team = teams.trainer_teams.data
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

        elif pkmn_teams.pokemon_submit.data and pkmn_teams.validate():
            pkmn_team = pkmn_teams.pokemon_teams.data
            connection = get_pymysql_connection()

            if pkmn_team != "Blank":    
                try:
                    with connection.cursor() as cursor: # https://pymysql.readthedocs.io/en/latest/user/examples.html
                        sql = """
                        SELECT t.team_name, tp.pokemon_name, COUNT(tp.pokemon_name) AS pokemon_count
                        FROM teams as t
                        JOIN trainers as tr ON t.team_id = tr.team_ID
                        JOIN trainer_pokemon as tp on tp.trainer_ID = tr.trainer_ID
                        WHERE t.team_name = %s
                        GROUP BY tp.pokemon_name
                        ORDER BY pokemon_count DESC
                        """
                        cursor.execute(sql, (pkmn_team,))
                        results = cursor.fetchall()
                        df = pd.DataFrame(results)
                finally:
                    connection.close()

    df = style_df(df)
    return render_template('teams.html', regions=regions, region=region, teams=teams, team=team, pkmn_teams=pkmn_teams, pkmn_team=pkmn_team, tables=[df.to_html(header="true", border=2, justify="center")])

if __name__ == '__main__':
    app.run(debug=True, port=50001)