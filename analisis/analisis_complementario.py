#!/usr/bin/env python3
"""Análisis complementarios pedidos en la revisión por pares (n = 113).

Lee únicamente data/IA-EDU-DATA-pseudonimizado.csv y escribe
analisis/complementario.txt: IC de Wilson de cada ítem, acuerdo con el ítem de
experiencia con IA por área e institución, prueba de Fisher y odds ratio
ajustado dentro de ciencias de la salud, contraste de conocimiento de ingeniería
y tecnología frente a las demás áreas (Mann-Whitney, Welch, diferencia con IC,
d de Cohen y delta de Cliff con IC por remuestreo) y alfas alternativos.
Requiere numpy y scipy.
"""
from __future__ import annotations
import csv, math
from pathlib import Path
import numpy as np
import scipy.stats as ss

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "IA-EDU-DATA-pseudonimizado.csv"
OUT = Path(__file__).resolve().parent / "complementario.txt"
L = {"Totalmente en desacuerdo": 1, "En desacuerdo": 2, "Neutral": 3, "De acuerdo": 4, "Totalmente de acuerdo": 5}

rows = list(csv.reader(DATA.open(encoding="utf-8-sig"), delimiter=";"))
d = rows[1:]
n = len(d)
area = np.array([r[1] for r in d]); inst = np.array([r[6] for r in d]); sex = np.array([r[4] for r in d])
age = np.array([float(r[3]) for r in d]); yrs = np.array([float(r[2]) for r in d])
X = np.array([[L[r[i]] for i in range(7, 32)] for r in d], float)
lines = []
w = lines.append

def wilson(k, m, z=1.96):
    p = k / m; den = 1 + z * z / m
    c = (p + z * z / (2 * m)) / den
    h = z * math.sqrt(p * (1 - p) / m + z * z / (4 * m * m)) / den
    return 100 * (c - h), 100 * (c + h)

w(f"n = {n}")
w("## Acuerdo por ítem (n, %, IC 95 % de Wilson)")
for j in range(25):
    k = int((X[:, j] >= 4).sum()); lo, hi = wilson(k, n)
    w(f"{j + 1:02d} {k} {100 * k / n:.1f} ({lo:.1f}-{hi:.1f})")
use = X[:, 19]
k = int((use >= 4).sum())
w(f"\nÍtem 20 (experiencia con IA): acuerdo {k}/{n}; desacuerdo {int((use <= 2).sum())}; neutral {int((use == 3).sum())}")
w("## Ítem 20 por área")
for a in sorted(set(area)):
    m = area == a; kk = int((use[m] >= 4).sum()); lo, hi = wilson(kk, int(m.sum()))
    w(f"{a}: {kk}/{int(m.sum())} {100 * kk / m.sum():.1f} ({lo:.1f}-{hi:.1f})")
H = area == "Ciencias médicas y de la salud"
w("## Ciencias de la salud, por institución")
tab = []
for t in ("Privada", "Pública"):
    m = H & (inst == t); kk = int((use[m] >= 4).sum()); lo, hi = wilson(kk, int(m.sum()))
    tab.append([kk, int(m.sum()) - kk])
    w(f"{t}: {kk}/{int(m.sum())} {100 * kk / m.sum():.1f} ({lo:.1f}-{hi:.1f})")
w(f"Fisher: {ss.fisher_exact(tab)}")
p1 = tab[0][0] / sum(tab[0]); p2 = tab[1][0] / sum(tab[1])
se = math.sqrt(p1 * (1 - p1) / sum(tab[0]) + p2 * (1 - p2) / sum(tab[1]))
w(f"Diferencia (privada - pública): {100 * (p1 - p2):.1f} puntos (IC {100 * (p1 - p2 - 1.96 * se):.1f} a {100 * (p1 - p2 + 1.96 * se):.1f})")

