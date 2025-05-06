# inserir_evento.py
import sqlite3
from datetime import date

eventos = [
    ("FGTS", "Pagamento", "Mensal", "2025-05-07", "Pessoal", 2, "rh@empresa.com", 1, "Depósito obrigatório até o dia 7."),
    ("INSS", "Pagamento", "Mensal", "2025-05-20", "Pessoal", 3, "rh@empresa.com", 1, "Pagamento mensal de INSS."),
    ("EFD Contribuições", "Entrega", "Mensal", "2025-05-10", "Fiscal", 5, "fiscal@empresa.com", 1, "Entrega no SPED."),
]

con = sqlite3.connect("agenda.db")
cursor = con.cursor()

for evento in eventos:
    cursor.execute("""
    INSERT INTO eventos (nome, tipo, periodicidade, data_vencimento, departamento, alerta_dias, alerta_email, alerta_popup, observacoes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, evento)

con.commit()
con.close()
print("Eventos inseridos com sucesso!")
