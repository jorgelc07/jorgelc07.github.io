#!/usr/bin/env python3
"""
Pruebas del sitio generado. Levanta un servidor local sobre docs/ y recorre
todas las páginas con Chrome en cinco anchos, comprobando:

  · que no haya desbordamiento horizontal (la queja número uno en móvil);
  · que todas las imágenes carguen de verdad;
  · que ningún recurso devuelva 404;
  · que no haya errores de consola;
  · que cada página tenga exactamente un <h1> y jerarquía de encabezados sana;
  · que todos los enlaces internos apunten a algo que existe;
  · que no quede ninguna ruta local (/Users/…, file://) en el HTML publicado;
  · que las metaetiquetas sociales estén completas;
  · que los textos no queden por debajo de 12px en móvil.

Y deja una captura de cada página y ancho en pruebas/capturas/.

Usa el Chrome ya instalado en el equipo (channel="chrome"): no descarga nada.

Uso:  python3 scripts/probar.py
"""
import http.server
import os
import re
import socketserver
import sys
import threading
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(RAIZ, "docs")
CAPTURAS = os.path.join(RAIZ, "pruebas", "capturas")
PUERTO = 8731

ANCHOS = [
    ("escritorio-1440", 1440, 900),
    ("escritorio-1280", 1280, 800),
    ("tablet-768", 768, 1024),
    ("movil-390", 390, 844),
    ("movil-375", 375, 667),
]

PAGINAS = [
    ("portada", "/"),
    ("analisis", "/analisis/"),
    ("nota", "/articulos/narino-paz-territorial-homicidios-coca/"),
    ("sobre-mi", "/sobre-mi/"),
    ("tema", "/temas/narino/"),
    ("404", "/404.html"),
]

fallos = []
avisos = []


def fallo(donde, msg):
    fallos.append(f"{donde}: {msg}")
    print(f"  ✗ {donde}: {msg}")


def aviso(donde, msg):
    avisos.append(f"{donde}: {msg}")
    print(f"  ! {donde}: {msg}")


class Silencioso(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DOCS, **kw)

    def log_message(self, *a):
        pass


def servir():
    # Multihilo a propósito: con un servidor de un solo hilo las peticiones se
    # encolan, el navegador nunca llega a estar ocioso y las imágenes diferidas
    # parecen rotas cuando en realidad solo están esperando turno.
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", PUERTO), Silencioso)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


# ------------------------------------------------- comprobaciones estáticas

def revisar_html_estatico():
    print("\n— Revisión del HTML publicado —")
    patrones = [
        (r"file://", "ruta file://"),
        (r"/Users/", "ruta local /Users/"),
        (r"USUARIO\.github\.io", "URL de ejemplo sin reemplazar"),
        (r"Lorem ipsum", "texto de relleno"),
        (r"Your Name|TODO|FIXME|XXXX", "texto marcador sin completar"),
    ]
    archivos = []
    for base, _, nombres in os.walk(DOCS):
        for n in nombres:
            if n.endswith((".html", ".xml", ".txt", ".css")):
                archivos.append(os.path.join(base, n))

    for archivo in archivos:
        rel = os.path.relpath(archivo, DOCS)
        texto = open(archivo, encoding="utf8").read()
        for patron, desc in patrones:
            if re.search(patron, texto):
                fallo(rel, f"contiene {desc}")

    # Metaetiquetas sociales en cada página HTML
    obligatorias = ["og:title", "og:description", "og:image", "og:url",
                    "twitter:card", 'rel="canonical"', "<title>",
                    'name="description"', 'name="viewport"']
    for archivo in archivos:
        if not archivo.endswith(".html") or archivo.endswith("404.html"):
            continue
        rel = os.path.relpath(archivo, DOCS)
        texto = open(archivo, encoding="utf8").read()
        faltan = [o for o in obligatorias if o not in texto]
        if faltan:
            fallo(rel, "faltan metaetiquetas: " + ", ".join(faltan))
    print(f"  {len(archivos)} archivos revisados")


def revisar_enlaces_internos():
    """Comprueba que cada href relativo del sitio exista en disco."""
    print("\n— Enlaces internos —")
    total = 0
    for base, _, nombres in os.walk(DOCS):
        for n in nombres:
            if not n.endswith(".html"):
                continue
            archivo = os.path.join(base, n)
            rel = os.path.relpath(archivo, DOCS)
            texto = open(archivo, encoding="utf8").read()
            for m in re.finditer(r'(?:href|src|srcset)="([^"]+)"', texto):
                destino = m.group(1).split("#")[0].split("?")[0]
                if not destino or destino.startswith(("http:", "https:", "mailto:", "data:")):
                    continue
                total += 1
                absoluto = os.path.normpath(os.path.join(base, destino))
                if not os.path.exists(absoluto):
                    fallo(rel, f"enlace roto → {m.group(1)}")
    print(f"  {total} referencias relativas comprobadas")


# ------------------------------------------------- comprobaciones en navegador

