import sqlite3
import pandas as pd
import joblib

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

print("====================================")
print(" TREINAMENTO DA IA - EMOMAP ")
print("====================================")

# ======================
# CONECTAR AO BANCO
# ======================

conexao = sqlite3.connect("emomap.db")

df = pd.read_sql_query(
    "SELECT * FROM avaliacao",
    conexao
)

conexao.close()

# ======================
# VERIFICAR SE EXISTEM DADOS
# ======================

if df.empty:
    print("ERRO: Nenhum dado encontrado no banco.")
    exit()

print("\nTotal de registros:", len(df))
print(df.head())

# ======================
# CRIAR A CLASSE DE RISCO
# ======================

def classificar_risco(indice):

    if indice <= 5:
        return "Baixo"

    elif indice <= 10:
        return "Moderado"

    else:
        return "Alto"

df["risco"] = df["indice"].apply(classificar_risco)

# ======================
# CODIFICAR VARIÁVEIS
# ======================

colunas_texto = [
    "sexo",
    "sono",
    "celular",
    "atividade",
    "alimentacao",
    "emocao",
    "social"
]

encoders = {}

for coluna in colunas_texto:

    encoder = LabelEncoder()

    df[coluna] = encoder.fit_transform(df[coluna].astype(str))

    encoders[coluna] = encoder

encoder_risco = LabelEncoder()

df["risco"] = encoder_risco.fit_transform(df["risco"])

# ======================
# VARIÁVEIS DE ENTRADA
# ======================

X = df[
    [
        "idade",
        "sexo",
        "sono",
        "celular",
        "atividade",
        "alimentacao",
        "estresse",
        "emocao",
        "social",
        "pressao"
    ]
]

y = df["risco"]

# ======================
# TREINAR MODELO
# ======================

modelo = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

modelo.fit(X, y)

# ======================
# SALVAR MODELO
# ======================

joblib.dump(modelo, "modelo_emomap.pkl")

print("\n====================================")
print(" IA TREINADA COM SUCESSO!")
print(" Modelo salvo como:")
print(" modelo_emomap.pkl")
print("====================================")