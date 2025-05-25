import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="usuario",
        password="sua_senha",
        database="sistema_barbearia"
    )
