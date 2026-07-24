import sqlite3

conexao = sqlite3.connect("emomap.db")
cursor = conexao.cursor()

cursor.execute("""
SELECT bairro,
       ROUND(AVG(indice),2)
FROM avaliacao
GROUP BY bairro
""")

dados = cursor.fetchall()

print(dados)

conexao.close()