from flask import Flask, render_template, request
from wtforms import Form, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from load_data import POKEMON, MOVES, ABILITIES, TYPES, REGIONS, TEAMS, TRAINERS
import pandas as pd

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

app = Flask(__name__)

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

@app.route("/newtrainer")
def newtrainer():
    return render_template('newtrainer.html')

@app.route("/trainers")
def trainers():
    return render_template('trainers.html')

@app.route("/teams")
def teams():
    return render_template('teams.html')

if __name__ == '__main__':
    app.run(debug=True)