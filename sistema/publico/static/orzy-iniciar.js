/* Orzy, visual novo. Gerado de orzy/marca/visual-novo/fonte/pacote.py em 2026-10-18 (prévia versão 7). */
/* Liga a página: no site cada página tem uma tela só, então mostra a que estiver no HTML (na prévia quem fazia
   isso era o seletor de telas). Vem por último, depois do JS da página. */
(function () {
  "use strict";
  const telas = (window.ORZY && window.ORZY.telas) || {};
  Object.keys(telas).forEach((id) => {
    const tela = telas[id];
    if (tela && tela.mostrar && document.getElementById("t-" + id)) requestAnimationFrame(() => tela.mostrar());
  });
})();
