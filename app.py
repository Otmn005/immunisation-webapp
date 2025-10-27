from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/b_level1')
def b_level1():
    # mission / persona overview
    return render_template("b_level1.html")

@app.route('/b_level2', methods=['GET','POST'])
def b_level2():
    conn = sqlite3.connect('immunisation.db')
    cur = conn.cursor()
    data = []
    if request.method == 'POST':
        econ = request.form['econ']
        infection = request.form['infection']
        year = request.form['year']
        # todo: maybe make this cleaner later
        cur.execute("""
            SELECT Country, InfectionType, Year, Cases, Deaths,
                   ROUND(Cases*100000.0/Population,2) AS Rate
            FROM infection
            WHERE EconomicStatus=? AND InfectionType=? AND Year=?;
        """, (econ, infection, year))
        data = cur.fetchall()
    conn.close()
    return render_template("b_level2.html", data=data)

@app.route('/b_level3', methods=['GET','POST'])
def b_level3():
    rows = []
    if request.method == 'POST':
        infection = request.form['infection']
        year = request.form['year']
        # using hardcoded demo data first
        rows = [
            ("Australia", 12.4),
            ("India", 25.3),
            ("Vietnam", 27.8)
        ]
    return render_template("b_level3.html", rows=rows)
