#!/usr/bin/env node
/*
 * Generador del sitio de Jorge Luis Congacha.
 *
 *   content/sitio.json        configuración global (URL, nombre, navegación)
 *   content/articulos/*.md    una nota por archivo, con metadatos al inicio
 *   content/paginas/*.md      páginas fijas (sobre mí)
 *          ↓   node scripts/build.js
 *   docs/                     el sitio publicable, HTML plano
 *
 * Node puro, sin dependencias de npm. Se puede leer entero.
 * Uso:  node scripts/build.js
 */

const fs = require('fs');
const path = require('path');

const RAIZ = path.dirname(__dirname);
const CONTENIDO = path.join(RAIZ, 'content');
const SALIDA = path.join(RAIZ, 'docs');

/* ------------------------------------------------------------------ utilidades */

const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
  'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];

function fechaLarga(iso) {
  const [a, m, d] = iso.split('-').map(Number);
  return `${d} de ${MESES[m - 1]} de ${a}`;
}

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function slugify(s) {
  return s.normalize('NFD').replace(/[̀-ͯ]/g, '')
    .toLowerCase().trim()
    .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

/** Ruta relativa desde una página a un recurso de la raíz del sitio. */
function rel(profundidad, destino) {
  const prefijo = profundidad === 0 ? '' : '../'.repeat(profundidad);
  return (prefijo + destino) || './';
}

/** Ancho y alto de un PNG, leyendo la cabecera IHDR (evita saltos de maqueta). */
function medidaPNG(archivo) {
  try {
    const b = fs.readFileSync(archivo).subarray(0, 33);
    if (b.readUInt32BE(0) !== 0x89504e47) return null;
    return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
  } catch { return null; }
}

function escribir(rutaRelativa, contenido) {
  const destino = path.join(SALIDA, rutaRelativa);
  fs.mkdirSync(path.dirname(destino), { recursive: true });
  fs.writeFileSync(destino, contenido);
}

/* --------------------------------------------------- front matter + markdown */

/** Metadatos entre --- al inicio del archivo. Subconjunto simple de YAML. */
function leerFrontMatter(texto) {
  const m = texto.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return { meta: {}, cuerpo: texto };
  const meta = {};
  for (const linea of m[1].split(/\r?\n/)) {
    const par = linea.match(/^([\w]+):\s*(.*)$/);
    if (!par) continue;
    let v = par[2].trim();
    if (v.startsWith('[') && v.endsWith(']')) {
      // Lista. Si viene con comillas es JSON válido y se respetan las comas
      // internas; si viene suelta (["a, b"] vs [a, b]) se separa por comas.
      try {
        v = JSON.parse(v);
      } catch {
        v = v.slice(1, -1).split(',').map(x => x.trim().replace(/^["']|["']$/g, ''))
          .filter(Boolean);
      }
    } else {
      v = v.replace(/^["']|["']$/g, '');
      if (v === 'true') v = true;
      else if (v === 'false') v = false;
    }
    meta[par[1]] = v;
  }
  return { meta, cuerpo: texto.slice(m[0].length) };
}

/** Marcas de línea: **negrita**, *cursiva*, [texto](url), `código`. */
function enLinea(s) {
  return esc(s)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[\s(])\*([^*\n]+)\*/g, '$1<em>$2</em>')
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, t, u) =>
      /^https?:/.test(u)
        ? `<a href="${u}" rel="noopener">${t}</a>`
        : `<a href="${u}">${t}</a>`);
}

/**
 * Markdown reducido, suficiente para notas:
 *   ## y ###          subtítulos
 *   párrafos          texto corrido
 *   - / 1.            listas
 *   >                 cita destacada
 *   :::figura ...:::  gráfico con pie y fuente
 *   líneas con <      HTML tal cual
 */
function markdown(texto, ctx) {
  const lineas = texto.split(/\r?\n/);
  const salida = [];
  let i = 0;
  let primerParrafo = true;

  const cerrarLista = (tipo) => salida.push(`</${tipo}>`);

  while (i < lineas.length) {
    const linea = lineas[i];

    if (!linea.trim()) { i++; continue; }

    // Bloque de figura
    if (linea.trim().startsWith(':::figura')) {
      const campos = {};
      const src = linea.match(/src=(\S+)/);
      if (src) campos.src = src[1];
      i++;
      while (i < lineas.length && !lineas[i].trim().startsWith(':::')) {
        const par = lineas[i].match(/^\s*(\w+):\s*(.*)$/);
        if (par) campos[par[1]] = par[2].trim();
        i++;
      }
      i++; // cierre :::
      salida.push(figura(campos, ctx));
      continue;
    }

    // HTML tal cual
    if (linea.trimStart().startsWith('<')) {
      const bloque = [];
      while (i < lineas.length && lineas[i].trim()) bloque.push(lineas[i++]);
      salida.push(bloque.join('\n'));
      continue;
    }

    // Subtítulos
    const enc = linea.match(/^(#{2,4})\s+(.*)$/);
    if (enc) {
      const n = enc[1].length;
      salida.push(`<h${n} id="${slugify(enc[2])}">${enLinea(enc[2])}</h${n}>`);
      i++;
      continue;
    }

    // Separador
    if (/^---+$/.test(linea.trim())) { salida.push('<hr>'); i++; continue; }

    // Cita destacada
    if (linea.trimStart().startsWith('>')) {
      const bloque = [];
      while (i < lineas.length && lineas[i].trimStart().startsWith('>')) {
        bloque.push(lineas[i].replace(/^\s*>\s?/, ''));
        i++;
      }
      salida.push(`<blockquote class="cita"><p>${enLinea(bloque.join(' '))}</p></blockquote>`);
      continue;
    }

    // Listas
    const vinneta = /^\s*[-*]\s+/;
    const numerada = /^\s*\d+\.\s+/;
    if (vinneta.test(linea) || numerada.test(linea)) {
      const ordenada = numerada.test(linea);
      const patron = ordenada ? numerada : vinneta;
      salida.push(ordenada ? '<ol>' : '<ul>');
      while (i < lineas.length && patron.test(lineas[i])) {
        salida.push(`<li>${enLinea(lineas[i].replace(patron, ''))}</li>`);
        i++;
      }
      cerrarLista(ordenada ? 'ol' : 'ul');
      continue;
    }

    // Párrafo (una o varias líneas seguidas)
    const bloque = [];
    while (i < lineas.length && lineas[i].trim()
      && !/^(#{2,4}\s|>|:::|---+$)/.test(lineas[i].trim())
      && !vinneta.test(lineas[i]) && !numerada.test(lineas[i])
      && !lineas[i].trimStart().startsWith('<')) {
      bloque.push(lineas[i].trim());
      i++;
    }
    const clase = primerParrafo ? ' class="entradilla"' : '';
    primerParrafo = false;
    salida.push(`<p${clase}>${enLinea(bloque.join(' '))}</p>`);
  }

  return salida.join('\n');
}

/** <figure> con WebP + respaldo PNG, medidas explícitas, pie y nota de fuente. */
function figura(c, ctx) {
  if (!c.src) return '';
  const png = c.src;
  const webp = png.replace(/\.png$/i, '.webp');
  const hayWebp = fs.existsSync(path.join(SALIDA, webp));
  const med = medidaPNG(path.join(SALIDA, png));
  const dims = med ? ` width="${med.w}" height="${med.h}"` : '';
  const carga = ctx.primeraFigura ? '' : ' loading="lazy"';
  ctx.primeraFigura = false;

  const fuente = c.fuente
    ? `<span class="figura__fuente">Fuente: ${enLinea(c.fuente)}</span>` : '';
  const nota = c.nota
    ? `<span class="figura__nota">Nota: ${enLinea(c.nota)}</span>` : '';

  return `<figure class="figura">
  <picture>
    ${hayWebp ? `<source srcset="${rel(ctx.profundidad, webp)}" type="image/webp">` : ''}
    <img src="${rel(ctx.profundidad, png)}" alt="${esc(c.alt || c.pie || '')}"${dims}${carga} decoding="async">
  </picture>
  <figcaption>
    <span class="figura__pie">${enLinea(c.pie || '')}</span>
    ${fuente}${nota}
  </figcaption>
</figure>`;
}

/* -------------------------------------------------------------------- maqueta */

function cabecera(sitio, p, pagina) {
  const enlaces = [
    ['Inicio', 'index.html'],
    ['Análisis', 'analisis/index.html'],
    ['Sobre mí', 'sobre-mi/index.html'],
  ];
  const items = enlaces.map(([texto, destino]) => {
    const activo = pagina === destino ? ' aria-current="page"' : '';
    return `<li><a href="${rel(p, destino)}"${activo}>${texto}</a></li>`;
  }).join('\n        ');

  return `<a class="saltar" href="#contenido">Saltar al contenido</a>
  <header class="masthead">
    <div class="contenedor">
      <p class="masthead__marca">
        <a href="${rel(p, 'index.html')}">${esc(sitio.nombre)}</a>
      </p>
      <p class="masthead__lema">${esc(sitio.lema)}</p>
      <nav class="menu" aria-label="Secciones">
        <ul>
        ${items}
        <li><a class="menu__cv" href="${rel(p, sitio.cv)}">CV<span class="menu__cv-largo"> (PDF)</span></a></li>
        </ul>
      </nav>
    </div>
  </header>`;
}

function pie(sitio, p) {
  return `<footer class="pie">
    <div class="contenedor">
      <p class="pie__marca">${esc(sitio.nombre)}</p>
      <p class="pie__lema">${esc(sitio.lema)}</p>
      <ul class="pie__enlaces">
        <li><a href="${rel(p, 'analisis/index.html')}">Análisis</a></li>
        <li><a href="${rel(p, 'sobre-mi/index.html')}">Sobre mí</a></li>
        <li><a href="${rel(p, sitio.cv)}">CV (PDF)</a></li>
        <li><a href="https://x.com/${sitio.x}" rel="me noopener">X · @${esc(sitio.x)}</a></li>
        <li><a href="mailto:${esc(sitio.correo)}">${esc(sitio.correo)}</a></li>
        <li><a href="${rel(p, 'feed.xml')}">RSS</a></li>
      </ul>
      <p class="pie__legal">© ${new Date().getFullYear()} ${esc(sitio.autor)}. Los textos y gráficos son de elaboración propia salvo indicación en contrario; las fuentes de los datos se citan en cada nota.</p>
    </div>
  </footer>`;
}

/** Documento completo. `pagina` es la ruta de salida, usada para el enlace activo. */
function documento({ sitio, profundidad: p, pagina, titulo, descripcion, ruta,
  imagen, tipo = 'website', clase = '', contenido, fecha, tituloSocial }) {
  // En la pestaña conviene "Nota · Sitio"; en la tarjeta de X no, porque ahí el
  // sitio ya va en og:site_name y repetirlo come caracteres del titular.
  const social = tituloSocial || titulo;
  const url = sitio.url.replace(/\/$/, '') + '/' + ruta.replace(/index\.html$/, '');
  const urlImagen = imagen
    ? sitio.url.replace(/\/$/, '') + '/' + imagen
    : sitio.url.replace(/\/$/, '') + '/' + sitio.imagenSocial;

  return `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(titulo)}</title>
<meta name="description" content="${esc(descripcion)}">
<link rel="canonical" href="${url}">
<meta name="author" content="${esc(sitio.autor)}">
<meta name="theme-color" content="${sitio.color}">

<meta property="og:type" content="${tipo}">
<meta property="og:site_name" content="${esc(sitio.nombre)}">
<meta property="og:locale" content="es_CO">
<meta property="og:title" content="${esc(social)}">
<meta property="og:description" content="${esc(descripcion)}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${urlImagen}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${esc(social)}">
${fecha ? `<meta property="article:published_time" content="${fecha}">\n<meta property="article:author" content="${esc(sitio.autor)}">` : ''}

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(social)}">
<meta name="twitter:description" content="${esc(descripcion)}">
<meta name="twitter:image" content="${urlImagen}">
<meta name="twitter:creator" content="@${esc(sitio.x)}">

<link rel="icon" href="${rel(p, 'favicon.svg')}" type="image/svg+xml">
<link rel="apple-touch-icon" href="${rel(p, 'assets/img/icono-180.png')}">
<link rel="alternate" type="application/rss+xml" title="${esc(sitio.nombre)}" href="${rel(p, 'feed.xml')}">
<link rel="preload" as="font" type="font/woff2" href="${rel(p, 'assets/fuentes/source-serif-4-normal-latin.woff2')}" crossorigin>
<link rel="stylesheet" href="${rel(p, 'assets/fuentes/fuentes.css')}">
<link rel="stylesheet" href="${rel(p, 'assets/css/estilo.css')}">
</head>
<body${clase ? ` class="${clase}"` : ''}>
  ${cabecera(sitio, p, pagina)}
  <main id="contenido">
${contenido}
  </main>
  ${pie(sitio, p)}
</body>
</html>
`;
}

/* ------------------------------------------------------------------- fragmentos */

/** Tarjeta de nota para portada y listado. */
function reseña(a, sitio, p, { grande = false } = {}) {
  const enlace = rel(p, `articulos/${a.slug}/index.html`);
  const img = a.imagen ? `
      <a class="resena__imagen" href="${enlace}" tabindex="-1" aria-hidden="true">
        <img src="${rel(p, a.imagen)}" alt="" loading="lazy" decoding="async">
      </a>` : '';
  return `<article class="resena${grande ? ' resena--grande' : ''}">${img}
      <div class="resena__texto">
        <p class="antetitulo">${esc(a.categoria)}</p>
        <h3 class="resena__titulo"><a href="${enlace}">${esc(a.titulo)}</a></h3>
        <p class="resena__bajada">${esc(a.bajada)}</p>
        <p class="metadatos"><time datetime="${a.fecha}">${fechaLarga(a.fecha)}</time> · ${a.minutos} min de lectura</p>
      </div>
    </article>`;
}

function listaTemas(temas, p, sitio) {
  return `<ul class="temas">
      ${temas.map(t =>
    `<li><a href="${rel(p, `temas/${t.slug}/index.html`)}">${esc(t.nombre)} <span>${t.notas.length}</span></a></li>`
  ).join('\n      ')}
    </ul>`;
}

/* ------------------------------------------------------------------------ build */

function main() {
  const sitio = JSON.parse(fs.readFileSync(path.join(CONTENIDO, 'sitio.json'), 'utf8'));
  const baseUrl = sitio.url.replace(/\/$/, '');

  if (/EDITAR|usuario/i.test(sitio.url)) {
    console.warn('\n  ⚠  content/sitio.json → "url" todavía es un valor de ejemplo.');
    console.warn('     Cámbialo por la URL real y vuelve a ejecutar el build.\n');
  }

  // -- Notas -----------------------------------------------------------------
  const dirNotas = path.join(CONTENIDO, 'articulos');
  const articulos = fs.readdirSync(dirNotas).filter(f => f.endsWith('.md')).map(f => {
    const bruto = fs.readFileSync(path.join(dirNotas, f), 'utf8');
    const { meta, cuerpo } = leerFrontMatter(bruto);
    const slug = meta.slug || f.replace(/\.md$/, '');
    const palabras = cuerpo.replace(/:::[\s\S]*?:::/g, '').split(/\s+/).filter(Boolean).length;
    return {
      ...meta,
      slug,
      cuerpo,
      temas: Array.isArray(meta.temas) ? meta.temas : (meta.temas ? [meta.temas] : []),
      minutos: Math.max(1, Math.round(palabras / 200)),
    };
  }).sort((a, b) => b.fecha.localeCompare(a.fecha));

  // -- Temas (solo los que se usan) ------------------------------------------
  const mapaTemas = new Map();
  for (const a of articulos) {
    for (const nombre of a.temas) {
      const slug = slugify(nombre);
      if (!mapaTemas.has(slug)) mapaTemas.set(slug, { nombre, slug, notas: [] });
      mapaTemas.get(slug).notas.push(a);
    }
  }
  const temas = [...mapaTemas.values()].sort((a, b) => b.notas.length - a.notas.length
    || a.nombre.localeCompare(b.nombre));

  const rutas = [];

  // -- Página de cada nota ---------------------------------------------------
  for (const a of articulos) {
    const p = 2;
    const ruta = `articulos/${a.slug}/index.html`;
    const ctx = { profundidad: p, primeraFigura: true };
    const urlNota = `${baseUrl}/articulos/${a.slug}/`;
    const compartir = `https://x.com/intent/post?text=${encodeURIComponent(a.titulo)}&url=${encodeURIComponent(urlNota)}`;

    const fuentes = (a.fuentes || []).length ? `
      <section class="fuentes" aria-labelledby="fuentes-datos">
        <h2 id="fuentes-datos">Fuentes de los datos</h2>
        <ul>
          ${a.fuentes.map(f => `<li>${enLinea(f)}</li>`).join('\n          ')}
        </ul>
      </section>` : '';

    const pdf = a.pdf ? `<a class="boton" href="${rel(p, a.pdf)}" download>Descargar la versión en PDF</a>` : '';

    const contenido = `    <article class="nota">
      <header class="nota__cabecera">
        <p class="antetitulo"><a href="${rel(p, `temas/${slugify(a.categoria)}/index.html`)}">${esc(a.categoria)}</a></p>
        <h1>${esc(a.titulo)}</h1>
        <p class="bajada">${esc(a.bajada)}</p>
        <div class="firma">
          <p class="firma__autor">Por <strong>${esc(a.autor || sitio.autor)}</strong></p>
          <p class="metadatos">
            <time datetime="${a.fecha}">${fechaLarga(a.fecha)}</time>
            · ${a.minutos} min de lectura
            · <a href="https://x.com/${sitio.x}" rel="noopener">@${esc(sitio.x)}</a>
          </p>
        </div>
        <div class="acciones">
          ${pdf}
          <a class="boton boton--secundario" href="${compartir}" rel="noopener" target="_blank">Compartir en X</a>
        </div>
      </header>

      <div class="cuerpo">
${markdown(a.cuerpo, ctx)}
      </div>
${fuentes}
      <footer class="nota__pie">
        <p class="metadatos">Temas: ${a.temas.map(t =>
      `<a href="${rel(p, `temas/${slugify(t)}/index.html`)}">${esc(t)}</a>`).join(' · ')}</p>
        <p class="metadatos">Escribió esta nota <strong>${esc(a.autor || sitio.autor)}</strong> · <a href="mailto:${esc(sitio.correo)}">${esc(sitio.correo)}</a> · <a href="https://x.com/${sitio.x}" rel="noopener">@${esc(sitio.x)}</a></p>
        <p><a class="volver" href="${rel(p, 'analisis/index.html')}">Ver todas las notas</a></p>
      </footer>
    </article>`;

    escribir(ruta, documento({
      sitio, profundidad: p, pagina: 'analisis/index.html', ruta,
      titulo: `${a.titulo} · ${sitio.nombre}`, tituloSocial: a.titulo,
      descripcion: a.descripcion, imagen: a.imagenSocial || a.imagen,
      tipo: 'article', clase: 'pagina-nota', contenido, fecha: a.fecha,
    }));
    rutas.push({ ruta, fecha: a.fecha });
  }

  // -- Portada ---------------------------------------------------------------
  {
    const p = 0;
    const destacado = articulos.find(a => a.destacado) || articulos[0];
    const resto = articulos.filter(a => a !== destacado);
    const enlaceDestacado = `articulos/${destacado.slug}/index.html`;

    const recientes = resto.length ? `
      <section class="seccion" aria-labelledby="recientes">
        <h2 class="seccion__titulo" id="recientes">Notas recientes</h2>
        <div class="lista-notas">
          ${resto.slice(0, 6).map(a => reseña(a, sitio, p)).join('\n          ')}
        </div>
        <p class="seccion__mas"><a href="${rel(p, 'analisis/index.html')}">Ver todas las notas</a></p>
      </section>` : '';

    const contenido = `    <div class="contenedor">
      <p class="entradilla-sitio">${esc(sitio.presentacion)}</p>

      <section class="destacado" aria-labelledby="destacado-titulo">
        <p class="etiqueta-seccion">La nota</p>
        <div class="destacado__grid">
          <div class="destacado__texto">
            <p class="antetitulo">${esc(destacado.categoria)}</p>
            <h2 class="destacado__titulo" id="destacado-titulo">
              <a href="${rel(p, enlaceDestacado)}">${esc(destacado.titulo)}</a>
            </h2>
            <p class="destacado__bajada">${esc(destacado.bajada)}</p>
            <p class="metadatos">Por ${esc(destacado.autor || sitio.autor)} · <time datetime="${destacado.fecha}">${fechaLarga(destacado.fecha)}</time> · ${destacado.minutos} min de lectura</p>
            <p><a class="boton" href="${rel(p, enlaceDestacado)}">Leer el análisis</a></p>
          </div>
          <figure class="destacado__figura">
            <a href="${rel(p, enlaceDestacado)}" tabindex="-1" aria-hidden="true">
              <img src="${rel(p, destacado.imagen)}" alt="" width="1600" height="896" decoding="async">
            </a>
            <figcaption>${esc(destacado.pieDestacado || '')}</figcaption>
          </figure>
        </div>
      </section>
${recientes}
      <section class="seccion" aria-labelledby="temas-titulo">
        <h2 class="seccion__titulo" id="temas-titulo">Temas</h2>
        ${listaTemas(temas, p, sitio)}
      </section>

      <section class="seccion perfil-breve" aria-labelledby="quien">
        <h2 class="seccion__titulo" id="quien">Quién escribe</h2>
        <p>${esc(sitio.bioCorta)}</p>
        <p class="perfil-breve__acciones">
          <a class="boton boton--secundario" href="${rel(p, 'sobre-mi/index.html')}">Sobre mí</a>
          <a class="boton boton--secundario" href="${rel(p, sitio.cv)}">Ver el CV (PDF)</a>
        </p>
      </section>
    </div>`;

    escribir('index.html', documento({
      sitio, profundidad: p, pagina: 'index.html', ruta: 'index.html',
      titulo: `${sitio.nombre} · ${sitio.lema}`,
      descripcion: sitio.descripcion, clase: 'pagina-portada', contenido,
    }));
    rutas.push({ ruta: 'index.html', fecha: articulos[0].fecha });
  }

  // -- Listado de análisis ---------------------------------------------------
  {
    const p = 1;
    const contenido = `    <div class="contenedor contenedor--estrecho">
      <header class="cabecera-seccion">
        <h1>Análisis</h1>
        <p class="bajada">Notas propias sobre política, elecciones, economía, conflicto y desarrollo territorial, con los datos y las fuentes a la vista.</p>
      </header>
      <div class="lista-notas lista-notas--completa">
        ${articulos.map(a => reseña(a, sitio, p)).join('\n        ')}
      </div>
      <section class="seccion" aria-labelledby="temas-listado">
        <h2 class="seccion__titulo" id="temas-listado">Temas</h2>
        ${listaTemas(temas, p, sitio)}
      </section>
    </div>`;
    escribir('analisis/index.html', documento({
      sitio, profundidad: p, pagina: 'analisis/index.html', ruta: 'analisis/index.html',
      titulo: `Análisis · ${sitio.nombre}`,
      descripcion: 'Todas las notas de análisis publicadas: política, elecciones, economía, conflicto, datos y desarrollo territorial en Nariño y Colombia.',
      contenido,
    }));
    rutas.push({ ruta: 'analisis/index.html', fecha: articulos[0].fecha });
  }

  // -- Una página por tema ---------------------------------------------------
  for (const t of temas) {
    const p = 2;
    const ruta = `temas/${t.slug}/index.html`;
    const contenido = `    <div class="contenedor contenedor--estrecho">
      <header class="cabecera-seccion">
        <p class="antetitulo">Tema</p>
        <h1>${esc(t.nombre)}</h1>
        <p class="bajada">${t.notas.length} ${t.notas.length === 1 ? 'nota publicada' : 'notas publicadas'} en esta línea de trabajo.</p>
      </header>
      <div class="lista-notas lista-notas--completa">
        ${t.notas.map(a => reseña(a, sitio, p)).join('\n        ')}
      </div>
      <section class="seccion" aria-labelledby="otros-temas">
        <h2 class="seccion__titulo" id="otros-temas">Otros temas</h2>
        ${listaTemas(temas, p, sitio)}
      </section>
    </div>`;
    escribir(ruta, documento({
      sitio, profundidad: p, pagina: 'analisis/index.html', ruta,
      titulo: `${t.nombre} · ${sitio.nombre}`, tituloSocial: `${t.nombre} · ${sitio.nombre}`,
      descripcion: `Notas de análisis sobre ${t.nombre.toLowerCase()} en ${sitio.nombre}.`,
      contenido,
    }));
    rutas.push({ ruta, fecha: t.notas[0].fecha });
  }

  // -- Páginas fijas ---------------------------------------------------------
  const dirPaginas = path.join(CONTENIDO, 'paginas');
  for (const f of fs.readdirSync(dirPaginas).filter(f => f.endsWith('.md'))) {
    const { meta, cuerpo } = leerFrontMatter(fs.readFileSync(path.join(dirPaginas, f), 'utf8'));
    const slug = meta.slug || f.replace(/\.md$/, '');
    const p = 1;
    const ruta = `${slug}/index.html`;
    const ctx = { profundidad: p, primeraFigura: true };

    const contenido = `    <div class="contenedor contenedor--estrecho">
      <article class="pagina">
        <header class="cabecera-seccion">
          <h1>${esc(meta.titulo)}</h1>
          ${meta.bajada ? `<p class="bajada">${esc(meta.bajada)}</p>` : ''}
        </header>
        <div class="cuerpo">
${markdown(cuerpo, ctx)}
        </div>
      </article>
    </div>`;
    escribir(ruta, documento({
      sitio, profundidad: p, pagina: ruta, ruta,
      titulo: `${meta.titulo} · ${sitio.nombre}`, tituloSocial: `${meta.titulo} · ${sitio.nombre}`,
      descripcion: meta.descripcion, imagen: meta.imagenSocial,
      tipo: 'profile', contenido,
    }));
    rutas.push({ ruta, fecha: meta.fecha || articulos[0].fecha });
  }

  // -- 404 -------------------------------------------------------------------
  // GitHub Pages sirve esta página desde cualquier ruta, así que no puede usar
  // rutas relativas: lleva estilos en línea y enlaces absolutos.
  escribir('404.html', `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Página no encontrada · ${esc(sitio.nombre)}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="${baseUrl}/favicon.svg" type="image/svg+xml">
<style>
  html { -webkit-text-size-adjust: 100%; }
  body { margin: 0; background: ${sitio.papel}; color: #1B1A18; font: 400 1.0625rem/1.6 Georgia, 'Times New Roman', serif; }
  .caja { max-width: 34rem; margin: 0 auto; padding: 5rem 1.25rem; }
  .marca { font: 600 0.8125rem/1 system-ui, sans-serif; letter-spacing: .16em; text-transform: uppercase; color: ${sitio.color}; margin: 0 0 3rem; }
  h1 { font-size: 2rem; line-height: 1.2; margin: 0 0 .75rem; color: ${sitio.color}; }
  a { color: ${sitio.color}; }
  ul { padding-left: 1.1rem; }
</style>
</head>
<body>
  <div class="caja">
    <p class="marca"><a href="${baseUrl}/" style="text-decoration:none">${esc(sitio.nombre)}</a></p>
    <h1>Esta página no existe</h1>
    <p>El enlace puede estar mal escrito o la nota pudo haber cambiado de dirección.</p>
    <ul>
      <li><a href="${baseUrl}/">Ir a la portada</a></li>
      <li><a href="${baseUrl}/analisis/">Ver todas las notas</a></li>
      <li><a href="${baseUrl}/sobre-mi/">Sobre mí</a></li>
    </ul>
  </div>
</body>
</html>
`);

  // -- sitemap, robots, feed -------------------------------------------------
  const urls = rutas.map(r =>
    `  <url><loc>${baseUrl}/${r.ruta.replace(/index\.html$/, '')}</loc><lastmod>${r.fecha}</lastmod></url>`
  ).join('\n');
  escribir('sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>
`);

  escribir('robots.txt', `User-agent: *
Allow: /

Sitemap: ${baseUrl}/sitemap.xml
`);

  const items = articulos.map(a => `    <item>
      <title>${esc(a.titulo)}</title>
      <link>${baseUrl}/articulos/${a.slug}/</link>
      <guid isPermaLink="true">${baseUrl}/articulos/${a.slug}/</guid>
      <pubDate>${new Date(a.fecha + 'T12:00:00Z').toUTCString()}</pubDate>
      <description>${esc(a.descripcion)}</description>
      <category>${esc(a.categoria)}</category>
    </item>`).join('\n');
  escribir('feed.xml', `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${esc(sitio.nombre)}</title>
    <link>${baseUrl}/</link>
    <atom:link href="${baseUrl}/feed.xml" rel="self" type="application/rss+xml"/>
    <description>${esc(sitio.descripcion)}</description>
    <language>es-CO</language>
${items}
  </channel>
</rss>
`);

  // Evita que GitHub Pages procese el sitio con Jekyll.
  escribir('.nojekyll', '');

  console.log(`\n  ${articulos.length} nota(s) · ${temas.length} tema(s) · ${rutas.length} página(s)`);
  console.log(`  Sitio generado en docs/  ·  URL configurada: ${sitio.url}\n`);
}

main();
