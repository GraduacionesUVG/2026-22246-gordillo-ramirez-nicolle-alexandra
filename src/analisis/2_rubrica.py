"""
Resume las calificaciones de la rubrica tecnica.

Entrada: rubrica_calificaciones.csv con columnas
    calificador,version,criterio,puntaje
donde version = tradicional | ia, puntaje = 1..4 (segun tu rubrica) y un renglon por
calificador x version x criterio.

Salida: promedio y desviacion por criterio y version, total por version, y si hay
2 o mas calificadores, acuerdo entre calificadores (kappa ponderado cuadratico entre
cada par y % de acuerdo exacto / dentro de +-1 punto).

Uso:  python 2_rubrica.py rubrica_calificaciones.csv
"""
import sys, itertools
import numpy as np, pandas as pd

def kappa_cuadratico(a, b, k_min, k_max):
    cats = np.arange(k_min, k_max + 1); k = len(cats)
    O = np.zeros((k, k))
    for x, y in zip(a, b): O[int(x) - k_min, int(y) - k_min] += 1
    E = np.outer(O.sum(1), O.sum(0)) / O.sum()
    W = ((np.arange(k)[:, None] - np.arange(k)[None, :]) ** 2) / (k - 1) ** 2
    den = (W * E).sum()
    return 1 - (W * O).sum() / den if den > 0 else float("nan")

df = pd.read_csv(sys.argv[1])
res = df.groupby(["criterio", "version"])["puntaje"].agg(["mean", "std"]).round(2).unstack("version")
print("\nPuntaje por criterio y version (media, desviacion):\n", res)
tot = df.groupby(["calificador", "version"])["puntaje"].mean().groupby("version").agg(["mean", "std"]).round(2)
print("\nPromedio total por version (promedio de los calificadores):\n", tot)

cal = sorted(df.calificador.unique())
if len(cal) >= 2:
    p = df.pivot_table(index=["version", "criterio"], columns="calificador", values="puntaje")
    kmin, kmax = int(df.puntaje.min()), int(df.puntaje.max())
    print("\nAcuerdo entre calificadores:")
    for c1, c2 in itertools.combinations(cal, 2):
        d = p[[c1, c2]].dropna()
        exacto = (d[c1] == d[c2]).mean() * 100
        cerca = ((d[c1] - d[c2]).abs() <= 1).mean() * 100
        print(f"  {c1} vs {c2}: kappa ponderado = {kappa_cuadratico(d[c1], d[c2], kmin, kmax):.2f}; "
              f"acuerdo exacto = {exacto:.0f}%; dentro de +-1 = {cerca:.0f}% (n = {len(d)})")
else:
    print("\n(Un solo calificador: reporta como limitacion que no se midio acuerdo entre calificadores.)")
