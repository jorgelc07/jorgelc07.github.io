# Jorge Luis Congacha — publicación de análisis

Sitio web personal de análisis, datos y artículos.
Estático, sin backend, sin base de datos y con hosting gratuito.

**URL pública:** https://jorgelc07.github.io — **en línea desde el 8 de agosto de 2026**
**Repositorio:** https://github.com/jorgelc07/jorgelc07.github.io (público)

---

## 1. Qué es esto

Una pequeña publicación digital para divulgar análisis político, electoral,
económico, de conflicto y violencia y de desarrollo territorial, con foco en
Nariño y Colombia.

El caso de uso central: publico un hilo en X, lo cierro con un enlace a este
sitio, y quien quiera leer la nota completa con sus gráficos y sus fuentes
entra acá.

Está pensado para durar sin mantenimiento: no hay dependencias que actualizar,
ni servidor que se caiga, ni factura que pagar.

**Costo total: $0.** GitHub Pages en repositorio público es gratuito de forma
permanente. No hay ningún servicio de pago, suscripción, prueba gratuita ni
medio de pago asociado a este proyecto.

---

## 2. Estructura de carpetas

```
web_jorgeluis/
│
├── content/                      ← LO QUE SE EDITA PARA PUBLICAR
│   ├── sitio.json                    configuración global (URL, nombre, correo, X)
│   ├── articulos/                    una nota por archivo .md
│   │   └── narino-paz-territorial-homicidios-coca.md
│   └── paginas/                      páginas fijas
│       └── sobre-mi.md
│
├── scripts/                      ← HERRAMIENTAS
│   ├── build.js                      genera el sitio (Node, sin dependencias)
│   ├── probar.py                     pruebas automáticas en 5 anchos
│   ├── extraer_graficos.py           saca los gráficos del .docx y los optimiza
│   ├── generar_imagenes.py           favicon + tarjetas para compartir en X
│   ├── preparar_documentos.py                CV sin teléfono + PDF sin metadatos
│   └── publicar.sh                   despliegue a GitHub Pages
│
├── docs/                         ← EL SITIO PUBLICADO (generado, no editar a mano)
│   ├── index.html                    portada
│   ├── analisis/                     listado de notas
│   ├── articulos/<slug>/             cada nota
│   ├── temas/<slug>/                 páginas por tema
│   ├── sobre-mi/                     perfil
│   ├── assets/
│   │   ├── css/estilo.css            única hoja de estilos
│   │   ├── fuentes/                  tipografías auto-alojadas (woff2)
│   │   ├── img/graficos/             gráficos en WebP + PNG
│   │   ├── img/social/               tarjetas 1200×630 para X
│   │   └── documentos/               CV y PDF de la nota
│   ├── 404.html, sitemap.xml, feed.xml, robots.txt, favicon.svg
│   └── .nojekyll
│
├── originales/                   ← COPIAS DE LOS ARCHIVOS DE ORIGEN, NO SE TOCAN
│   ├── CV - Jorge Luis Congacha.pdf      (con teléfono; NO se publica)
│   ├── narino_paz_territorial_coca_otros.pdf / .docx
│   ├── graficos_v9_finales/
│   └── graficos_nota/                    los 11 gráficos extraídos del .docx
│
├── docs-proyecto/
│   ├── plan.md                       el plan escrito antes de programar
│   └── decisiones.md                 por qué cada decisión técnica
│
├── pruebas/capturas/             capturas de las pruebas (no se versionan)
└── README.md
```

> **`docs/` es salida generada.** Cualquier cosa que edites ahí a mano se pierde
> en el siguiente `node scripts/build.js`. Lo que se edita está en `content/`.
> Las dos excepciones, que sí se editan a mano, son `docs/assets/css/estilo.css`
> y los archivos de `docs/assets/img/` y `docs/assets/documentos/`.

---

## 3. Tecnología

| Pieza | Elección | Por qué |
|---|---|---|
| Generador | `scripts/build.js`, Node puro | ~550 líneas legibles, cero dependencias, nada que actualizar |
| Contenido | Markdown + metadatos | Escribir una nota es escribir un archivo de texto |
| Estilos | Un solo CSS a mano | Sin framework, sin build de CSS |
| JavaScript | **ninguno** | El sitio no necesita JS para leerse; es más rápido, más accesible y no se rompe |
| Tipografías | Source Serif 4 + Inter, auto-alojadas | Sin peticiones a Google en cada visita |
| Imágenes | WebP con respaldo PNG | 3,0 MB → 823 KB sin perder legibilidad |
| Hosting | GitHub Pages | Gratis, HTTPS incluido, despliegue con `git push` |

Node solo hace falta para **generar** el sitio. Lo que se publica es HTML plano:
aunque Node desaparezca, `docs/` sigue funcionando.

