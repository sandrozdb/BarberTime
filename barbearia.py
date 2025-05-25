import tkinter as tk
from tkinter import messagebox, simpledialog
import conexao

# --- Cadastro Barbearia ---
def cadastrar_barbearia():
    nome = entry_nome.get()
    cnpj = entry_cnpj.get()

    if not nome or not cnpj:
        messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
        return

    conn = conexao.conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Barbearia (nome, cnpj)
            VALUES (%s, %s)
        """, (nome, cnpj))
        conn.commit()
        messagebox.showinfo("Sucesso", "Barbearia cadastrada com sucesso.")
        entry_nome.delete(0, tk.END)
        entry_cnpj.delete(0, tk.END)
        abrir_painel(janela)
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    finally:
        conn.close()

# --- Login Barbearia ---
def login_barbearia():
    nome = entry_nome.get()
    cnpj = entry_cnpj.get()

    if not nome or not cnpj:
        messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
        return

    conn = conexao.conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Barbearia WHERE nome = %s AND cnpj = %s", (nome, cnpj))
    barbearia = cursor.fetchone()
    conn.close()

    if barbearia:
        messagebox.showinfo("Login", "Login realizado com sucesso.")
        abrir_painel(janela)
    else:
        messagebox.showerror("Erro", "Barbearia não encontrada. Verifique os dados.")

# --- Abrir Painel ---
def abrir_painel(janela_login):
    janela_login.withdraw()  # Esconder janela login

    painel = tk.Toplevel()
    painel.title("Painel da Barbearia")

    tk.Label(painel, text="Bem-vindo à sua barbearia!", font=("Arial", 14)).pack(pady=10)

    tk.Button(painel, text="Cadastrar Barbeiro", command=cadastrar_barbeiro, width=30).pack(pady=5)
    tk.Button(painel, text="Listar Barbeiros", command=listar_barbeiros, width=30).pack(pady=5)
    tk.Button(painel, text="Ver Clientes Agendados", command=ver_agendamentos, width=30).pack(pady=5)
    tk.Button(painel, text="Remover Barbeiro", command=remover_barbeiro, width=30).pack(pady=5)

    def on_close():
        painel.destroy()
        janela_login.deiconify()  # Mostrar login de novo quando fechar painel

    painel.protocol("WM_DELETE_WINDOW", on_close)

# --- Cadastro Barbeiro ---
def cadastrar_barbeiro():
    def confirmar():
        nome = entry_nome_barbeiro.get()
        cpf = entry_cpf_barbeiro.get()

        if not nome or not cpf:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
            return

        conn = conexao.conectar()
        cursor = conn.cursor()

        try:
            email = f"{cpf}@barbearia.com"
            senha = "1234"
            telefone = ""

            cursor.execute("""
                INSERT INTO Usuario (nome, email, senha, cpf_cnpj, tipo, nivel_acesso, telefone)
                VALUES (%s, %s, %s, %s, 'profissional', 'barbeiro', %s)
            """, (nome, email, senha, cpf, telefone))
            barbeiro_id = cursor.lastrowid

            cursor.execute("SELECT id_barbearia FROM Barbearia ORDER BY id_barbearia DESC LIMIT 1")
            barbearia = cursor.fetchone()
            if not barbearia:
                messagebox.showerror("Erro", "Nenhuma barbearia encontrada.")
                return

            barbearia_id = barbearia[0]

            cursor.execute("""
                INSERT INTO Barbeiros_Barbearias (barbeiro_id, barbearia_id)
                VALUES (%s, %s)
            """, (barbeiro_id, barbearia_id))

            conn.commit()
            messagebox.showinfo("Sucesso", "Barbeiro cadastrado com sucesso.")
            janela_cadastro.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
        finally:
            conn.close()

    janela_cadastro = tk.Toplevel()
    janela_cadastro.title("Cadastrar Barbeiro")

    tk.Label(janela_cadastro, text="Nome:").grid(row=0, column=0, padx=10, pady=5)
    entry_nome_barbeiro = tk.Entry(janela_cadastro)
    entry_nome_barbeiro.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(janela_cadastro, text="CPF:").grid(row=1, column=0, padx=10, pady=5)
    entry_cpf_barbeiro = tk.Entry(janela_cadastro)
    entry_cpf_barbeiro.grid(row=1, column=1, padx=10, pady=5)

    tk.Button(janela_cadastro, text="Cadastrar", command=confirmar).grid(row=2, column=0, columnspan=2, pady=10)

# --- Listar Barbeiros ---
def listar_barbeiros():
    conn = conexao.conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, cpf_cnpj FROM Usuario WHERE tipo = 'profissional'")
    barbeiros = cursor.fetchall()
    conn.close()

    if not barbeiros:
        messagebox.showinfo("Barbeiros", "Nenhum barbeiro cadastrado.")
        return

    lista = "\n".join([f"{nome} - CPF: {cpf}" for nome, cpf in barbeiros])
    messagebox.showinfo("Lista de Barbeiros", lista)

# --- Ver Agendamentos ---
def ver_agendamentos():
    conn = conexao.conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT U.nome, A.data, A.hora, S.nome
        FROM Agendamento A
        JOIN Usuario U ON A.cliente_id = U.id_usuario
        JOIN Agendamento_Servicos AS ASV ON ASV.agendamento_id = A.id_agendamento
        JOIN Servico S ON ASV.servico_id = S.id_servico
    """)
    agendamentos = cursor.fetchall()
    conn.close()

    if not agendamentos:
        messagebox.showinfo("Agendamentos", "Nenhum cliente agendado.")
        return

    lista = "\n".join([f"Cliente: {nome} | Data: {data} | Hora: {hora} | Serviço: {servico}"
                       for nome, data, hora, servico in agendamentos])
    messagebox.showinfo("Clientes Agendados", lista)

