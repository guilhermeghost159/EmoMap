// ======================================================
// EMOMAP - DASHBOARD
// ======================================================

// Variáveis globais dos gráficos
let graficoBarras = null;
let graficoPizza = null;


// ======================================================
// CRIA O GRÁFICO DE BARRAS
// ======================================================

const elementoBarras = document.getElementById("graficoBarras");

if (elementoBarras) {

    const ctxBarras = elementoBarras.getContext("2d");

    graficoBarras = new Chart(ctxBarras, {

        type: "bar",

        data: {

            labels: bairros.map(item => item.bairro),

            datasets: [

                {

                    label: "Média de Estresse",

                    data: bairros.map(item => item.media),

                    borderWidth: 1

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    display: true

                }

            },

            scales: {

                y: {

                    beginAtZero: true,

                    max: 15,

                    title: {

                        display: true,

                        text: "Índice de Estresse"

                    }

                },

                x: {

                    title: {

                        display: true,

                        text: "Bairros"

                    }

                }

            }

        }

    });

}



// ======================================================
// CRIA O GRÁFICO DE PIZZA
// ======================================================

const elementoPizza = document.getElementById("graficoPizza");

if (elementoPizza) {

    const ctxPizza = elementoPizza.getContext("2d");

    graficoPizza = new Chart(ctxPizza, {

        type: "pie",

        data: {

            labels: Object.keys(emocoes),

            datasets: [

                {

                    label: "Estado Emocional",

                    data: Object.values(emocoes),

                    borderWidth: 1

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    position: "bottom"

                }

            }

        }

    });

}



// ======================================================
// ATUALIZA KPIs
// ======================================================

function atualizarKPIs(dados){
    
    console.log("Atualizando KPIs", dados);

    document.getElementById("kpi-total").textContent = dados.total;

    document.getElementById("kpi-media").textContent = dados.media;

    document.getElementById("kpi-emocao").textContent = dados.emocao;

    document.getElementById("kpi-bairro").textContent = dados.bairro;

}



// ======================================================
// ATUALIZA INSIGHTS
// ======================================================

function atualizarInsights(dados){

    document.getElementById("insight-total").textContent = dados.total;

    document.getElementById("insight-media").textContent = dados.media;

    document.getElementById("insight-emocao").textContent = dados.emocao;

    document.getElementById("insight-bairro").textContent = dados.bairro;

}



// ======================================================
// ATUALIZA OS GRÁFICOS
// ======================================================

function atualizarGraficos(dados){

    if(graficoBarras){

        graficoBarras.data.labels =

            dados.bairros.map(item => item.bairro);

        graficoBarras.data.datasets[0].data =

            dados.bairros.map(item => item.media);

        graficoBarras.update();

    }


    if(graficoPizza){

        graficoPizza.data.labels =

            Object.keys(dados.emocoes);

        graficoPizza.data.datasets[0].data =

            Object.values(dados.emocoes);

        graficoPizza.update();

    }

}



// ======================================================
// ATUALIZA TODO O DASHBOARD
// ======================================================

function atualizarDashboard(){

    fetch("/api/dashboard")

    .then(resposta => resposta.json())

    .then(dados =>{

        console.clear();

        console.log("Dashboard atualizado");

        console.log(dados);

        atualizarKPIs(dados);

        atualizarInsights(dados);

        atualizarGraficos(dados);

    })

    .catch(erro=>{

        console.error("Erro:", erro);

    });

}



// ======================================================
// INICIALIZAÇÃO
// ======================================================

// Atualiza imediatamente quando abre a página
atualizarDashboard();

// Atualiza automaticamente a cada 30 segundos
setInterval(atualizarDashboard, 30000);

// Durante os testes, você pode usar:
// setInterval(atualizarDashboard, 5000);