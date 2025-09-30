import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
import csv, os
import qrcode
from PIL import Image, ImageTk
import openpyxl
from openpyxl.styles import Font, Border, Side, Alignment, PatternFill 
from openpyxl.utils import get_column_letter

CSV_FILE = "carrinhos.csv"
SENHA_MESTRE = "1234" 

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["codigo", "data_ultima_limpeza", "historico", "periodicidade_dias"])
else:
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        if "periodicidade_dias" not in header:
            messagebox.showinfo("Atualização do CSV",
                                "Detectamos uma versão antiga do arquivo CSV.\n"
                                "Adicionando a coluna 'periodicidade_dias' com valor padrão de 180 dias para carrinhos existentes.")

            temp_file = CSV_FILE + ".tmp"
            with open(CSV_FILE, "r", newline="", encoding="utf-8") as infile, \
                 open(temp_file, "w", newline="", encoding="utf-8") as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)

                new_header = header + ["periodicidade_dias"]
                writer.writerow(new_header)

                for row in reader:
                    writer.writerow(row + ["180"])

            os.remove(CSV_FILE)
            os.rename(temp_file, CSV_FILE)


# -------- Funções --------
def calcular_status(proxima_data):
    hoje = datetime.today().date()
    dias = (proxima_data - hoje).days
    if dias < 0:
        return "❌ VENCIDO", "#e74c3c"  
    elif dias <= 20:  
        return "VENCE EM BREVE", "#e74c3c" 
    elif dias <= 30: 
        return "ATENÇÃO: PRÓXIMO DO VENCIMENTO", "#f1c40f" 
    else:
        return "✅ EM DIA", "#2ecc71" 


def estilo_botao(botao, cor_bg, cor_hover):
    botao.config(
        bg=cor_bg,
        fg="white",
        relief="flat",
        font=("Segoe UI", 13, "bold"),
        width=18,
        height=2,
        bd=0,
        highlightthickness=0,
        cursor="hand2",
        activebackground=cor_hover,
    )

    def on_enter(e):
        botao.config(bg=cor_hover)

    def on_leave(e):
        botao.config(bg=cor_bg)

    botao.bind("<Enter>", on_enter)
    botao.bind("<Leave>", on_leave)


def buscar_carrinho():
    global carrinho_atual
    codigo = entrada.get().strip()
    carrinho_atual = None
    with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
        for linha in csv.DictReader(csvfile):
            if linha["codigo"] == codigo:
                data_ultima = datetime.strptime(
                    linha["data_ultima_limpeza"], "%Y-%m-%d"
                ).date()

                periodicidade_dias = int(linha.get("periodicidade_dias", 180)) 
                proxima = data_ultima + timedelta(days=periodicidade_dias)

                status, cor = calcular_status(proxima)
                resultado_frame.config(highlightbackground=cor, highlightthickness=3)
                resultado_label.config(
                    text=(
                        f"Carrinho: {codigo}\n\n"
                        f"🗓️ Última limpeza: {data_ultima.strftime('%d/%m/%Y')}\n"
                        f"📅 Periodicidade: {periodicidade_dias} dias\n" 
                        f"📅 Próxima limpeza: {proxima.strftime('%d/%m/%Y')}\n"
                        f"🔎 Status: {status}"
                    ),
                    fg="#2c3e50",
                )
                carrinho_atual = linha
                return
    resultado_frame.config(highlightbackground="#95a5a6", highlightthickness=3)
    resultado_label.config(text="❌ carrinho não encontrado", fg="#7f8c8d")


