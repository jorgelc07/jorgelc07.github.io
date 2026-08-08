#!/usr/bin/env python3
"""
Genera el favicon, el icono de iOS y las imágenes de previsualización social
(1200x630) que se ven cuando se comparte un enlace en X, WhatsApp o LinkedIn.

Las tipografías en TTF se descargan a scripts/.cache-fuentes/ (ignorada por git)
solo cuando hace falta regenerar las imágenes. Las imágenes resultantes sí se
versionan, así que el sitio se reconstruye sin necesidad de red.

Uso:  python3 scripts/generar_imagenes.py
"""
import json
import os
import subprocess
import textwrap

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(RAIZ, "docs")
SOCIAL = os.path.join(DOCS, "assets", "img", "social")
CACHE = os.path.join(RAIZ, "scripts", ".cache-fuentes")

AZUL = (27, 59, 111)
AZUL_PROFUNDO = (18, 44, 85)
PAPEL = (251, 248, 243)
TINTA = (27, 26, 24)
GRIS = (94, 89, 81)
FILETE = (221, 213, 200)
BLANCO = (255, 255, 255)

UA_ANTIGUO = "Mozilla/4.0"  # fuerza que Google Fonts devuelva TTF y no woff2
API = ("https://fonts.googleapis.com/css"
       "?family=Source+Serif+4:400,600,700|Inter:400,500,600")

# (archivo local, orden en que aparece la URL en la respuesta del API)
FUENTES = {
    "inter-400.ttf": 0,
    "inter-500.ttf": 1,
    "inter-600.ttf": 2,
    "serif-400.ttf": 3,
    "serif-600.ttf": 4,
    "serif-700.ttf": 5,
}


def curl(url, ua=UA_ANTIGUO):
    r = subprocess.run(["curl", "-sSfL", "-A", ua, url], capture_output=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"error descargando {url}: {r.stderr.decode()}")
    return r.stdout


def asegurar_fuentes():
    os.makedirs(CACHE, exist_ok=True)
    if all(os.path.exists(os.path.join(CACHE, n)) for n in FUENTES):
        return
    print("  descargando tipografías TTF para componer las imágenes…")
    css = curl(API).decode("utf8")
    urls = [l.split("url(")[1].split(")")[0] for l in css.splitlines() if "url(" in l]
    for nombre, i in FUENTES.items():
        with open(os.path.join(CACHE, nombre), "wb") as f:
            f.write(curl(urls[i]))


def fuente(nombre, tam):
    return ImageFont.truetype(os.path.join(CACHE, nombre), tam)


def ancho(d, texto, f):
    return d.textbbox((0, 0), texto, font=f)[2]


def espaciado(d, xy, texto, f, fill, sep):
    """Dibuja texto con letter-spacing (PIL no lo soporta de fábrica)."""
    x, y = xy
    for ch in texto:
        d.text((x, y), ch, font=f, fill=fill)
        x += ancho(d, ch, f) + sep
    return x


def ancho_espaciado(d, texto, f, sep):
    return sum(ancho(d, ch, f) + sep for ch in texto) - sep


def envolver(d, texto, f, ancho_max):
    """Parte el texto en líneas que quepan en ancho_max píxeles."""
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if ancho(d, prueba, f) <= ancho_max or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


# ------------------------------------------------------------------ favicon

def favicon():
    """Marca tipográfica sobre azul: iniciales JC bajo un filete."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Jorge Luis Congacha">
  <rect width="64" height="64" fill="#1B3B6F"/>
  <rect x="12" y="14" width="40" height="2.5" fill="#FBF8F3"/>
  <text x="32" y="47" text-anchor="middle"
        font-family="Georgia, 'Times New Roman', serif" font-size="30" font-weight="700"
        letter-spacing="1" fill="#FBF8F3">JC</text>
</svg>
"""
    with open(os.path.join(DOCS, "favicon.svg"), "w") as f:
        f.write(svg)

    # Versión PNG para iOS, que no acepta SVG.
    im = Image.new("RGB", (180, 180), AZUL)
    d = ImageDraw.Draw(im)
    d.rectangle([34, 40, 146, 47], fill=PAPEL)
    f = fuente("serif-700.ttf", 84)
    t = "JC"
    d.text(((180 - ancho(d, t, f)) / 2, 128), t, font=f, fill=PAPEL, anchor="ls")
    im.save(os.path.join(DOCS, "assets", "img", "icono-180.png"), optimize=True)
    print("  favicon.svg + icono-180.png")


# ------------------------------------------------- tarjetas para compartir

def marco(d, W, H):
    d.rectangle([0, 0, W, 12], fill=AZUL)


