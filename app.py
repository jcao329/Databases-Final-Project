from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/pokemon")
def pokemon():
    return render_template('pokemon.html')

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