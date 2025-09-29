import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
import csv, os
import qrcode
from PIL import Image, ImageTk

CSV_FILE = 'carrinhos.csv'

# Garante que o arquivo CSV exista
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(['codigo', 'data_ultima_limpeza', 'historico'])

# -------- Funções --------
def calcular_status(proxima_data):
    hoje = datetime.today().date()
    dias = (proxima_data - hoje).days
    if dias < 0:
        return "❌ VENCIDO", "#e74c3c"
    elif dias <= 7:
        return "⚠️ PERTO DE VENCER", "#f1c40f"
    else:
        return "✅ EM DIA", "#2ecc71"

def estilo_botao(botao, cor_bg, cor_hover):
    botao.config(
        bg=cor_bg, fg="white", relief="flat",
        font=("Segoe UI", 13, "bold"),
        width=18, height=2, bd=0, highlightthickness=0,
        cursor="hand2", activebackground=cor_hover
    )
    def on_enter(e): botao.config(bg=cor_hover)
    def on_leave(e): botao.config(bg=cor_bg)
    botao.bind("<Enter>", on_enter)
    botao.bind("<Leave>", on_leave)

def buscar_carrinho():
    global carrinho_atual
    codigo = entrada.get().strip()
    carrinho_atual = None
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        for linha in csv.DictReader(csvfile):
            if linha['codigo'] == codigo:
                data_ultima = datetime.strptime(linha['data_ultima_limpeza'], "%Y-%m-%d").date()
                proxima = data_ultima + timedelta(days=180)
                status, cor = calcular_status(proxima)
                resultado_frame.config(highlightbackground=cor, highlightthickness=3)
                resultado_label.config(
                    text=(
                        f"Carrinho: {codigo}\n\n"
                        f"🗓️Última limpeza: {data_ultima.strftime('%d/%m/%Y')}\n"
                        f"📅 Próxima limpeza: {proxima.strftime('%d/%m/%Y')}\n"
                        f"🔎 Status: {status}"
                    ),
                    fg="#2c3e50"
                )
                carrinho_atual = linha
                return
    resultado_frame.config(highlightbackground="#95a5a6", highlightthickness=3)
    resultado_label.config(text="❌ carrinho não encontrado", fg="#7f8c8d")

def gerar_e_mostrar_qrcode(codigo, data_limpeza_str):
    conteudo_qrcode = f"Codigo: {codigo}\nData: {data_limpeza_str}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=4, border=2)
    qr.add_data(conteudo_qrcode)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    janela_qrcode = tk.Toplevel(root)
    janela_qrcode.title(f"QR Code: carrinho {codigo}")
    janela_qrcode.configure(bg="#f4f6f9")
    janela_qrcode.resizable(False, False)
    janela_qrcode.transient(root)
    janela_qrcode.grab_set()

    main_frame_qr = tk.Frame(janela_qrcode, bg="#f4f6f9", padx=20, pady=20)
    main_frame_qr.pack(expand=True, fill="both")

    tk.Label(main_frame_qr, text=f"QR Code para carrinho {codigo}",
             font=("Segoe UI", 18, "bold"), bg="#f4f6f9", fg="#2c3e50").pack(pady=(0, 15))

    qr_image_frame = tk.Frame(main_frame_qr, bg="#ffffff", bd=2, relief="solid")
    qr_image_frame.pack(pady=10)
    img_tk = ImageTk.PhotoImage(img_qr)
    lbl_qr = tk.Label(qr_image_frame, image=img_tk, bg="#ffffff")
    lbl_qr.image = img_tk
    lbl_qr.pack(padx=10, pady=10)

    tk.Label(main_frame_qr, text=f"Código: {codigo} | Data: {data_limpeza_str}",
             font=("Segoe UI", 12), bg="#f4f6f9", fg="#007bff").pack(pady=10)

    def salvar_qrcode_png():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG files", "*.png")],
            initialfile=f"qrcode_carrinho_{codigo}.png")
        if file_path:
            img_qr.save(file_path)
            messagebox.showinfo("Sucesso", f"QR Code salvo em:\n{file_path}")

    btn_salvar_qr = tk.Button(main_frame_qr, text="⬇️ Salvar como PNG", command=salvar_qrcode_png)
    estilo_botao(btn_salvar_qr, "#2980b9", "#2471a3")
    btn_salvar_qr.pack(pady=20)

    janela_qrcode.update_idletasks()
    janela_qrcode.geometry(f"{main_frame_qr.winfo_reqwidth()+40}x{main_frame_qr.winfo_reqheight()+40}")
    janela_qrcode.wait_window(janela_qrcode)
    root.grab_release()

