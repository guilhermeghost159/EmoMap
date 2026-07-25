from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import folium
from folium.plugins import HeatMap
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file


app = Flask(__name__)

app.secret_key = "emomap2026"


# 1º - criar conexão
def conectar_banco():

    banco = sqlite3.connect("emomap.db")

    banco.row_factory = sqlite3.Row

    return banco


# 2º - criar tabelas
def criar_tabelas():

    conexao = conectar_banco()
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
        convivencia TEXT,
        indice REAL
    )
    """)

    conexao.commit()
    conexao.close()


# 3º - executar depois das funções existirem
criar_tabelas()

# ======================
# PÁGINA INICIAL
# ======================

@app.route("/")
def inicio():

    return render_template("index.html")



# ======================
# ETAPA 1
# DADOS PESSOAIS
# ======================

@app.route("/questionario", methods=["GET", "POST"])
def questionario():


    if request.method == "POST":


        session["nome"] = request.form.get("nome")

        session["idade"] = request.form.get("idade")

        session["sexo"] = request.form.get("sexo")

        session["bairro"] = request.form.get("bairro")



        print("===== DADOS PESSOAIS =====")

        print("Nome:", session["nome"])

        print("Idade:", session["idade"])

        print("Sexo:", session["sexo"])

        print("Bairro:", session["bairro"])



        return redirect(url_for("habitos"))



    return render_template("questionario.html")




# ======================
# ETAPA 2
# HÁBITOS
# ======================


@app.route("/habitos", methods=["GET", "POST"])
def habitos():


    if request.method == "POST":


        session["sono"] = request.form.get("sono")

        session["celular"] = request.form.get("celular")

        session["atividade"] = request.form.get("atividade")

        session["alimentacao"] = request.form.get("alimentacao")



        print("===== HÁBITOS =====")

        print("Sono:", session["sono"])

        print("Celular:", session["celular"])

        print("Atividade:", session["atividade"])

        print("Alimentação:", session["alimentacao"])



        return redirect(url_for("emocoes"))



    return render_template("habitos.html")




# ======================
# ETAPA 3
# EMOÇÕES
# ======================


@app.route("/emocoes", methods=["GET", "POST"])
def emocoes():


    if request.method == "POST":


        estresse = request.form.get("estresse")

        emocao = request.form.get("emocao")

        social = request.form.get("social")

        pressao = request.form.get("pressao")



        if not estresse or not pressao:

            return "Preencha todos os campos"



        estresse = int(estresse)

        pressao = int(pressao)



        indice = estresse + pressao



        if indice <= 5:

            classificacao = "🟢 Baixo Estresse"



        elif indice <= 10:

            classificacao = "🟡 Estresse Moderado"



        else:

            classificacao = "🔴 Alto Estresse"




        # ======================
        # SALVAR NO BANCO
        # ======================


        dados = (

            session.get("nome"),

            session.get("idade"),

            session.get("sexo"),

            session.get("bairro"),

            session.get("sono"),

            session.get("celular"),

            session.get("atividade"),

            session.get("alimentacao"),

            estresse,

            emocao,

            social,

            pressao,

            indice

        )



        salvar_dados(dados)



        print("===== AVALIAÇÃO SALVA =====")

        print(dados)



        return render_template(

            "resultado.html",

            indice=indice,

            classificacao=classificacao

        )



    return render_template("emocoes.html")




# ======================
# INICIAR SISTEMA
# ======================
# ======================
# RANKING
# ======================

@app.route("/ranking")
def ranking():

    conexao = sqlite3.connect("emomap.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT bairro,
               ROUND(AVG(indice), 2) AS media
        FROM avaliacao
        GROUP BY bairro
        ORDER BY media DESC
    """)

    ranking = cursor.fetchall()

    conexao.close()

    return render_template(
        "ranking.html",
        ranking=ranking
    )


# ======================
# MAPA
# ======================

# ======================
# MAPA
# ======================