def gerar_e_mostrar_qrcode(codigo, data_limpeza_str, periodicidade_dias_str):
    conteudo_qrcode = f"Codigo: {codigo}\nData: {data_limpeza_str}\nPeriodicidade: {periodicidade_dias_str} dias"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=2,
    )
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

    tk.Label(
        main_frame_qr,
        text=f"QR Code para carrinho {codigo}",
        font=("Segoe UI", 18, "bold"),
        bg="#f4f6f9",
        fg="#2c3e50",
    ).pack(pady=(0, 15))

    qr_image_frame = tk.Frame(main_frame_qr, bg="#ffffff", bd=2, relief="solid")
    qr_image_frame.pack(pady=10)
    img_tk = ImageTk.PhotoImage(img_qr)
    lbl_qr = tk.Label(qr_image_frame, image=img_tk, bg="#ffffff")
    lbl_qr.image = img_tk
    lbl_qr.pack(padx=10, pady=10)

    tk.Label(
        main_frame_qr,
        text=f"Código: {codigo} | Data: {data_limpeza_str} | Periodicidade: {periodicidade_dias_str} dias",
        font=("Segoe UI", 12),
        bg="#f4f6f9",
        fg="#007bff",
    ).pack(pady=10)

    def salvar_qrcode_png():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile=f"qrcode_carrinho_{codigo}.png",
        )
        if file_path:
            img_qr.save(file_path)
            messagebox.showinfo("Sucesso", f"QR Code salvo em:\n{file_path}")

    btn_salvar_qr = tk.Button(
        main_frame_qr, text="⬇️ Salvar como PNG", command=salvar_qrcode_png
    )
    estilo_botao(btn_salvar_qr, "#2980b9", "#2471a3")
    btn_salvar_qr.pack(pady=20)

    janela_qrcode.update_idletasks()
    janela_qrcode.geometry(
        f"{main_frame_qr.winfo_reqwidth()+40}x{main_frame_qr.winfo_reqheight()+40}"
    )
    janela_qrcode.wait_window(janela_qrcode)
    root.grab_release()


def cadastrar():
    codigo = entrada_codigo.get().strip()
    data = entrada_data.get().strip()
    historico = entrada_hist.get().strip()
    periodicidade_str = entrada_periodicidade.get().strip()

    try:
        data_formatada = datetime.strptime(data, "%d/%m/%Y").date()
    except ValueError:
        messagebox.showerror("Erro", "Data inválida! Use DD/MM/AAAA.")
        return
    if data_formatada > datetime.today().date():
        messagebox.showerror("Erro", "Data futura inválida.")
        return

    try:
        periodicidade_dias = int(periodicidade_str)
        if periodicidade_dias <= 0:
            messagebox.showerror("Erro", "Periodicidade deve ser um número inteiro positivo.")
            return
    except ValueError:
        messagebox.showerror("Erro", "Periodicidade inválida! Digite um número de dias.")
        return

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as csvfile:
        for row in csv.DictReader(csvfile):
            if row["codigo"] == codigo:
                messagebox.showwarning("Aviso", f"carrinho '{codigo}' já existe.")
                return

    if messagebox.askyesno(
        "Gerar QR Code?", f"Deseja gerar QR Code para a Carrinho '{codigo}'?"
    ):
        gerar_e_mostrar_qrcode(codigo, data, periodicidade_str)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as csvfile:
        csv.writer(csvfile).writerow([codigo, data_formatada.isoformat(), historico, str(periodicidade_dias)])

    messagebox.showinfo("Sucesso", "Carrinho cadastrado com sucesso!")
    janela_cadastro.destroy()


