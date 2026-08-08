#!/usr/bin/env python3
"""
Extrae los 11 gráficos incrustados en el .docx de la nota y genera las
versiones optimizadas para la web.

- Los originales se guardan sin modificar en  originales/graficos_nota/
- Las versiones web (PNG 1600px + WebP) van a  docs/assets/img/graficos/

Uso:  python3 scripts/extraer_graficos.py
"""
import os
import re
import shutil
import zipfile

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX = os.path.join(RAIZ, "originales", "narino_paz_territorial_coca_otros.docx")
ORIG = os.path.join(RAIZ, "originales", "graficos_nota")
WEB = os.path.join(RAIZ, "docs", "assets", "img", "graficos")

ANCHO_WEB = 1600  # px; suficiente para pantallas 2x en una columna de 800px

# Orden de aparición en el documento -> nombre estable usado en la web.
NOMBRES = [
    "fig01-homicidios-narino-colombia-2010-2025",
    "fig02-homicidios-subregion-2022-2025",
    "fig03-mapa-cambio-homicidios-municipio-2022-2025",
    "fig04-tasa-homicidios-grupo-territorial-2010-2025",
    "fig05-extorsion-narino-2010-2025",
    "fig06-tumaco-homicidios-vs-coca-2016-2024",
    "fig07-coca-narino-2001-2024",
    "fig08-coca-top-municipios-2024",
    "fig09-mapa-coca-cambio-2022-2024",
    "fig10-asesinatos-selectivos-cnmh-2010-2025",
    "fig11-amenazas-desplazamiento-2016-2024",
]


def orden_imagenes(z):
    """Devuelve las rutas de las imágenes en el orden en que aparecen en el texto."""
    xml = z.read("word/document.xml").decode("utf-8")
    rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    mapa = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
    vistas, salida = set(), []
    for m in re.finditer(r'r:embed="([^"]+)"', xml):
        rid = m.group(1)
        if rid in vistas:
            continue
        vistas.add(rid)
        salida.append("word/" + mapa[rid])
    return salida


def main():
    os.makedirs(ORIG, exist_ok=True)
    os.makedirs(WEB, exist_ok=True)

    with zipfile.ZipFile(DOCX) as z:
        rutas = orden_imagenes(z)
        assert len(rutas) == len(NOMBRES), f"esperaba {len(NOMBRES)} figuras, hay {len(rutas)}"
        for ruta, nombre in zip(rutas, NOMBRES):
            destino = os.path.join(ORIG, nombre + ".png")
            with z.open(ruta) as f, open(destino, "wb") as g:
                shutil.copyfileobj(f, g)

    total_o = total_w = 0
    for nombre in NOMBRES:
        origen = os.path.join(ORIG, nombre + ".png")
        im = Image.open(origen).convert("RGB")  # los charts son opacos sobre blanco
        if im.width > ANCHO_WEB:
            alto = round(im.height * ANCHO_WEB / im.width)
            im = im.resize((ANCHO_WEB, alto), Image.LANCZOS)

        png = os.path.join(WEB, nombre + ".png")
        webp = os.path.join(WEB, nombre + ".webp")
        im.save(png, "PNG", optimize=True)
        im.save(webp, "WEBP", quality=92, method=6)

        total_o += os.path.getsize(origen)
        total_w += min(os.path.getsize(png), os.path.getsize(webp))
        print(
            f"{nombre:52s} {im.width}x{im.height}  "
            f"png {os.path.getsize(png)//1024:4d} KB   webp {os.path.getsize(webp)//1024:4d} KB"
        )

    print(f"\noriginales: {total_o//1024} KB  ->  web (mejor formato): {total_w//1024} KB")


if __name__ == "__main__":
    main()
