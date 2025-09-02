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
    global carrinho_atual
    codigo = entrada.get().strip()
    encontrado = False
    carrinho_atual = None

    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        leitor = csv.DictReader(csvfile)
        for linha in leitor:
            if linha['codigo'] == codigo:
                data_ultima = datetime.strptime(linha['data_ultima_limpeza'], "%Y-%m-%d").date()
                proxima = data_ultima + timedelta(days=180)
                status, cor = calcular_status(proxima)
                resultado.config(
                    text=(f"Código: {codigo}\n"
                          f"Última limpeza: {data_ultima.strftime('%d/%m/%Y')}\n"
                          f"Próxima limpeza: {proxima.strftime('%d/%m/%Y')}\n"
                          f"Status: {status}"),
                    bg=cor, fg="white"
                )
                carrinho_atual = linha
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
    janela_cadastro.geometry("500x400")

    tk.Label(janela_cadastro, text="Cadastro de Carrinho",
             font=("Segoe UI", 18, "bold"), bg="#f8f9fa", fg="#212529").pack(pady=10)

    campo_frame = tk.Frame(janela_cadastro, bg="#f8f9fa")
    campo_frame.pack(fill="both", expand=True, pady=5)

    def campo(texto):
        lbl = tk.Label(campo_frame, text=texto, font=("Segoe UI", 13),
                       bg="#f8f9fa", fg="#495057", anchor='w')
        lbl.pack(fill='x', padx=20)
        entry = tk.Entry(campo_frame, font=("Segoe UI", 13), relief='solid', borderwidth=1)
        entry.pack(fill='x', padx=20, pady=3)
        return entry

    entrada_codigo = campo("Código:")
    entrada_data = campo("Data última limpeza (DD/MM/AAAA):")
    entrada_hist = campo("Histórico:")

    tk.Button(janela_cadastro, text="Cadastrar", command=cadastrar,
              bg="#0275d8", fg="white", font=("Segoe UI", 13, "bold"),
              relief="flat", height=2).pack(pady=15, fill="x", padx=20)


# ----------- NOVA FUNÇÃO DE EDITAR -----------
def editar():
    global carrinho_atual
    if not carrinho_atual:
        messagebox.showwarning("Aviso", "Primeiro consulte um carrinho para editar.")
        return

    def salvar_edicao():
        nova_data = entrada_data_edit.get().strip()
        novo_hist = entrada_hist_edit.get().strip()

        try:
            data_formatada = datetime.strptime(nova_data, "%d/%m/%Y").date()
        except ValueError:
            messagebox.showerror("Erro", "Data inválida! Use DD/MM/AAAA.")
            return

        linhas = []
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            leitor = csv.DictReader(csvfile)
            for linha in leitor:
                if linha['codigo'] == carrinho_atual['codigo']:
                    linha['data_ultima_limpeza'] = data_formatada.isoformat()
                    linha['historico'] = novo_hist
                linhas.append(linha)

        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            campos = ['codigo', 'data_ultima_limpeza', 'historico']
            escritor = csv.DictWriter(csvfile, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(linhas)

        messagebox.showinfo("Sucesso", "Carrinho editado com sucesso!")
        janela_edicao.destroy()
        buscar_carrinho()

    janela_edicao = tk.Toplevel(root)
    janela_edicao.title("Editar Carrinho")
    janela_edicao.configure(bg="#f8f9fa")
    janela_edicao.geometry("500x350")

    tk.Label(janela_edicao, text=f"Editar Carrinho {carrinho_atual['codigo']}",
             font=("Segoe UI", 18, "bold"), bg="#f8f9fa", fg="#212529").pack(pady=10)

    tk.Label(janela_edicao, text="Nova data de limpeza (DD/MM/AAAA):",
             font=("Segoe UI", 13), bg="#f8f9fa", fg="#495057").pack()
    entrada_data_edit = tk.Entry(janela_edicao, font=("Segoe UI", 13))
    entrada_data_edit.pack(fill="x", padx=20, pady=5)
    entrada_data_edit.insert(0, datetime.strptime(carrinho_atual['data_ultima_limpeza'], "%Y-%m-%d").strftime("%d/%m/%Y"))

    tk.Label(janela_edicao, text="Histórico:",
             font=("Segoe UI", 13), bg="#f8f9fa", fg="#495057").pack()
    entrada_hist_edit = tk.Entry(janela_edicao, font=("Segoe UI", 13))
    entrada_hist_edit.pack(fill="x", padx=20, pady=5)
    entrada_hist_edit.insert(0, carrinho_atual['historico'])

    tk.Button(janela_edicao, text="Salvar", command=salvar_edicao,
              bg="#0275d8", fg="white", font=("Segoe UI", 13, "bold"),
              relief="flat", height=2).pack(pady=15, fill="x", padx=20)

# ---------- INTERFACE PRINCIPAL --------------

root = tk.Tk()
root.title("Controle de Limpeza de Carrinhos")
root.state('zoomed')
root.configure(bg="#f8f9fa")

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

tk.Label(root, text="Controle de Limpeza de Carrinhos",
         font=("Segoe UI", 30, "bold"),
         bg="#f8f9fa", fg="#212529").grid(row=0, column=0, pady=20)

main_frame = tk.Frame(root, bg="#f8f9fa")
main_frame.grid(row=1, column=0, sticky="nsew")
main_frame.grid_rowconfigure(2, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

entrada = tk.Entry(main_frame, font=("Segoe UI", 20), justify="center",
                   relief="solid", borderwidth=1)
entrada.grid(row=0, column=0, pady=15, padx=90, sticky="ew")
entrada.bind("<Return>", lambda e: buscar_carrinho())

btn_frame = tk.Frame(main_frame, bg="#f8f9fa")
btn_frame.grid(row=1, column=0, pady=15)

tk.Button(btn_frame, text="Consultar", command=buscar_carrinho,
          bg="#5cb85c", fg="white", font=("Segoe UI", 14, "bold"),
          relief="flat", height=2, width=20).grid(row=0, column=0, padx=15)

tk.Button(btn_frame, text="Novo Cadastro", command=abrir_cadastro,
          bg="#6c757d", fg="white", font=("Segoe UI", 14, "bold"),
          relief="flat", height=2, width=20).grid(row=0, column=1, padx=15)

tk.Button(btn_frame, text="Editar", command=editar,
          bg="#f0ad4e", fg="white", font=("Segoe UI", 14, "bold"),
          relief="flat", height=2, width=20).grid(row=0, column=2, padx=15)

resultado = tk.Label(main_frame, text="", font=("Segoe UI", 16),
                     bg="white", relief="groove", wraplength=1000, justify="left")
resultado.grid(row=2, column=0, sticky="nsew", padx=50, pady=30)

root.mainloop()
