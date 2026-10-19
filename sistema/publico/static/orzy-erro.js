/* Orzy, visual novo. Gerado de orzy/marca/visual-novo/fonte/src/erro.js em 2026-10-18 (prévia versão 7). */
/* ================================================================== página de erro: a queda toca de novo a cada vez */
window.ORZY = window.ORZY || { telas: {} };

(function () {
  "use strict";
  const raiz = document.getElementById("t-erro");
  if (!raiz) return;

  // o brilho do ponto para de pulsar fora da tela
  if ("IntersectionObserver" in window) {
    const cena = raiz.querySelector(".er-cena");
    if (cena) new IntersectionObserver(([e]) => raiz.classList.toggle("er-fora", !e.isIntersecting)).observe(cena);
  }

  window.ORZY.telas.erro = {
    mostrar() {
      raiz.classList.remove("er-tocar");
      void raiz.offsetWidth;
      raiz.classList.add("er-tocar");
    },
  };
})();
