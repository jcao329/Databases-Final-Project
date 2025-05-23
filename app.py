from flask import Flask, render_template, request
from wtforms import Form, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass


class SimpleForm(Form):
    user = SelectField('User', choices=[('Blank', ''), ('Admin', 'Admin'), ('Regular', 'Regular')])
    submit = SubmitField('Go')


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password@localhost/Pokemon"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/pokemon", methods=['GET', 'POST'])
def pokemon():
    form = SimpleForm(request.form)
    value = 'nothing'
    if request.method == 'POST':
        value = form.user.data
    return render_template('pokemon.html', form=form, value=value)

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