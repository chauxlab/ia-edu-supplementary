#!/usr/bin/env python3
"""Análisis descriptivo de la encuesta a docentes universitarios sobre IA y bioética.

Lee únicamente el archivo de respuestas depositado. No simula observaciones.

Esta es la versión del repositorio público: lee el CSV pseudonimizado en
data/, que no incluye la columna de texto libre presente en el archivo de
respuestas original (retenida de este repositorio como precaución; ver
README.md).
"""

from __future__ import annotations

import csv
import math
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "IA-EDU-DATA-pseudonimizado.csv"
OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

LIKERT = {
    "Totalmente en desacuerdo": 1,
    "En desacuerdo": 2,
    "Neutral": 3,
    "De acuerdo": 4,
    "Totalmente de acuerdo": 5,
}
ACUERDO = {"De acuerdo", "Totalmente de acuerdo"}


def desviacion_estandar(valores: list[float]) -> float:
    return statistics.stdev(valores) if len(valores) > 1 else float("nan")


def media(valores: list[float]) -> float:
    return statistics.fmean(valores)


def alfa_cronbach(matriz: list[list[float]]) -> float:
    k = len(matriz[0])
    n = len(matriz)
    varianzas_item = []
    for j in range(k):
        columna = [matriz[i][j] for i in range(n)]
        varianzas_item.append(statistics.variance(columna))
    totales = [sum(fila) for fila in matriz]
    varianza_total = statistics.variance(totales)
    if varianza_total == 0:
        return float("nan")
    return (k / (k - 1)) * (1 - sum(varianzas_item) / varianza_total)


