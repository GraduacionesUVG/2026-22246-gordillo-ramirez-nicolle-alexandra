"""
Correlacion de Spearman entre las metricas tecnicas (SSIM, PSNR) de cada recurso grafico
y su percepcion en la encuesta, calculada por grupo.

Uso:
    python 3_spearman.py Formulario_de_tesis_respuestas.xlsx metricas_tecnicas.csv

Para cada recurso se calcula, a partir del Excel:
  - puntaje_ia : promedio de los 4 items (agradable, encaja, reconocible, calidad del dibujo)
                 de la version con IA.
  - delta      : puntaje_ia - puntaje_tradicional (cuanto cambia la percepcion).
Se reporta rho y p EXACTO (permutaciones; con n = 6 hay 720) para
SSIM y PSNR contra cada una de las dos variables, en: grupo no informado, grupo informado.
Elige UNA de las dos variables (puntaje_ia o delta) en tu metodologia y reporta esa;
la otra queda como analisis complementario.
Supuesto: el primer bloque de respuestas = version tradicional, el segundo = version IA.
"""
import sys, itertools
import numpy as np, pandas as pd
from scipy import stats

xlsx, csvm = sys.argv[1], sys.argv[2]
df = pd.read_excel(xlsx, sheet_name=0)
grupo = df.iloc[:, 2].map({"Grupo 1": "No informado", "Grupo 2": "Informado"})
v = df.iloc[:, 3:].apply(pd.to_numeric)
b1, b2 = v.iloc[:, :40], v.iloc[:, 40:]
els = ["mesas", "sillas", "cafetera", "clientes", "jugador", "lavamanos"]  # orden en el formulario

def comp(b, e):  # promedio de los 4 items del recurso e
    return np.mean([b.iloc[:, 11 + 6 * d + e].values for d in range(4)], axis=0)

met = pd.read_csv(csvm).set_index("recurso")
met["psnr_db"] = pd.to_numeric(met["psnr_db"], errors="coerce")  # 'inf' -> NaN
faltan = [e for e in els if e not in met.index]
if faltan: sys.exit(f"Faltan recursos en el CSV de metricas: {faltan}")

def spearman_exacto(x, y):
    rho = stats.spearmanr(x, y).statistic
    n = len(x); rx = stats.rankdata(x)
    obs = abs(rho); cnt = tot = 0
    for perm in itertools.permutations(range(n)):
        r = stats.spearmanr(rx, stats.rankdata(np.array(y)[list(perm)])).statistic
        tot += 1; cnt += abs(r) >= obs - 1e-12
    return rho, cnt / tot

filas = []
for g in ["No informado", "Informado"]:
    m = (grupo == g).values
    tabla = pd.DataFrame({
        "recurso": els,
        "puntaje_ia": [comp(b2, i)[m].mean() for i in range(6)],
        "puntaje_trad": [comp(b1, i)[m].mean() for i in range(6)],
    })
    tabla["delta"] = tabla.puntaje_ia - tabla.puntaje_trad
    tabla = tabla.set_index("recurso").join(met[["ssim", "psnr_db"]])
    print(f"\n=== Grupo {g} ===\n{tabla.round(3)}")
    for metrica in ["ssim", "psnr_db"]:
        for var in ["puntaje_ia", "delta"]:
            d = tabla[[metrica, var]].dropna()
            if len(d) < 4:
                print(f"  {metrica} vs {var}: n = {len(d)} (muy pocos datos)"); continue
            rho, p = spearman_exacto(d[metrica].values, d[var].values)
            filas.append(dict(grupo=g, metrica=metrica, variable=var, n=len(d), rho=round(rho, 3), p_exacto=round(p, 3)))
res = pd.DataFrame(filas)
print("\n=== Spearman (p exacto por permutaciones) ===\n", res.to_string(index=False))
print("\nReferencia: con n = 6, |rho| >= 0.886 para p < 0.05 (bilateral). Reporta tambien el poder limitado.")
res.to_csv("spearman_resultados.csv", index=False)

# diagrama de dispersion (SSIM vs puntaje de la version IA) por grupo
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True)
for ax, g in zip(axs, ["No informado", "Informado"]):
    m = (grupo == g).values
    y = [comp(b2, i)[m].mean() for i in range(6)]; x = [met.loc[e, "ssim"] for e in els]
    ax.scatter(x, y, color="#d9a441", edgecolor="k")
    for e, xi, yi in zip(els, x, y): ax.annotate(e, (xi, yi), textcoords="offset points", xytext=(4, 4), fontsize=7)
    ax.set_title(f"Grupo {g.lower()}"); ax.set_xlabel("SSIM"); ax.spines[["top", "right"]].set_visible(False)
axs[0].set_ylabel("Puntaje promedio de la version con IA")
plt.tight_layout(); plt.savefig("fig_spearman.pdf"); plt.savefig("fig_spearman.png", dpi=200)
print("Figura guardada: fig_spearman.pdf")