# --- Remover Barbeiro ---
def remover_barbeiro():
    cpf = simpledialog.askstring("Remover Barbeiro", "Digite o CPF do barbeiro para remover:")

    if not cpf:
        return  # Usuário cancelou ou não digitou nada

    confirmar = messagebox.askyesno("Confirmação", f"Tem certeza que deseja remover o barbeiro com CPF {cpf}?")
    if not confirmar:
        return

    conn = conexao.conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM Usuario WHERE cpf_cnpj = %s AND tipo = 'profissional'", (cpf,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Erro", "Barbeiro não encontrado.")
            return

        barbeiro_id = result[0]

        cursor.execute("DELETE FROM Barbeiros_Barbearias WHERE barbeiro_id = %s", (barbeiro_id,))
        cursor.execute("DELETE FROM Usuario WHERE id_usuario = %s", (barbeiro_id,))

        conn.commit()
        messagebox.showinfo("Sucesso", "Barbeiro removido com sucesso.")
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    finally:
        conn.close()

# --- Interface inicial simplificada: nome, cnpj, botões entrar e cadastrar ---
janela = tk.Tk()
janela.title("Login/Cadastro Barbearia")

frame = tk.Frame(janela, padx=20, pady=20)
frame.pack()

tk.Label(frame, text="Nome da Barbearia:").grid(row=0, column=0, sticky="e", pady=5)
entry_nome = tk.Entry(frame)
entry_nome.grid(row=0, column=1, pady=5)

tk.Label(frame, text="CNPJ:").grid(row=1, column=0, sticky="e", pady=5)
entry_cnpj = tk.Entry(frame)
entry_cnpj.grid(row=1, column=1, pady=5)

btn_frame = tk.Frame(frame)
btn_frame.grid(row=2, column=0, columnspan=2, pady=15)

btn_entrar = tk.Button(btn_frame, text="Entrar", width=15, command=login_barbearia)
btn_entrar.pack(side=tk.LEFT, padx=10)

btn_cadastrar = tk.Button(btn_frame, text="Cadastrar", width=15, command=cadastrar_barbearia)
btn_cadastrar.pack(side=tk.LEFT, padx=10)

janela.mainloop()
