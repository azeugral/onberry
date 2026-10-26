/* On Berry · interações leves (sem dependências) */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.add("js");
  var reduz = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ano no rodapé */
  var ano = document.getElementById("ano");
  if (ano) ano.textContent = new Date().getFullYear();

  /* hero: 120 quadros 4K tocados pela rolagem. Parado, fica no quadro 034
     (o melhor da sequência); nada se mexe até a pessoa rolar. */
  var hero = document.getElementById("inicio");
  var palco = hero.querySelector(".palco");
  var tela = document.getElementById("tela");
  var N = 120, PARADO = 33;            // índice 33 = arquivo 034.webp
  var conexao = navigator.connection || {};
  var curto = function () { return window.innerHeight < 560 && window.innerWidth > window.innerHeight; };
  var anima = !reduz && !conexao.saveData && !!tela.getContext;
  var ctx = anima ? tela.getContext("2d", { alpha: false }) : null;
  var quadros = [], conjunto = "", desenhado = -1, pos = PARADO, alvo = PARADO, rodando = false, prog = 0;

  function escolheConjunto() {
    if (window.innerHeight > window.innerWidth) return "m";
    return window.innerWidth * Math.min(window.devicePixelRatio || 1, 2) >= 2600 ? "4k" : "hd";
  }
  /* ordem de carga: o quadro parado primeiro, depois 1 a cada 16, 8, 4, 2, 1 */
  function ordem() {
    var vistos = {}, lista = [PARADO];
    vistos[PARADO] = 1;
    [16, 8, 4, 2, 1].forEach(function (passo) {
      for (var i = 0; i < N; i += passo) if (!vistos[i]) { vistos[i] = 1; lista.push(i); }
    });
    return lista;
  }
  function carrega() {
    var atual = conjunto, fila = ordem(), ativos = 0;
    quadros = new Array(N);
    desenhado = -1;
    (function proximo() {
      while (ativos < 6 && fila.length) {
        var i = fila.shift(), img = new Image();
        ativos++;
        img.decoding = "async";
        img.src = "assets/quadros/" + atual + "/" + ("00" + (i + 1)).slice(-3) + ".webp";
        (function (i, img) {
          var fim = function () { ativos--; if (atual === conjunto) proximo(); };
          (img.decode ? img.decode() : Promise.resolve()).then(function () {
            if (atual !== conjunto) return;
            quadros[i] = img;
            if (i === PARADO) { desenhado = -1; desenha(Math.round(pos)); tela.classList.add("pronto"); }
          }).then(fim, fim);
        })(i, img);
      }
    })();
  }
  function maisPerto(i) {
    if (quadros[i]) return quadros[i];
    for (var d = 1; d < N / 2; d++) {
      var a = quadros[(i - d + N) % N], b = quadros[(i + d) % N];
      if (a || b) return a || b;
    }
    return null;
  }
  function desenha(i) {
    i = ((i % N) + N) % N;
    var img = maisPerto(i);
    if (!img) return;
    var chave = quadros[i] ? i : -2 - i;
    if (chave === desenhado) return;
    desenhado = chave;
    var W = tela.width, H = tela.height;
    var s = Math.max(W / img.naturalWidth, H / img.naturalHeight);
    var w = img.naturalWidth * s, h = img.naturalHeight * s;
    ctx.drawImage(img, (W - w) / 2, (H - h) / 2, w, h);
  }
  function dimensiona() {
    var ativo = anima && !curto();
    hero.classList.toggle("rolagem", ativo);
    if (!ativo) { palco.style.removeProperty("--sai"); return; }
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = Math.round(tela.clientWidth * dpr), h = Math.round(tela.clientHeight * dpr);
    if (tela.width !== w || tela.height !== h) { tela.width = w; tela.height = h; desenhado = -1; }
    var novo = escolheConjunto();
    if (novo !== conjunto) { conjunto = novo; tela.classList.remove("pronto"); carrega(); }
    else desenha(Math.round(pos));
  }
  function progressoHero() {
    var r = hero.getBoundingClientRect(), total = r.height - window.innerHeight;
    return total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 0;
  }
  /* só roda enquanto há diferença entre o quadro mostrado e o da rolagem; depois para */
  var antes = 0;
  function passo(agora) {
    var dt = Math.min(0.05, (agora - (antes || agora)) / 1000) || 0.016;
    antes = agora;
    pos += (alvo - pos) * (1 - Math.exp(-dt * 12));
    if (Math.abs(alvo - pos) < 0.02) pos = alvo;
    desenha(Math.round(pos));
    if (pos !== alvo) requestAnimationFrame(passo);
    else { rodando = false; antes = 0; }
  }
  function heroScroll() {
    if (!hero.classList.contains("rolagem")) return;
    prog = progressoHero();
    alvo = PARADO + prog * N;
    var sai = Math.min(1, Math.max(0, (prog - 0.42) / 0.4));
    palco.style.setProperty("--sai", sai.toFixed(3));
    if (!rodando && pos !== alvo) { rodando = true; requestAnimationFrame(passo); }
  }
  if (anima) {
    dimensiona();
    window.addEventListener("resize", function () { dimensiona(); heroScroll(); });
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

  /* borda de luz dos painéis de vidro acompanha o ponteiro (só com mouse) */
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches && !reduz) {
    [].slice.call(document.querySelectorAll(".vidro")).forEach(function (el) {
      el.addEventListener("pointermove", function (e) {
        var r = el.getBoundingClientRect();
        el.style.setProperty("--mx", (e.clientX - r.left) + "px");
        el.style.setProperty("--my", (e.clientY - r.top) + "px");
      });
      el.addEventListener("pointerleave", function () {
        el.style.removeProperty("--mx");
        el.style.removeProperty("--my");
      });
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
      if (anima) heroScroll();
      ativo();
      if (!reduz) paralaxe();
    });
  }
  window.addEventListener("scroll", noScroll, { passive: true });
  window.addEventListener("resize", noScroll);
  noScroll();
})();