### Requisitos

- **Node.js** (cualquier versión reciente) — para `build.js`.
- **Python 3 con Playwright y Pillow** — solo para las pruebas y las imágenes.
- **Google Chrome** — las pruebas usan el que ya está instalado, no descargan otro.

---

## 4. Abrirlo localmente

**Opción rápida:** doble clic en `docs/index.html`. Todas las rutas son
relativas, así que el sitio funciona incluso abierto como archivo.

**Opción recomendada** (idéntica a producción, con URLs limpias):

```bash
cd "…/Pagina Jorge Luis/web_jorgeluis/docs"
python3 -m http.server 8000
```

Y abrir http://localhost:8000

Se para con `Ctrl+C`.

---

## 5. Cómo agregar una nueva nota

### Paso 1 — Crear el archivo

Copiar `content/articulos/narino-paz-territorial-homicidios-coca.md` como
plantilla, o empezar de cero con esta cabecera:

```markdown
---
titulo: El título de la nota, tal como se verá
slug: el-titulo-de-la-nota
fecha: 2026-09-15
autor: Jorge Luis Congacha
categoria: Elecciones
temas: [Nariño, Elecciones, Datos]
bajada: Dos o tres líneas que resumen la nota. Se ven en la portada y bajo el título.
descripcion: Frase de ~155 caracteres para Google y para la tarjeta de X.
imagen: assets/img/graficos/mi-grafico-principal.png
pieDestacado: Figura 1. Lo que muestra el gráfico de portada.
imagenSocial: assets/img/social/el-titulo-de-la-nota.png
pdf: assets/documentos/el-titulo-de-la-nota.pdf
destacado: true
fuentes: ["DANE. Qué dato se tomó de ahí.", "Registraduría. Qué dato se tomó de ahí."]
---

El primer párrafo se muestra más grande: es la entrada de la nota.

Después, párrafos normales separados por una línea en blanco.

## Un subtítulo

Más texto. Se pueden usar **negritas**, *cursivas* y [enlaces](https://ejemplo.com).

> Una frase destacada, si hace falta.
```

Campos: `destacado: true` marca cuál es la nota grande de la portada
(solo una); `pdf` es opcional; `fuentes` es opcional pero recomendable.
`temas` genera solas las páginas de tema — no hay que crear nada más.

### Paso 2 — Escribir el cuerpo

Marcas disponibles:

| Se escribe | Sale |
|---|---|
| `## Texto` | Subtítulo con filete azul |
| `### Texto` | Subtítulo menor |
| `**texto**` | Negrita |
| `*texto*` | Cursiva |
| `[texto](url)` | Enlace |
| `> texto` | Frase destacada |
| `- item` | Lista |
| `1. item` | Lista numerada |
| Una línea que empiece con `<` | HTML tal cual |

### Paso 3 — Insertar un gráfico

```
:::figura src=assets/img/graficos/mi-grafico.png
alt: Descripción de lo que muestra el gráfico, para quien no puede verlo.
pie: Figura 1. Título del gráfico.
fuente: DANE. Elaboración propia.
nota: Alguna advertencia metodológica, si aplica.
:::
```

`alt` y `pie` son distintos a propósito: `alt` describe la imagen para lectores
de pantalla, `pie` es el texto visible debajo. `fuente` y `nota` son opcionales
y se imprimen precedidos de «Fuente:» y «Nota:».

Los gráficos se salen del ancho del texto en pantallas grandes y ocupan el
100 % en móvil.

### Paso 4 — Generar y revisar

```bash
node scripts/build.js
python3 scripts/probar.py     # opcional pero recomendable
```

### Paso 5 — Publicar

```bash
git add -A && git commit -m "Nueva nota: ..." && git push
```

En 1–2 minutos está en línea.

---

## 6. Cómo agregar imágenes y gráficos

Las imágenes de la web van en `docs/assets/img/graficos/`.

**Si vienen de un `.docx`** (como la primera nota), `scripts/extraer_graficos.py`
las saca sin recomprimir, las redimensiona a 1600 px y genera el WebP.
Hay que ajustar la lista `NOMBRES` del script al documento nuevo.

**Si son sueltas**, conviene:

1. Guardar el original en `originales/`.
2. Generar la versión web (1600 px de ancho es suficiente para pantallas 2x):

```bash
python3 -c "
from PIL import Image
im = Image.open('originales/mi-grafico.png').convert('RGB')
if im.width > 1600:
    im = im.resize((1600, round(im.height*1600/im.width)), Image.LANCZOS)
im.save('docs/assets/img/graficos/mi-grafico.png', optimize=True)
im.save('docs/assets/img/graficos/mi-grafico.webp', quality=92, method=6)
"
```

