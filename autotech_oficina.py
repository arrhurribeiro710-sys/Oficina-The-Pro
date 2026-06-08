import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class OficinaTechPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OficinaTech Pro")
        self.geometry("1300x800")
        self.configure(fg_color="#0F172A")

        self.conn = sqlite3.connect("oficinatech.db")
        self.cursor = self.conn.cursor()

        self.criar_banco()
        self.tela_login()

    def criar_banco(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            senha TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            telefone TEXT,
            email TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            modelo TEXT,
            placa TEXT,
            ano TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            veiculo TEXT,
            servico TEXT,
            valor REAL,
            status TEXT,
            data TEXT
        )
        """)

        self.cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO usuarios(usuario, senha) VALUES (?, ?)",
                ("admin", "123")
            )

        self.conn.commit()

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    def limpar_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def tela_login(self):
        self.limpar_tela()

        frame = ctk.CTkFrame(self, width=420, height=430, corner_radius=20, fg_color="#111827")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            frame,
            text="OficinaTech Pro",
            font=("Arial", 32, "bold"),
            text_color="#38BDF8"
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            frame,
            text="Sistema de Gestão de Oficina",
            font=("Arial", 16)
        ).pack(pady=5)

        self.usuario_entry = ctk.CTkEntry(frame, placeholder_text="Usuário", width=300, height=45)
        self.usuario_entry.pack(pady=15)

        self.senha_entry = ctk.CTkEntry(frame, placeholder_text="Senha", show="*", width=300, height=45)
        self.senha_entry.pack(pady=10)

        ctk.CTkButton(
            frame,
            text="Entrar",
            width=300,
            height=45,
            command=self.login
        ).pack(pady=25)

        ctk.CTkLabel(
            frame,
            text="Usuário: admin | Senha: 123",
            font=("Arial", 13),
            text_color="#94A3B8"
        ).pack()

    def login(self):
        usuario = self.usuario_entry.get()
        senha = self.senha_entry.get()

        self.cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND senha = ?",
            (usuario, senha)
        )

        if self.cursor.fetchone():
            self.tela_sistema()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")

    def tela_sistema(self):
        self.limpar_tela()

        self.sidebar = ctk.CTkFrame(self, width=240, fg_color="#111827", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            self.sidebar,
            text="OficinaTech",
            font=("Arial", 28, "bold"),
            text_color="#38BDF8"
        ).pack(pady=35)

        botoes = [
            ("Dashboard", self.tela_dashboard),
            ("Clientes", self.tela_clientes),
            ("Veículos", self.tela_veiculos),
            ("Ordens de Serviço", self.tela_ordens),
            ("Histórico", self.tela_historico),
            ("Relatórios", self.tela_relatorios),
            ("Sair", self.tela_login)
        ]

        for texto, comando in botoes:
            ctk.CTkButton(
                self.sidebar,
                text=texto,
                height=45,
                corner_radius=12,
                fg_color="#1E293B",
                hover_color="#334155",
                command=comando
            ).pack(fill="x", padx=15, pady=7)

        self.main = ctk.CTkFrame(self, fg_color="#0F172A")
        self.main.pack(side="left", fill="both", expand=True)

        self.tela_dashboard()

    def card(self, parent, titulo, valor, cor):
        frame = ctk.CTkFrame(parent, width=220, height=120, corner_radius=18, fg_color="#1E293B")
        frame.pack(side="left", padx=10)
        frame.pack_propagate(False)

        ctk.CTkLabel(frame, text=titulo, font=("Arial", 17, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(frame, text=str(valor), font=("Arial", 25, "bold"), text_color=cor).pack()

    def tela_dashboard(self):
        self.limpar_main()

        ctk.CTkLabel(
            self.main,
            text="Dashboard Administrativo",
            font=("Arial", 34, "bold")
        ).pack(pady=25)

        self.cursor.execute("SELECT COUNT(*) FROM clientes")
        clientes = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM veiculos")
        veiculos = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM ordens")
        ordens = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT SUM(valor) FROM ordens WHERE status = 'Concluído'")
        faturamento = self.cursor.fetchone()[0] or 0

        cards = ctk.CTkFrame(self.main, fg_color="transparent")
        cards.pack(pady=10)

        self.card(cards, "Clientes", clientes, "#38BDF8")
        self.card(cards, "Veículos", veiculos, "#22C55E")
        self.card(cards, "Ordens", ordens, "#F97316")
        self.card(cards, "Faturamento", f"R$ {faturamento:.2f}", "#EAB308")

        self.grafico_status()

    def grafico_status(self):
        frame = ctk.CTkFrame(self.main, corner_radius=20, fg_color="#1E293B")
        frame.pack(fill="both", expand=True, padx=40, pady=30)

        self.cursor.execute("SELECT status, COUNT(*) FROM ordens GROUP BY status")
        dados = self.cursor.fetchall()

        status = []
        quantidade = []

        for linha in dados:
            status.append(linha[0])
            quantidade.append(linha[1])

        if not status:
            status = ["Sem dados"]
            quantidade = [1]

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(status, quantidade)
        ax.set_title("Ordens de Serviço por Status")
        ax.set_ylabel("Quantidade")

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def tela_clientes(self):
        self.limpar_main()

        ctk.CTkLabel(self.main, text="Cadastro de Clientes", font=("Arial", 32, "bold")).pack(pady=20)

        self.nome_cliente = ctk.CTkEntry(self.main, placeholder_text="Nome", width=400)
        self.nome_cliente.pack(pady=8)

        self.tel_cliente = ctk.CTkEntry(self.main, placeholder_text="Telefone", width=400)
        self.tel_cliente.pack(pady=8)

        self.email_cliente = ctk.CTkEntry(self.main, placeholder_text="Email", width=400)
        self.email_cliente.pack(pady=8)

        ctk.CTkButton(self.main, text="Salvar Cliente", command=self.salvar_cliente).pack(pady=15)

    def salvar_cliente(self):
        nome = self.nome_cliente.get()
        telefone = self.tel_cliente.get()
        email = self.email_cliente.get()

        if nome == "" or telefone == "":
            messagebox.showerror("Erro", "Preencha nome e telefone.")
            return

        self.cursor.execute(
            "INSERT INTO clientes(nome, telefone, email) VALUES (?, ?, ?)",
            (nome, telefone, email)
        )
        self.conn.commit()

        messagebox.showinfo("Sucesso", "Cliente salvo com sucesso.")
        self.tela_clientes()

    def tela_veiculos(self):
        self.limpar_main()

        ctk.CTkLabel(self.main, text="Cadastro de Veículos", font=("Arial", 32, "bold")).pack(pady=20)

        self.cliente_veiculo = ctk.CTkEntry(self.main, placeholder_text="Cliente", width=400)
        self.cliente_veiculo.pack(pady=8)

        self.modelo_veiculo = ctk.CTkEntry(self.main, placeholder_text="Modelo", width=400)
        self.modelo_veiculo.pack(pady=8)

        self.placa_veiculo = ctk.CTkEntry(self.main, placeholder_text="Placa", width=400)
        self.placa_veiculo.pack(pady=8)

        self.ano_veiculo = ctk.CTkEntry(self.main, placeholder_text="Ano", width=400)
        self.ano_veiculo.pack(pady=8)

        ctk.CTkButton(self.main, text="Salvar Veículo", command=self.salvar_veiculo).pack(pady=15)

    def salvar_veiculo(self):
        cliente = self.cliente_veiculo.get()
        modelo = self.modelo_veiculo.get()
        placa = self.placa_veiculo.get().upper()
        ano = self.ano_veiculo.get()

        if cliente == "" or modelo == "" or placa == "":
            messagebox.showerror("Erro", "Preencha cliente, modelo e placa.")
            return

        self.cursor.execute(
            "INSERT INTO veiculos(cliente, modelo, placa, ano) VALUES (?, ?, ?, ?)",
            (cliente, modelo, placa, ano)
        )
        self.conn.commit()

        messagebox.showinfo("Sucesso", "Veículo salvo com sucesso.")
        self.tela_veiculos()

    def tela_ordens(self):
        self.limpar_main()

        ctk.CTkLabel(self.main, text="Ordem de Serviço", font=("Arial", 32, "bold")).pack(pady=20)

        self.os_cliente = ctk.CTkEntry(self.main, placeholder_text="Cliente", width=420)
        self.os_cliente.pack(pady=7)

        self.os_veiculo = ctk.CTkEntry(self.main, placeholder_text="Veículo", width=420)
        self.os_veiculo.pack(pady=7)

        self.os_servico = ctk.CTkEntry(self.main, placeholder_text="Serviço", width=420)
        self.os_servico.pack(pady=7)

        self.os_valor = ctk.CTkEntry(self.main, placeholder_text="Valor", width=420)
        self.os_valor.pack(pady=7)

        self.os_status = ctk.CTkComboBox(
            self.main,
            values=["Aberto", "Em andamento", "Concluído"],
            width=420
        )
        self.os_status.set("Aberto")
        self.os_status.pack(pady=7)

        ctk.CTkButton(self.main, text="Salvar Ordem", command=self.salvar_ordem).pack(pady=15)

    def salvar_ordem(self):
        cliente = self.os_cliente.get()
        veiculo = self.os_veiculo.get()
        servico = self.os_servico.get()
        status = self.os_status.get()

        try:
            valor = float(self.os_valor.get())
        except:
            messagebox.showerror("Erro", "Digite um valor válido.")
            return

        if valor < 0:
            messagebox.showerror("Erro", "O valor não pode ser negativo.")
            return

        if cliente == "" or veiculo == "" or servico == "":
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        self.cursor.execute(
            """
            INSERT INTO ordens(cliente, veiculo, servico, valor, status, data)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (cliente, veiculo, servico, valor, status, datetime.now().strftime("%d/%m/%Y %H:%M"))
        )
        self.conn.commit()

        messagebox.showinfo("Sucesso", "Ordem cadastrada.")
        self.tela_ordens()

    def tela_historico(self):
        self.limpar_main()

        ctk.CTkLabel(self.main, text="Histórico de Ordens", font=("Arial", 32, "bold")).pack(pady=15)

        busca_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        busca_frame.pack(pady=10)

        self.busca = ctk.CTkEntry(busca_frame, placeholder_text="Buscar por cliente, veículo ou status", width=420)
        self.busca.pack(side="left", padx=8)

        ctk.CTkButton(busca_frame, text="Buscar", command=self.buscar_ordens).pack(side="left", padx=8)
        ctk.CTkButton(busca_frame, text="Mostrar Tudo", command=self.carregar_ordens).pack(side="left", padx=8)

        self.tabela = ttk.Treeview(
            self.main,
            columns=("ID", "Cliente", "Veículo", "Serviço", "Valor", "Status", "Data"),
            show="headings",
            height=18
        )

        for col in ("ID", "Cliente", "Veículo", "Serviço", "Valor", "Status", "Data"):
            self.tabela.heading(col, text=col)

        self.tabela.column("ID", width=50)
        self.tabela.column("Cliente", width=150)
        self.tabela.column("Veículo", width=150)
        self.tabela.column("Serviço", width=220)
        self.tabela.column("Valor", width=100)
        self.tabela.column("Status", width=130)
        self.tabela.column("Data", width=150)

        self.tabela.pack(pady=15)

        botoes = ctk.CTkFrame(self.main, fg_color="transparent")
        botoes.pack()

        ctk.CTkButton(botoes, text="Concluir", command=lambda: self.alterar_status("Concluído")).pack(side="left", padx=8)
        ctk.CTkButton(botoes, text="Em andamento", command=lambda: self.alterar_status("Em andamento")).pack(side="left", padx=8)
        ctk.CTkButton(botoes, text="Excluir", fg_color="#DC2626", command=self.excluir_ordem).pack(side="left", padx=8)

        self.carregar_ordens()

    def carregar_ordens(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        self.cursor.execute("SELECT * FROM ordens ORDER BY id DESC")
        dados = self.cursor.fetchall()

        for linha in dados:
            self.tabela.insert(
                "",
                "end",
                values=(linha[0], linha[1], linha[2], linha[3], f"R$ {linha[4]:.2f}", linha[5], linha[6])
            )

    def buscar_ordens(self):
        termo = self.busca.get()

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        self.cursor.execute(
            """
            SELECT * FROM ordens
            WHERE cliente LIKE ? OR veiculo LIKE ? OR status LIKE ?
            ORDER BY id DESC
            """,
            (f"%{termo}%", f"%{termo}%", f"%{termo}%")
        )

        dados = self.cursor.fetchall()

        for linha in dados:
            self.tabela.insert(
                "",
                "end",
                values=(linha[0], linha[1], linha[2], linha[3], f"R$ {linha[4]:.2f}", linha[5], linha[6])
            )

    def pegar_id_selecionado(self):
        selecionado = self.tabela.selection()

        if not selecionado:
            messagebox.showerror("Erro", "Selecione uma ordem na tabela.")
            return None

        valores = self.tabela.item(selecionado[0], "values")
        return valores[0]

    def alterar_status(self, novo_status):
        ordem_id = self.pegar_id_selecionado()

        if ordem_id is None:
            return

        self.cursor.execute(
            "UPDATE ordens SET status = ? WHERE id = ?",
            (novo_status, ordem_id)
        )
        self.conn.commit()

        messagebox.showinfo("Sucesso", "Status atualizado.")
        self.carregar_ordens()

    def excluir_ordem(self):
        ordem_id = self.pegar_id_selecionado()

        if ordem_id is None:
            return

        self.cursor.execute("DELETE FROM ordens WHERE id = ?", (ordem_id,))
        self.conn.commit()

        messagebox.showinfo("Sucesso", "Ordem excluída.")
        self.carregar_ordens()

    def tela_relatorios(self):
        self.limpar_main()

        ctk.CTkLabel(self.main, text="Relatórios", font=("Arial", 32, "bold")).pack(pady=25)

        ctk.CTkButton(
            self.main,
            text="Exportar Relatório TXT",
            width=280,
            height=45,
            command=self.exportar_relatorio
        ).pack(pady=20)

    def exportar_relatorio(self):
        self.cursor.execute("SELECT * FROM ordens ORDER BY id DESC")
        dados = self.cursor.fetchall()

        total = 0

        with open("relatorio_oficinatech.txt", "w", encoding="utf-8") as arquivo:
            arquivo.write("===== RELATÓRIO OFICINATECH PRO =====\n")
            arquivo.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")

            for linha in dados:
                total += linha[4]
                arquivo.write(
                    f"ID: {linha[0]}\n"
                    f"Cliente: {linha[1]}\n"
                    f"Veículo: {linha[2]}\n"
                    f"Serviço: {linha[3]}\n"
                    f"Valor: R$ {linha[4]:.2f}\n"
                    f"Status: {linha[5]}\n"
                    f"Data: {linha[6]}\n"
                    "-----------------------------------\n"
                )

            arquivo.write(f"\nTotal geral: R$ {total:.2f}\n")

        messagebox.showinfo("Exportado", "Relatório salvo com sucesso.")


if __name__ == "__main__":
    app = OficinaTechPro()
    app.mainloop()