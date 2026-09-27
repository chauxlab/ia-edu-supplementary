#!/usr/bin/env python3
"""Descriptive analysis of the university-teacher AI and bioethics survey.

Reads the deposited response file only. Does not simulate observations.

This is the public-repository version: it reads the pseudonymized CSV in
data/, which does not include the open-ended free-text column present in
the original response file (withheld from this repository as a precaution;
see README.md).
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
AGREE = {"De acuerdo", "Totalmente de acuerdo"}

DOMAIN_EN = {
    "Conocimiento general sobre inteligencia artificial": "General knowledge of AI",
    "Percepciones éticas sobre la inteligencia artificial": "Ethical perceptions of AI",
    "Aplicación de la inteligencia artificial en la educación": "AI in education",
    "Necesidad de formación en inteligencia artificial y bioética": "Training needs in AI and bioethics",
    "Integración de la bioética en el currículo": "Curricular integration of AI and bioethics",
    "Experiencia y percepción personal": "Personal experience and perception",
    "Percepciones futuras y tendencias": "Future perceptions and trends",
}

AREA_EN = {
    "Ciencias médicas y de la salud": "Health sciences",
    "Ciencias sociales": "Social sciences",
    "Ingeniería y tecnología": "Engineering and technology",
    "Humanidades": "Humanities",
    "Ciencias agrícolas": "Agricultural sciences",
}


def sample_sd(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else float("nan")


def mean(values: list[float]) -> float:
    return statistics.fmean(values)


def cronbach(matrix: list[list[float]]) -> float:
    k = len(matrix[0])
    n = len(matrix)
    item_vars = []
    for j in range(k):
        col = [matrix[i][j] for i in range(n)]
        item_vars.append(statistics.variance(col))
    totals = [sum(row) for row in matrix]
    total_var = statistics.variance(totals)
    if total_var == 0:
        return float("nan")
    return (k / (k - 1)) * (1 - sum(item_vars) / total_var)


def spearman(x: list[float], y: list[float]) -> float:
    def ranks(vals: list[float]) -> list[float]:
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        r = [0.0] * len(vals)
        i = 0
        while i < len(vals):
            j = i
            while j + 1 < len(vals) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = ranks(x), ranks(y)
    mx, my = mean(rx), mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def cohens_d(a: list[float], b: list[float]) -> float:
    na, nb = len(a), len(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    if sp == 0:
        return float("nan")
    return (mean(a) - mean(b)) / sp


def mann_whitney_p(a: list[float], b: list[float]) -> float:
    """Two-sided Mann-Whitney U via normal approximation with tie correction."""
    n1, n2 = len(a), len(b)
    combined = [(v, 0) for v in a] + [(v, 1) for v in b]
    combined.sort(key=lambda t: t[0])
    ranks = [0.0] * len(combined)
    i = 0
    tie_term = 0.0
    while i < len(combined):
        j = i
        while j + 1 < len(combined) and combined[j + 1][0] == combined[i][0]:
            j += 1
        avg = (i + j) / 2 + 1
        tie_n = j - i + 1
        if tie_n > 1:
            tie_term += tie_n**3 - tie_n
        for k in range(i, j + 1):
            ranks[k] = avg
        i = j + 1
    r1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)
    u1 = r1 - n1 * (n1 + 1) / 2
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    mu = n1 * n2 / 2
    n = n1 + n2
    tie_corr = tie_term / (n * (n - 1)) if n > 1 else 0
    sigma2 = (n1 * n2 / 12) * ((n + 1) - tie_corr)
    if sigma2 <= 0:
        return float("nan")
    z = (u - mu + 0.5) / math.sqrt(sigma2)
    # two-sided from complementary error function
    p = math.erfc(abs(z) / math.sqrt(2))
    return p


def load() -> tuple[list[str], list[dict[str, str]]]:
    with DATA.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    return fields, rows


def main() -> None:
    fields, rows = load()
    n = len(rows)
    id_key, area_key, exp_key, age_key, sex_key, gender_key, inst_key = fields[:7]
    item_fields = fields[7:]

    domains: list[tuple[str, list[str]]] = []
    for field in item_fields:
        domain, _item = field.split(".", 1)
        if not domains or domains[-1][0] != domain:
            domains.append((domain, []))
        domains[-1][1].append(field)

    ages = [float(r[age_key]) for r in rows]
    exps = [float(r[exp_key]) for r in rows]

    lines: list[str] = []
    w = lines.append
    w(f"source: {DATA}")
    w(f"n: {n}")
    w(f"unique_ids: {len({r[id_key] for r in rows})}")
    w(f"likert_items: {len(item_fields)}")
    w(f"incomplete_likert: {sum(1 for r in rows if any(not (r[f] or '').strip() for f in item_fields))}")
    w("")
    w("## Sample")
    for label, key, mapping in (
        ("area", area_key, AREA_EN),
        ("sex", sex_key, None),
        ("gender", gender_key, None),
        ("institution", inst_key, None),
    ):
        counts = Counter(r[key] for r in rows)
        w(f"{label}:")
        for name, count in counts.most_common():
            shown = mapping.get(name, name) if mapping else name
            w(f"  {shown}: {count} ({100 * count / n:.1f}%)")
    sex_gender_mismatch = 0
    expected = {"Femenino": "Mujer", "Masculino": "Hombre"}
    for r in rows:
        if expected.get(r[sex_key]) != r[gender_key]:
            sex_gender_mismatch += 1
    w(f"sex_gender_mismatches: {sex_gender_mismatch}")
    w(
        f"age: n={len(ages)} mean={mean(ages):.2f} sd={sample_sd(ages):.2f} "
        f"median={statistics.median(ages):.1f} min={min(ages):.0f} max={max(ages):.0f}"
    )
    w(
        f"experience_years: n={len(exps)} mean={mean(exps):.2f} sd={sample_sd(exps):.2f} "
        f"median={statistics.median(exps):.1f} min={min(exps):.0f} max={max(exps):.0f}"
    )
    w(f"spearman_age_experience: {spearman(ages, exps):.3f}")
    w("")

    item_rows = []
    w("## Items")
    for index, field in enumerate(item_fields, start=1):
        domain, item = field.split(".", 1)
        coded = [LIKERT[r[field]] for r in rows]
        agree = sum(1 for r in rows if r[field] in AGREE)
        strong = sum(1 for r in rows if r[field] == "Totalmente de acuerdo")
        neutral = sum(1 for r in rows if r[field] == "Neutral")
        item_rows.append(
            {
                "item": index,
                "domain_en": DOMAIN_EN[domain],
                "item_es": item,
                "mean": f"{mean(coded):.2f}",
                "sd": f"{sample_sd(coded):.2f}",
                "agree_n": agree,
                "agree_pct": f"{100 * agree / n:.1f}",
                "strongly_agree_pct": f"{100 * strong / n:.1f}",
                "neutral_pct": f"{100 * neutral / n:.1f}",
            }
        )
        w(
            f"{index:02d} agree={100 * agree / n:5.1f}% mean={mean(coded):.2f} "
            f"sd={sample_sd(coded):.2f} | {DOMAIN_EN[domain]} | {item}"
        )

    w("")
    w("## Domains")
    domain_scores: dict[str, list[float]] = {}
    for domain, item_list in domains:
        matrix = [[LIKERT[r[f]] for f in item_list] for r in rows]
        scores = [mean(row) for row in matrix]
        domain_scores[domain] = scores
        alpha = cronbach(matrix)
        w(
            f"{DOMAIN_EN[domain]}: items={len(item_list)} alpha={alpha:.3f} "
            f"mean={mean(scores):.2f} sd={sample_sd(scores):.2f}"
        )

    technical = "Ingeniería y tecnología"
    w("")
    w("## Engineering and technology versus all other areas")
    for domain, _items in domains:
        a = [domain_scores[domain][i] for i, r in enumerate(rows) if r[area_key] == technical]
        b = [domain_scores[domain][i] for i, r in enumerate(rows) if r[area_key] != technical]
        d = cohens_d(a, b)
        p = mann_whitney_p(a, b)
        w(
            f"{DOMAIN_EN[domain]}: tech_n={len(a)} tech_mean={mean(a):.2f} "
            f"other_n={len(b)} other_mean={mean(b):.2f} d={d:.2f} mannwhitney_p={p:.4g}"
        )

    knowledge = "Conocimiento general sobre inteligencia artificial"
    w("")
    w(f"spearman_experience_knowledge: {spearman(exps, domain_scores[knowledge]):.3f}")
    w(f"spearman_age_knowledge: {spearman(ages, domain_scores[knowledge]):.3f}")

    private = "Privada"
    w("")
    w("## Private versus public institution, general knowledge")
    a = [domain_scores[knowledge][i] for i, r in enumerate(rows) if r[inst_key] == private]
    b = [domain_scores[knowledge][i] for i, r in enumerate(rows) if r[inst_key] != private]
    w(
        f"private_n={len(a)} private_mean={mean(a):.2f} sd={sample_sd(a):.2f} "
        f"public_n={len(b)} public_mean={mean(b):.2f} sd={sample_sd(b):.2f} "
        f"d={cohens_d(a, b):.2f} mannwhitney_p={mann_whitney_p(a, b):.4g}"
    )

    summary = OUT / "resumen.txt"
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")

    items_path = OUT / "items.csv"
    with items_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(item_rows[0].keys()))
        writer.writeheader()
        writer.writerows(item_rows)
    print(summary.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
