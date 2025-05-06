# alerta_popups.py
import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox

def checar_alertas():
    hoje = datetime.today().date()

    con = sqlite3.connect("agenda.db")
    cursor = con.cursor()

    cursor.execute("SELECT nome, data_vencimento, alerta_dias, alerta_popup FROM eventos")
    eventos = cursor.fetchall()
    con.close()

    for nome, data_str, dias_antes, popup in eventos:
        data_venc = datetime.strptime(data_str, "%Y-%m-%d").date()
        alerta_data = data_venc - timedelta(days=dias_antes)

        if hoje >= alerta_data and hoje <= data_venc:
            if popup:
                exibir_popup(nome, data_venc)

def exibir_popup(nome, data):
    root = tk.Tk()
    root.withdraw()  # esconde a janela principal
    messagebox.showinfo("🚨 Alerta de Vencimento", f"O evento '{nome}' vence em {data.strftime('%d/%m/%Y')}!")
    root.destroy()

if __name__ == "__main__":
    checar_alertas()
