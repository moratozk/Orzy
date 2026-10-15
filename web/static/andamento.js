// Atualiza a página de andamento e leva a pessoa para o relatório quando ele termina.
(function () {
  var caixa = document.getElementById("dados");
  if (!caixa) return;

  var barra = document.getElementById("barra");
  var etapa = document.getElementById("etapa");
  var contagem = document.getElementById("contagem");

  function atualizar() {
    fetch(caixa.dataset.andamento, { cache: "no-store", credentials: "same-origin" })
      .then(function (resposta) { return resposta.ok ? resposta.json() : null; })
      .then(function (dados) {
        if (!dados) return setTimeout(atualizar, 4000);
        if (dados.estado !== "gerando") {
          window.location.replace(caixa.dataset.destino);
          return;
        }
        etapa.textContent = dados.etapa;
        barra.max = Math.max(dados.total, 1);
        barra.value = dados.feitos;
        contagem.textContent = dados.total ? dados.feitos + " de " + dados.total : "";
        setTimeout(atualizar, 2000);
      })
      .catch(function () { setTimeout(atualizar, 4000); });
  }

  atualizar();
})();