def abrir_cadastro():
    global janela_cadastro, entrada_codigo, entrada_data, entrada_hist, entrada_periodicidade
    janela_cadastro = tk.Toplevel(root)
    janela_cadastro.title("➕ Cadastrar Carrinho")
    janela_cadastro.configure(bg="#f4f6f9")
    janela_cadastro.geometry("500x500")
    janela_cadastro.transient(root)
    janela_cadastro.grab_set()

    tk.Label(
        janela_cadastro,
        text="Cadastro de Carrinho",
        font=("Segoe UI", 18, "bold"),
        bg="#f4f6f9",
        fg="#2c3e50",
    ).pack(pady=10)

    frame = tk.Frame(janela_cadastro, bg="white", relief="solid", bd=1)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    def campo(texto, valor_inicial=""):
        tk.Label(
            frame,
            text=texto,
            font=("Segoe UI", 13),
            bg="white",
            fg="#495057",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(10, 0))
        entry = tk.Entry(frame, font=("Segoe UI", 13), relief="solid", bd=1)
        entry.pack(fill="x", padx=20, pady=5, ipady=5)
        entry.insert(0, valor_inicial)
        return entry

    entrada_codigo = campo("🔢 Código:")
    entrada_data = campo("📅 Data última limpeza (DD/MM/AAAA):")
    entrada_hist = campo("📝 Histórico:")
    entrada_periodicidade = campo("🗓️ Periodicidade de vencimento (dias):", "180")

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
        nova_periodicidade_str = entrada_periodicidade_edit.get().strip()

        try:
            data_formatada = datetime.strptime(nova_data, "%d/%m/%Y").date()
        except ValueError:
            messagebox.showerror("Erro", "Data inválida! Use DD/MM/AAAA.")
            return
        if data_formatada > datetime.today().date():
            messagebox.showerror("Erro", "Data futura inválida.")
            return

        try:
            nova_periodicidade_dias = int(nova_periodicidade_str)
            if nova_periodicidade_dias <= 0:
                messagebox.showerror("Erro", "Periodicidade deve ser um número inteiro positivo.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Periodicidade inválida! Digite um número de dias.")
            return

        linhas = []
        with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            header = reader.fieldnames

            for linha in reader:
                if linha["codigo"] == carrinho_atual["codigo"]:
                    linha["data_ultima_limpeza"] = data_formatada.isoformat()
                    linha["historico"] = novo_hist
                    linha["periodicidade_dias"] = str(nova_periodicidade_dias)
                linhas.append(linha)

        with open(CSV_FILE, "w", newline="", encoding="utf-8") as csvfile:
            escritor = csv.DictWriter(
                csvfile, fieldnames=header
            )
            escritor.writeheader()
            escritor.writerows(linhas)
        messagebox.showinfo("Sucesso", "Carrinho editado com sucesso!")
        janela_edicao.destroy()
        buscar_carrinho()
     
    janela_edicao = tk.Toplevel(root)
    janela_edicao.title(f"✏️ Editar Carrinho {carrinho_atual['codigo']}")
    janela_edicao.configure(bg="#f4f6f9")
    janela_edicao.geometry("500x450")
    janela_edicao.transient(root)
    janela_edicao.grab_set()

    tk.Label(
        janela_edicao,
        text=f"Editar Carrinho {carrinho_atual['codigo']}",
        font=("Segoe UI", 18, "bold"),
        bg="#f4f6f9",
        fg="#2c3e50",
    ).pack(pady=10)

    frame = tk.Frame(janela_edicao, bg="white", relief="solid", bd=1)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    tk.Label(
        frame,
        text="📅 Nova Data (DD/MM/AAAA):",
        font=("Segoe UI", 13),
        bg="white",
        fg="#495057",
    ).pack(pady=(10, 0))
    entrada_data_edit = tk.Entry(frame, font=("Segoe UI", 13))
    entrada_data_edit.pack(fill="x", padx=20, pady=5, ipady=5)
    entrada_data_edit.insert(
        0,
        datetime.strptime(carrinho_atual["data_ultima_limpeza"], "%Y-%m-%d").strftime(
            "%d/%m/%Y"
        ),
    )

    tk.Label(
        frame, text="📝 Histórico:", font=("Segoe UI", 13), bg="white", fg="#495057"
    ).pack(pady=(10, 0))
    entrada_hist_edit = tk.Entry(frame, font=("Segoe UI", 13))
    entrada_hist_edit.pack(fill="x", padx=20, pady=5, ipady=5)
    entrada_hist_edit.insert(0, carrinho_atual["historico"])

    tk.Label(
        frame, text="🗓️ Periodicidade (dias):", font=("Segoe UI", 13), bg="white", fg="#495057"
    ).pack(pady=(10, 0))
    entrada_periodicidade_edit = tk.Entry(frame, font=("Segoe UI", 13))
    entrada_periodicidade_edit.pack(fill="x", padx=20, pady=5, ipady=5)
    entrada_periodicidade_edit.insert(0, carrinho_atual.get("periodicidade_dias", "180"))

    btn = tk.Button(janela_edicao, text="Salvar Edição", command=salvar_edicao)
    estilo_botao(btn, "#f39c12", "#d68910")
    btn.pack(pady=15, fill="x", padx=20)

    entrada_data_edit.focus_set()
    janela_edicao.wait_window(janela_edicao)
    root.grab_release()


