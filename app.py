from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3, os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'secret-key'
DB = 'clienti.db'

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE clienti (
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

@app.before_first_request
def setup():
    init_db()

@app.route('/', methods=['GET'])
def index():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM clienti")
    clienti = c.fetchall()
    conn.close()
    return render_template('index.html', clienti=clienti)

@app.route('/add', methods=['POST'])
def add_client():
    nume = request.form['nume']
    telefon = request.form['telefon']
    localitate = request.form['localitate']
    cnp = request.form['cnp']
    data_nasterii = request.form['data_nasterii']
    cantitate = request.form.get('cantitate', '0')
    if not nume or not telefon or not localitate:
        flash("Completează toate câmpurile obligatorii", "error")
        return redirect(url_for('index'))
    try:
        if data_nasterii:
            datetime.strptime(data_nasterii, "%d.%m.%Y")
        if cantitate:
            float(cantitate)
    except ValueError:
        flash("Verifică formatul datelor introduse", "error")
        return redirect(url_for('index'))
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO clienti (nume, telefon, localitate, cnp, data_nasterii, cantitate_total) VALUES (?, ?, ?, ?, ?, ?)",
              (nume, telefon, localitate, cnp, data_nasterii, float(cantitate) if cantitate else 0))
    conn.commit()
    conn.close()
    flash("Client adăugat cu succes", "success")
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_client(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM clienti WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Client șters", "success")
    return redirect(url_for('index'))

@app.route('/update_cantitate/<int:id>', methods=['POST'])
def update_cantitate(id):
    cantitate = request.form.get('cantitate_update')
    try:
        cant_val = float(cantitate)
    except (ValueError, TypeError):
        flash("Introdu o cantitate validă", "error")
        return redirect(url_for('index'))
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE clienti SET cantitate_total = ? WHERE id = ?", (cant_val, id))
    conn.commit()
    conn.close()
    flash("Cantitate actualizată", "success")
    return redirect(url_for('index'))

@app.route('/verifica_nasteri')
def verifica_nasteri():
    maine = (datetime.now() + timedelta(days=1)).strftime("%d.%m")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT nume, data_nasterii FROM clienti WHERE data_nasterii IS NOT NULL")
    mesaje = []
    for nume, data_nasterii in c.fetchall():
        try:
            zi_luna = datetime.strptime(data_nasterii, "%d.%m.%Y").strftime("%d.%m")
            if zi_luna == maine:
                mesaje.append(f"Mâine este ziua lui {nume} – {data_nasterii}")
        except ValueError:
            continue
    conn.close()
    if mesaje:
        for mesaj in mesaje:
            flash(mesaj, "alarm")
    else:
        flash("Niciun client nu are ziua de naștere mâine.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)