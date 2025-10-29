import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

#  Home / Landing Page
@app.route("/")
def index():
    return render_template("index.html")


#  Sub-task B Routes
@app.route('/b_level1')
def b_level1():
    return render_template("b_level1.html")


@app.route('/b_level2', methods=['GET','POST'])
def b_level2():
    data = []
    if request.method == 'POST':
        econ = request.form['econ'].strip()
        infection = request.form['infection'].strip()
        year = request.form['year'].strip()

        # simple guard: ignore empty form
        if econ and infection and year.isdigit():
            conn = sqlite3.connect('immunisation.db')
            cur = conn.cursor()
            query = """
                SELECT Country, InfectionType, Year, Cases, Deaths,
                       ROUND(Cases * 100000.0 / Population, 2) AS Rate
                FROM infection
                WHERE EconomicStatus = ? AND InfectionType = ? AND Year = ?;
            """
            cur.execute(query, (econ, infection, int(year)))
            data = cur.fetchall()
            conn.close()

    return render_template("b_level2.html", data=data)


@app.route('/b_level3', methods=['GET','POST'])
def b_level3():
    rows = []
    if request.method == 'POST':
        # placeholder data until DB added later
        rows = [
            ("India", 22.4),
            ("Kenya", 30.5),
            ("Vietnam", 19.8)
        ]
    return render_template("b_level3.html", rows=rows)


#  Sub-task A Routes
@app.route('/a_level1')
def a_level1():
    return render_template("a_level1.html")


@app.route('/a_level2', methods=['GET','POST'])
def a_level2():
    rows1, rows2 = [], []
    if request.method == 'POST':
        rows1 = [
            {'antigen': 'MCV1', 'year': 2022, 'country': 'Australia', 'region': 'Oceania', 'coverage': 93.4},
            {'antigen': 'MCV1', 'year': 2022, 'country': 'Vietnam', 'region': 'SE Asia', 'coverage': 95.1}
        ]
        rows2 = [
            {'antigen': 'MCV1', 'year': 2022, 'country_count': 12, 'region': 'Oceania'},
            {'antigen': 'MCV1', 'year': 2022, 'country_count': 18, 'region': 'SE Asia'}
        ]
    return render_template("a_level2.html", rows1=rows1, rows2=rows2)


@app.route('/a_level3', methods=['GET','POST'])
def a_level3():
    rows = []
    if request.method == 'POST':
        rows = [
            {'country': 'Kenya', 'vaccination_rate_increase': 14.2, 'start_year': 2018, 'end_year': 2024},
            {'country': 'Laos', 'vaccination_rate_increase': 11.6, 'start_year': 2018, 'end_year': 2024}
        ]

    return render_template("a_level3.html", rows=rows)


if __name__ == "__main__":
    app.run(debug=True)