def gerar_relatorio():
    hoje = datetime.today().date()
    if hoje.month == 12:
        primeiro_dia_proximo_mes = hoje.replace(year=hoje.year + 1, month=1, day=1)
    else:
        primeiro_dia_proximo_mes = hoje.replace(month=hoje.month + 1, day=1)

    carrinhos_proximo_mes = []
    with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
        for linha in csv.DictReader(csvfile):
            data_ultima = datetime.strptime(
                linha["data_ultima_limpeza"], "%Y-%m-%d"
            ).date()

            periodicidade_dias = int(linha.get("periodicidade_dias", 180))
            proxima = data_ultima + timedelta(days=periodicidade_dias)

            if (proxima.year == primeiro_dia_proximo_mes.year and proxima.month == primeiro_dia_proximo_mes.month) or \
               (proxima < hoje):
                carrinhos_proximo_mes.append(
                    {
                        "codigo": linha["codigo"],
                        "ultima": data_ultima, 
                        "proxima": proxima, 
                        "periodicidade": periodicidade_dias,
                        "historico": linha["historico"],
                        "status_vencimento": "VENCIDO" if proxima < hoje else "A VENCER"
                    }
                )

    carrinhos_proximo_mes.sort(key=lambda x: x['proxima']) 
    if not os.path.exists("relatorios"):
        os.makedirs("relatorios")

    file_path_excel = f"relatorios/relatorio_carrinhos_{primeiro_dia_proximo_mes.month:02d}_{primeiro_dia_proximo_mes.year}.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Relatório de Carrinhos"

    header_font = Font(name='Segoe UI', size=12, bold=True, color='FFFFFF')
    title_font = Font(name='Segoe UI', size=16, bold=True, color='2C3E50')
    border_style = Border(left=Side(style='thin'), right=Side(style='thin'),
                          top=Side(style='thin'), bottom=Side(style='thin'))
    fill_header = PatternFill(start_color='34495E', end_color='34495E', fill_type='solid')
    fill_vencido = PatternFill(start_color='E74C3C', end_color='E74C3C', fill_type='solid')
    fill_avencer = PatternFill(start_color='F1C40F', end_color='F1C40F', fill_type='solid') 
    alignment_center = Alignment(horizontal='center', vertical='center')
    alignment_left = Alignment(horizontal='left', vertical='center')

    sheet.merge_cells('A1:F1')
    title_cell = sheet['A1']
    title_cell.value = "RELATÓRIO DE LIMPEZA DE CARRINHOS"
    title_cell.font = title_font
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    title_cell.fill = PatternFill(start_color='ECF0F1', end_color='ECF0F1', fill_type='solid') 

    sheet.merge_cells('A2:F2')
    subtitle_cell = sheet['A2']
    subtitle_cell.value = f"Referente ao mês {primeiro_dia_proximo_mes.month:02d}/{primeiro_dia_proximo_mes.year} e Vencidos"
    subtitle_cell.font = Font(name='Segoe UI', size=12, bold=True, color='7F8C8D')
    subtitle_cell.alignment = Alignment(horizontal='center', vertical='center')
    subtitle_cell.fill = PatternFill(start_color='ECF0F1', end_color='ECF0F1', fill_type='solid')

    sheet.row_dimensions[1].height = 30
    sheet.row_dimensions[2].height = 20

    headers = ["CÓDIGO", "ÚLTIMA LIMPEZA", "PRÓXIMA LIMPEZA", "PERIOD. (dias)", "STATUS", "HISTÓRICO"]
    sheet.append([]) 
    sheet.append(headers) 

    for col_idx, header_text in enumerate(headers, 1):
        cell = sheet.cell(row=4, column=col_idx) 
        cell.font = header_font
        cell.fill = fill_header
        cell.border = border_style
        cell.alignment = alignment_center

    row_num = 5
    if carrinhos_proximo_mes:
        for c in carrinhos_proximo_mes:
            sheet.cell(row=row_num, column=1, value=c['codigo']).alignment = alignment_center
            sheet.cell(row=row_num, column=2, value=c['ultima']).number_format = 'DD/MM/YYYY'
            sheet.cell(row=row_num, column=3, value=c['proxima']).number_format = 'DD/MM/YYYY'
            sheet.cell(row=row_num, column=4, value=c['periodicidade']).alignment = alignment_center
            sheet.cell(row=row_num, column=5, value=c['status_vencimento']).alignment = alignment_center
            sheet.cell(row=row_num, column=6, value=c['historico']).alignment = alignment_left

            status_cell = sheet.cell(row=row_num, column=5)
            if c['status_vencimento'] == "VENCIDO":
                status_cell.fill = fill_vencido
                status_cell.font = Font(color='FFFFFF', bold=True)
            elif c['status_vencimento'] == "A VENCER":
                status_cell.fill = fill_avencer
                status_cell.font = Font(color='000000', bold=True)


            for col_idx in range(1, len(headers) + 1):
                cell = sheet.cell(row=row_num, column=col_idx)
                cell.border = border_style

            row_num += 1
    else:
        sheet.merge_cells(f'A5:F5')
        sheet['A5'].value = "Não há carrinhos para relatar neste período."
        sheet['A5'].alignment = Alignment(horizontal='center', vertical='center')
        sheet['A5'].font = Font(name='Segoe UI', size=12, italic=True, color='7F8C8D')

        for col_idx in range(1, len(headers) + 1):
            sheet.cell(row=5, column=col_idx).border = border_style


    column_widths = [12, 18, 18, 15, 15, 40] 
    for i, width in enumerate(column_widths):
        sheet.column_dimensions[get_column_letter(i+1)].width = width

    try:
        workbook.save(file_path_excel)
        messagebox.showinfo("Relatório", f"Relatório gerado com sucesso!\n\nArquivo Excel: '{file_path_excel}'")
    except Exception as e:
        messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo Excel. Erro: {e}")