def cadastrar():
    codigo = entrada_codigo.get().strip()
    data = entrada_data.get().strip()
    historico = entrada_hist.get().strip()
    try:
        data_formatada = datetime.strptime(data, "%d/%m/%Y").date()
    except ValueError:
        messagebox.showerror("Erro", "Data inválida! Use DD/MM/AAAA.")
        return
    if data_formatada > datetime.today().date():
        messagebox.showerror("Erro", "Data futura inválida.")
        return
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
        for row in csv.DictReader(csvfile):
            if row['codigo'] == codigo:
                messagebox.showwarning("Aviso", f"carrinho '{codigo}' já existe.")
                return
    if messagebox.askyesno("Gerar QR Code?", f"Deseja gerar QR Code para a Carrinho '{codigo}'?"):
        gerar_e_mostrar_qrcode(codigo, data)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        csv.writer(csvfile).writerow([codigo, data_formatada.isoformat(), historico])
    messagebox.showinfo("Sucesso", "Carrinho cadastrado com sucesso!")
    janela_cadastro.destroy()

def abrir_cadastro():
    global janela_cadastro, entrada_codigo, entrada_data, entrada_hist
    janela_cadastro = tk.Toplevel(root)
    janela_cadastro.title("➕ Cadastrar Carrinho")
    janela_cadastro.configure(bg="#f4f6f9")
    janela_cadastro.geometry("500x400")
    janela_cadastro.transient(root)
    janela_cadastro.grab_set()

    tk.Label(janela_cadastro, text="Cadastro de Carrinho",
             font=("Segoe UI", 18, "bold"), bg="#f4f6f9", fg="#2c3e50").pack(pady=10)

    frame = tk.Frame(janela_cadastro, bg="white", relief="solid", bd=1)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    def campo(texto):
        tk.Label(frame, text=texto, font=("Segoe UI", 13),
                 bg="white", fg="#495057", anchor="w").pack(fill="x", padx=20, pady=(10, 0))
        entry = tk.Entry(frame, font=("Segoe UI", 13), relief="solid", bd=1)
        entry.pack(fill="x", padx=20, pady=5, ipady=5)
        return entry

    entrada_codigo = campo("🔢 Código:")
    entrada_data = campo("📅 Data última limpeza (DD/MM/AAAA):")
    entrada_hist = campo("📝 Histórico:")

    btn_salvar = tk.Button(janela_cadastro, text="Salvar Cadastro", command=cadastrar)
    estilo_botao(btn_salvar, "#27ae60", "#229954")
    btn_salvar.pack(pady=15, fill="x", padx=20)

    entrada_codigo.focus_set()
    janela_cadastro.wait_window(janela_cadastro)
    root.grab_release()

def editar():
    global carrinho_atual
    if not carrinho_atual:
        messagebox.showwarning("Aviso", "Consulte um carrinho para editar.")
        return
    def salvar_edicao():
        nova_data = entrada_data_edit.get().strip()
        novo_hist = entrada_hist_edit.get().strip()
        try:
            data_formatada = datetime.strptime(nova_data, "%d/%m/%Y").date()
        except ValueError:
            messagebox.showerror("Erro", "Data inválida! Use DD/MM/AAAA.")
            return
        if data_formatada > datetime.today().date():
            messagebox.showerror("Erro", "Data futura inválida.")
            return
        linhas = []
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            for linha in csv.DictReader(csvfile):
                if linha['codigo'] == carrinho_atual['codigo']:
                    linha['data_ultima_limpeza'] = data_formatada.isoformat()
                    linha['historico'] = novo_hist
                linhas.append(linha)
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            escritor = csv.DictWriter(csvfile, fieldnames=['codigo', 'data_ultima_limpeza', 'historico'])
            escritor.writeheader(); escritor.writerows(linhas)
        messagebox.showinfo("Sucesso", "Carrinho editado com sucesso!")
        janela_edicao.destroy(); buscar_carrinho(); gerar_relatorio()

    janela_edicao = tk.Toplevel(root)
    janela_edicao.title(f"✏️ Editar Carrinho {carrinho_atual['codigo']}")
    janela_edicao.configure(bg="#f4f6f9"); janela_edicao.geometry("500x350")
    janela_edicao.transient(root); janela_edicao.grab_set()

    tk.Label(janela_edicao, text=f"Editar Carrinho {carrinho_atual['codigo']}",
             font=("Segoe UI", 18, "bold"), bg="#f4f6f9", fg="#2c3e50").pack(pady=10)

    frame = tk.Frame(janela_edicao, bg="white", relief="solid", bd=1)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    tk.Label(frame, text="📅 Nova Data (DD/MM/AAAA):",
             font=("Segoe UI", 13), bg="white", fg="#495057").pack(pady=(10, 0))
    entrada_data_edit = tk.Entry(frame, font=("Segoe UI", 13))
    entrada_data_edit.pack(fill="x", padx=20, pady=5, ipady=5)
    entrada_data_edit.insert(0, datetime.strptime(carrinho_atual['data_ultima_limpeza'], "%Y-%m-%d").strftime("%d/%m/%Y"))

    tk.Label(frame, text="📝 Histórico:",
             font=("Segoe UI", 13), bg="white", fg="#495057").pack(pady=(10, 0))
    entrada_hist_edit = tk.Entry(frame, font=("Segoe UI", 13))
    entrada_hist_edit.pack(fill="x", padx=20, pady=5, ipady=5)
    entrada_hist_edit.insert(0, carrinho_atual['historico'])

    btn = tk.Button(janela_edicao, text="Salvar Edição", command=salvar_edicao)
    estilo_botao(btn, "#f39c12", "#d68910")
    btn.pack(pady=15, fill="x", padx=20)

    entrada_data_edit.focus_set()
    janela_edicao.wait_window(janela_edicao); root.grab_release()

