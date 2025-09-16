import tkinter as tk # Bibliotecas 
from tkinter import messagebox
from datetime import datetime, timedelta
import csv
import os

CSV_FILE = 'carrinhos.csv'

if not os.path.exists(CSV_FILE): #Verifica se existe um arquivo.csv, se nao existir ele cria e coloca as linhas
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['codigo', 'data_ultima_limpeza', 'historico'])


def calcular_status(proxima_data): # Funçao que vai calcular o status das carrinhos
    hoje = datetime.today().date()
    dias = (proxima_data - hoje).days
    if dias < 0:
        return "VENCIDO", "#dc3545"
    elif dias <= 7:
        return "PERTO DE VENCER", "#ffc107"
    else:
        return "EM DIA", "#28a745"


def buscar_carrinho(): # Funçao que quando eu colocar o nome da carrinho ele vai consultar e buscar lá no .csv, trazendo as informações da carrinho.
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
                    text=(f" Carrinho: {codigo}\n"
                          f" Última limpeza: {data_ultima.strftime('%d/%m/%Y')}\n"
                          f" Próxima limpeza: {proxima.strftime('%d/%m/%Y')}\n"
                          f" Status: {status}"),
                    bg=cor, fg="white"
                )
                carrinho_atual = linha
                encontrado = True
                break

    if not encontrado:
        resultado.config(text="❌ Carrinho não encontrado",
                         bg="#6c757d", fg="white")

# Função para entrar com os dados do cadastro com validação de erro
def cadastrar():
    codigo = entrada_codigo.get().strip()
    data_str = entrada_data.get().strip() # Renomeado para evitar conflito com data_formatada
    historico = entrada_hist.get().strip()

    try:
        data_formatada = datetime.strptime(data_str, "%d/%m/%Y").date()
        
        # Validação adicional para anos muito antigos ou futuros irreais
        if data_formatada.year < 1900 or data_formatada.year > (datetime.now().year + 5): # Ajuste o intervalo se necessário
             messagebox.showerror("Erro", "Ano inválido! Insira um ano entre 1900 e o ano atual + 5.")
             return

    except ValueError:
        messagebox.showerror("Erro", "Data inválida! Verifique o formato (DD/MM/AAAA) e se a data é real (ex: 30/02 não existe).")
        return
    
    # Validação para não aceitar datas que ainda não chegaram
    hoje = datetime.today().date()
    if data_formatada > hoje:
        messagebox.showerror("Erro", "Essa data ainda não chegou! Coloque uma data válida.")
        return

    # Verificar se o código do carrinho já existe
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
        leitor = csv.DictReader(csvfile)
        for row in leitor:
            if row['codigo'] == codigo:
                messagebox.showwarning("Aviso", f"Esse carrinho '{codigo}' já existe.")
                return

    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        escritor = csv.writer(csvfile)
        escritor.writerow([codigo, data_formatada.isoformat(), historico])

    messagebox.showinfo("Sucesso", "Carrinho cadastrado com sucesso!")
    janela_cadastro.destroy()

    gerar_relatorio() 

def abrir_cadastro():
    global janela_cadastro, entrada_codigo, entrada_data, entrada_hist
    janela_cadastro = tk.Toplevel(root)
    janela_cadastro.title("➕ Cadastrar carrinho")
    janela_cadastro.configure(bg="#f1f3f6")
    janela_cadastro.geometry("500x400")
    janela_cadastro.transient(root)
    janela_cadastro.grab_set() 

    tk.Label(janela_cadastro, text="Cadastro de carrinho",
             font=("Segoe UI", 18, "bold"), bg="#f1f3f6", fg="#212529").pack(pady=10)

    campo_frame = tk.Frame(janela_cadastro, bg="#ffffff", relief="solid", bd=1)
    campo_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def campo(texto):
        lbl = tk.Label(campo_frame, text=texto, font=("Segoe UI", 13),
                       bg="#ffffff", fg="#495057", anchor='w')
        lbl.pack(fill='x', padx=20, pady=(10, 0))
        entry = tk.Entry(campo_frame, font=("Segoe UI", 13), relief='solid', borderwidth=1)
        entry.pack(fill='x', padx=20, pady=5, ipady=5)
        return entry

    entrada_codigo = campo("🔢 Código:")
    entrada_data = campo("📅 Data última limpeza (DD/MM/AAAA):")
    entrada_hist = campo("📝 Histórico:")

    def formatar_data(event=None):
        current_text = entrada_data.get().replace("/", "")
        new_text = ""
        for i, char in enumerate(current_text):
            if not char.isdigit():
                continue
            if i == 2 or i == 4:
                new_text += "/" + char
            else:
                new_text += char
        if len(new_text) > 10:
            new_text = new_text[:10]
        if entrada_data.get() != new_text:
            entrada_data.delete(0, tk.END)
            entrada_data.insert(0, new_text)

    entrada_data.bind("<KeyRelease>", formatar_data)

    btn_salvar = tk.Button(janela_cadastro, text="Salvar Cadastro", command=cadastrar)
    estilo_botao(btn_salvar, "#007bff", "#0069d9")
    btn_salvar.pack(pady=15, fill="x", padx=20)

    janela_cadastro.bind('<Return>', lambda event=None: btn_salvar.invoke())
    entrada_codigo.focus_set()

    janela_cadastro.wait_window(janela_cadastro) 
    root.grab_release() 

