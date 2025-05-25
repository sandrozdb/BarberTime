import tkinter as tk
from tkinter import messagebox
import conexao
import datetime

# Janela principal cliente (login/cadastro)
def tela_principal_cliente():
    def cadastrar_cliente():
        nome = entry_nome.get().strip()
        cpf = entry_cpf.get().strip()
        if not nome or not cpf:
            messagebox.showwarning("Erro", "Preencha todos os campos!")
            return

        try:
            conn = conexao.conectar()
            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT id_usuario FROM Usuario WHERE cpf_cnpj = %s", (cpf,))
            if cursor.fetchone():
                messagebox.showwarning("Aviso", "Cliente com este CPF já cadastrado. Faça login.")
                return
            cursor.execute("""
                INSERT INTO Usuario (nome, cpf_cnpj, tipo)
                VALUES (%s, %s, 'cliente')
            """, (nome, cpf))
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente cadastrado!")
            janela_cliente.destroy()
            abrir_tela_agendamento(cpf)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
        finally:
            conn.close()

    def login_cliente():
        cpf = entry_cpf.get().strip()
        nome = entry_nome.get().strip()
        if not cpf or not nome:
            messagebox.showwarning("Erro", "Preencha CPF e Nome para entrar!")
            return
        try:
            conn = conexao.conectar()
            cursor = conn.cursor(buffered=True)
            cursor.execute("""
                SELECT id_usuario FROM Usuario
                WHERE cpf_cnpj = %s AND nome = %s AND tipo = 'cliente'
            """, (cpf, nome))
            resultado = cursor.fetchone()
            if resultado:
                messagebox.showinfo("Sucesso", "Login realizado!")
                janela_cliente.destroy()
                abrir_tela_agendamento(cpf)
            else:
                messagebox.showerror("Erro", "Cliente não encontrado. Verifique os dados.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
        finally:
            conn.close()

    janela_cliente = tk.Tk()
    janela_cliente.title("Cliente - Login / Cadastro")

    tk.Label(janela_cliente, text="Nome:").grid(row=0, column=0, padx=10, pady=5)
    entry_nome = tk.Entry(janela_cliente)
    entry_nome.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(janela_cliente, text="CPF:").grid(row=1, column=0, padx=10, pady=5)
    entry_cpf = tk.Entry(janela_cliente)
    entry_cpf.grid(row=1, column=1, padx=10, pady=5)

    tk.Button(janela_cliente, text="Cadastrar", command=cadastrar_cliente).grid(row=2, column=0, pady=10)
    tk.Button(janela_cliente, text="Entrar", command=login_cliente).grid(row=2, column=1, pady=10)

    janela_cliente.mainloop()

# Tela de agendamento + remoção
def abrir_tela_agendamento(cpf_cliente):
    janela_agenda = tk.Tk()
    janela_agenda.title("Agendar / Remover Serviço")

    tk.Label(janela_agenda, text="Escolha a Barbearia:").grid(row=0, column=0, padx=10, pady=5)
    barbearia_var = tk.StringVar(janela_agenda)
    barbearia_menu = tk.OptionMenu(janela_agenda, barbearia_var, "")
    barbearia_menu.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(janela_agenda, text="Serviço:").grid(row=1, column=0, padx=10, pady=5)
    entry_servico = tk.Entry(janela_agenda)
    entry_servico.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(janela_agenda, text="Data (dd/mm/aaaa):").grid(row=2, column=0, padx=10, pady=5)
    entry_data = tk.Entry(janela_agenda)
    entry_data.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(janela_agenda, text="Hora (HH:mm):").grid(row=3, column=0, padx=10, pady=5)
    entry_hora = tk.Entry(janela_agenda)
    entry_hora.grid(row=3, column=1, padx=10, pady=5)

    # Lista de agendamentos
    tk.Label(janela_agenda, text="Seus Agendamentos:").grid(row=0, column=2, padx=10)
    listbox_agendamentos = tk.Listbox(janela_agenda, width=50)
    listbox_agendamentos.grid(row=1, column=2, rowspan=4, padx=10, pady=5)

    def carregar_agendamentos():
        listbox_agendamentos.delete(0, tk.END)
        try:
            conn = conexao.conectar()
            cursor = conn.cursor(buffered=True)
            cursor.execute("""
                SELECT A.id_agendamento, B.nome, S.nome, A.data, A.hora
                FROM Agendamento A
                JOIN Barbearia B ON A.barbearia_id = B.id_barbearia
                JOIN Agendamento_Servicos ASV ON A.id_agendamento = ASV.agendamento_id
                JOIN Servico S ON ASV.servico_id = S.id_servico
                JOIN Usuario U ON A.cliente_id = U.id_usuario
                WHERE U.cpf_cnpj = %s
                ORDER BY A.data, A.hora
            """, (cpf_cliente,))
            agendamentos = cursor.fetchall()
            if not agendamentos:
                listbox_agendamentos.insert(tk.END, "Nenhum agendamento encontrado.")
            else:
                for row in agendamentos:
                    id_ag, barbearia_nome, servico_nome, data, hora = row
                    data_str = data.strftime('%d/%m/%Y') if isinstance(data, (datetime.date, datetime.datetime)) else str(data)
                    hora_str = hora.strftime('%H:%M') if isinstance(hora, (datetime.time, datetime.datetime)) else str(hora)
                    texto = f"ID {id_ag} - {barbearia_nome} | {servico_nome} | {data_str} {hora_str}"
                    listbox_agendamentos.insert(tk.END, texto)
            conn.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar agendamentos: {e}")

    def agendar():
        barbearia = barbearia_var.get()
        servico = entry_servico.get().strip()
        data = entry_data.get().strip()
        hora = entry_hora.get().strip()

        if not barbearia or "Nenhuma" in barbearia or not servico or not data or not hora:
            messagebox.showwarning("Erro", "Preencha todos os campos corretamente!")
            return

        try:
            data_sql = datetime.datetime.strptime(data, "%d/%m/%Y").date()
            hora_sql = datetime.datetime.strptime(hora, "%H:%M").time()
        except ValueError:
            messagebox.showerror("Erro", "Data ou hora com formato inválido!")
            return

        try:
            conn = conexao.conectar()
            cursor = conn.cursor(buffered=True)

            # Buscar cliente_id
            cursor.execute("SELECT id_usuario FROM Usuario WHERE cpf_cnpj = %s", (cpf_cliente,))
            cliente = cursor.fetchone()
            if not cliente:
                messagebox.showerror("Erro", "Cliente não encontrado no banco de dados.")
                return
            cliente_id = cliente[0]

            # Buscar barbearia_id
            cursor.execute("SELECT id_barbearia FROM Barbearia WHERE nome = %s", (barbearia,))
            barbearia_res = cursor.fetchone()
            if not barbearia_res:
                messagebox.showerror("Erro", "Barbearia não encontrada no banco de dados.")
                return
            barbearia_id = barbearia_res[0]

            # Buscar barbeiro_id
            cursor.execute("SELECT barbeiro_id FROM Barbeiros_Barbearias WHERE barbearia_id = %s LIMIT 1", (barbearia_id,))
            barbeiro_res = cursor.fetchone()
            if not barbeiro_res:
                messagebox.showerror("Erro", "Nenhum barbeiro cadastrado nesta barbearia.")
                return
            barbeiro_id = barbeiro_res[0]

            # Buscar ou inserir serviço
            cursor.execute("SELECT id_servico FROM Servico WHERE nome = %s", (servico,))
            servico_res = cursor.fetchone()
            if not servico_res:
                cursor.execute("INSERT INTO Servico (nome) VALUES (%s)", (servico,))
                servico_id = cursor.lastrowid
            else:
                servico_id = servico_res[0]

            # Inserir agendamento
            cursor.execute("""
                INSERT INTO Agendamento (cliente_id, barbeiro_id, barbearia_id, data, hora)
                VALUES (%s, %s, %s, %s, %s)
            """, (cliente_id, barbeiro_id, barbearia_id, data_sql, hora_sql))
            agendamento_id = cursor.lastrowid

            # Inserir relação agendamento-serviço
            cursor.execute("""
                INSERT INTO Agendamento_Servicos (agendamento_id, servico_id)
                VALUES (%s, %s)
            """, (agendamento_id, servico_id))

            conn.commit()
            messagebox.showinfo("Sucesso", "Agendamento realizado!")
            carregar_agendamentos()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
        finally:
            conn.close()

    def remover_agendamento():
        selecionado = listbox_agendamentos.curselection()
        if not selecionado:
            messagebox.showwarning("Erro", "Selecione um agendamento para remover!")
            return
        texto = listbox_agendamentos.get(selecionado[0])
        try:
            agendamento_id = int(texto.split()[1])  # Extrai ID do texto: "ID 123 - ..."
        except Exception:
            messagebox.showerror("Erro", "Selecione um agendamento válido.")
            return

        confirmar = messagebox.askyesno("Confirmar", "Deseja remover este agendamento?")
        if not confirmar:
            return

        try:
            conn = conexao.conectar()
            cursor = conn.cursor(buffered=True)
            cursor.execute("DELETE FROM Agendamento_Servicos WHERE agendamento_id = %s", (agendamento_id,))
            cursor.execute("DELETE FROM Agendamento WHERE id_agendamento = %s", (agendamento_id,))
            conn.commit()
            messagebox.showinfo("Removido", "Agendamento removido com sucesso!")
            carregar_agendamentos()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
        finally:
            conn.close()

    # Carregar barbearias no menu suspenso
    try:
        conn = conexao.conectar()
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT nome FROM Barbearia")
        barbearias = [b[0] for b in cursor.fetchall()]
        conn.close()
        menu = barbearia_menu["menu"]
        menu.delete(0, "end")
        if barbearias:
            barbearia_var.set(barbearias[0])
            for b in barbearias:
                menu.add_command(label=b, command=lambda valor=b: barbearia_var.set(valor))
        else:
            barbearia_var.set("Nenhuma barbearia cadastrada")
            menu.add_command(label="Nenhuma barbearia cadastrada", command=lambda: None)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar barbearias: {e}")

    tk.Button(janela_agenda, text="Agendar", command=agendar).grid(row=5, column=0, columnspan=2, pady=10)
    tk.Button(janela_agenda, text="Remover Agendamento", command=remover_agendamento).grid(row=5, column=2, pady=10)

    carregar_agendamentos()
    janela_agenda.mainloop()

if __name__ == "__main__":
    tela_principal_cliente()