def gerar_relatorio():
    hoje = datetime.today().date()
    proximo_mes, ano_proximo = (1, hoje.year+1) if hoje.month==12 else (hoje.month+1, hoje.year)
    carrinhos_proximo_mes = []
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        for linha in csv.DictReader(csvfile):
            data_ultima = datetime.strptime(linha['data_ultima_limpeza'], "%Y-%m-%d").date()
            proxima = data_ultima + timedelta(days=180)
            if proxima.month == proximo_mes and proxima.year == ano_proximo:
                carrinhos_proximo_mes.append({
                    "codigo": linha["codigo"],
                    "ultima": data_ultima.strftime("%d/%m/%Y"),
                    "proxima": proxima.strftime("%d/%m/%Y"),
                    "historico": linha["historico"]
                })
    if not os.path.exists("relatorios"): os.makedirs("relatorios")
    file_path = f"relatorios/relatorio_carrinhos_{proximo_mes:02d}_{ano_proximo}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("RELATÓRIO DE LIMPEZA DE CARRINHOS\n")
        f.write(f"Referente ao mês {proximo_mes:02d}/{ano_proximo}\n")
        f.write("="*50 + "\n\n")
        if carrinhos_proximo_mes:
            for c in carrinhos_proximo_mes:
                f.write(f"carrinho: {c['codigo']}\nÚltima: {c['ultima']}\nPróxima: {c['proxima']}\nHistórico: {c['historico']}\n")
                f.write("-"*50 + "\n")
        else:
            f.write("Não há carrinhos com vencimento para este período.\n")
    messagebox.showinfo("Relatório", f"Relatório salvo em '{file_path}'.")

# -------- Layout Principal --------
root = tk.Tk()
root.title(" Controle de Limpeza de Carrinhos")
root.state('zoomed'); root.configure(bg="#f4f6f9")

tk.Label(root, text=" Controle de Limpeza de Carrinhos",
         font=("Segoe UI", 32, "bold"),
         bg="#f4f6f9", fg="#2c3e50").pack(pady=20)

main_frame = tk.Frame(root, bg="white", relief="groove", bd=2)
main_frame.pack(fill="both", expand=True, padx=80, pady=30)

entrada = tk.Entry(main_frame, font=("Segoe UI", 20),
                   relief="solid", justify="center", bd=2)
entrada.insert(0, "Digite o código do carrinho...")
entrada.config(fg="gray")
entrada.bind("<FocusIn>", lambda e: (entrada.delete(0,"end"), entrada.config(fg="black")))
entrada.bind("<Return>", lambda e: buscar_carrinho())
entrada.pack(pady=30, padx=200, ipady=10, fill="x")

btn_frame = tk.Frame(main_frame, bg="white")
btn_frame.pack(pady=20)
btns = [
    ("🔍 Consultar", buscar_carrinho, "#34495e", "#2c3e50"),
    ("➕ Novo Cadastro", abrir_cadastro, "#27ae60", "#229954"),
    ("✏️ Editar", editar, "#f39c12", "#d68910"),
    ("📄 Relatório", gerar_relatorio, "#2980b9", "#2471a3"),
]
for i,(txt,cmd,c1,c2) in enumerate(btns):
    b=tk.Button(btn_frame,text=txt,command=cmd); estilo_botao(b,c1,c2); b.grid(row=0,column=i,padx=15)

resultado_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=2,
                           highlightthickness=3, highlightbackground="#95a5a6")
resultado_frame.pack(fill="both", expand=True, padx=60, pady=30)
resultado_label = tk.Label(resultado_frame, text="", font=("Segoe UI", 18),
                           bg="white", fg="#2c3e50", justify="left", anchor="nw")
resultado_label.pack(padx=30, pady=30, anchor="w")

if datetime.today().day == 1: gerar_relatorio()
root.mainloop()