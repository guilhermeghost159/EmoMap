import sqlite3


conexao = sqlite3.connect("emomap.db")

cursor = conexao.cursor()


cursor.execute("SELECT * FROM avaliacao")


dados = cursor.fetchall()


print("===== DADOS SALVOS NO EMOMAP =====")


for dado in dados:
    print(dado)


conexao.close()