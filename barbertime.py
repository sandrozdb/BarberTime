import os
import sys
import subprocess
import tkinter as tk

# Caminho da pasta onde está o script atual (menu principal)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def abrir_cliente():
    caminho_cliente = os.path.join(BASE_DIR, "cliente.py")
    subprocess.Popen([sys.executable, caminho_cliente])

def abrir_barbearia():
    caminho_barbearia = os.path.join(BASE_DIR, "barbearia.py")
    subprocess.Popen([sys.executable, caminho_barbearia])

janela = tk.Tk()
janela.title("BarberTime - Menu Principal")

tk.Label(janela, text="Bem-vindo ao BarberTime!").pack(pady=10)
tk.Button(janela, text="Acessar como Cliente", command=abrir_cliente).pack(pady=5)
tk.Button(janela, text="Acessar como Barbearia", command=abrir_barbearia).pack(pady=5)

janela.mainloop()
