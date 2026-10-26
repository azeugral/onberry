"""Aplica a logo OFICIAL da On-Berry (arquivo do cliente, RGBA) no site.

Gera em assets/logo/:
  oficial-vertical.webp/png   logo completa (símbolo + On-Berry), para o rodapé
  simbolo.webp/png            só o símbolo (o "On" entrelaçado com a estrela)
  horizontal-clara.svg        versão de leitura: símbolo + "On-Berry" em Saira expandida, texto creme
  horizontal-escura.svg       idem, texto anil (fundos claros)
e na raiz: favicon.ico, favicon-32.png, favicon-192.png, favicon-512.png, apple-touch-icon.png

python tools/logo_oficial.py
"""
import base64, io
from pathlib import Path
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

RAIZ = Path(__file__).resolve().parents[1]
REF = RAIZ.parent / "_ref"
OFICIAL = REF / "logo-oficial" / "oficial-fundo-branco.webp"
SAI = RAIZ / "assets" / "logo"
SAI.mkdir(parents=True, exist_ok=True)

FUNDO_FAV = (8, 16, 58)        # azul-noite do fundo da arte oficial escura
AZUL_FOLHA = "#2F6BEA"         # folha do "O" na arte oficial

im = Image.open(OFICIAL).convert("RGBA")
a = im.getchannel("A")
caixa = a.point(lambda v: 255 if v > 8 else 0).getbbox()
logo = im.crop(caixa)

# separa símbolo e texto pela faixa vazia entre eles
alfa = logo.getchannel("A")
w, h = logo.size
linhas = [max(alfa.crop((0, y, w, y + 1)).getdata()) for y in range(h)]
vazias = [y for y, v in enumerate(linhas) if v <= 8 and y > h * 0.6]
corte = vazias[0] if vazias else int(h * 0.8)
simbolo = logo.crop((0, 0, w, corte))
simbolo = simbolo.crop(simbolo.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
print("logo", logo.size, "simbolo", simbolo.size, "corte", corte)


def salva(img, nome, alturas):
    for alt in alturas:
        r = img.resize((round(img.width * alt / img.height), alt), Image.LANCZOS)
        suf = "" if alt == alturas[0] else f"-{alt}"
        r.save(SAI / f"{nome}{suf}.webp", quality=92, method=6)
        r.save(SAI / f"{nome}{suf}.png", optimize=True)


salva(logo, "oficial-vertical", [900, 420])
salva(simbolo, "simbolo", [600, 240])

# ---------------------------------------------------------------- favicons
def favicon(t):
    c = Image.new("RGBA", (t, t), FUNDO_FAV + (255,))
    # símbolo alto e estreito: ocupa 86% da altura
    alt = round(t * 0.86)
    s = simbolo.resize((max(1, round(simbolo.width * alt / simbolo.height)), alt), Image.LANCZOS)
    c.alpha_composite(s, ((t - s.width) // 2, (t - alt) // 2))
    return c

for nome, t in (("favicon-32.png", 32), ("favicon-192.png", 192), ("favicon-512.png", 512), ("apple-touch-icon.png", 180)):
    favicon(t).save(RAIZ / nome)
favicon(256).save(RAIZ / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
(RAIZ / "favicon.svg").unlink(missing_ok=True)

# ---------------------------------------------------------------- horizontal de leitura
f = TTFont(REF / "fonts" / "Saira.ttf")
f = instancer.instantiateVariableFont(f, {"wght": 600, "wdth": 112.5})
gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
cap = f["OS/2"].sCapHeight
x, partes, pos_o = 0, [], None
for i, ch in enumerate("On-Berry"):
    g = cmap[ord(ch)]
    if i == 0:
        pos_o = (x, hmtx[g][0])
    pen = SVGPathPen(gs)
    gs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
    partes.append(pen.getCommands())
    x += hmtx[g][0] - 0.01 * f["head"].unitsPerEm
larg_txt = x

ALT = 64                       # altura do desenho
esc_s = ALT / simbolo.height
w_simb = simbolo.width * esc_s
gap = 15
esc_t = 27 / cap               # versal de 30 px
base = ALT / 2 + 13.5            # texto centrado no símbolo
x_txt = w_simb + gap
W = x_txt + larg_txt * esc_t + 4

# símbolo embutido (svg em <img> não carrega arquivo externo)
s_png = simbolo.resize((round(simbolo.width * 192 / simbolo.height), 192), Image.LANCZOS)
buf = io.BytesIO(); s_png.save(buf, "PNG", optimize=True)
b64 = base64.b64encode(buf.getvalue()).decode()

# folha sobre o "O", como na logo oficial
ox, ow = pos_o
fx = x_txt + (ox + ow * 0.80) * esc_t
fy = base - cap * esc_t - 3
folha = (f'<path transform="translate({fx:.1f},{fy:.1f}) rotate(-28)" '
         f'd="M0,0 C3.2,-6.4 9.6,-8.6 13,-8.2 C12.4,-4.4 9.4,1.6 0,0 Z" fill="{AZUL_FOLHA}"/>')

def horizontal(cor, nome):
    corpo = (f'<image href="data:image/png;base64,{b64}" x="0" y="0" width="{w_simb:.1f}" height="{ALT}"/>'
             f'<path transform="translate({x_txt:.1f},{base:.1f}) scale({esc_t:.5f})" d="{" ".join(partes)}" fill="{cor}"/>'
             + folha)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -6 {W:.1f} {ALT + 6}" role="img" aria-label="On-Berry">'
           f'{corpo}</svg>')
    (SAI / nome).write_text(svg, encoding="utf-8")

horizontal("#F4EFE4", "horizontal-clara.svg")
horizontal("#151735", "horizontal-escura.svg")
print("ok", round(W), "x", ALT + 6)