def spearman(x: list[float], y: list[float]) -> float:
    def rangos(valores: list[float]) -> list[float]:
        orden = sorted(range(len(valores)), key=lambda i: valores[i])
        r = [0.0] * len(valores)
        i = 0
        while i < len(valores):
            j = i
            while j + 1 < len(valores) and valores[orden[j + 1]] == valores[orden[i]]:
                j += 1
            promedio = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[orden[k]] = promedio
            i = j + 1
        return r

    rx, ry = rangos(x), rangos(y)
    mx, my = media(rx), media(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def d_de_cohen(a: list[float], b: list[float]) -> float:
    na, nb = len(a), len(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    if sp == 0:
        return float("nan")
    return (media(a) - media(b)) / sp


def p_mann_whitney(a: list[float], b: list[float]) -> float:
    """U de Mann-Whitney a dos colas, aproximación normal con corrección por empates."""
    n1, n2 = len(a), len(b)
    combinado = [(v, 0) for v in a] + [(v, 1) for v in b]
    combinado.sort(key=lambda t: t[0])
    rangos = [0.0] * len(combinado)
    i = 0
    termino_empates = 0.0
    while i < len(combinado):
        j = i
        while j + 1 < len(combinado) and combinado[j + 1][0] == combinado[i][0]:
            j += 1
        promedio = (i + j) / 2 + 1
        n_empate = j - i + 1
        if n_empate > 1:
            termino_empates += n_empate**3 - n_empate
        for k in range(i, j + 1):
            rangos[k] = promedio
        i = j + 1
    r1 = sum(rangos[k] for k in range(len(combinado)) if combinado[k][1] == 0)
    u1 = r1 - n1 * (n1 + 1) / 2
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    mu = n1 * n2 / 2
    n = n1 + n2
    correccion_empates = termino_empates / (n * (n - 1)) if n > 1 else 0
    sigma2 = (n1 * n2 / 12) * ((n + 1) - correccion_empates)
    if sigma2 <= 0:
        return float("nan")
    z = (u - mu + 0.5) / math.sqrt(sigma2)
    # dos colas, a partir de la función de error complementaria
    p = math.erfc(abs(z) / math.sqrt(2))
    return p


def cargar() -> tuple[list[str], list[dict[str, str]]]:
    with DATA.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        filas = list(reader)
        campos = list(reader.fieldnames or [])
    return campos, filas


def main() -> None:
    campos, filas = cargar()
    n = len(filas)
    clave_id, clave_area, clave_exp, clave_edad, clave_sexo, clave_genero, clave_inst = campos[:7]
    campos_item = campos[7:]

    dominios: list[tuple[str, list[str]]] = []
    for campo in campos_item:
        dominio, _item = campo.split(".", 1)
        if not dominios or dominios[-1][0] != dominio:
            dominios.append((dominio, []))
        dominios[-1][1].append(campo)

    edades = [float(r[clave_edad]) for r in filas]
    experiencias = [float(r[clave_exp]) for r in filas]

    lineas: list[str] = []
    w = lineas.append
    w(f"fuente: {DATA}")
    w(f"n: {n}")
    w(f"ids_unicos: {len({r[clave_id] for r in filas})}")
    w(f"items_likert: {len(campos_item)}")
    w(f"likert_incompleto: {sum(1 for r in filas if any(not (r[f] or '').strip() for f in campos_item))}")
    w("")
    w("## Muestra")
    for etiqueta, clave in (
        ("area", clave_area),
        ("sexo", clave_sexo),
        ("genero", clave_genero),
        ("institucion", clave_inst),
    ):
        conteos = Counter(r[clave] for r in filas)
        w(f"{etiqueta}:")
        for nombre, conteo in conteos.most_common():
            w(f"  {nombre}: {conteo} ({100 * conteo / n:.1f}%)")
    discordancia_sexo_genero = 0
    esperado = {"Femenino": "Mujer", "Masculino": "Hombre"}
    for r in filas:
        if esperado.get(r[clave_sexo]) != r[clave_genero]:
            discordancia_sexo_genero += 1
    w(f"discordancias_sexo_genero: {discordancia_sexo_genero}")
    w(
        f"edad: n={len(edades)} media={media(edades):.2f} de={desviacion_estandar(edades):.2f} "
        f"mediana={statistics.median(edades):.1f} min={min(edades):.0f} max={max(edades):.0f}"
    )
    w(
        f"experiencia_docente_anos: n={len(experiencias)} media={media(experiencias):.2f} de={desviacion_estandar(experiencias):.2f} "
        f"mediana={statistics.median(experiencias):.1f} min={min(experiencias):.0f} max={max(experiencias):.0f}"
    )
    w(f"spearman_edad_experiencia: {spearman(edades, experiencias):.3f}")
    w("")

    filas_item = []
    w("## Ítems")
    for indice, campo in enumerate(campos_item, start=1):
        dominio, item = campo.split(".", 1)
        codificado = [LIKERT[r[campo]] for r in filas]
        acuerdo = sum(1 for r in filas if r[campo] in ACUERDO)
        totalmente_acuerdo = sum(1 for r in filas if r[campo] == "Totalmente de acuerdo")
        neutral = sum(1 for r in filas if r[campo] == "Neutral")
        filas_item.append(
            {
                "item": indice,
                "dominio": dominio,
                "item_texto": item,
                "media": f"{media(codificado):.2f}",
                "de": f"{desviacion_estandar(codificado):.2f}",
                "acuerdo_n": acuerdo,
                "acuerdo_pct": f"{100 * acuerdo / n:.1f}",
                "totalmente_acuerdo_pct": f"{100 * totalmente_acuerdo / n:.1f}",
                "neutral_pct": f"{100 * neutral / n:.1f}",
            }
        )
        w(
            f"{indice:02d} acuerdo={100 * acuerdo / n:5.1f}% media={media(codificado):.2f} "
            f"de={desviacion_estandar(codificado):.2f} | {dominio} | {item}"
        )

    w("")
    w("## Dominios")
    puntajes_dominio: dict[str, list[float]] = {}
    for dominio, lista_items in dominios:
        matriz = [[LIKERT[r[f]] for f in lista_items] for r in filas]
        puntajes = [media(fila) for fila in matriz]
        puntajes_dominio[dominio] = puntajes
        alfa = alfa_cronbach(matriz)
        w(
            f"{dominio}: items={len(lista_items)} alfa={alfa:.3f} "
            f"media={media(puntajes):.2f} de={desviacion_estandar(puntajes):.2f}"
        )

    tecnica = "Ingeniería y tecnología"
    w("")
    w("## Ingeniería y tecnología frente al resto de las áreas")
    for dominio, _items in dominios:
        a = [puntajes_dominio[dominio][i] for i, r in enumerate(filas) if r[clave_area] == tecnica]
        b = [puntajes_dominio[dominio][i] for i, r in enumerate(filas) if r[clave_area] != tecnica]
        d = d_de_cohen(a, b)
        p = p_mann_whitney(a, b)
        w(
            f"{dominio}: n_tecnica={len(a)} media_tecnica={media(a):.2f} "
            f"n_resto={len(b)} media_resto={media(b):.2f} d={d:.2f} p_mannwhitney={p:.4g}"
        )

    conocimiento = "Conocimiento general sobre inteligencia artificial"
    w("")
    w(f"spearman_experiencia_conocimiento: {spearman(experiencias, puntajes_dominio[conocimiento]):.3f}")
    w(f"spearman_edad_conocimiento: {spearman(edades, puntajes_dominio[conocimiento]):.3f}")

    privada = "Privada"
    w("")
    w("## Institución privada frente a pública, conocimiento general")
    a = [puntajes_dominio[conocimiento][i] for i, r in enumerate(filas) if r[clave_inst] == privada]
    b = [puntajes_dominio[conocimiento][i] for i, r in enumerate(filas) if r[clave_inst] != privada]
    w(
        f"n_privada={len(a)} media_privada={media(a):.2f} de={desviacion_estandar(a):.2f} "
        f"n_publica={len(b)} media_publica={media(b):.2f} de={desviacion_estandar(b):.2f} "
        f"d={d_de_cohen(a, b):.2f} p_mannwhitney={p_mann_whitney(a, b):.4g}"
    )

    resumen = OUT / "resumen.txt"
    resumen.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    ruta_items = OUT / "items.csv"
    with ruta_items.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(filas_item[0].keys()))
        writer.writeheader()
        writer.writerows(filas_item)
    print(resumen.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
