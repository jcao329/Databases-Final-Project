from flask import Flask, render_template, request
from wtforms import Form, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class SimpleForm(Form):
    user = SelectField('User', choices=[(1, 'Admin'), (2, 'Regular')])
    submit = SubmitField('Go')


class MyForm(Form):
    name = StringField('name', validators=[DataRequired()])

class Base(DeclarativeBase):
  pass

app = Flask(__name__)

#ModuleNotFoundError: No module named 'MySQLdb'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password@localhost/Pokemon"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/pokemon")
def pokemon():
    form = SimpleForm(request.form)
    return render_template('pokemon.html', form=form)

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