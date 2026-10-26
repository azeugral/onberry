"""Confere o hero por rolagem: parado no quadro 034, só anda com o scroll.

python tools/conferir_hero.py [url]  -> prints em ../_ref/prints/hero-*.jpg
"""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8820/"
OUT = Path(__file__).resolve().parents[2] / "_ref" / "prints"
OUT.mkdir(parents=True, exist_ok=True)

# assinatura do canvas: média de alguns pixels, para saber se o quadro mudou
ASSINATURA = """() => { const c = document.getElementById('tela'); const x = c.getContext('2d');
  const d = x.getImageData(0, 0, c.width, c.height).data; let s = 0;
  for (let i = 0; i < d.length; i += 4 * 997) s += d[i] + d[i + 1] * 3 + d[i + 2] * 7; return s; }"""

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    rel = {}
    for nome, cfg in {
        "pc": dict(viewport={"width": 1440, "height": 900}),
        "celular": dict(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True),
        "celular-320": dict(viewport={"width": 320, "height": 568}, device_scale_factor=2, is_mobile=True, has_touch=True),
    }.items():
        pg = b.new_context(**cfg).new_page()
        erros = []
        pg.on("pageerror", lambda e: erros.append(str(e)))
        pg.goto(URL, wait_until="networkidle")
        pg.wait_for_timeout(2500)
        a1 = pg.evaluate(ASSINATURA)
        pg.wait_for_timeout(2000)
        a2 = pg.evaluate(ASSINATURA)
        pg.screenshot(path=str(OUT / f"hero-{nome}-0.jpg"), type="jpeg", quality=82)
        info = pg.evaluate("""() => ({rolagem: document.getElementById('inicio').classList.contains('rolagem'),
            pronto: document.getElementById('tela').classList.contains('pronto'),
            alturaHero: Math.round(document.getElementById('inicio').getBoundingClientRect().height),
            scrollW: document.documentElement.scrollWidth, W: innerWidth,
            conteudoCabe: (() => { const c = document.querySelector('.hero-conteudo').getBoundingClientRect(); return c.top >= 0 && c.bottom <= innerHeight + 1; })()})""")
        estados = []
        for frac in (0.25, 0.5, 0.85):
            pg.evaluate(f"""() => {{ const h = document.getElementById('inicio'); window.scrollTo(0, (h.offsetHeight - innerHeight) * {frac}); }}""")
            pg.wait_for_timeout(900)
            estados.append(dict(frac=frac, assinatura=pg.evaluate(ASSINATURA),
                                sai=pg.evaluate("getComputedStyle(document.querySelector('.palco')).getPropertyValue('--sai')")))
            pg.screenshot(path=str(OUT / f"hero-{nome}-{int(frac*100)}.jpg"), type="jpeg", quality=82)
        rel[nome] = dict(parado_igual=(a1 == a2), **info, estados=estados, erros=erros)
    b.close()
print(json.dumps(rel, ensure_ascii=False, indent=1))