El build detecta solo si existe el `.webp` y arma el `<picture>` correspondiente.
En el `.md` siempre se referencia el `.png`.

**Regla:** revisar que los números y las etiquetas del gráfico se lean en el
móvil. Un gráfico con letra de 8 px en el original se vuelve ilegible.

### Tarjeta para compartir en X

```bash
python3 scripts/generar_imagenes.py
```

Lee los metadatos de cada nota y compone una tarjeta 1200×630 con el titular y
el gráfico principal. Se guarda en `docs/assets/img/social/<slug>.png`.

---

## 7. Cómo actualizar el CV

1. Reemplazar `originales/CV - Jorge Luis Congacha.pdf` por el nuevo.
2. `python3 scripts/preparar_documentos.py`

El script genera `docs/assets/documentos/cv-jorge-luis-congacha.pdf` **borrando
el número de teléfono** (redacción real: los glifos se eliminan del PDF, no se
tapan con un rectángulo) y limpiando los metadatos. Después verifica que el
número ya no sea extraíble y falla si lo sigue siendo.

3. Actualizar a mano `content/paginas/sobre-mi.md` si cambió la trayectoria.
4. `node scripts/build.js`

---

## 8. Cómo probar los cambios

```bash
python3 scripts/probar.py
```

Levanta un servidor local y recorre todas las páginas con Chrome en
**1440, 1280, 768, 390 y 375 px**, comprobando:

- desbordamiento horizontal (el problema clásico en móvil);
- que todas las imágenes carguen de verdad;
- recursos 404 y errores de consola;
- un solo `<h1>` por página;
- enlaces internos rotos;
- que no quede ninguna ruta local (`/Users/…`, `file://`) ni URL de ejemplo;
- metaetiquetas sociales completas;
- texto por debajo de 12 px y áreas táctiles menores de 40 px.

Deja una captura de cada página y cada ancho en `pruebas/capturas/`
(30 imágenes). Devuelve código de salida 1 si algo falla.

---

## 9. Cómo publicar

El repositorio ya existe, el remoto ya está configurado y GitHub Pages ya está
activo sirviendo `/docs`. **No hay que volver a configurar nada.**

### Una sola vez: dejar la sesión de GitHub guardada

El despliegue inicial se hizo con un token temporal que **no se guardó** en el
equipo. Para no tener que autenticarse en cada publicación, ejecuta una vez:

```bash
gh auth login
```

Responde: `GitHub.com` → `HTTPS` → `Y` (autenticar Git) → `Login with a web
browser`, y pega el código que aparece. Queda guardado en el llavero de macOS.

`gh` ya está instalado (es gratuito y de código abierto). Si algún día no lo
estuviera: `brew install gh`.

### Después, cada cambio

```bash
node scripts/build.js
git add -A
git commit -m "Descripción del cambio"
git push
```

O, si prefieres que además compruebe que no se publique nada indebido:

```bash
bash scripts/publicar.sh "Descripción del cambio"
```

GitHub Pages reconstruye solo. Tarda entre 30 segundos y 2 minutos.
El estado del despliegue se ve en la pestaña **Actions** del repositorio.

---

## 10. Hosting

**GitHub Pages**, sirviendo la carpeta `/docs` de la rama `main` del
repositorio `jorgelc07/jorgelc07.github.io`. Ya configurado y funcionando,
con HTTPS forzado.

- Gratis mientras el repositorio sea público. Sin límite de tiempo.
- HTTPS con certificado automático.
- Límites del plan gratuito: 1 GB de repositorio y 100 GB de tráfico al mes.
  Este sitio pesa ~5 MB; con el tráfico previsto no se acerca ni de lejos.
- **Nunca pide medio de pago.**

### Si algún día hace falta cambiar

El sitio es HTML estático, así que se mueve a cualquier parte sin tocar código:

- **Cloudflare Pages** (gratis): conectar el repositorio, dejar vacío el comando
  de build y poner `docs` como directorio de salida.
- **Netlify** (gratis): igual.
- **Dominio propio:** cuando exista, cambiar `url` en `content/sitio.json`,
  reconstruir, y añadir el dominio en Ajustes → Pages. *Comprar el dominio sí
  cuesta dinero; el hosting seguiría siendo gratis.*

---

## 11. Decisiones de diseño

Referencia estudiada: la jerarquía editorial de Página 10 (antetítulo → titular
→ bajada → firma → cuerpo con gráficos). **No se copió su código ni su diseño**;
la identidad es propia.

- **Cabecera tipo masthead**, no barra de navegación de portafolio: el nombre
  grande y centrado, el lema debajo, un filete y la navegación. La idea es que
  se lea como una publicación, no como el CV en línea de alguien.
- **Columna de texto de 36rem** (~68 caracteres). Los gráficos se salen a 54rem
  en pantallas grandes: composición editorial, no una columna uniforme.
