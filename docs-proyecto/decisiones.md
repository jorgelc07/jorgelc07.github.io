# Registro de decisiones

Por qué el proyecto quedó como quedó. Escrito para que, dentro de un año, se
entienda el razonamiento antes de cambiar algo.

---

## 1. Generador propio en vez de Astro, Eleventy o Hugo

**Decisión:** `scripts/build.js`, ~550 líneas de Node sin ninguna dependencia
de npm.

**Alternativas consideradas:**

- *HTML a mano, sin build.* Se descartó porque cada nota nueva obligaría a
  editar a mano la portada, el listado, las páginas de tema, el sitemap y el
  feed. Con tres artículos ya sería insostenible y se empezarían a acumular
  incoherencias.
- *Astro / Eleventy / Hugo.* Resuelven bien el problema, pero traen
  `node_modules`, versiones que se rompen, avisos de seguridad de dependencias
  transitivas y un `package.json` que mantener. Para una publicación de una
  sola persona con pocas notas al año, eso es mantenimiento sin retorno: el
  riesgo real no es que el sitio sea poco moderno, es que en dos años no
  compile.
- *Renderizar el listado con JavaScript desde un JSON.* Descartado: rompe el
  SEO y, sobre todo, rompe las tarjetas de previsualización de X, que es
  justamente el canal por el que va a llegar la gente.

**Criterio que decidió:** el sitio tiene que poder reconstruirse dentro de
cinco años sin arqueología. Cero dependencias significa que solo puede fallar
Node, y aun así el HTML de `docs/` ya está generado y commiteado.

---

## 2. Hosting: GitHub Pages

**Decisión:** GitHub Pages sirviendo `/docs` de la rama `main`.

**Por qué:**

- Gratuito de forma permanente en repositorios públicos, sin pedir tarjeta.
- HTTPS automático.
- El despliegue es `git push`. No hay panel de control ni un pipeline que se
  rompa por su cuenta.
- El control de versiones y el hosting son la misma cosa: no hay estado que se
  desincronice.

**Cloudflare Pages** quedó como plan B. Es igual de gratuito y algo más rápido
en la red de distribución, pero añade una cuenta más y un panel más. Migrar es
trivial (salida estática, sin comando de build), así que no hay coste en
elegir GitHub primero.

**Se descartó WordPress** por costo, base de datos, superficie de ataque y
actualizaciones constantes; y cualquier VPS por lo mismo más la factura.

**Por qué `/docs` y no la raíz:** publicar desde `/docs` mantiene separado el
código fuente (`content/`, `scripts/`) del sitio publicado. La alternativa
—generar en la raíz— mezcla ambas cosas y hace difícil ver qué se edita y qué
se genera. El coste es un clic más al configurar Pages, una sola vez.

---

## 3. Repositorio `jorgelc07.github.io` en vez de un repo con nombre

**Decisión:** repositorio especial de usuario, que sirve en la raíz del dominio.

Da la URL más corta (`jorgelc07.github.io`), que es la que se va a pegar al
final de cada hilo en X. Una URL con subcarpeta se ve más larga y más frágil.
Solo se puede tener un repositorio así por cuenta, pero este sitio es
precisamente el que merece ese lugar.

---

## 4. Rutas relativas en todo el sitio

**Decisión:** el generador calcula el prefijo (`../`, `../../`) según la
profundidad de cada página. No hay ni una ruta absoluta en el HTML, salvo en
`404.html`.

**Por qué:** hace que el mismo HTML funcione abierto con doble clic
(`file://`), en un servidor local, en `usuario.github.io/` y en un dominio
propio el día que exista. Y hace estructuralmente imposible que se filtre una
ruta local del computador al sitio publicado, que era un requisito explícito.

**La excepción del 404:** GitHub Pages sirve `404.html` desde cualquier ruta
inexistente, incluida `/una/ruta/muy/profunda/`. Con rutas relativas, los
estilos y enlaces de esa página apuntarían a sitios distintos según desde
dónde se llegue. Por eso `404.html` lleva sus estilos en línea y enlaces
absolutos: es la única página que no puede ser relativa.

---

## 5. Cero JavaScript

**Decisión:** el sitio no carga ni un byte de JS.

Se consideraron un menú hamburguesa, una barra de progreso de lectura y una
ampliación de gráficos al hacer clic. Se descartaron los tres:

- El menú son cuatro enlaces cortos que caben en una fila hasta en 375 px.
  Un hamburguesa habría añadido estado, foco que gestionar, atributos ARIA y
  una forma más de que algo falle, a cambio de nada.
- La barra de progreso es decoración.
- La ampliación de gráficos la resuelve el navegador: los gráficos están a
  1600 px, y en móvil se abren en pestaña nueva o con zoom nativo.

**Consecuencia:** el sitio funciona con JS desactivado, carga instantáneamente
y no tiene nada que se pueda romper con una actualización del navegador.

---

