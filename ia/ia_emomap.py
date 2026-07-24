import sqlite3
import pandas as pd

# Conecta ao banco
conexao = sqlite3.connect("emomap.db")

# Lê a tabela
df = pd.read_sql_query(
    "SELECT * FROM avaliacao",
    conexao
)

conexao.close()

print("===== BANCO DE DADOS =====")
print(df)
print("\n===== INFORMAÇÕES =====")
print(df.info())

print("\n===== DADOS FALTANDO =====")
print(df.isnull().sum())
print("\n===== CLASSIFICAÇÃO DE RISCO =====")

def classificar(indice):

    if indice <= 5:
        return "Baixo"

    elif indice <= 10:
        return "Moderado"

    else:
        return "Alto"


df["risco"] = df["indice"].apply(classificar)

print(df[["indice", "risco"]])