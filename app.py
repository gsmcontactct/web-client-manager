from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "clienti.db"

def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS clienti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nume TEXT NOT NULL,
                telefon TEXT NOT NULL,
                localitate TEXT NOT NULL,
                cnp TEXT,
                data_nasterii TEXT,
                cantitate_total REAL DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM clienti")
    clienti = c.fetchall()
    conn.close()
    return render_template("index.html", clienti=clienti)

@app.route('/add', methods=['POST'])
def add_client():
    nume = request.form['nume']
    telefon = request.form['telefon']
    localitate = request.form['localitate']
    cnp = request.form['cnp']
    data_nasterii = request.form['data_nasterii']

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO clienti (nume, telefon, localitate, cnp, data_nasterii) VALUES (?, ?, ?, ?, ?)",
              (nume, telefon, localitate, cnp, data_nasterii))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:client_id>')
def delete_client(client_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM clienti WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)