## 6. Contenido: Markdown con metadatos

**Decisión:** una nota es un archivo `.md` con un bloque de metadatos al
inicio, y un bloque `:::figura` para los gráficos.

Se evaluó usar HTML directamente (más control, pero incómodo de escribir) y
Markdown completo con una librería (una dependencia más). El subconjunto
implementado —encabezados, párrafos, listas, negrita, cursiva, enlaces, cita
destacada, HTML crudo cuando haga falta— cubre lo que una nota de análisis
necesita.

**El bloque `:::figura` es la pieza clave.** Una figura de análisis tiene
cuatro cosas distintas que no se pueden confundir:

```
:::figura src=…
alt:    lo que se le describe a quien no ve la imagen
pie:    el texto visible debajo ("Figura 3. …")
fuente: de dónde salen los datos
nota:   la advertencia metodológica
:::
```

La sintaxis estándar de Markdown para imágenes (`![alt](src "título")`) solo
tiene dos huecos y obligaría a mezclar `alt` con `pie`, que es un error de
accesibilidad frecuente y además pierde la fuente. En una publicación cuyo
argumento es «acá están los datos y sus fuentes», eso no era negociable.

---

## 7. Paleta y sensación de papel

**Decisión:** azul `#1B3B6F` sobre papel `#FBF8F3`.

El azul es de la familia institucional pedida (Johns Hopkins, Yale) pero con
valor propio, no una copia de un color de marca. Se ajustó para que siga
leyéndose como azul y no como negro azulado: a partir de aproximadamente
`#0D2340` el ojo lo interpreta como negro y se pierde la identidad.

El fondo no es blanco puro. `#FBF8F3` tiene la calidez justa para sugerir papel
sin volverse sepia ni parecer un error de calibración de pantalla.

**El problema de los gráficos:** los 11 PNG vienen con fondo blanco opaco
(`#FFFFFF`), no transparente. Sobre papel cálido, un rectángulo blanco a sangre
se ve como una mancha. La solución fue convertirlo en decisión de diseño:
cada gráfico va sobre una placa blanca con filete, que se lee como una lámina
impresa pegada sobre la página. Si en el futuro se generan gráficos con fondo
transparente o con el color de papel, habría que quitar ese filete.

**Contraste medido:** tinta/papel 16,42:1 · azul/papel 10,42:1 · papel/azul
profundo 13,07:1 · gris tinta/papel 6,56:1. Todos superan el mínimo AA de
4,5:1. Los grises de metadatos y pies de figura quedan en torno a 6,6–7,0:1,
por debajo de AAA; se aceptó porque son texto secundario y subirlos más
apagaría la jerarquía entre cuerpo y metadatos.

---

## 8. Tipografía

**Decisión:** Source Serif 4 para titulares y cuerpo; Inter para interfaz.

Source Serif está diseñada específicamente para lectura larga en pantalla, que
es exactamente el caso: notas de 2.000 palabras con gráficos. Se descartaron
Playfair Display (demasiado de revista de moda para un texto sobre conflicto
armado) y Lora (correcta pero menos definida en tamaños pequeños).

Usar el mismo serif en titular y cuerpo da unidad de publicación; el contraste
lo aporta Inter en navegación, metadatos y pies de figura, que es donde el
lector necesita distinguir «esto es contenido» de «esto es señalización».

**Auto-alojadas y no desde Google Fonts.** Evita una conexión a un tercero en
cada visita, elimina un punto de fallo externo, mejora la privacidad de quien
lee y hace el sitio más rápido. Solo se conservan los subconjuntos latin y
latin-ext: unos 166 KB en la carga típica en español.

---

## 9. Composición y responsive

**Decisión:** columna de texto de 36rem; los gráficos se salen a 54rem.

36rem son unos 68 caracteres por línea, dentro del rango cómodo (55–75) para
texto largo. Si el cuerpo y los gráficos compartieran ancho, los gráficos
quedarían apretados y el conjunto se vería como un blog; si todo fuera ancho,
el texto sería incómodo de leer.

Se implementa con una rejilla CSS de columnas nombradas: el texto ocupa la
columna central y las figuras se extienden a los bordes.

> **Trampa encontrada durante las pruebas:** los nombres de línea de la rejilla
> deben terminar en `-start` y `-end` en inglés. Se escribieron primero como
> `texto-inicio` / `texto-fin` y la forma corta `grid-column: texto` dejó de
> funcionar en silencio: el navegador creaba columnas implícitas y el texto se
> salía 150 px de la pantalla en móvil. No daba error en ninguna parte; solo lo
> detectó la prueba de desbordamiento horizontal.

**Puntos de quiebre:** 34em (la reseña pasa a miniatura + texto), 48em (el
destacado pasa a dos columnas y crecen los márgenes) y 62em (ajustes de aire).
Están puestos donde el contenido lo pedía, no en anchos de dispositivos
concretos, que cambian cada año.

---

## 10. Imágenes

