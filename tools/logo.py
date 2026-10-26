"""Gera a identidade da On Berry: marca (mirtilo com coroa), wordmark em curvas e favicons.

python tools/logo.py   -> assets/logo/*.svg, favicon.svg, favicon-*.png, apple-touch-icon.png
"""
import math, io, subprocess
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

RAIZ = Path(__file__).resolve().parents[1]
FONTES = RAIZ.parent / "_ref" / "fonts"
SAI = RAIZ / "assets" / "logo"
SAI.mkdir(parents=True, exist_ok=True)

ANIL = "#151735"
CREME = "#F4EFE4"
OURO = "#C9973F"


def coroa(cx, cy, R, r_furo, rot=-90):
    """Coroa do mirtilo vista de cima: anel com 5 sepalas curtas em ponta e o centro aberto."""
    rb = R * 0.60            # raio da base do anel
    meia = math.radians(17)  # meia-largura de cada sepala na base
    d = ""
    for i in range(5):
        a = math.radians(rot + i * 72)
        e = (cx + rb * math.cos(a - meia), cy + rb * math.sin(a - meia))
        t = (cx + R * math.cos(a), cy + R * math.sin(a))
        dd = (cx + rb * math.cos(a + meia), cy + rb * math.sin(a + meia))
        prox = math.radians(rot + (i + 1) * 72) - meia
        n = (cx + rb * math.cos(prox), cy + rb * math.sin(prox))
        # flancos levemente concavos
        c1 = (cx + R * 0.78 * math.cos(a - meia * 0.35), cy + R * 0.78 * math.sin(a - meia * 0.35))
        c2 = (cx + R * 0.78 * math.cos(a + meia * 0.35), cy + R * 0.78 * math.sin(a + meia * 0.35))
        d += ("M" if i == 0 else "L") + f"{e[0]:.2f},{e[1]:.2f} "
        d += f"Q{c1[0]:.2f},{c1[1]:.2f} {t[0]:.2f},{t[1]:.2f} Q{c2[0]:.2f},{c2[1]:.2f} {dd[0]:.2f},{dd[1]:.2f} "
        d += f"A{rb:.2f},{rb:.2f} 0 0,1 {n[0]:.2f},{n[1]:.2f} "
    return d + "Z", (cx, cy, r_furo)


def marca(cor_fruta, cor_coroa, tam=100, brilho=None):
    """Mirtilo visto de cima, coroa um pouco acima do centro (vista 3/4 sutil)."""
    c = tam / 2
    d_coroa, (fx, fy, fr) = coroa(0, 0, tam * 0.27, tam * 0.108, rot=-90)
    corpo = f'<circle cx="{c}" cy="{c}" r="{tam * 0.46}" fill="{cor_fruta}"/>'
    luz = ""
    if brilho:
        luz = (f'<path d="M{c - tam*0.33:.1f},{c + tam*0.06:.1f} A{tam*0.34:.1f},{tam*0.34:.1f} 0 0 0 {c + tam*0.12:.1f},{c + tam*0.38:.1f}" '
               f'fill="none" stroke="{brilho}" stroke-width="{tam*0.022:.2f}" stroke-linecap="round" opacity=".55"/>')
    # vista 3/4 sutil: coroa sobe um pouco e achata
    g = f'<g transform="translate({c:.2f},{c - tam * 0.045:.2f}) scale(1,.9)">'
    return (corpo + luz + g + f'<path d="{d_coroa}" fill="{cor_coroa}"/>'
            + f'<circle cx="{fx:.2f}" cy="{fy:.2f}" r="{fr:.2f}" fill="{cor_fruta}"/></g>')


def texto_em_curvas(ttf, texto, wght, opsz=None, tracking=0.0, ital=False):
    f = TTFont(ttf)
    eixos = {"wght": wght}
    if opsz and "opsz" in [a.axisTag for a in f["fvar"].axes]:
        eixos["opsz"] = opsz
    f = instancer.instantiateVariableFont(f, eixos)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    upm = f["head"].unitsPerEm
    hmtx = f["hmtx"]
    kern = {}
    x = 0
    paths = []
    for ch in texto:
        g = cmap.get(ord(ch))
        if g is None:
            continue
        pen = SVGPathPen(gs)
        tp = TransformPen(pen, (1, 0, 0, -1, x, 0))
        gs[g].draw(tp)
        d = pen.getCommands()
        if d:
            paths.append(d)
        x += hmtx[g][0] + tracking * upm
    asc = f["hhea"].ascent
    cap = getattr(f["OS/2"], "sCapHeight", asc * 0.7) or asc * 0.7
    return " ".join(paths), x - tracking * upm, upm, cap


def svg(w, h, corpo, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" {extra}>{corpo}</svg>')


NEWS = FONTES / "Newsreader.ttf"
MAN = FONTES / "Manrope.ttf"

d_nome, larg_nome, upm, cap = texto_em_curvas(NEWS, "On Berry", 520, opsz=60, tracking=-0.012)
d_sub, larg_sub, upm2, cap2 = texto_em_curvas(MAN, "VALE DO SÃO FRANCISCO", 600, tracking=0.26)


def lockup(cor_txt, cor_fruta, cor_coroa, cor_sub, nome_arq, com_sub=True):
    # escala: altura de versal do nome = 40 px
    esc = 40 / cap
    alt_marca = 64
    gap = 16
    x0 = alt_marca + gap
    w_nome = larg_nome * esc
    esc_s = min(7.0 / cap2, (w_nome * 0.97) / larg_sub)
    w_sub = larg_sub * esc_s
    base = 42
    corpo = f'<g transform="translate(0,0)">{marca(cor_fruta, cor_coroa, alt_marca)}</g>'
    corpo += f'<path transform="translate({x0},{base}) scale({esc:.5f})" d="{d_nome}" fill="{cor_txt}"/>'
    h = alt_marca
    if com_sub:
        h = max(alt_marca, base + 23)
        # subtitulo centralizado sob o nome
        xs = x0 + (w_nome - w_sub) / 2 if w_sub < w_nome else x0
        corpo += f'<path transform="translate({xs:.2f},{base + 21}) scale({esc_s:.5f})" d="{d_sub}" fill="{cor_sub}"/>'
    w = x0 + max(w_nome, w_sub if com_sub else 0) + 2
    (SAI / nome_arq).write_text(svg(w, h, corpo, 'role="img" aria-label="On Berry"'), encoding="utf-8")
    return w, h


# variacoes
lockup(CREME, CREME, ANIL, "#AEB6D2", "logo-clara.svg")          # sobre fundo escuro
lockup(ANIL, ANIL, CREME, "#5B6390", "logo-escura.svg")          # sobre fundo claro
lockup(CREME, CREME, ANIL, "#AEB6D2", "logo-clara-simples.svg", com_sub=False)
lockup(ANIL, ANIL, CREME, "#5B6390", "logo-escura-simples.svg", com_sub=False)
(SAI / "marca-anil.svg").write_text(svg(100, 100, marca(ANIL, CREME, 100)), encoding="utf-8")
(SAI / "marca-creme.svg").write_text(svg(100, 100, marca(CREME, ANIL, 100)), encoding="utf-8")

# favicon: fruta creme sobre quadro anil com cantos levemente vivos
fav = (f'<rect width="100" height="100" rx="18" fill="{ANIL}"/>'
       f'<g transform="translate(9,9) scale(.82)">{marca("#C7CEE6", ANIL, 100)}</g>')
(RAIZ / "favicon.svg").write_text(svg(100, 100, fav), encoding="utf-8")

# selo para redes/og: marca com nome em arco
print("ok", round(larg_nome), round(larg_sub))