@app.route("/mapa")
def mapa():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT bairro,
               ROUND(AVG(indice), 2) AS media
        FROM avaliacao
        GROUP BY bairro
    """)

    dados = cursor.fetchall()
    conexao.close()

    mapa = folium.Map(
        location=[-4.1299, -38.2412],
        zoom_start=11
    )

    localidades = {
        "Centro": [-4.1299, -38.2412],
        "Coqueiral": [-4.1360, -38.2450],
        "Mutirão": [-4.1400, -38.2480],
        "Rio Novo": [-4.1240, -38.2300],
        "Alto Luminoso": [-4.1330, -38.2360],
        "Jardim Icaraí": [-4.1310, -38.2460],
        "Caponga": [-4.0390, -38.1860],
        "Barra da Caponga": [-4.0600, -38.1800],
        "Águas Belas": [-4.0730, -38.1920],
        "Guanacés": [-4.1900, -38.3000],
        "Cristais": [-4.1800, -38.2800],
        "Barra Nova": [-4.1000, -38.2200],
        "Tijucussu": [-4.1700, -38.2700],
        "Moita Redonda": [-4.1500, -38.2600],
        "Pitombeiras": [-4.1600, -38.2900],
        "Jacarecoara": [-4.1100, -38.2100]
    }

    # Lista para o HeatMap
    pontos_heatmap = []

    for bairro, media in dados:

        if bairro not in localidades:
            continue

        coordenada = localidades[bairro]

        # Adiciona ponto ao HeatMap
        pontos_heatmap.append([
            coordenada[0],
            coordenada[1],
            media
        ])

        # Define a cor do marcador
        if media <= 5:
            cor = "green"
            classificacao = "Baixo Estresse"

        elif media <= 10:
            cor = "orange"
            classificacao = "Estresse Moderado"

        else:
            cor = "red"
            classificacao = "Alto Estresse"

        # Marcador
        folium.CircleMarker(
            location=coordenada,
            radius=15,
            color=cor,
            fill=True,
            fill_color=cor,
            fill_opacity=0.8,
            popup=f"""
            <b>{bairro}</b><br>
            Índice Médio: {media}<br>
            {classificacao}
            """
        ).add_to(mapa)

    # HeatMap
    HeatMap(
        pontos_heatmap,
        radius=40,
        blur=25,
        min_opacity=0.4
    ).add_to(mapa)

    # Legenda
    legenda = """
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        width: 190px;
        background-color: white;
        border:2px solid grey;
        border-radius:10px;
        padding:10px;
        z-index:9999;
        font-size:14px;
        box-shadow:2px 2px 8px rgba(0,0,0,0.3);
    ">
        <b>🧠 EmoMap</b><br><br>

        🟢 Baixo Estresse (0–5)<br>
        🟠 Moderado (6–10)<br>
        🔴 Alto Estresse (11–15)
    </div>
    """

    mapa.get_root().html.add_child(folium.Element(legenda))

    return mapa._repr_html_()

@app.route("/dashboard")
def dashboard():

    # ======================
    # FILTROS
    # ======================

    idade = request.args.get("idade")
    sexo = request.args.get("sexo")
    bairro = request.args.get("bairro")

    conexao = conectar_banco()
    cursor = conexao.cursor()

    # ======================
    # LISTAS DOS FILTROS
    # ======================

    cursor.execute("SELECT DISTINCT idade FROM avaliacao ORDER BY idade")
    lista_idades = [linha["idade"] for linha in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT sexo FROM avaliacao ORDER BY sexo")
    lista_sexos = [linha["sexo"] for linha in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT bairro FROM avaliacao ORDER BY bairro")
    lista_bairros = [linha["bairro"] for linha in cursor.fetchall()]

    # ======================
    # TOTAL PARTICIPANTES
    # ======================

    cursor.execute("SELECT COUNT(*) AS total FROM avaliacao")
    total_participantes = cursor.fetchone()["total"]

    # ======================
    # MÉDIA GERAL
    # ======================

    cursor.execute("SELECT ROUND(AVG(indice),2) AS media FROM avaliacao")
    resultado = cursor.fetchone()

    media_geral = resultado["media"] if resultado["media"] else 0

    # ======================
    # EMOÇÃO PREDOMINANTE
    # ======================

    cursor.execute("""
        SELECT emocao,
               COUNT(*) AS quantidade
        FROM avaliacao
        GROUP BY emocao
        ORDER BY quantidade DESC
        LIMIT 1
    """)

    resultado = cursor.fetchone()

    emocao_predominante = resultado["emocao"] if resultado else "Sem dados"

    # ======================
    # BAIRRO MAIS CRÍTICO
    # ======================

    cursor.execute("""
        SELECT bairro,
               ROUND(AVG(indice),2) AS media
        FROM avaliacao
        GROUP BY bairro
        ORDER BY media DESC
        LIMIT 1
    """)

    resultado = cursor.fetchone()

    bairro_critico = resultado["bairro"] if resultado else "Sem dados"

    # ======================
    # CONSULTA DOS BAIRROS
    # ======================

    sql = """
        SELECT bairro,
               ROUND(AVG(indice),2) AS media
        FROM avaliacao
        WHERE 1=1
    """

    parametros = []

    if idade:
        sql += " AND idade=?"
        parametros.append(idade)

    if sexo:
        sql += " AND sexo=?"
        parametros.append(sexo)

    if bairro:
        sql += " AND bairro=?"
        parametros.append(bairro)

    sql += """
        GROUP BY bairro
        ORDER BY media DESC
    """

    cursor.execute(sql, parametros)

    bairros = cursor.fetchall()

    dados_bairros = []

    for linha in bairros:

        dados_bairros.append({

            "bairro": linha["bairro"],

            "media": linha["media"]

        })

    # ======================
    # DISTRIBUIÇÃO DAS EMOÇÕES
    # ======================

    cursor.execute("""
        SELECT emocao,
               COUNT(*) quantidade
        FROM avaliacao
        GROUP BY emocao
    """)

    dados_emocoes = {}

    for linha in cursor.fetchall():

        dados_emocoes[linha["emocao"]] = linha["quantidade"]

    print("===== KPIs =====")
    print(total_participantes)
    print(media_geral)
    print(emocao_predominante)
    print(bairro_critico)

    conexao.close()

    return render_template(

        "dashboard.html",

        dados_bairros=dados_bairros,
        dados_emocoes=dados_emocoes,

        lista_idades=lista_idades,
        lista_sexos=lista_sexos,
        lista_bairros=lista_bairros,

        idade_selecionada=idade,
        sexo_selecionado=sexo,
        bairro_selecionado=bairro,

        total_participantes=total_participantes,
        media_geral=media_geral,
        emocao_predominante=emocao_predominante,
        bairro_critico=bairro_critico

    )
@app.route("/api/dashboard")
def api_dashboard():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    # ======================
    # TOTAL DE PARTICIPANTES
    # ======================

    cursor.execute("SELECT COUNT(*) AS total FROM avaliacao")
    total = cursor.fetchone()["total"]

    # ======================
    # MÉDIA GERAL
    # ======================

    cursor.execute("""
        SELECT ROUND(AVG(indice), 2) AS media
        FROM avaliacao
    """)

    resultado = cursor.fetchone()
    media_geral = resultado["media"] if resultado["media"] else 0

    # ======================
    # EMOÇÃO PREDOMINANTE
    # ======================

    cursor.execute("""
        SELECT emocao,
               COUNT(*) AS quantidade
        FROM avaliacao
        GROUP BY emocao
        ORDER BY quantidade DESC
        LIMIT 1
    """)

    resultado = cursor.fetchone()
    emocao_predominante = resultado["emocao"] if resultado else "Sem dados"

    # ======================
    # BAIRRO CRÍTICO
    # ======================

    cursor.execute("""
        SELECT bairro,
               ROUND(AVG(indice), 2) AS media
        FROM avaliacao
        GROUP BY bairro
        ORDER BY media DESC
        LIMIT 1
    """)

    resultado = cursor.fetchone()
    bairro_critico = resultado["bairro"] if resultado else "Sem dados"

    # ======================
    # DADOS DO GRÁFICO DE BARRAS
    # ======================

    cursor.execute("""
        SELECT bairro,
               ROUND(AVG(indice), 2) AS media
        FROM avaliacao
        GROUP BY bairro
        ORDER BY media DESC
    """)

    dados_bairros = []

    for linha in cursor.fetchall():
        dados_bairros.append({
            "bairro": linha["bairro"],
            "media": linha["media"]
        })

    # ======================
    # DADOS DO GRÁFICO DE PIZZA
    # ======================

    cursor.execute("""
        SELECT emocao,
               COUNT(*) AS quantidade
        FROM avaliacao
        GROUP BY emocao
    """)

    dados_emocoes = {}

    for linha in cursor.fetchall():
        dados_emocoes[linha["emocao"]] = linha["quantidade"]

    conexao.close()

    print("API NOVA EXECUTANDO")

    return jsonify({

        "total": total,
        "media_geral": media_geral,
        "emocao_predominante": emocao_predominante,
        "bairro_critico": bairro_critico,
        "bairros": dados_bairros,
        "emocoes": dados_emocoes

    })

@app.route("/pdf")
def gerar_pdf():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            nome,
            idade,
            sexo,
            bairro,
            indice,
            emocao
        FROM avaliacao
        ORDER BY bairro
    """)

    dados = cursor.fetchall()

    conexao.close()

    pdf = SimpleDocTemplate("relatorio_emomap.pdf")

    estilos = getSampleStyleSheet()

    elementos = []

    elementos.append(
        Paragraph("<b>Relatório EmoMap</b>", estilos["Title"])
    )

    tabela = [["Nome", "Idade", "Sexo", "Bairro", "Índice", "Emoção"]]

    for linha in dados:

        tabela.append([
            linha["nome"],
            linha["idade"],
            linha["sexo"],
            linha["bairro"],
            linha["indice"],
            linha["emocao"]
        ])

    tabela_pdf = Table(tabela)

    tabela_pdf.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),

        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,1),(-1,-1),colors.beige),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("BOTTOMPADDING",(0,0),(-1,0),10)

    ]))

    elementos.append(tabela_pdf)

    pdf.build(elementos)

    return "PDF criado com sucesso!"

@app.route("/atualizar_db")
def atualizar_db():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        ALTER TABLE avaliacao
        ADD COLUMN social TEXT
    """)

    conexao.commit()
    conexao.close()

    return "Coluna social criada!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)