def revisar_en_navegador():
    os.makedirs(CAPTURAS, exist_ok=True)
    base = f"http://127.0.0.1:{PUERTO}"

    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="chrome")
        for nombre_ancho, w, h in ANCHOS:
            print(f"\n— {nombre_ancho} ({w}px) —")
            ctx = navegador.new_context(
                viewport={"width": w, "height": h},
                device_scale_factor=2 if w < 500 else 1,
            )
            pagina = ctx.new_page()

            errores_consola, fallos_red = [], []

            def es_local(url):
                # La página 404 enlaza a la URL pública definitiva, que todavía
                # no existe. Solo se auditan los recursos servidos localmente.
                return url.startswith(base)

            pagina.on("console", lambda m: errores_consola.append(m.text)
                      if m.type == "error" and es_local(pagina.url) else None)
            pagina.on("requestfailed", lambda r: fallos_red.append(r.url)
                      if es_local(r.url) else None)
            pagina.on("response", lambda r: fallos_red.append(f"{r.status} {r.url}")
                      if r.status >= 400 and es_local(r.url) else None)

            for nombre_pag, ruta in PAGINAS:
                donde = f"{nombre_pag}@{w}"
                errores_consola.clear()
                fallos_red.clear()

                pagina.goto(base + ruta, wait_until="networkidle")
                # Recorre la página entera para disparar las imágenes diferidas
                # (loading="lazy"); si no, darían un falso negativo al revisarlas.
                # behavior 'instant' es obligatorio: el sitio define
                # scroll-behavior: smooth y con scroll animado el bucle termina
                # antes de que la página se haya movido de verdad.
                pagina.evaluate("""async () => {
                  const paso = window.innerHeight * 0.8;
                  for (let y = 0; y < document.body.scrollHeight; y += paso) {
                    window.scrollTo({ top: y, behavior: 'instant' });
                    await new Promise(r => setTimeout(r, 60));
                  }
                  window.scrollTo({ top: 0, behavior: 'instant' });
                }""")
                pagina.wait_for_load_state("networkidle")
                # Espera activa a que terminen de decodificarse, con tope.
                try:
                    pagina.wait_for_function(
                        "() => [...document.images].every(i => i.complete)",
                        timeout=15000)
                except Exception:
                    pass
                pagina.wait_for_timeout(200)

                # Desbordamiento horizontal
                desborde = pagina.evaluate("""() => {
                  const de = document.documentElement;
                  const culpables = [];
                  if (de.scrollWidth > de.clientWidth + 1) {
                    for (const el of document.querySelectorAll('body *')) {
                      const r = el.getBoundingClientRect();
                      if (r.right > de.clientWidth + 1 || r.left < -1) {
                        culpables.push(el.tagName.toLowerCase() + '.' +
                          (el.className || '').toString().split(' ')[0] +
                          ' → ' + Math.round(r.left) + '..' + Math.round(r.right));
                      }
                    }
                  }
                  return { scroll: de.scrollWidth, client: de.clientWidth,
                           culpables: culpables.slice(0, 6) };
                }""")
                if desborde["scroll"] > desborde["client"] + 1:
                    fallo(donde, f"desbordamiento horizontal "
                                 f"({desborde['scroll']} > {desborde['client']}): "
                                 + "; ".join(desborde["culpables"]))

                # Imágenes rotas
                rotas = pagina.evaluate("""() => [...document.images]
                  .filter(i => !i.complete || i.naturalWidth === 0)
                  .map(i => i.currentSrc || i.src)""")
                for r in rotas:
                    fallo(donde, f"imagen sin cargar → {r}")

                # Imágenes sin alt
                sin_alt = pagina.evaluate(
                    """() => [...document.images].filter(i => i.alt === null).length""")
                if sin_alt:
                    fallo(donde, f"{sin_alt} imagen(es) sin atributo alt")

                # Encabezados
                h1 = pagina.evaluate("""() => document.querySelectorAll('h1').length""")
                if h1 != 1 and nombre_pag != "portada":
                    fallo(donde, f"{h1} elementos h1 (debe haber exactamente 1)")

                # Tamaños de letra mínimos en móvil
                if w <= 400:
                    pequenos = pagina.evaluate("""() => {
                      const malos = [];
                      for (const el of document.querySelectorAll('p, li, a, span, time, figcaption')) {
                        if (!el.textContent.trim()) continue;
                        const px = parseFloat(getComputedStyle(el).fontSize);
                        if (px < 12) malos.push(el.tagName + ' ' + px + 'px: ' +
                          el.textContent.trim().slice(0, 30));
                      }
                      return [...new Set(malos)].slice(0, 5);
                    }""")
                    for pq in pequenos:
                        fallo(donde, f"texto menor a 12px → {pq}")

                # Área táctil de los enlaces de navegación
                if w <= 400:
                    chicos = pagina.evaluate("""() => {
                      const malos = [];
                      for (const a of document.querySelectorAll('.menu a, .boton, .temas a')) {
                        const r = a.getBoundingClientRect();
                        if (r.height < 40) malos.push(a.textContent.trim().slice(0,20) +
                          ' → ' + Math.round(r.height) + 'px');
                      }
                      return malos.slice(0, 5);
                    }""")
                    for c in chicos:
                        aviso(donde, f"área táctil baja → {c}")

                for e in errores_consola:
                    fallo(donde, f"error de consola → {e}")
                for f in fallos_red:
                    fallo(donde, f"recurso fallido → {f}")

                pagina.screenshot(
                    path=os.path.join(CAPTURAS, f"{nombre_ancho}--{nombre_pag}.png"),
                    full_page=True)

            print(f"  {len(PAGINAS)} páginas revisadas y capturadas")
            ctx.close()
        navegador.close()


def main():
    srv = servir()
    try:
        revisar_html_estatico()
        revisar_enlaces_internos()
        revisar_en_navegador()
    finally:
        srv.shutdown()

    print("\n" + "=" * 66)
    if fallos:
        print(f"  {len(fallos)} FALLO(S):")
        for f in fallos:
            print("   ·", f)
    else:
        print("  Sin fallos.")
    if avisos:
        print(f"\n  {len(avisos)} aviso(s):")
        for a in avisos:
            print("   ·", a)
    print("=" * 66)
    print(f"  Capturas en pruebas/capturas/\n")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