**Decisión:** WebP con respaldo PNG, ambos a 1600 px de ancho.

Los originales están entre 1.800 y 3.000 px y suman 3,0 MB. A 1600 px siguen
viéndose nítidos en pantallas de alta densidad (la columna ancha son 864 px
CSS, así que 1600 px cubre 2x de sobra) y el conjunto baja a 823 KB en WebP:
casi cuatro veces menos, sin pérdida visible en los números y etiquetas de los
gráficos, que era el riesgo real.

Los originales sin tocar quedan en `originales/graficos_nota/`.

`width` y `height` van explícitos en cada `<img>` (el generador los lee de la
cabecera del PNG) para que el navegador reserve el espacio y la página no dé
saltos mientras carga. Todas las figuras salvo la primera son `loading="lazy"`.

---

## 11. SEO y compartir en X

**Decisión:** metaetiquetas generadas desde los metadatos de cada nota;
tarjeta social compuesta dentro del proyecto.

Cada página lleva `title`, `description`, `canonical`, Open Graph completo y
`twitter:card=summary_large_image`. La tarjeta 1200×630 se compone con el
titular a la izquierda y el gráfico principal de la nota a la derecha: al
compartir en X se ve de qué trata y que hay datos detrás, sin abrir el enlace.

**Detalle deliberado:** el `<title>` de la pestaña es «Nota · Jorge Luis
Congacha», pero `og:title` lleva solo el titular. En la tarjeta de X el nombre
del sitio ya aparece por `og:site_name`, y repetirlo consume caracteres del
titular, que es lo que hace clicar.

Todas las URLs absolutas (canonical, og:url, sitemap, feed) se derivan de un
único valor `url` en `content/sitio.json`. Cambiar de dirección o poner un
dominio propio es editar una línea y reconstruir.

---

## 12. Privacidad: el CV

**Decisión:** se publica una copia del CV sin el número de teléfono.

El PDF original lo incluye. Publicarlo en un repositorio público lo deja
accesible a cualquiera y a los rastreadores automáticos que recogen datos de
contacto. La página «Sobre mí» publica solo el correo institucional y la cuenta
de X, que ya son públicos.

**Cómo se hace:** `scripts/preparar_documentos.py` usa redacción real de PyMuPDF, que
elimina los glifos del contenido del PDF. No es un rectángulo blanco encima
—ese truco deja el texto extraíble con copiar y pegar— y el script lo verifica
después: vuelve a extraer el texto del PDF publicado y falla si el número
sigue ahí. También limpia los metadatos del archivo, que suelen delatar rutas
locales y el software usado.

El original queda intacto en `originales/`.

---

## 13. Pruebas

**Decisión:** `scripts/probar.py`, con Playwright sobre el Chrome ya instalado.

Se usa `channel="chrome"` en vez del Chromium que descarga Playwright: evita
bajar 150 MB y prueba contra el navegador real.

Lo que se comprueba está elegido por lo que de verdad se rompe en un sitio así:
desbordamiento horizontal en móvil, imágenes que no cargan, enlaces internos
rotos, rutas locales filtradas, metaetiquetas incompletas, texto diminuto y
áreas táctiles pequeñas. No se comprueban cosas que no van a cambiar solas.

> **Dos falsos negativos que costaron tiempo,** anotados para no repetirlos:
> el servidor de pruebas era de un solo hilo y encolaba las peticiones, con lo
> que las imágenes parecían rotas cuando solo esperaban turno; y el recorrido
> automático de la página usaba `scrollTo` normal, que con el `scroll-behavior:
> smooth` del sitio anima el desplazamiento y nunca llegaba abajo, así que las
> imágenes diferidas no se disparaban. Ambas cosas hacían fallar la prueba con
> el sitio correcto.

---

## 14. Cómo escalar cuando haya más artículos

Lo que ya funciona sin tocar nada:

- **Notas.** Un `.md` más en `content/articulos/`. Portada, listado, temas,
  sitemap y feed se rehacen solos. La portada muestra el destacado y hasta seis
  notas recientes; el listado, todas.
- **Temas.** Se crean solos a partir del campo `temas` de cada nota. No hay una
  lista que mantener: un tema existe si alguna nota lo usa.

Lo que habrá que hacer llegado el momento:

- **Más de ~30 notas:** paginar el listado. El generador ya ordena por fecha;
  faltaría cortar en páginas de 20.
- **Más de ~50 notas:** un buscador. Con el sitio estático, la opción sensata
  es generar un índice JSON en el build y filtrarlo en el cliente. Sería la
  primera vez que haga falta JavaScript, y solo en esa página.
- **Series o especiales:** hoy se resuelven con un tema. Si alguna vez hacen
  falta portadas propias por serie, el generador de páginas de tema es el sitio
  natural donde añadirlo.

Lo que conviene **no** hacer: migrar a un framework porque el sitio creció. Con
200 notas esto sigue generándose en menos de un segundo.
