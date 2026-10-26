"""Recorta e exporta as fotos reais (Instagram) e os renders do hero para o site.

python tools/processar.py fotos   -> assets/img/*.webp|jpg
python tools/processar.py hero    -> assets/hero/*.mp4 + posters + og.jpg (depois do render do Blender)
python tools/processar.py icones  -> favicon-*.png, apple-touch-icon.png
"""
import sys, subprocess, shutil
from pathlib import Path
from PIL import Image, ImageEnhance

RAIZ = Path(__file__).resolve().parents[1]
REF = RAIZ.parent / "_ref"
IMG = RAIZ / "assets" / "img"
HERO = RAIZ / "assets" / "hero"
IMG.mkdir(parents=True, exist_ok=True)
HERO.mkdir(parents=True, exist_ok=True)

# nome: (arquivo do IG, proporcao w/h, deslocamento vertical 0..1, largura final)
FOTOS = {
    "embalagem": ("01_2026-09-08_DdCpdaovDNG.jpg", 4 / 5, 0.02, 1000),
    "flor": ("02_2026-08-07_DbwFAaqP2Fm.jpg", 4 / 5, 0.20, 1000),
    "plantio": ("03_2026-08-07_DbwDNVpPEjx.jpg", 4 / 5, 0.38, 1000),
    "plantio-largo": ("03_2026-08-07_DbwDNVpPEjx.jpg", 16 / 10, 0.42, 1125),
}


def recorta(im, prop, dy):
    w, h = im.size
    if w / h > prop:
        nw = int(h * prop)
        x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = int(w / prop)
    y = int((h - nh) * dy)
    return im.crop((0, y, w, y + nh))


def fotos():
    for nome, (arq, prop, dy, larg) in FOTOS.items():
        im = Image.open(REF / "ig" / arq).convert("RGB")
        # corta a faixa de interface do story (cantos arredondados) nas fotos verticais
        if im.size == (1125, 2000):
            im = im.crop((14, 14, 1111, 1986))
        if nome == "embalagem":  # evita o texto e o emoji do story embaixo
            im = im.crop((46, 100, 1046, 1350))
        if nome == "colheita-uva":  # tira a moldura de madeira da arte original
            im = im.crop((52, 40, im.width - 40, im.height - 40))
        im = recorta(im, prop, dy)
        if im.width > larg:
            im = im.resize((larg, round(larg / prop)), Image.LANCZOS)
        im = ImageEnhance.Contrast(im).enhance(1.04)
        im.save(IMG / f"{nome}.webp", quality=82, method=6)
        im.save(IMG / f"{nome}.jpg", quality=84, optimize=True, progressive=True)
        print(nome, im.size)


def hero():
    rend = REF / "render"
    for modo, larg in (("desktop", 1920), ("mobile", 1080)):
        pasta = rend / modo
        if not (pasta / "f_0001.png").exists():
            print("sem frames", modo); continue
        saida = HERO / f"mirtilos-{modo}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", str(pasta / "f_%04d.png"),
                        "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", "-an", str(saida)], check=True)
        im = Image.open(pasta / "f_0001.png").convert("RGB")
        im.save(HERO / f"poster-{modo}.jpg", quality=82, optimize=True, progressive=True)
        im.save(HERO / f"poster-{modo}.webp", quality=80, method=6)
        print(modo, saida.stat().st_size // 1024, "KB")
    st = rend / "still" / "still.png"
    if st.exists():
        im = Image.open(st).convert("RGB")
        im.save(IMG / "mirtilos-4k.jpg", quality=88, optimize=True, progressive=True)
        im.resize((2560, 1440), Image.LANCZOS).save(IMG / "mirtilos-2560.webp", quality=84, method=6)
        im.resize((1280, 720), Image.LANCZOS).save(IMG / "mirtilos-1280.webp", quality=82, method=6)
        print("still ok")


def icones():
    from playwright.sync_api import sync_playwright
    svg = (RAIZ / "favicon.svg").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nome, t in (("favicon-32.png", 32), ("favicon-192.png", 192), ("favicon-512.png", 512),
                        ("apple-touch-icon.png", 180)):
            pg = b.new_page(viewport={"width": t, "height": t})
            pg.set_content(f'<style>html,body{{margin:0;background:transparent}}</style>'
                           f'<img src="{svg}" style="width:{t}px;height:{t}px;display:block">')
            pg.wait_for_timeout(150)
            pg.screenshot(path=str(RAIZ / nome), omit_background=True)
            pg.close()
        b.close()
    print("icones ok")


if __name__ == "__main__":
    {"fotos": fotos, "hero": hero, "icones": icones}[sys.argv[1] if len(sys.argv) > 1 else "fotos"]()
