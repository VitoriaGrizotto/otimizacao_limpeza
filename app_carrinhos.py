import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import csv
import os

CSV_FILE = 'carrinhos.csv'

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['codigo', 'data_ultima_limpeza', 'historico'])

def calcular_status(proxima_data):
    hoje = datetime.today().date()
    dias = (proxima_data - hoje).days
    if dias < 0:
        return "VENCIDO", "#d9534f"  
    elif dias <= 7:
        return "PERTO DE VENCER", "#f0ad4e" 
    else:
        return "EM DIA", "#5cb85c" 

def buscar_carrinho():
    codigo = entrada.get().strip()
    encontrado = False
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        leitor = csv.DictReader(csvfile)
        for linha in leitor:
            if linha['codigo'] == codigo:
                data_ultima = datetime.strptime(linha['data_ultima_limpeza'], "%Y-%m-%d").date()
                proxima = data_ultima + timedelta(days=180)
                status, cor = calcular_status(proxima)
                resultado.config(
                    text=(
                        f"Código: {codigo}\n"
                        f"Última limpeza: {data_ultima.strftime('%d/%m/%Y')}\n"
                        f"Próxima limpeza: {proxima.strftime('%d/%m/%Y')}\n"
                        f"Status: {status}"
                    ),
                    bg=cor,
                    fg="white"
                )
                encontrado = True
                break
    if not encontrado:
        resultado.config(text="Carrinho não encontrado", bg="#6c757d", fg="white")

def cadastrar():
    codigo = entrada_codigo.get().strip()
    data = entrada_data.get().strip()
    historico = entrada_hist.get().strip()

    try:
        data_formatada = datetime.strptime(data, "%d/%m/%Y").date()
    except ValueError:
        messagebox.showerror("Erro", "Data inválida! Use DD/MM/AAAA.")
        return

    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        escritor = csv.writer(csvfile)
        escritor.writerow([codigo, data_formatada.isoformat(), historico])

    messagebox.showinfo("Sucesso", "Carrinho cadastrado com sucesso!")
    janela_cadastro.destroy()

def abrir_cadastro():
    global janela_cadastro, entrada_codigo, entrada_data, entrada_hist
    janela_cadastro = tk.Toplevel(root)
    janela_cadastro.title("Cadastrar Carrinho")
    janela_cadastro.configure(bg="#f8f9fa")
    janela_cadastro.geometry("350x300")
    janela_cadastro.resizable(False, False)

    tk.Label(janela_cadastro, text="Cadastro de Carrinho", font=("Segoe UI", 14, "bold"), bg="#f8f9fa", fg="#343a40").pack(pady=10)

    campo_frame = tk.Frame(janela_cadastro, bg="#f8f9fa")
    campo_frame.pack(pady=5)

    def campo(texto):
        lbl = tk.Label(campo_frame, text=texto, font=("Segoe UI", 10), bg="#f8f9fa", fg="#495057", anchor='w')
        lbl.pack(fill='x')
        entry = tk.Entry(campo_frame, font=("Segoe UI", 10), width=30, relief='solid', borderwidth=1)
        entry.pack(pady=2)
        return entry

    entrada_codigo = campo("Código:")
    entrada_data = campo("Data última limpeza (DD/MM/AAAA):")
    entrada_hist = campo("Histórico:")

    tk.Button(
        janela_cadastro, text="Cadastrar", command=cadastrar,
        bg="#0275d8", fg="white", font=("Segoe UI", 10, "bold"),
        relief="flat", width=25, height=2
    ).pack(pady=15)

root = tk.Tk()
root.title("Controle de Limpeza de Carrinhos")
root.geometry("480x420")
root.configure(bg="#f8f9fa")
root.resizable(False, False)

tk.Label(root, text="Controle de Limpeza", font=("Segoe UI", 18, "bold"), bg="#f8f9fa", fg="#343a40").pack(pady=15)

entrada = tk.Entry(root, font=("Segoe UI", 14), width=25, justify="center", relief="solid", borderwidth=1)
entrada.pack(pady=5)
entrada.bind("<Return>", lambda e: buscar_carrinho())

btn_frame = tk.Frame(root, bg="#f8f9fa")
btn_frame.pack(pady=10)

tk.Button(
    btn_frame, text="Consultar", command=buscar_carrinho,
    bg="#5cb85c", fg="white", font=("Segoe UI", 10, "bold"),
    width=20, relief="flat"
).grid(row=0, column=0, padx=5)

tk.Button(
    btn_frame, text="Novo Cadastro", command=abrir_cadastro,
    bg="#6c757d", fg="white", font=("Segoe UI", 10, "bold"),
    width=20, relief="flat"
).grid(row=0, column=1, padx=5)

resultado = tk.Label(root, text="", font=("Segoe UI", 12), width=50, height=6,
                     bg="white", relief="groove", wraplength=400, justify="left")
resultado.pack(pady=20)

root.mainloop()