def logit(Xm, y):
    b = np.zeros(Xm.shape[1])
    for _ in range(100):
        p = 1 / (1 + np.exp(-Xm @ b)); W = p * (1 - p)
        Hm = Xm.T @ (Xm * W[:, None]); st = np.linalg.solve(Hm, Xm.T @ (y - p)); b += st
        if abs(st).max() < 1e-9: break
    return b, np.sqrt(np.diag(np.linalg.inv(Hm)))
Xm = np.column_stack([np.ones(H.sum()), (inst[H] == "Privada").astype(float), (sex[H] == "Femenino").astype(float), (age[H] - 45) / 10, (yrs[H] - 15) / 10])
bb, s_ = logit(Xm, (use[H] >= 4).astype(float))
w(f"OR ajustado (privada, por sexo, edad/10 y años/10): {math.exp(bb[1]):.2f} (IC {math.exp(bb[1] - 1.96 * s_[1]):.2f}-{math.exp(bb[1] + 1.96 * s_[1]):.2f})")

w("## Conocimiento: ingeniería y tecnología frente a las demás áreas")
K = X[:, :4].mean(1); eng = area == "Ingeniería y tecnología"; g1 = K[eng]; g2 = K[~eng]
w(f"Ing. n={len(g1)} media {g1.mean():.2f} DE {g1.std(ddof=1):.2f}; resto n={len(g2)} media {g2.mean():.2f} DE {g2.std(ddof=1):.2f}")
w(f"Mann-Whitney: {ss.mannwhitneyu(g1, g2, alternative='two-sided')}")
w(f"Welch: {ss.ttest_ind(g1, g2, equal_var=False)}")
diff = g1.mean() - g2.mean(); v1 = g1.var(ddof=1) / len(g1); v2 = g2.var(ddof=1) / len(g2)
df = (v1 + v2) ** 2 / (v1 ** 2 / (len(g1) - 1) + v2 ** 2 / (len(g2) - 1)); tq = ss.t.ppf(.975, df); se = math.sqrt(v1 + v2)
w(f"Diferencia {diff:.2f} (IC {diff - tq * se:.2f} a {diff + tq * se:.2f})")
sp = math.sqrt(((len(g1) - 1) * g1.var(ddof=1) + (len(g2) - 1) * g2.var(ddof=1)) / (len(g1) + len(g2) - 2))
def cliff(x, y): return ((x[:, None] > y[None, :]).sum() - (x[:, None] < y[None, :]).sum()) / (len(x) * len(y))
rng = np.random.default_rng(1); bc = []; bd = []
for _ in range(5000):
    s1 = rng.choice(g1, len(g1)); s2 = rng.choice(g2, len(g2)); bc.append(cliff(s1, s2))
    bd.append((s1.mean() - s2.mean()) / math.sqrt(((len(s1) - 1) * s1.var(ddof=1) + (len(s2) - 1) * s2.var(ddof=1)) / (len(s1) + len(s2) - 2)))
w(f"d de Cohen {diff / sp:.2f} (IC remuestreo {np.percentile(bd, 2.5):.2f} a {np.percentile(bd, 97.5):.2f}); delta de Cliff {cliff(g1, g2):.2f} (IC {np.percentile(bc, 2.5):.2f} a {np.percentile(bc, 97.5):.2f})")

def alpha(M):
    k = M.shape[1]; return k / (k - 1) * (1 - M.var(0, ddof=1).sum() / M.sum(1).var(ddof=1))
w("## Dominios alternativos")
w(f"Aplicación en la educación, ítems 10-12: alfa {alpha(X[:, 9:12]):.2f}; ítem 13: acuerdo {int((X[:, 12] >= 4).sum())}/{n}; r con 10-12: " + ", ".join(f"{np.corrcoef(X[:, 12], X[:, j])[0, 1]:.2f}" for j in (9, 10, 11)))
w(f"Experiencia y percepción personal, ítems 21-23: alfa {alpha(X[:, 20:23]):.2f}")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(OUT.read_text(encoding="utf-8"))
