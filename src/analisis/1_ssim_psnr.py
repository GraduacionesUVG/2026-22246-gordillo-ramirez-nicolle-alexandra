"""
Calcula SSIM y PSNR entre cada recurso grafico tradicional y su equivalente con IA.

Estructura esperada de carpetas (los nombres de archivo deben coincidir):
    recursos/tradicional/mesas.png   recursos/ia/mesas.png
    recursos/tradicional/sillas.png  recursos/ia/sillas.png
    ... (cafetera, clientes, jugador, lavamanos)

Uso:
    python 1_ssim_psnr.py recursos            # escribe metricas_tecnicas.csv

Decisiones metodologicas (documentalas en tu metodologia):
  - Fondo transparente: se compone sobre un fondo gris uniforme (--fondo 128).
  - Recorte: se recorta al rectangulo que contiene los pixeles no transparentes de
    CUALQUIERA de las dos imagenes (si no, el fondo vacio compartido infla SSIM/PSNR).
    Usa --sin-recorte para comparar el lienzo completo.
  - Si las dos imagenes tienen distinto tamano se centran en un lienzo comun (no se
    reescalan, para no alterar los pixeles) y se avisa en pantalla.
  - SSIM sobre RGB (channel_axis) con data_range=255; PSNR en dB sobre RGB.
"""
import argparse, csv, sys
from pathlib import Path
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity, peak_signal_noise_ratio

def cargar(ruta):
    return Image.open(ruta).convert("RGBA")

def a_lienzo_comun(a, b):
    w, h = max(a.width, b.width), max(a.height, b.height)
    avisos = a.size != b.size
    def centrar(im):
        lienzo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        lienzo.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
        return lienzo
    return centrar(a), centrar(b), avisos

def caja_union(a, b):
    ma = np.array(a)[..., 3] > 0
    mb = np.array(b)[..., 3] > 0
    m = ma | mb
    ys, xs = np.where(m)
    if len(ys) == 0:
        return (0, 0, a.width, a.height)
    return (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)

def sobre_fondo(im, fondo):
    base = Image.new("RGBA", im.size, (fondo, fondo, fondo, 255))
    base.alpha_composite(im)
    return np.array(base.convert("RGB"))

def metricas(ruta_t, ruta_i, fondo=128, recortar=True):
    a, b = cargar(ruta_t), cargar(ruta_i)
    a, b, aviso = a_lienzo_comun(a, b)
    if recortar:
        box = caja_union(a, b)
        a, b = a.crop(box), b.crop(box)
    A, B = sobre_fondo(a, fondo), sobre_fondo(b, fondo)
    win = min(7, min(A.shape[0], A.shape[1]))
    if win % 2 == 0:
        win -= 1
    ssim = structural_similarity(A, B, channel_axis=2, data_range=255, win_size=win)
    psnr = peak_signal_noise_ratio(A, B, data_range=255)
    return ssim, psnr, A.shape[1], A.shape[0], aviso

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpeta")
    ap.add_argument("--fondo", type=int, default=128)
    ap.add_argument("--sin-recorte", action="store_true")
    ap.add_argument("--salida", default="metricas_tecnicas.csv")
    args = ap.parse_args()
    raiz = Path(args.carpeta)
    trad, ia = raiz / "tradicional", raiz / "ia"
    filas = []
    for t in sorted(trad.glob("*.png")):
        i = ia / t.name
        if not i.exists():
            print(f"[!] Falta {i}", file=sys.stderr); continue
        ssim, psnr, w, h, aviso = metricas(t, i, args.fondo, not args.sin_recorte)
        if aviso:
            print(f"[aviso] {t.stem}: tamanos distintos, se centraron en un lienzo comun")
        filas.append(dict(recurso=t.stem, ssim=round(ssim, 4),
                          psnr_db=("inf" if np.isinf(psnr) else round(psnr, 2)),
                          ancho_comparado=w, alto_comparado=h))
        print(f"{t.stem:12s} SSIM={ssim:.4f}  PSNR={psnr:.2f} dB  ({w}x{h} px comparados)")
    with open(args.salida, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=["recurso", "ssim", "psnr_db", "ancho_comparado", "alto_comparado"])
        wr.writeheader(); wr.writerows(filas)
    print(f"\nGuardado en {args.salida}")

if __name__ == "__main__":
    main()
