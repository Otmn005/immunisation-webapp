import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/b_level1')
def b_level1():
    return render_template("b_level1.html")


@app.route('/b_level2', methods=['GET','POST'])
def b_level2():
    data = []
    if request.method == 'POST':
        data = [
            ("Brazil", "Measles", 2022, 5000, 50, 3.2),
            ("Nigeria", "Measles", 2022, 12000, 100, 5.4)
        ]
    return render_template("b_level2.html", data=data)


@app.route('/b_level3', methods=['GET','POST'])
def b_level3():
    rows = []
    if request.method == 'POST':
        rows = [
            ("India", 22.4),
            ("Kenya", 30.5),
            ("Vietnam", 19.8)
        ]
    return render_template("b_level3.html", rows=rows)


if __name__ == "__main__":
    app.run(debug=True)
