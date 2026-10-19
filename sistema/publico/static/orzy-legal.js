/* Orzy, visual novo. Gerado de orzy/marca/visual-novo/fonte/src/legal.js em 2026-10-18 (prévia versão 7). */
/* ================================================================== Política de Privacidade e Termos de Uso */
window.ORZY = window.ORZY || { telas: {} };

(function () {
  "use strict";
  const reduzir = window.matchMedia("(prefers-reduced-motion: reduce)");
  const largo = window.matchMedia("(min-width: 900px)");

  document.querySelectorAll(".t-legal").forEach((raiz) => {
    const $ = (sel) => raiz.querySelector(sel);
    const $$ = (sel) => Array.from(raiz.querySelectorAll(sel));
    const artigo = $(".lg-texto");
    const titulos = $$(".lg-texto h2[id]");
    const linksIndice = $$(".lg-indice a[data-secao]");
    const indiceCel = $(".lg-indice-cel");
    const anel = $(".lg-cheio");
    const pct = $(".lg-pct");
    const lado = $(".lg-lado");
    const barra = $(".lg-barra span");

    // ---------------------------------------------------------------- menu do celular (igual ao da página inicial)
    const botaoMenu = $(".sc-menu-botao");
    const menu = $(".sc-menu");
    function abrirMenu(sim) {
      menu.hidden = !sim;
      botaoMenu.setAttribute("aria-expanded", String(sim));
      raiz.classList.toggle("sc-menu-aberto", sim);
    }
    const fecharMenu = () => { if (!menu.hidden) abrirMenu(false); };
    botaoMenu.addEventListener("click", () => abrirMenu(menu.hidden));
    document.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape" && !menu.hidden) { abrirMenu(false); botaoMenu.focus(); }
    });
    document.addEventListener("click", (ev) => {
      if (!menu.hidden && !menu.contains(ev.target) && !botaoMenu.contains(ev.target)) abrirMenu(false);
    });
    if (largo.addEventListener) largo.addEventListener("change", (e) => { if (e.matches) fecharMenu(); });

    // ---------------------------------------------------------------- topo muda quando a página sai do começo
    const topo = $(".sc-topo");
    const sentinela = $(".sc-sentinela");
    if ("IntersectionObserver" in window && topo && sentinela) {
      new IntersectionObserver(([e]) => topo.classList.toggle("sc-rolou", !e.isIntersecting && !raiz.hidden)).observe(sentinela);
    }

    // ---------------------------------------------------------------- links
    raiz.addEventListener("click", (ev) => {
      const link = ev.target.closest && ev.target.closest("a");
      if (!link || !raiz.contains(link)) return;
      if (link.closest(".sc-menu")) fecharMenu();
      // "Como funciona", "Situações" e "Segurança" levam para a seção da página inicial (a troca de tela é da navegação)
      if (link.dataset.alvo) { window.ORZY.rolarPara = link.dataset.alvo; return; }
      const secao = link.dataset.secao;
      if (!secao) return;
      const alvo = document.getElementById(secao);
      if (!alvo) return;
      ev.preventDefault();
      if (indiceCel && indiceCel.contains(link)) indiceCel.open = false;
      alvo.scrollIntoView({ behavior: reduzir.matches ? "auto" : "smooth", block: "start" });
      if (!alvo.hasAttribute("tabindex")) alvo.setAttribute("tabindex", "-1");
      alvo.focus({ preventScroll: true });
    });

    // ---------------------------------------------------------------- leitura: seção atual no índice e quanto já leu
    let atual = null;
    let pedido = 0;
    function marcar(id) {
      if (id === atual) return;
      atual = id;
      linksIndice.forEach((a) => {
        if (a.dataset.secao === id) a.setAttribute("aria-current", "location");
        else a.removeAttribute("aria-current");
      });
      // no computador, o item atual fica à vista dentro do índice
      const visivel = lado && lado.offsetParent && lado.querySelector(`a[data-secao="${id}"]`);
      if (visivel && lado.scrollHeight > lado.clientHeight) {
        const caixa = lado.getBoundingClientRect();
        const item = visivel.getBoundingClientRect();
        if (item.top < caixa.top + 60 || item.bottom > caixa.bottom - 20) {
          lado.scrollTop += item.top - caixa.top - caixa.height / 2;
        }
      }
    }
    function medir() {
      pedido = 0;
      if (raiz.hidden || !artigo) return;
      const janela = window.innerHeight;
      // seção atual: o último título que já passou de um terço da tela
      let id = titulos.length ? titulos[0].id : null;
      for (const t of titulos) {
        if (t.getBoundingClientRect().top <= janela * 0.34) id = t.id;
        else break;
      }
      marcar(id);
      // quanto já leu: 0 com o começo do texto na altura do índice, 1 com o fim do texto à vista
      const caixa = artigo.getBoundingClientRect();
      const total = caixa.height - janela * 0.6;
      const lido = Math.min(1, Math.max(0, (janela * 0.4 - caixa.top) / Math.max(1, total)));
      if (anel) anel.style.strokeDashoffset = String(100 - lido * 100);
      if (pct) pct.textContent = `${Math.round(lido * 100)}%`;
      if (barra) barra.style.transform = `scaleX(${lido})`;
      raiz.classList.toggle("lg-lido", lido >= 0.995);
    }
    const pedir = () => { if (!pedido) pedido = requestAnimationFrame(medir); };
    window.addEventListener("scroll", pedir, { passive: true });
    window.addEventListener("resize", pedir);

    window.ORZY.telas[raiz.dataset.tela] = {
      mostrar() {
        fecharMenu();
        if (indiceCel) indiceCel.open = false;
        atual = null;
        medir();
      },
    };
  });
})();
