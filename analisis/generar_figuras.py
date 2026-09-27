#!/usr/bin/env python3
"""Genera las figuras del manuscrito a partir de la encuesta real.

Versión del repositorio público: lee el CSV pseudonimizado en data/, que no
incluye la columna de texto libre del archivo de respuestas original
(retenida de este repositorio como precaución; ver README.md). No simula
observaciones. Reproduce, en gráficos, cifras ya verificadas en
analisis/resumen.txt.
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "IA-EDU-DATA-pseudonimizado.csv"
OUT = Path(__file__).resolve().parents[1] / "figuras"
OUT.mkdir(parents=True, exist_ok=True)

AZUL = "#2a78d6"
GRIS_TEXTO = "#0b0b0b"
GRIS_SECUNDARIO = "#52514e"

LIKERT = {
    "Totalmente en desacuerdo": 1,
    "En desacuerdo": 2,
    "Neutral": 3,
    "De acuerdo": 4,
    "Totalmente de acuerdo": 5,
}
ACUERDO = {"De acuerdo", "Totalmente de acuerdo"}

DOMINIOS_ORDEN = [
    "Conocimiento general sobre inteligencia artificial",
    "Percepciones éticas sobre la inteligencia artificial",
    "Aplicación de la inteligencia artificial en la educación",
    "Necesidad de formación en inteligencia artificial y bioética",
    "Integración de la bioética en el currículo",
    "Experiencia y percepción personal",
    "Percepciones futuras y tendencias",
]
DOMINIOS_ETIQUETA = {
    "Conocimiento general sobre inteligencia artificial": "Conocimiento general\nsobre IA",
    "Percepciones éticas sobre la inteligencia artificial": "Percepciones éticas",
    "Aplicación de la inteligencia artificial en la educación": "Aplicación en\nla educación",
    "Necesidad de formación en inteligencia artificial y bioética": "Necesidad de\nformación",
    "Integración de la bioética en el currículo": "Integración\ncurricular",
    "Experiencia y percepción personal": "Experiencia y\npercepción personal",
    "Percepciones futuras y tendencias": "Percepciones\nfuturas",
}


def media(valores: list[float]) -> float:
    return statistics.fmean(valores)


def de(valores: list[float]) -> float:
    return statistics.stdev(valores) if len(valores) > 1 else float("nan")


def cargar() -> tuple[list[str], list[dict[str, str]]]:
    with DATA.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        filas = list(reader)
        campos = list(reader.fieldnames or [])
    return campos, filas


def estilo_ejes(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="both", colors=GRIS_SECUNDARIO, labelsize=9)
    ax.xaxis.label.set_color(GRIS_TEXTO)
    ax.yaxis.label.set_color(GRIS_TEXTO)


def figura_1(campos: list[str], filas: list[dict[str, str]]) -> None:
    campos_item = campos[7:]
    dominios: dict[str, list[str]] = {}
    for campo in campos_item:
        dominio, _item = campo.split(".", 1)
        dominios.setdefault(dominio, []).append(campo)

    medias, des = [], []
    for dominio in DOMINIOS_ORDEN:
        matriz = [[LIKERT[r[f]] for f in dominios[dominio]] for r in filas]
        puntajes = [media(fila) for fila in matriz]
        medias.append(media(puntajes))
        des.append(de(puntajes))

    orden = sorted(range(len(DOMINIOS_ORDEN)), key=lambda i: medias[i])
    etiquetas = [DOMINIOS_ETIQUETA[DOMINIOS_ORDEN[i]] for i in orden]
    medias_o = [medias[i] for i in orden]
    des_o = [des[i] for i in orden]

    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
    y = range(len(etiquetas))
    ax.barh(y, medias_o, xerr=des_o, color=AZUL, height=0.6, capsize=3,
            error_kw={"ecolor": GRIS_SECUNDARIO, "elinewidth": 1})
    for i, (m, s) in enumerate(zip(medias_o, des_o)):
        ax.text(m + s + 0.08, i, f"{m:.2f}", va="center", fontsize=9, color=GRIS_TEXTO)
    ax.set_yticks(list(y))
    ax.set_yticklabels(etiquetas, fontsize=9)
    ax.set_xlim(1, 5.6)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xlabel("Puntaje de dominio (1-5, media ± DE)")
    ax.axvline(3, color=GRIS_SECUNDARIO, linewidth=0.8, linestyle=":", alpha=0.6)
    estilo_ejes(ax)
    fig.tight_layout()
    fig.savefig(OUT / "figura1_puntajes_dominio.png", facecolor="white")
    plt.close(fig)


def figura_2(campos: list[str], filas: list[dict[str, str]]) -> None:
    area_key = campos[1]
    inst_key = campos[6]
    campos_item = campos[7:]
    campo_uso = next(f for f in campos_item if f.startswith("Experiencia y percepción personal") and "utilizado" in f.lower())

    # Ciencias agrícolas (n=7) queda fuera de esta figura por decisión editorial
    # ya registrada en ia-edu-notas-editoriales.md: la celda es demasiado
    # pequeña para featurear (las 7 respuestas son "Neutral" en este ítem,
    # 0.0%, un artefacto de tamaño de celda, no un hallazgo interpretable).
    areas_orden = [
        "Ingeniería y tecnología",
        "Ciencias sociales",
        "Humanidades",
        "Ciencias médicas y de la salud",
    ]
    etiquetas_area = {
        "Ingeniería y tecnología": "Ingeniería y\ntecnología",
        "Ciencias sociales": "Ciencias\nsociales",
        "Humanidades": "Humanidades",
        "Ciencias médicas y de la salud": "Ciencias de\nla salud",
    }

    pct_area = []
    n_area = []
    for area in areas_orden:
        sub = [r for r in filas if r[area_key] == area]
        uso = sum(1 for r in sub if r[campo_uso] in ACUERDO)
        n_area.append(len(sub))
        pct_area.append(100 * uso / len(sub))

    salud = [r for r in filas if r[area_key] == "Ciencias médicas y de la salud"]
    priv = [r for r in salud if r[inst_key] == "Privada"]
    pub = [r for r in salud if r[inst_key] != "Privada"]
    pct_inst = [
        100 * sum(1 for r in priv if r[campo_uso] in ACUERDO) / len(priv),
        100 * sum(1 for r in pub if r[campo_uso] in ACUERDO) / len(pub),
    ]
    n_inst = [len(priv), len(pub)]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(9, 4), dpi=300, sharey=True,
        gridspec_kw={"width_ratios": [5, 2]},
    )

    x1 = range(len(areas_orden))
    ax1.bar(x1, pct_area, color=AZUL, width=0.6)
    for i, (p, n) in enumerate(zip(pct_area, n_area)):
        ax1.text(i, p + 2, f"{p:.1f}%\n(n={n})", ha="center", fontsize=8, color=GRIS_TEXTO)
    ax1.set_xticks(list(x1))
    ax1.set_xticklabels([etiquetas_area[a] for a in areas_orden], fontsize=8)
    ax1.set_ylabel("Uso declarado de IA en\ninvestigación o docencia (%)")
    ax1.set_ylim(0, 78)
    ax1.set_title("Por área académica", fontsize=10, color=GRIS_TEXTO, loc="left")
    estilo_ejes(ax1)

    x2 = range(2)
    ax2.bar(x2, pct_inst, color=AZUL, width=0.5)
    for i, (p, n) in enumerate(zip(pct_inst, n_inst)):
        ax2.text(i, p + 2, f"{p:.1f}%\n(n={n})", ha="center", fontsize=8, color=GRIS_TEXTO)
    ax2.set_xticks(list(x2))
    ax2.set_xticklabels(["Privada", "Pública"], fontsize=9)
    ax2.set_ylim(0, 78)
    ax2.set_title("Ciencias de la salud,\npor institución", fontsize=10, color=GRIS_TEXTO, loc="left")
    estilo_ejes(ax2)
    ax2.tick_params(axis="y", left=False)

    fig.tight_layout()
    fig.savefig(OUT / "figura2_uso_declarado.png", facecolor="white")
    plt.close(fig)


def main() -> None:
    campos, filas = cargar()
    figura_1(campos, filas)
    figura_2(campos, filas)
    print(f"Figuras escritas en {OUT}")


if __name__ == "__main__":
    main()