- **Los gráficos van sobre placa blanca con filete** porque los PNG traen fondo
  blanco opaco. Sobre el papel cálido se leen como láminas impresas.
- **Sin tarjetas redondeadas, sin sombras, sin degradados, sin animaciones.**
  La jerarquía la hacen el filete, el espacio, el tamaño y el contraste
  serif/sans.
- **Cero JavaScript.** No hay menú hamburguesa: cuatro enlaces cortos caben en
  una fila hasta en 375 px. Menos código, menos que se rompa.

El razonamiento completo está en `docs-proyecto/decisiones.md`.

---

## 12. Colores y tipografías

### Paleta

| Variable CSS | Valor | Uso |
|---|---|---|
| `--azul` | `#1B3B6F` | Cabecera, titulares, filetes, enlaces |
| `--azul-profundo` | `#122C55` | Hover, fondo del pie de página |
| `--papel` | `#FBF8F3` | Fondo general |
| `--papel-sombra` | `#F2ECE2` | Bloques secundarios |
| `--tinta` | `#1B1A18` | Texto de lectura |
| `--gris-tinta` | `#5E5951` | Metadatos y pies de figura |
| `--filete` | `#DDD5C8` | Líneas |

Azul de familia institucional (Johns Hopkins / Yale) pero con valor propio:
azul de verdad, no negro azulado. El fondo nunca es blanco puro.

Contraste medido (WCAG): tinta sobre papel **16,42:1**; azul sobre papel
**10,42:1**; papel sobre azul profundo **13,07:1**; gris tinta sobre papel
**6,56:1**. Todos superan el mínimo AA (4,5:1); los dos grises de metadatos
quedan algo por debajo de AAA (7:1), que es un objetivo, no un requisito.

### Tipografías

- **Source Serif 4** — titulares y cuerpo.
- **Inter** — navegación, metadatos, pies de figura, botones.

Ambas con licencia SIL Open Font License 1.1. Auto-alojadas en
`docs/assets/fuentes/` (subconjuntos latin y latin-ext, ~166 KB en la carga
típica). Para regenerarlas: `python3 scripts/descargar_fuentes.py`.

---

## 13. Advertencias importantes

1. **No editar nada dentro de `docs/*.html`.** Se regenera. Editar `content/`.

2. **`originales/` no se toca.** Es la copia de seguridad de los archivos de
   partida. El CV que hay ahí **tiene el teléfono** y por eso no se publica: lo
   que se publica es la copia redactada que produce `scripts/preparar_documentos.py`.

3. **Al cambiar la URL del sitio** hay que editar `url` en `content/sitio.json`
   y reconstruir. Si no, las URLs canónicas, el sitemap y las tarjetas de X
   apuntarán al sitio equivocado.

4. **Rutas siempre relativas.** El generador las calcula según la profundidad de
   cada página. Si alguna vez se escribe una ruta absoluta a mano, el sitio se
   rompe al publicarse en una subcarpeta. `scripts/probar.py` lo detecta.

5. **La carpeta está dentro de OneDrive.** OneDrive puede descargar archivos
   bajo demanda y eso ha dado problemas en procesos largos. Si un script falla
   con `PermissionError`, abrir la carpeta en Finder para forzar la
   sincronización y volver a intentar.

6. **Antes de publicar contenido nuevo, revisar que no lleve datos privados.**
   El repositorio es público: todo lo que entre en `docs/` es visible para
   cualquiera, y los buscadores lo indexan.

7. **No hace falta pagar nada, nunca.** Si algún servicio pide tarjeta, plan de
   pago o prueba gratuita para publicar este sitio, es señal de que algo está
   mal configurado: GitHub Pages sobre repositorio público no lo requiere.

---

## 14. Sobre la primera nota

Procede de `narino_paz_territorial_coca_otros copy.docx` (versión 10, 11
figuras). El texto se transcribió **íntegro, sin modificar ni resumir**.

Lo único que se añadió a la estructura del documento es el subtítulo
**«Tres conclusiones»**, tomado literalmente de la frase que abre esa sección
(«Los datos disponibles permiten extraer, al menos, tres conclusiones»). Los
otros dos subtítulos, «La coca en Nariño» y «Otros datos de Nariño», ya
estaban en el original.

Los 11 gráficos se extrajeron del propio `.docx`, donde están sin recomprimir.
Se verificó por checksum que 10 de ellos son idénticos a los de
`graficos_v9_finales/`; el undécimo (Figura 4, tasa por grupo territorial) solo
existe dentro del documento, porque se incorporó después de la versión 9.

Los pies de figura y las notas de fuente están transcritos del propio documento
y de los pies impresos dentro de cada gráfico. No se inventó ninguna cifra,
fuente ni afirmación.
