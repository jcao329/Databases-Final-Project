from flask import Flask, render_template, request
from wtforms import Form, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from load_data import POKEMON, MOVES, ABILITIES, TYPES, REGIONS, TEAMS, TRAINERS
import pandas as pd
import pymysql
import os

class Base(DeclarativeBase):
  pass


class MovesForm(Form):
    moves = [('Blank', '')]
    for move in MOVES:
        moves.append((move, move))
    moves = SelectField('Moves', choices=moves)
    submit = SubmitField('Go')

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


class PokemonsForm(Form):
    pmons = [('Blank', '')]
    for p in POKEMON:
        pmons.append((p, p))
    pokemons = SelectField('Regions', choices=pmons)
    

class NameForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


def get_pymysql_connection(): # https://www.geeksforgeeks.org/connect-to-mysql-using-pymysql-in-python/
    return pymysql.connect(
        host='localhost',
        user='root',
        password=os.environ["MYSQL_DB_PWD"], # MODIFY FOR YOUR PASSWORD
        db='Pokemon',
        cursorclass=pymysql.cursors.DictCursor
    )

app = Flask(__name__)
# app.secret_key = 'dev_pokemon_secret_1234'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password@localhost/Pokemon"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/pokemon", methods=['GET', 'POST'])
def pokemon():
    moves = MovesForm(request.form)
    abilities = AbilitiesForm(request.form)
    types1 = TypesForm(request.form)
    regions = RegionsForm(request.form)

    move = 'no move'
    ability = 'no ability'
    type1 = 'no type1'
    region = 'no region'

    df = pd.read_csv('data/pokemon.csv')

    if request.method == 'POST':
        move = moves.moves.data
        ability = abilities.abilities.data
        type1 = types1.types.data
        region = regions.regions.data

    return render_template('pokemon.html', moves=moves, abilities=abilities, types1=types1, regions=regions, 
                           ability=ability, type1=type1, region=region, move=move, tables=[df.to_html(header="true")])

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

    pokemon = 'no pokemon'

    df = pd.read_csv('data/trainers.csv')

    if request.method == 'POST' and pokemons.validate():
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
        else:
            df = pd.read_csv('data/trainers.csv')

    styled_df = style_df(df)
    return render_template('trainers.html', pokemons=pokemons, pokemon=pokemon, tables=[styled_df.to_html(header="true", border=2, justify="center")])

@app.route("/teams")
def teams():
    return render_template('teams.html')

if __name__ == '__main__':
    app.run(debug=True)