def verificar_senha(callback_funcao):
    """
    Abre uma janela para solicitar a senha. Se a senha estiver correta,
    chama a 'callback_funcao'.
    """
    janela_senha = tk.Toplevel(root)
    janela_senha.title("Autenticação")
    janela_senha.geometry("300x180")
    janela_senha.configure(bg="#f4f6f9")
    janela_senha.resizable(False, False)
    janela_senha.transient(root)
    janela_senha.grab_set() 

    def tentar_login():
        senha_digitada = entrada_senha.get()
        if senha_digitada == SENHA_MESTRE:
            janela_senha.destroy()
            callback_funcao()
        else:
            messagebox.showerror("Erro de Senha", "Senha incorreta!")
            entrada_senha.delete(0, tk.END) 
            entrada_senha.focus_set()

    tk.Label(janela_senha, text="Digite a senha para acessar:",
             font=("Segoe UI", 12), bg="#f4f6f9", fg="#2c3e50").pack(pady=15)

    entrada_senha = tk.Entry(janela_senha, show="*", font=("Segoe UI", 14), relief="solid", bd=1)
    entrada_senha.pack(pady=5, padx=20, fill="x", ipady=5)
    entrada_senha.bind("<Return>", lambda e: tentar_login()) 
    entrada_senha.focus_set()

    btn_login = tk.Button(janela_senha, text="Entrar", command=tentar_login)
    estilo_botao(btn_login, "#3498db", "#2980b9") 
    btn_login.config(width=10, height=1) 
    btn_login.pack(pady=15)

    janela_senha.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (janela_senha.winfo_width() // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (janela_senha.winfo_height() // 2)
    janela_senha.geometry(f"+{x}+{y}")

root = tk.Tk()
root.title(" Controle de Limpeza de Carrinhos")
root.state("zoomed")
root.configure(bg="#f4f6f9")

tk.Label(
    root,
    text=" Controle de Limpeza de Carrinhos",
    font=("Segoe UI", 32, "bold"),
    bg="#f4f6f9",
    fg="#2c3e50",
).pack(pady=20)

main_frame = tk.Frame(root, bg="white", relief="groove", bd=2)
main_frame.pack(fill="both", expand=True, padx=80, pady=30)

entrada = tk.Entry(
    main_frame, font=("Segoe UI", 20), relief="solid", justify="center", bd=2
)
entrada.insert(0, "Digite o código do carrinho...")
entrada.config(fg="gray")
entrada.bind(
    "<FocusIn>", lambda e: (entrada.delete(0, "end"), entrada.config(fg="black"))
)
entrada.bind("<Return>", lambda e: buscar_carrinho())
entrada.pack(pady=30, padx=200, ipady=10, fill="x")

btn_frame = tk.Frame(main_frame, bg="white")
btn_frame.pack(pady=20)
btns = [
    ("🔍 Consultar", buscar_carrinho, "#34495e", "#2c3e50"),
    ("➕ Novo Cadastro", abrir_cadastro, "#27ae60", "#229954"), 
    ("✏️ Editar", lambda: verificar_senha(editar), "#f39c12", "#d68910"), 
    ("📄 Relatório", gerar_relatorio, "#2980b9", "#2471a3"),
]
for i, (txt, cmd, c1, c2) in enumerate(btns):
    b = tk.Button(btn_frame, text=txt, command=cmd)
    estilo_botao(b, c1, c2)
    b.grid(row=0, column=i, padx=15)

resultado_frame = tk.Frame(
    main_frame,
    bg="white",
    relief="solid",
    bd=2,
    highlightthickness=3,
    highlightbackground="#95a5a6",
)
resultado_frame.pack(fill="both", expand=True, padx=60, pady=30)
resultado_label = tk.Label(
    resultado_frame,
    text="",
    font=("Segoe UI", 18),
    bg="white",
    fg="#2c3e50",
    justify="left",
    anchor="nw",
)
resultado_label.pack(padx=30, pady=30, anchor="w")

root.mainloop()