def tarjeta_articulo(sitio, art, destino):
    """Mitad izquierda: titular. Mitad derecha: el gráfico de la nota."""
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), PAPEL)
    d = ImageDraw.Draw(im)
    marco(d, W, H)

    izq, pad_x = 660, 56

    # Gráfico a la derecha, sobre placa blanca
    grafico = os.path.join(DOCS, art["imagen"].replace("/", os.sep))
    if os.path.exists(grafico):
        g = Image.open(grafico).convert("RGB")
        caja_w, caja_h = W - izq - 48, H - 12 - 96
        escala = min(caja_w / g.width, caja_h / g.height)
        g = g.resize((int(g.width * escala), int(g.height * escala)), Image.LANCZOS)
        gx = izq + (caja_w - g.width) // 2 + 24
        gy = 12 + (caja_h - g.height) // 2 + 48
        d.rectangle([gx - 1, gy - 1, gx + g.width, gy + g.height], outline=FILETE)
        im.paste(g, (gx, gy))
    d.line([(izq - 8, 12), (izq - 8, H)], fill=FILETE, width=1)

    # Cabecera
    y = 52
    f_marca = fuente("serif-600.ttf", 21)
    espaciado(d, (pad_x, y), sitio["nombre"].upper(), f_marca, AZUL, 2.2)
    y += 44
    d.line([(pad_x, y), (izq - 60, y)], fill=AZUL, width=2)
    y += 26

    # Antetítulo
    f_kicker = fuente("inter-600.ttf", 15)
    espaciado(d, (pad_x, y), art["categoria"].upper(), f_kicker, GRIS, 2.0)
    y += 40

    # Titular
    f_tit = fuente("serif-700.ttf", 48)
    lineas = envolver(d, art["titulo"], f_tit, izq - pad_x - 60)
    if len(lineas) > 5:
        f_tit = fuente("serif-700.ttf", 40)
        lineas = envolver(d, art["titulo"], f_tit, izq - pad_x - 60)
    for linea in lineas[:6]:
        d.text((pad_x, y), linea, font=f_tit, fill=TINTA)
        y += int(f_tit.size * 1.22)

    # Pie
    f_pie = fuente("inter-400.ttf", 17)
    d.line([(pad_x, H - 92), (izq - 60, H - 92)], fill=FILETE, width=1)
    d.text((pad_x, H - 74), f"{art['autor']}  ·  @{sitio['x']}", font=f_pie, fill=GRIS)

    im.save(destino, optimize=True)
    print(f"  {os.path.relpath(destino, RAIZ)}")


def tarjeta_portada(sitio, destino):
    """Tarjeta tipográfica del sitio, sin gráfico."""
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), PAPEL)
    d = ImageDraw.Draw(im)
    marco(d, W, H)

    pad = 86
    f_nombre = fuente("serif-700.ttf", 78)
    partes = sitio["nombre"].upper().split()
    y = 176
    for parte in [" ".join(partes[:2]), " ".join(partes[2:])] if len(partes) > 2 else [sitio["nombre"].upper()]:
        if not parte:
            continue
        espaciado(d, (pad, y), parte, f_nombre, AZUL, 4)
        y += 92

    y += 18
    d.line([(pad, y), (W - pad, y)], fill=AZUL, width=2)
    y += 30

    f_lema = fuente("inter-500.ttf", 21)
    espaciado(d, (pad, y), sitio["lema"].upper(), f_lema, GRIS, 3)

    f_desc = fuente("serif-400.ttf", 25)
    y += 66
    for linea in envolver(d, sitio["descripcion"], f_desc, W - pad * 2)[:3]:
        d.text((pad, y), linea, font=f_desc, fill=GRIS)
        y += 38

    im.save(destino, optimize=True)
    print(f"  {os.path.relpath(destino, RAIZ)}")


# ------------------------------------------------------------------- main

def main():
    asegurar_fuentes()
    os.makedirs(SOCIAL, exist_ok=True)

    with open(os.path.join(RAIZ, "content", "sitio.json")) as f:
        sitio = json.load(f)

    favicon()
    tarjeta_portada(sitio, os.path.join(SOCIAL, "portada.png"))

    # Una tarjeta por nota, leyendo los metadatos del propio .md
    dir_notas = os.path.join(RAIZ, "content", "articulos")
    for archivo in sorted(os.listdir(dir_notas)):
        if not archivo.endswith(".md"):
            continue
        with open(os.path.join(dir_notas, archivo), encoding="utf8") as f:
            texto = f.read()
        bloque = texto.split("---")[1]
        meta = {}
        for linea in bloque.splitlines():
            if ":" in linea and not linea.startswith(" "):
                k, v = linea.split(":", 1)
                meta[k.strip()] = v.strip()
        slug = meta.get("slug", archivo[:-3])
        tarjeta_articulo(
            sitio,
            {
                "titulo": meta["titulo"],
                "categoria": meta["categoria"],
                "autor": meta.get("autor", sitio["autor"]),
                "imagen": meta["imagen"],
            },
            os.path.join(SOCIAL, slug + ".png"),
        )


if __name__ == "__main__":
    main()
