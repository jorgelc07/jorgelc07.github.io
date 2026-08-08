# Plan del sitio — Jorge Luis Congacha

Documento escrito **antes** de programar (Fase 2). Refleja las decisiones tomadas
después de auditar los materiales de origen. El registro razonado de cada decisión
está en `decisiones.md`.

---

## 1. Qué es este sitio

Una publicación personal de análisis basado en datos: notas propias sobre política,
elecciones, economía, conflicto, desarrollo territorial y Nariño/Colombia. El caso de
uso central es un lector que llega desde un hilo en X y quiere leer la nota completa
con sus gráficos y fuentes.

Consecuencias de diseño que se derivan de ahí:

- La **nota** es la unidad del sitio, no el portafolio ni el CV.
- Debe verse bien compartida en X (Open Graph / Twitter Card correctos).
- Mobile es el escenario principal de lectura, no el secundario.
- Tiene que aguantar crecer a decenas de notas sin rehacer nada.

## 2. Arquitectura

**Sitio estático generado por un script propio de Node, sin dependencias externas.**

```
content/articulos/*.md   →   node scripts/build.js   →   docs/**/*.html
```

- Cada nota es **un archivo Markdown** con metadatos al inicio (front matter).
- `scripts/build.js` (Node puro, cero paquetes de npm) convierte ese Markdown en
  HTML y lo envuelve en la maqueta del sitio. También genera portada, listado,
  páginas de tema, `sitemap.xml`, `feed.xml` y `robots.txt`.
- La salida (`docs/`) es HTML plano. **No hay JavaScript necesario para leer**: el JS
  del sitio solo maneja el menú móvil y el progreso de lectura.

### Por qué así y no de otra forma

| Alternativa | Por qué se descartó |
|---|---|
| HTML a mano, sin build | Cada nota nueva obligaría a editar portada, listado, sitemap y feed a mano. Se rompe al tercer artículo. |
| Astro / Eleventy / Hugo | Resuelven el problema, pero traen `node_modules`, actualizaciones, breaking changes y un `package.json` que hay que mantener. Para una publicación de una persona es mantenimiento sin retorno. |
| WordPress | Costo, base de datos, superficie de ataque, actualizaciones. Descartado por el encargo. |
| Listado renderizado con JS en el cliente | Rompe el SEO y las tarjetas de previsualización de X. |

El build es **un archivo de ~500 líneas que se puede leer entero en 15 minutos**. Si en
cinco años Node cambia, el HTML de `docs/` sigue funcionando igual: está commiteado.

### Regla clave: rutas relativas

Todo enlace y recurso del sitio usa rutas **relativas** calculadas por el generador
según la profundidad de cada página (`../../assets/css/estilo.css`). Esto hace que el
sitio funcione idéntico:

- abierto con doble clic (`file://`),
- en un servidor local,
- en `usuario.github.io/repo/` (subcarpeta),
- y en un dominio propio el día que exista.

Y garantiza que **ninguna ruta local del computador quede en el HTML publicado**.

## 3. Hosting

**GitHub Pages**, sirviendo la carpeta `/docs` de la rama `main`.

- Gratis y sin límite de tiempo para repositorios públicos.
- HTTPS automático.
- El despliegue es `git push`: no hay panel, ni build remoto, ni Action que se rompa.
- Publicar desde `/docs` mantiene separado el código fuente del sitio publicado.
- Cloudflare Pages queda como plan B documentado (mismo repo, sin build command,
  directorio de salida `docs`). Migrar no cuesta nada porque la salida es estática.

## 4. Identidad visual

Referencia conceptual: prensa y revistas de análisis. Se estudió la jerarquía
editorial de Página 10 (antetítulo → titular → bajada → firma → cuerpo con gráficos a
ancho de columna) **sin copiar su código ni su diseño**. La identidad propia se
construye con:

### Color

| Rol | Valor | Uso |
|---|---|---|
| Azul editorial | `#1B3B6F` | Cabecera, titulares, filetes, enlaces |
| Azul profundo | `#122C55` | Estados hover, franja superior |
| Papel | `#FBF8F3` | Fondo general (no blanco puro) |
| Papel sombra | `#F2ECE2` | Bloques secundarios |
| Tinta | `#1B1A18` | Texto de lectura |
| Gris tinta | `#5E5951` | Metadatos, pies de figura |
| Filete | `#DDD5C8` | Líneas y separaciones |

