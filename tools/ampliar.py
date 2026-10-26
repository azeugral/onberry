"""Super-resolução das artes do hero com OpenCV dnn_superres (EDSR), em blocos com sobreposição.

python tools/ampliar.py ENTRADA SAIDA [escala=4] [largura_final]
Os pesos ficam em PROJETOS LRGZ/_ferramentas/superres/EDSR_x{2,4}.pb
"""
import sys, time
from pathlib import Path
import cv2
import numpy as np

MODELOS = Path(__file__).resolve().parents[3] / "_ferramentas" / "superres"


def ampliar(img, escala, bloco=192, borda=12):
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(str(MODELOS / f"EDSR_x{escala}.pb"))
    sr.setModel("edsr", escala)
    h, w = img.shape[:2]
    out = np.zeros((h * escala, w * escala, 3), np.float32)
    peso = np.zeros((h * escala, w * escala, 1), np.float32)
    passo = bloco - 2 * borda
    total = ((h + passo - 1) // passo) * ((w + passo - 1) // passo)
    feitos, t0 = 0, time.time()
    for y in range(0, h, passo):
        for x in range(0, w, passo):
            y0, x0 = max(0, y - borda), max(0, x - borda)
            y1, x1 = min(h, y + passo + borda), min(w, x + passo + borda)
            r = sr.upsample(img[y0:y1, x0:x1]).astype(np.float32)
            # janela suave para emendar os blocos sem costura
            hh, ww = r.shape[:2]
            jy = np.minimum(np.arange(hh) + 1, np.arange(hh)[::-1] + 1).clip(max=borda * escala) / (borda * escala)
            jx = np.minimum(np.arange(ww) + 1, np.arange(ww)[::-1] + 1).clip(max=borda * escala) / (borda * escala)
            if y0 == 0: jy[: borda * escala] = 1
            if y1 == h: jy[-borda * escala:] = 1
            if x0 == 0: jx[: borda * escala] = 1
            if x1 == w: jx[-borda * escala:] = 1
            jan = (jy[:, None] * jx[None, :])[..., None].astype(np.float32)
            out[y0 * escala:y1 * escala, x0 * escala:x1 * escala] += r * jan
            peso[y0 * escala:y1 * escala, x0 * escala:x1 * escala] += jan
            feitos += 1
            if feitos % 10 == 0 or feitos == total:
                el = time.time() - t0
                print(f"{feitos}/{total} blocos · {el:.0f}s · faltam ~{el / feitos * (total - feitos):.0f}s", flush=True)
    return np.clip(out / np.maximum(peso, 1e-6), 0, 255).astype(np.uint8)


if __name__ == "__main__":
    ent, sai = sys.argv[1], sys.argv[2]
    escala = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    largura = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    img = cv2.imread(ent, cv2.IMREAD_COLOR)
    res = ampliar(img, escala)
    if largura:
        alt = round(res.shape[0] * largura / res.shape[1])
        res = cv2.resize(res, (largura, alt), interpolation=cv2.INTER_AREA)
    cv2.imwrite(sai, res)
    print("ok", res.shape[1], "x", res.shape[0])
