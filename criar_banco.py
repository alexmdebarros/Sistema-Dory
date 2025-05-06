# criar_banco.py
import sqlite3

con = sqlite3.connect("agenda.db")
cursor = con.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo TEXT,
    periodicidade TEXT,
    data_vencimento TEXT,
    departamento TEXT,
    alerta_dias INTEGER,
    alerta_email TEXT,
    alerta_popup INTEGER,
    observacoes TEXT
)
""")

con.commit()
con.close()
print("Banco criado com sucesso!")
