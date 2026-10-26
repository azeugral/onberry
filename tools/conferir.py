"""Tira prints em vários aparelhos e audita overflow horizontal.

python tools/conferir.py [url]   (padrão http://localhost:8820/)
Saída em ../_ref/prints/
"""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8820/"
OUT = Path(__file__).resolve().parents[2] / "_ref" / "prints"
OUT.mkdir(parents=True, exist_ok=True)

APARELHOS = {
    "desktop-1440": dict(viewport={"width": 1440, "height": 900}),
    "notebook-1280": dict(viewport={"width": 1280, "height": 720}),
    "tablet-768": dict(viewport={"width": 768, "height": 1024}, is_mobile=True, has_touch=True),
    "iphone-390": dict(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2),
    "android-360": dict(viewport={"width": 360, "height": 780}, is_mobile=True, has_touch=True, device_scale_factor=2),
    "pequeno-320": dict(viewport={"width": 320, "height": 568}, is_mobile=True, has_touch=True, device_scale_factor=2),
    "max-430": dict(viewport={"width": 430, "height": 932}, is_mobile=True, has_touch=True, device_scale_factor=2),
    "deitado-844": dict(viewport={"width": 844, "height": 390}, is_mobile=True, has_touch=True, device_scale_factor=2),
}

AUDIT = """() => {
  const W = document.documentElement.clientWidth, out = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width && (r.right > W + 1 || r.left < -1)) {
      let p = el, clip = false;
      while ((p = p.parentElement)) { const s = getComputedStyle(p); if (s.overflowX !== 'visible' || s.overflow === 'hidden') { clip = true; break; } }
      if (!clip) out.push(el.tagName + '.' + el.className + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
    }
  });
  return {W, scrollW: document.documentElement.scrollWidth, fora: out.slice(0, 12)};
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    rel = {}
    for nome, cfg in APARELHOS.items():
        ctx = b.new_context(**cfg, reduced_motion="reduce" if "--estatico" in sys.argv else "no-preference")
        pg = ctx.new_page()
        erros = []
        pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: erros.append(str(e)))
        pg.goto(URL, wait_until="networkidle")
        pg.wait_for_timeout(1800)
        pg.screenshot(path=str(OUT / f"{nome}-dobra.jpg"), type="jpeg", quality=80)
        # rola tudo para disparar as revelações
        pg.evaluate("""async () => { for (let y = 0; y < document.body.scrollHeight; y += 400) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 90)); } }""")
        pg.wait_for_timeout(1600)
        pg.evaluate("window.scrollTo(0, 0)")
        pg.wait_for_timeout(500)
        pg.screenshot(path=str(OUT / f"{nome}-inteira.jpg"), type="jpeg", quality=72, full_page=True)
        rel[nome] = dict(audit=pg.evaluate(AUDIT), erros=[e for e in erros if "mirtilos-" not in e][:5])
        ctx.close()
    b.close()
print(json.dumps(rel, ensure_ascii=False, indent=1))
