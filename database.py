import sqlite3


def criar_banco():

    conexao = sqlite3.connect("emomap.db")

    cursor = conexao.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS avaliacao (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT,

        idade INTEGER,

        sexo TEXT,

        bairro TEXT,

        sono TEXT,

        celular TEXT,

        atividade TEXT,

        alimentacao TEXT,

        estresse INTEGER,

        emocao TEXT,

        social TEXT,

        pressao INTEGER,

        indice INTEGER

    )
    """)


    conexao.commit()

    conexao.close()


criar_banco()