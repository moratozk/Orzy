/* Orzy, visual novo. Gerado de orzy/marca/visual-novo/fonte/src/inicio.js em 2026-10-18 (prévia versão 7). */
/* ================================================================== página inicial (layout do Caminho 3, fundo escuro) */
window.ORZY = window.ORZY || { telas: {} };

(function () {
  "use strict";
  const raiz = document.getElementById("t-inicio");
  if (!raiz) return;
  const $ = (sel, base = raiz) => base.querySelector(sel);
  const $$ = (sel, base = raiz) => Array.from(base.querySelectorAll(sel));
  const reduzir = window.matchMedia("(prefers-reduced-motion: reduce)");
  const temIO = "IntersectionObserver" in window;
  const fmt = new Intl.NumberFormat("pt-BR");
  const quieto = () => reduzir.matches || !temIO;

  raiz.classList.add("sc-js");

  // ------------------------------------------------------------------ links que rolam dentro da página
  raiz.addEventListener("click", (ev) => {
    const link = ev.target.closest && ev.target.closest("a[data-alvo]");
    if (!link || !raiz.contains(link)) return;
    ev.preventDefault();
    fecharMenu();
    const alvo = document.getElementById(link.dataset.alvo);
    if (!alvo) return;
    if (link.dataset.alvo === "sc-inicio") window.scrollTo({ top: 0, behavior: reduzir.matches ? "auto" : "smooth" });
    else alvo.scrollIntoView({ behavior: reduzir.matches ? "auto" : "smooth", block: "start" });
    if (!alvo.hasAttribute("tabindex")) alvo.setAttribute("tabindex", "-1");
    alvo.focus({ preventScroll: true });
  });

  // ------------------------------------------------------------------ menu do celular
  const botaoMenu = $(".sc-menu-botao");
  const menu = $("#sc-menu");
  function abrirMenu(sim) {
    if (!menu || !botaoMenu) return;
    menu.hidden = !sim;
    botaoMenu.setAttribute("aria-expanded", String(sim));
    raiz.classList.toggle("sc-menu-aberto", sim);
  }
  function fecharMenu() { if (menu && !menu.hidden) abrirMenu(false); }
  if (botaoMenu && menu) {
    botaoMenu.addEventListener("click", () => abrirMenu(menu.hidden));
    menu.addEventListener("click", (ev) => { if (ev.target.closest("a")) fecharMenu(); });
    document.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape" && !menu.hidden) { abrirMenu(false); botaoMenu.focus(); }
    });
    document.addEventListener("click", (ev) => {
      if (!menu.hidden && !menu.contains(ev.target) && !botaoMenu.contains(ev.target)) abrirMenu(false);
    });
    const largo = window.matchMedia("(min-width: 900px)");
    const aoMudar = (e) => { if (e.matches) fecharMenu(); };
    if (largo.addEventListener) largo.addEventListener("change", aoMudar);
  }

  // ------------------------------------------------------------------ faixas que se cruzam: repete o texto até cobrir a tela
  $$(".sc-fita-trilho").forEach((trilho) => {
    const grupo = trilho.firstElementChild;
    if (!grupo) return;
    const largura = grupo.getBoundingClientRect().width || 900;
    const porMetade = Math.max(2, Math.ceil(2800 / largura));
    for (let i = 1; i < porMetade * 2; i++) {
      const copia = grupo.cloneNode(true);
      trilho.appendChild(copia);
    }
  });

  // ------------------------------------------------------------------ números que contam
  function contar(el, duracao) {
    const ate = Number(el.dataset.ate);
    if (!Number.isFinite(ate)) return;
    if (reduzir.matches) { el.textContent = fmt.format(ate); return; }
    const t0 = performance.now();
    const passo = (t) => {
      const k = Math.min(1, (t - t0) / duracao);
      const e = 1 - Math.pow(1 - k, 4);
      el.textContent = fmt.format(Math.round(ate * e));
      if (k < 1) requestAnimationFrame(passo);
    };
    el.textContent = "0";
    requestAnimationFrame(passo);
  }

  // ------------------------------------------------------------------ telas do celular: tocar a animação de cada uma
  function tocarTela(tela) {
    if (!tela || reduzir.matches) return;
    tela.classList.remove("sc-tocar");
    void tela.offsetWidth;
    tela.classList.add("sc-tocar");
    $$("[data-ate]", tela).forEach((el) => contar(el, el.closest(".sc-imp-pct") ? 2400 : 1900));
  }

  // ------------------------------------------------------------------ passo a passo: o celular troca de tela
  const passos = $$(".sc-passo");
  const palco = $(".sc-palco");
  const telas = palco ? $$(".sc-tela", palco) : [];
  const marcas = palco ? $$(".sc-progresso li", palco) : [];
  let ativo = 0;
  function ativar(i) {
    if (i < 0 || i === ativo) return;
    ativo = i;
    passos.forEach((p, k) => p.classList.toggle("sc-ativo", k === i));
    telas.forEach((t, k) => t.classList.toggle("sc-ativa", k === i));
    marcas.forEach((m, k) => m.classList.toggle("sc-feito", k <= i));
    if (palco && palco.offsetParent) tocarTela(telas[i]);
  }

  // cópias pequenas, uma embaixo de cada passo (celular e tablet)
  const modelo = palco && $(".sc-cel", palco);
  const minis = [];
  if (modelo) {
    passos.forEach((passo, i) => {
      const vaga = $(".sc-passo-mini", passo);
      if (!vaga) return;
      const copia = modelo.cloneNode(true);
      $$(".sc-tela", copia).forEach((t, k) => {
        if (k === i) t.classList.add("sc-ativa");
        else t.remove();
      });
      vaga.appendChild(copia);
      minis.push(vaga);
    });
  }

  // ------------------------------------------------------------------ observadores
  if (temIO) {
    // topo muda quando a página sai do começo
    const topo = $(".sc-topo");
    const sentinela = $(".sc-sentinela");
    if (topo && sentinela) {
      new IntersectionObserver(([e]) => topo.classList.toggle("sc-rolou", !e.isIntersecting && !raiz.hidden)).observe(sentinela);
    }

    // revelar ao rolar
    const revelar = new IntersectionObserver((entradas) => {
      entradas.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add("sc-visto");
        revelar.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.12 });
    $$(".sc-revela").forEach((el) => {
      if (reduzir.matches) el.classList.add("sc-visto");
      else revelar.observe(el);
    });

    // contagens da faixa de números
    const contas = $$(".sc-conta");
    if (!reduzir.matches) contas.forEach((el) => { el.textContent = "0"; });
    const ioContas = new IntersectionObserver((entradas) => {
      entradas.forEach((e) => {
        if (!e.isIntersecting) return;
        ioContas.unobserve(e.target);
        const atraso = contas.indexOf(e.target) * 110;
        setTimeout(() => contar(e.target, 1700), reduzir.matches ? 0 : atraso);
      });
    }, { threshold: 0.6 });
    contas.forEach((el) => ioContas.observe(el));

    // o passo que cruza o meio da tela fica ativo
    const ioPassos = new IntersectionObserver((entradas) => {
      entradas.forEach((e) => { if (e.isIntersecting) ativar(passos.indexOf(e.target)); });
    }, { rootMargin: "-46% 0px -46% 0px" });
    passos.forEach((p) => ioPassos.observe(p));

    // cada celular pequeno toca a sua tela quando aparece
    const ioMinis = new IntersectionObserver((entradas) => {
      entradas.forEach((e) => {
        if (!e.isIntersecting) return;
        ioMinis.unobserve(e.target);
        tocarTela($(".sc-tela", e.target));
      });
    }, { threshold: 0.45 });
    minis.forEach((m) => ioMinis.observe(m));

    // o que gira fica parado fora da tela
    const ioPausa = new IntersectionObserver((entradas) => {
      entradas.forEach((e) => e.target.classList.toggle("sc-fora", !e.isIntersecting));
    });
    $$(".sc-anima").forEach((el) => ioPausa.observe(el));
  } else {
    $$(".sc-revela").forEach((el) => el.classList.add("sc-visto"));
  }

  // ------------------------------------------------------------------ entrada da abertura (de novo a cada vez que a tela aparece)
  function entrada() {
    raiz.classList.remove("sc-intro");
    void raiz.offsetWidth;
    raiz.classList.add("sc-intro");
  }

  window.ORZY.telas["inicio"] = {
    mostrar() {
      fecharMenu();
      if (!quieto()) entrada();
      // vindo de outra página do site ("Como funciona" no topo da Política de Privacidade, por exemplo)
      const alvo = window.ORZY.rolarPara && document.getElementById(window.ORZY.rolarPara);
      window.ORZY.rolarPara = null;
      if (alvo && raiz.contains(alvo)) alvo.scrollIntoView({ block: "start" });
    },
  };
})();