def editar():
    global carrinho_atual
    if not carrinho_atual:
        messagebox.showwarning("Aviso", "Primeiro consulte um carrinho para editar.")
        return

    def salvar_edicao():
        nova_data_str = entrada_data_edit.get().strip() 
        novo_hist = entrada_hist_edit.get().strip()

        try:
            data_formatada = datetime.strptime(nova_data_str, "%d/%m/%Y").date()
            
            if data_formatada.year < 1900 or data_formatada.year > (datetime.now().year + 5): # Ajuste o intervalo se necessário
                 messagebox.showerror("Erro", "Ano inválido! Insira um ano entre 1900 e o ano atual + 5.")
                 return

        except ValueError:
            messagebox.showerror("Erro", "Data inválida! Verifique o formato (DD/MM/AAAA) e se a data é real (ex: 30/02 não existe).")
            return
        
        hoje = datetime.today().date()
        if data_formatada > hoje:
            messagebox.showerror("Erro", "Essa data ainda não chegou! Coloque uma data válida.")
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

        gerar_relatorio() 

    janela_edicao = tk.Toplevel(root)
    janela_edicao.title(f"✏️ Editar carrinho {carrinho_atual['codigo']}")
    janela_edicao.configure(bg="#f1f3f6")
    janela_edicao.geometry("500x350")
    janela_edicao.transient(root) 
    janela_edicao.grab_set() 

    tk.Label(janela_edicao, text=f"Editar carrinho {carrinho_atual['codigo']}",
             font=("Segoe UI", 18, "bold"), bg="#f1f3f6", fg="#212529").pack(pady=10)

    frame = tk.Frame(janela_edicao, bg="#ffffff", relief="solid", bd=1)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    tk.Label(frame, text="📅 Nova data de limpeza (DD/MM/AAAA):",
             font=("Segoe UI", 13), bg="#ffffff", fg="#495057").pack(pady=(10, 0))
    entrada_data_edit = tk.Entry(frame, font=("Segoe UI", 13))
    entrada_data_edit.pack(fill="x", padx=20, pady=5, ipady=5)
    entrada_data_edit.insert(0, datetime.strptime(
        carrinho_atual['data_ultima_limpeza'], "%Y-%m-%d").strftime("%d/%m/%Y"))

    def formatar_data_edit(event=None):
        current_text = entrada_data_edit.get().replace("/", "")
        new_text = ""
        for i, char in enumerate(current_text):
            if not char.isdigit():
                continue
            if i == 2 or i == 4:
                new_text += "/" + char
            else:
                new_text += char
        if len(new_text) > 10:
            new_text = new_text[:10]
        if entrada_data_edit.get() != new_text:
            entrada_data_edit.delete(0, tk.END)
            entrada_data_edit.insert(0, new_text)

    entrada_data_edit.bind("<KeyRelease>", formatar_data_edit)

    tk.Label(frame, text="📝 Histórico:",
             font=("Segoe UI", 13), bg="#ffffff", fg="#495057").pack(pady=(10, 0))
    entrada_hist_edit = tk.Entry(frame, font=("Segoe UI", 13))
    entrada_hist_edit.pack(fill="x", padx=20, pady=5, ipady=5)
    entrada_hist_edit.insert(0, carrinho_atual['historico'])

    btn_salvar_edicao = tk.Button(janela_edicao, text="Salvar Edição", command=salvar_edicao)
    estilo_botao(btn_salvar_edicao, "#ffc107", "#e0a800")
    btn_salvar_edicao.pack(pady=15, fill="x", padx=20)

    janela_edicao.bind('<Return>', lambda event=None: btn_salvar_edicao.invoke())
    entrada_data_edit.focus_set()

    janela_edicao.wait_window(janela_edicao) 
    root.grab_release() 


