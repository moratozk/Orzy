/* Orzy: página de andamento do relatório (relatorios/andamento.html).
   Pergunta o andamento a cada 2 segundos, mexe no anel e nas etapas e abre o relatório quando ele termina ou dá erro.
   Os números vêm do servidor (andamento.json). O anel e as barras mudam pelo JS, porque a CSP não deixa style= no
   HTML. Sem JavaScript, a página se recarrega sozinha a cada 10 segundos. */
(function () {
  "use strict";
  const caixa = document.getElementById("si-andamento");
  if (!caixa) return;
  const anel = document.getElementById("si-anel-cheio");
  const pct = document.getElementById("si-pct");
  const etapa = document.getElementById("si-etapa");
  const etapas = document.getElementById("si-etapas");

  function desenhar(valor) {
    anel.style.strokeDashoffset = String(100 - valor);
    etapas.querySelectorAll("[data-barra]").forEach((barra) => {
      barra.style.transform = "scaleX(" + Number(barra.dataset.barra) / 100 + ")";
    });
  }

  function mostrar(dados) {
    pct.textContent = dados.pct;
    if (etapa.textContent !== dados.etapa) etapa.textContent = dados.etapa;
    dados.etapas.forEach((e, n) => {
      const item = etapas.children[n];
      if (!item) return;
      item.className = "ob-etapa" + (e.estado ? " " + e.estado : "");
      item.querySelector(".ob-etapa-conta").textContent = e.conta;
      item.querySelector("[data-barra]").dataset.barra = e.barra || 0;
    });
    desenhar(dados.pct);
  }

  function perguntar() {
    fetch(caixa.dataset.andamento, { cache: "no-store", credentials: "same-origin" })
      .then((resposta) => {
        // O relatório sumiu da sessão (ela acabou ou a pessoa saiu em outra aba): a página mostra o que houve.
        if (resposta.status === 404) {
          window.location.reload();
          return "parar";
        }
        return resposta.ok ? resposta.json() : null;
      })
      .then((dados) => {
        if (dados === "parar") return;
        if (!dados) return setTimeout(perguntar, 4000);
        if (dados.estado !== "gerando") return window.location.replace(caixa.dataset.destino);
        mostrar(dados);
        setTimeout(perguntar, 2000);
      })
      .catch(() => setTimeout(perguntar, 4000));
  }

  desenhar(Number(anel.dataset.pct) || 0);
  setTimeout(perguntar, 2000);
})();
