# Material suplementario abierto — Conocimiento, preocupaciones éticas y necesidades de formación de docentes universitarios sobre inteligencia artificial: una encuesta transversal en Paraguay

Andrea Paola Britos Gómez, Alcides Chaux — ChauxLab Institute, Asunción, Paraguay

Este repositorio contiene el material suplementario abierto del manuscrito enviado a *Investigación en Educación Médica* (Facultad de Medicina, UNAM). No contiene la versión maquetada final del manuscrito; el texto aquí depositado es la copia enviada por los autores.

## Contenido

- `protocolo/bioetica-ia-docencia-protocolo.pdf` — el protocolo de investigación, incluido el cuestionario completo (25 ítems Likert en siete dominios) sometido a consideración y aprobado por el comité de la Universidad Europea del Atlántico.
- `data/IA-EDU-DATA-pseudonimizado.csv` — las 667 respuestas analizadas. Cada fila lleva solo un identificador de estudio (`ID-001`...); no se recolectó nombre, dato de contacto ni institución empleadora. Delimitado por punto y coma, UTF-8.
- `analisis/analyze_survey.py` — el script de análisis. Lee únicamente `data/IA-EDU-DATA-pseudonimizado.csv`.
- `analisis/resumen.txt` — salida descriptiva e inferencial completa (los 25 ítems, puntajes de dominio, alfa de Cronbach, contrastes de grupo).
- `analisis/items.csv` — medias, desviaciones estándar y porcentajes de acuerdo a nivel de ítem.
- `manuscrito/ia-edu-manuscrito.md` — el texto del manuscrito (español, estilo Vancouver).
- `referencias/referencias-ia-edu.ris` — las 19 referencias del manuscrito, en formato RIS.

## Qué no está depositado aquí, y por qué

- El archivo de respuestas original incluía un ítem de texto libre con 202 respuestas. Se leyó en su totalidad durante la preparación del manuscrito; ninguna respuesta contenía una dirección de correo electrónico, un nombre propio ni el nombre de una institución empleadora. Se retiene de este repositorio como precaución, ya que el texto libre, combinado con los campos demográficos de la misma fila, podría en principio acotar la identidad de quien responde. Tampoco se analiza en el manuscrito.
- Un cuaderno usado en una etapa anterior y no relacionada de este proyecto de investigación simulaba figuras ilustrativas a partir de datos generados aleatoriamente (`numpy.random`), no de esta encuesta. Nunca alimentó los resultados del manuscrito y no forma parte de este material suplementario.
- Las respuestas del panel de revisión y de la prueba piloto (5 expertos; 25 docentes, usadas solo para depurar la redacción de los ítems antes del trabajo de campo) no se recolectaron como parte del conjunto de datos analítico y no están incluidas.

## Ética

El protocolo se sometió a consideración y fue aprobado por el comité de la Universidad Europea del Atlántico. El cuestionario era anónimo y no requería la recolección, uso ni almacenamiento de datos personales; no se asignó un número de aprobación. La participación fue voluntaria y exigía una respuesta activa de consentimiento antes de mostrar cualquier ítem.

## Licencia

Datos y código de análisis: CC BY 4.0. Texto del manuscrito: todos los derechos reservados por los autores hasta la decisión editorial.