def gerar_relatorio():
    hoje = datetime.today().date()
    if hoje.month == 12:
        proximo_mes = 1
        ano_proximo = hoje.year + 1
    else:
        proximo_mes = hoje.month + 1
        ano_proximo = hoje.year

    carrinhos_proximo_mes = []

    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        leitor = csv.DictReader(csvfile)
        for linha in leitor:
            try: 
                data_ultima = datetime.strptime(linha['data_ultima_limpeza'], "%Y-%m-%d").date()
            except ValueError:
                print(f"Aviso: Data inválida encontrada para o carrinho {linha['codigo']} no CSV. Ignorando esta entrada.")
                continue
                
            proxima = data_ultima + timedelta(days=180)
            if proxima.month == proximo_mes and proxima.year == ano_proximo:
                carrinhos_proximo_mes.append({
                    "codigo": linha["codigo"],
                    "ultima": data_ultima.strftime("%d/%m/%Y"),
                    "proxima": proxima.strftime("%d/%m/%Y"),
                    "historico": linha["historico"]
                })

    if not os.path.exists("relatorios"):
        os.makedirs("relatorios")

    file_path = f"relatorios/relatorio_carrinhos_{proximo_mes:02d}_{ano_proximo}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("RELATÓRIO DE LIMPEZA DE CARRINHOS\n")
        f.write(f"Referente ao mês {proximo_mes:02d}/{ano_proximo}\n")
        f.write("=" * 50 + "\n\n")

        if carrinhos_proximo_mes:
            for carrinho in carrinhos_proximo_mes:
                f.write(f"Carrinho: {carrinho['codigo']}\n")
                f.write(f"Última Limpeza: {carrinho['ultima']}\n")
                f.write(f"Próxima Limpeza: {carrinho['proxima']}\n")
                f.write(f"Histórico: {carrinho['historico']}\n")
                f.write("-" * 50 + "\n")
        else:
            f.write("Não há carrinhos com vencimento para este período.\n")

    messagebox.showinfo("Relatório Gerado",
                        f"Relatório referente a {proximo_mes:02d}/{ano_proximo} salvo em '{file_path}'.")

root = tk.Tk()
root.title("Controle de Limpeza de Carrinhos")
root.state('zoomed'),
root.configure(bg="#f1f3f6")

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

tk.Label(root, text="Controle de Limpeza de Carrinhos",
         font=("Segoe UI", 32, "bold"),
         bg="#f1f3f6", fg="#212529").grid(row=0, column=0, pady=20)

main_frame = tk.Frame(root, bg="#ffffff", relief="groove", bd=2)
main_frame.grid(row=1, column=0, sticky="nsew", padx=50, pady=20)
main_frame.grid_rowconfigure(2, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

def placeholder(event=None):
    if entrada.get() == "":
        entrada.insert(0, "Digite o código do carrinho...")
        entrada.config(fg="gray")

def focus_in(event):
    if entrada.get() == "Digite o código do carrinho...":
        entrada.delete(0, "end")
        entrada.config(fg="black")

entrada = tk.Entry(main_frame, font=("Segoe UI", 20),
                   relief="solid", justify="center")
entrada.grid(row=0, column=0, pady=20, padx=90, sticky="ew", ipady=10)
entrada.insert(0, "Digite o código do carrinho...")
entrada.config(fg="gray")
entrada.bind("<FocusIn>", focus_in)
entrada.bind("<FocusOut>", placeholder)
entrada.bind("<Return>", lambda e: buscar_carrinho()) 

def estilo_botao(botao, cor_bg, cor_hover):
    botao.config(bg=cor_bg, fg="white", relief="flat",
                 font=("Segoe UI", 14, "bold"), width=18, height=2)
    def on_enter(e): botao.config(bg=cor_hover)
    def on_leave(e): botao.config(bg=cor_bg)
    botao.bind("<Enter>", on_enter)
    botao.bind("<Leave>", on_leave)

btn_frame = tk.Frame(main_frame, bg="#ffffff")
btn_frame.grid(row=1, column=0, pady=15)

btn1 = tk.Button(btn_frame, text="🔍 Consultar", command=buscar_carrinho)
estilo_botao(btn1, "#4D4F4D", "#727572")
btn1.grid(row=0, column=0, padx=15)

btn2 = tk.Button(btn_frame, text="➕ Novo Cadastro", command=abrir_cadastro)
estilo_botao(btn2, "#59b86e", "#87d497")
btn2.grid(row=0, column=1, padx=15)

btn3 = tk.Button(btn_frame, text="✏️ Editar", command=editar)
estilo_botao(btn3, "#faa13c", "#eeb471")
btn3.grid(row=0, column=2, padx=15)

btn4 = tk.Button(btn_frame, text="📄 Gerar Relatório", command=gerar_relatorio)
estilo_botao(btn4, "#3670a3", "#6f96b8")
btn4.grid(row=0, column=3, padx=15)

resultado = tk.Label(main_frame, text="",
                     font=("Segoe UI", 18),
                     bg="#ffffff", fg="#212529",
                     relief="solid", bd=1,
                     wraplength=1000, justify="left")
resultado.grid(row=2, column=0, sticky="nsew", padx=50, pady=30)

if datetime.today().day == 1:
    gerar_relatorio()

root.mainloop()