Azul profundo de familia institucional (Johns Hopkins / Yale) pero con valor propio:
suficientemente azul para no leerse como negro, suficientemente oscuro para sostener
una cabecera. Sobre papel cálido da la sensación de impreso.

Los gráficos vienen sobre fondo blanco opaco, así que se presentan sobre una **placa
blanca con filete**: se lee como una lámina impresa, no como un parche.

### Tipografía

- **Source Serif 4** — titulares y cuerpo. Diseñada para lectura larga en pantalla.
- **Inter** — navegación, metadatos, pies de figura, botones.

Ambas se descargan una vez y se **auto-alojan** (`docs/assets/fuentes/`). Sin peticiones
a Google en cada visita: más rápido, más privado, sin dependencia de terceros.

### Lo que se evita deliberadamente

Tarjetas redondeadas flotantes, sombras, degradados, animaciones de entrada, iconos
decorativos, "hero" de portafolio. La jerarquía la hacen el filete, el espacio en
blanco, el tamaño y el contraste serif/sans.

## 5. Estructura del sitio

```
/                                  Portada: masthead, destacado, notas recientes, temas, perfil
/analisis/                         Listado completo de notas
/articulos/<slug>/                 Nota individual
/temas/<slug>/                     Notas por tema (se generan solas según los temas usados)
/sobre-mi/                         Perfil editorial + botón de CV
/assets/documentos/                CV en PDF y PDF de cada nota
404.html, sitemap.xml, feed.xml, robots.txt
```

## 6. Cómo se incorpora la primera nota

Fuente: `narino_paz_territorial_coca_otros copy.docx` (v10, 11 figuras) y su PDF.

1. El texto se transcribe **íntegro y sin alterar** a
   `content/articulos/narino-paz-territorial-homicidios-coca.md`. No se agrega ni se
   quita contenido; solo se estructuran subtítulos que ya existen en el documento
   ("La coca en Nariño", "Otros datos de Nariño") y se marcan como `##`.
2. La bajada de la nota se compone **con frases del propio artículo**, no con texto
   nuevo.
3. Los 11 gráficos se extraen del `.docx` (`scripts/extraer_graficos.py`), donde están
   los originales sin recomprimir. Se verificó por checksum que 10 de ellos son
   idénticos a los de `graficos_v9_finales/`; el undécimo (Figura 4, tasa por grupo
   territorial) solo existe dentro del documento porque se agregó después de la v9.
4. Cada figura se sirve como WebP con respaldo PNG a 1600 px, con su pie y su nota de
   fuente **transcritos del propio gráfico**.
5. La página incluye un botón "Descargar la versión en PDF" apuntando a una copia del
   PDF dentro del sitio.
6. Al final, una sección "Fuentes de los datos" que solo enumera las fuentes que
   aparecen citadas en el texto o al pie de los gráficos.

No se inventa ninguna cifra, fuente, enlace ni afirmación que no esté en el documento.

## 7. Perfil y CV

`sobre-mi/` se redacta a partir del CV, en tono editorial y en tercera persona breve.
Se publica: formación, experiencia como asistente de investigación, áreas de trabajo,
herramientas, correo institucional y X. **No se publica** el teléfono ni ningún otro
dato de contacto personal que aparezca en el PDF del CV.

El CV completo se ofrece como descarga. Advertencia registrada en el README: el PDF sí
contiene el teléfono, así que la decisión de publicarlo es del autor.

## 8. Compartir y SEO

Cada página lleva `title`, `description`, `canonical`, Open Graph y `summary_large_image`
de Twitter, generados desde el front matter. La imagen social de la nota (1200×630) se
compone dentro del proyecto a partir de uno de sus propios gráficos.

`canonical`, `og:url` y `sitemap.xml` se construyen a partir de un único valor
`sitio.url` en `content/sitio.json`: cambiar de URL (o poner un dominio propio) es
editar una línea y reconstruir.

## 9. Pruebas

Playwright (ya instalado) contra un servidor local, en 1440 / 1280 / 768 / 390 / 375 px:
capturas de todas las páginas, detección de desbordamiento horizontal, verificación de
que ningún enlace interno esté roto, que ninguna imagen falle y que no quede ninguna
ruta `file://` ni `/Users/` en el HTML publicado. Mínimo dos pasadas completas.

## 10. Agregar la próxima nota

1. Escribir `content/articulos/mi-nota.md` con el front matter.
2. Poner los gráficos en `docs/assets/img/graficos/`.
3. `node scripts/build.js`
4. `git commit && git push`

Portada, listado, temas, sitemap y feed se actualizan solos.
