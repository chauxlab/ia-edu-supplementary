# Supplementary materials — University teachers' knowledge, ethical concerns, and training needs regarding artificial intelligence: a cross-sectional survey in Paraguay

Andrea Paola Britos Gómez, Alcides Chaux — ChauxLab Institute, Asunción, Paraguay

This repository holds the open supplementary materials for the manuscript submitted to *Investigación en Educación Médica* (Facultad de Medicina, UNAM). It does not hold the manuscript's final typeset version; the manuscript text here is the author's submitted copy.

## Contents

- `protocolo/bioetica-ia-docencia-protocolo.pdf` — the research protocol, including the full questionnaire (25 Likert items in seven domains) submitted to and approved by the committee of the Universidad Europea del Atlántico.
- `data/IA-EDU-DATA-pseudonimizado.csv` — the 667 analyzed responses. Each row carries a study identifier (`ID-001`...) only; no name, contact detail, or employing institution was collected. Semicolon-delimited, UTF-8.
- `analisis/analyze_survey.py` — the analysis script. Reads only `data/IA-EDU-DATA-pseudonimizado.csv`.
- `analisis/resumen.txt` — full descriptive and inferential output (all 25 items, domain scores, Cronbach's alpha, group contrasts).
- `analisis/items.csv` — item-level means, standard deviations, and agreement percentages.
- `manuscrito/ia-edu-manuscrito.md` — the manuscript text (Spanish, Vancouver style).
- `referencias/referencias-ia-edu.ris` — the manuscript's 19 references, in RIS format.

## What is not deposited here, and why

- The original response file included a 202-response open-ended free-text item. It was read in full during manuscript preparation; none of the responses contained an email address, a name, or the name of an employing institution. It is withheld from this repository as a precaution, since free-text opinion, combined with the demographic fields in the same row, could in principle narrow down a respondent's identity. It is not analyzed in the manuscript either.
- A notebook used during an earlier, unrelated stage of this research project simulated illustrative figures from randomly generated data (`numpy.random`) rather than from this survey. It never fed into the manuscript's results and is not part of these supplementary materials.
- Panel-review and pilot-test responses (5 experts; 25 teachers, used only to refine item wording before fieldwork) were not collected as part of the analytic dataset and are not included.

## Ethics

The protocol was submitted to and approved by the committee of the Universidad Europea del Atlántico. The questionnaire was anonymous and did not require the collection, use, or storage of personal data; no approval number was assigned. Participation was voluntary and required an active consent response before any item was shown.

## License

Data and analysis code: CC BY 4.0. Manuscript text: all rights reserved by the authors pending journal decision.
