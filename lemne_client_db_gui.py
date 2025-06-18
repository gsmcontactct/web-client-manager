import sqlite3
from tkinter import *
from tkinter import messagebox
import os
from datetime import datetime, timedelta

DB_FILE = r"C:\Users\HP PC\Desktop\Lemne\clienti.db"

def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
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

def adauga_client():
    nume = entry_nume.get().strip()
    telefon = entry_telefon.get().strip()
    localitate = entry_localitate.get().strip()
    cnp = entry_cnp.get().strip()
    data_nasterii = entry_data_nasterii.get().strip()

    if not nume or not telefon or not localitate:
        messagebox.showerror("Eroare", "Completează toate câmpurile obligatorii")
        return

    if data_nasterii:
        try:
            datetime.strptime(data_nasterii, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Eroare", "Data nașterii trebuie să fie în formatul DD.MM.YYYY")
            return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO clienti (nume, telefon, localitate, cnp, data_nasterii) VALUES (?, ?, ?, ?, ?)",
              (nume, telefon, localitate, cnp, data_nasterii))
    conn.commit()
    conn.close()

    messagebox.showinfo("Succes", "Client adăugat")
    entry_nume.delete(0, END)
    entry_telefon.delete(0, END)
    entry_localitate.delete(0, END)
    entry_cnp.delete(0, END)
    entry_data_nasterii.delete(0, END)
    update_total_clienti()

def cauta_client():
    cauta = entry_cautare.get().strip().lower()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, nume, telefon, localitate, cnp, data_nasterii, cantitate_total FROM clienti")
    rezultate = c.fetchall()
    conn.close()

    listbox_rezultate.delete(0, END)
    for cid, nume, telefon, localitate, cnp, data_nasterii, cantitate in rezultate:
        if cauta in nume.lower() or cauta in telefon or cauta in localitate.lower():
            listbox_rezultate.insert(END, f"{cid} | {nume} | {telefon} | {localitate} | CNP: {cnp or '-'} | Data Nasterii: {data_nasterii or '-'} | {cantitate} tone")

def actualizeaza_cantitate():
    selected = listbox_rezultate.get(ACTIVE)
    if not selected:
        messagebox.showerror("Eroare", "Selectează un client")
        return

    try:
        id_client = int(selected.split('|')[0].strip())
    except:
        messagebox.showerror("Eroare", "ID client invalid")
        return

    cantitate = entry_cantitate.get().strip()
    if not cantitate or not cantitate.replace('.', '', 1).isdigit():
        messagebox.showerror("Eroare", "Introdu o cantitate validă")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE clienti SET cantitate_total = ? WHERE id = ?", (float(cantitate), id_client))
    conn.commit()
    conn.close()

    messagebox.showinfo("Succes", "Cantitate actualizată")
    entry_cantitate.delete(0, END)
    cauta_client()

def sterge_client():
    selected = listbox_rezultate.get(ACTIVE)
    if not selected:
        messagebox.showerror("Eroare", "Selectează un client")
        return

    try:
        id_client = int(selected.split('|')[0].strip())
    except:
        messagebox.showerror("Eroare", "ID client invalid")
        return

    confirmare = messagebox.askyesno("Confirmare", "Ești sigur că vrei să ștergi acest client?")
    if not confirmare:
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM clienti WHERE id = ?", (id_client,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Succes", "Client șters")
    cauta_client()
    update_total_clienti()

def update_total_clienti():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM clienti")
    total = c.fetchone()[0]
    conn.close()
    label_total_clienti.config(text=f"Total clienți: {total}")

def verifica_zile_nastere():
    maine = (datetime.now() + timedelta(days=1)).strftime("%d.%m")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT nume, data_nasterii FROM clienti WHERE data_nasterii IS NOT NULL")
    mesaje = []
    for nume, data_nasterii in c.fetchall():
        if data_nasterii:
            try:
                zi_luna = datetime.strptime(data_nasterii, "%d.%m.%Y").strftime("%d.%m")
                if zi_luna == maine:
                    mesaje.append(f"Mâine este ziua lui {nume} – {data_nasterii}")
            except ValueError:
                continue
    conn.close()
    if mesaje:
        messagebox.showinfo("Zile de naștere", "\n".join(mesaje))

# === GUI ===
init_db()
root = Tk()
root.title("Gestionare clienți - Lemne")

Label(root, text="Nume:").pack()
entry_nume = Entry(root, width=40)
entry_nume.pack()

Label(root, text="Telefon:").pack()
entry_telefon = Entry(root, width=40)
entry_telefon.pack()

Label(root, text="Localitate:").pack()
entry_localitate = Entry(root, width=40)
entry_localitate.pack()

Label(root, text="CNP:").pack()
entry_cnp = Entry(root, width=40)
entry_cnp.pack()

Label(root, text="Data Nasterii (DD.MM.YYYY):").pack()
entry_data_nasterii = Entry(root, width=40)
entry_data_nasterii.pack()

Button(root, text="Adaugă Client", command=adauga_client).pack(pady=5)

Label(root, text="Caută (nume/telefon/localitate):").pack()
entry_cautare = Entry(root, width=40)
entry_cautare.pack()
Button(root, text="Caută Client", command=cauta_client).pack(pady=5)

listbox_rezultate = Listbox(root, width=120)
listbox_rezultate.pack(pady=10)

Label(root, text="Cantitate TOTALĂ (tone):").pack()
entry_cantitate = Entry(root, width=20)
entry_cantitate.pack()
Button(root, text="Actualizează Cantitatea", command=actualizeaza_cantitate).pack(pady=5)
Button(root, text="Șterge Client", command=sterge_client).pack(pady=5)
Button(root, text="Verifică Zile de Naștere", command=verifica_zile_nastere).pack(pady=5)

label_total_clienti = Label(root, text="Total clienți: 0", font=('Arial', 10, 'bold'))
label_total_clienti.pack(pady=10)
update_total_clienti()
verifica_zile_nastere()

root.mainloop()
