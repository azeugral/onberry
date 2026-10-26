/* On Berry · interações leves (sem dependências) */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.add("js");
  var reduz = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ano no rodapé */
  var ano = document.getElementById("ano");
  if (ano) ano.textContent = new Date().getFullYear();

  /* vídeo do hero: escolhe o corte pela orientação e só carrega depois do primeiro paint */
  var video = document.querySelector(".hero-video");
  function carregaVideo() {
    if (!video || reduz) return;
    var conexao = navigator.connection || {};
    if (conexao.saveData) return;
    var retrato = window.matchMedia("(max-aspect-ratio: 1/1)").matches;
    var src = retrato ? video.dataset.mobile : video.dataset.desktop;
    if (video.getAttribute("src") === src) return;
    video.src = src;
    video.addEventListener("canplay", function () {
      var p = video.play();
      if (p && p.then) p.then(function () { video.classList.add("pronto"); }).catch(function () {});
      else video.classList.add("pronto");
    }, { once: true });
    video.load();
  }
  if (document.readyState === "complete") setTimeout(carregaVideo, 300);
  else window.addEventListener("load", function () { setTimeout(carregaVideo, 300); });
  var ultimoRetrato = window.matchMedia("(max-aspect-ratio: 1/1)").matches;
  window.addEventListener("resize", function () {
    var r = window.matchMedia("(max-aspect-ratio: 1/1)").matches;
    if (r !== ultimoRetrato) { ultimoRetrato = r; if (video) { video.classList.remove("pronto"); carregaVideo(); } }
  });
  /* pausa o vídeo fora da tela (bateria) */
  if (video && "IntersectionObserver" in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!video.src) return;
        if (e.isIntersecting) { var p = video.play(); if (p && p.catch) p.catch(function () {}); }
        else video.pause();
      });
    }, { threshold: 0.05 }).observe(video);
  }

  /* topo sólido após o hero */
  var topo = document.getElementById("topo");
  function topoScroll() { topo.classList.toggle("solido", window.scrollY > 40); }
  topoScroll();

  /* menu mobile */
  var botao = document.querySelector(".topo-menu");
  var menu = document.getElementById("menu");
  function fecha() {
    menu.hidden = true; botao.setAttribute("aria-expanded", "false");
    botao.setAttribute("aria-label", "Abrir menu"); document.body.classList.remove("menu-aberto");
  }
  botao.addEventListener("click", function () {
    var abrir = menu.hidden;
    if (!abrir) return fecha();
    menu.hidden = false; botao.setAttribute("aria-expanded", "true");
    botao.setAttribute("aria-label", "Fechar menu"); document.body.classList.add("menu-aberto");
    topo.classList.add("solido");
  });
  menu.addEventListener("click", function (e) { if (e.target.closest("a")) fecha(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !menu.hidden) fecha(); });
  window.addEventListener("resize", function () { if (window.innerWidth > 1080 && !menu.hidden) fecha(); });

  /* revelação no scroll, com escalonamento dentro do mesmo grupo */
  var alvos = [].slice.call(document.querySelectorAll("[data-r]"));
  if ("IntersectionObserver" in window && !reduz) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add("visto");
        io.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    alvos.forEach(function (el) {
      var irmaos = [].slice.call(el.parentElement.children).filter(function (x) { return x.hasAttribute("data-r"); });
      var i = irmaos.indexOf(el);
      if (i > 0) el.style.setProperty("--d", Math.min(i * 0.08, 0.4) + "s");
      io.observe(el);
    });
  } else {
    alvos.forEach(function (el) { el.classList.add("visto"); });
  }

  /* paralaxe leve das fotos */
  var par = [].slice.call(document.querySelectorAll("[data-par]"));
  function paralaxe() {
    var vh = window.innerHeight;
    par.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.bottom < -100 || r.top > vh + 100) return;
      var p = (r.top + r.height / 2 - vh / 2) / vh; // -1..1
      var forca = parseFloat(el.dataset.par) || 6;
      var img = el.querySelector("img");
      if (img) img.style.setProperty("--py", (p * forca * -1).toFixed(2) + "%");
    });
  }

  /* contagem dos números */
  var contadores = [].slice.call(document.querySelectorAll("[data-conta]"));
  function formata(el, v) {
    if (el.hasAttribute("data-decimal")) return v.toFixed(1).replace(".", ",");
    var n = Math.round(v);
    return el.hasAttribute("data-milhar") ? n.toLocaleString("pt-BR") : String(n);
  }
  if ("IntersectionObserver" in window && !reduz) {
    var ioN = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        ioN.unobserve(e.target);
        var el = e.target, alvo = parseFloat(el.dataset.conta), t0 = null, dur = 1600;
        (function passo(t) {
          if (!t0) t0 = t;
          var k = Math.min((t - t0) / dur, 1);
          var ease = 1 - Math.pow(1 - k, 4);
          el.textContent = formata(el, alvo * ease);
          if (k < 1) requestAnimationFrame(passo);
        })(performance.now());
      });
    }, { threshold: 0.5 });
    contadores.forEach(function (el) { el.textContent = formata(el, 0); ioN.observe(el); });
  }

  /* link ativo no menu */
  var links = [].slice.call(document.querySelectorAll(".topo-nav a"));
  var secoes = links.map(function (a) { return document.querySelector(a.getAttribute("href")); });
  function ativo() {
    var y = window.scrollY + window.innerHeight * 0.35, atual = -1;
    secoes.forEach(function (s, i) { if (s && s.offsetTop <= y) atual = i; });
    links.forEach(function (a, i) { a.classList.toggle("ativo", i === atual); });
  }

  var agendado = false;
  function noScroll() {
    if (agendado) return;
    agendado = true;
    requestAnimationFrame(function () {
      agendado = false;
      topoScroll();
      ativo();
      if (!reduz) paralaxe();
    });
  }
  window.addEventListener("scroll", noScroll, { passive: true });
  window.addEventListener("resize", noScroll);
  noScroll();
})();
