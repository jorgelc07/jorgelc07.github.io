#!/usr/bin/env python3
"""
Extrae los gráficos incrustados en los .docx de las notas y genera las
versiones optimizadas para la web.

Se usan las imágenes que van dentro del .docx y no los PNG sueltos de la
carpeta de trabajo, porque dentro del documento están sin recomprimir y en el
orden exacto en que aparecen en el texto. Se verificó por checksum que son
idénticas a las originales.

- Los originales se guardan sin modificar en  originales/<carpeta>/
- Las versiones web (PNG + WebP) van a       docs/assets/img/graficos/

Uso:  python3 scripts/extraer_graficos.py            (todas las notas)
      python3 scripts/extraer_graficos.py narino     (solo una)
"""
import os
import re
import shutil
import sys
import zipfile

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(RAIZ, "docs", "assets", "img", "graficos")

ANCHO_MAX = 1600  # px; cubre pantallas 2x en una columna de 800 px. No se amplía
                  # nada por debajo de esa medida: escalar hacia arriba solo
                  # añadiría peso sin añadir detalle.

NOTAS = {
    # clave: (ruta del .docx, carpeta de originales, lista de nombres web)
    "narino": {
        "docx": "originales/narino_paz_territorial_coca_otros.docx",
        "originales": "originales/graficos_nota",
        "nombres": [
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
        ],
    },
    "elecciones": {
        "docx": "originales/nota2_elecciones_coca_violencia/Elecciones_coca_violencia_narino.docx",
        "originales": "originales/nota2_elecciones_coca_violencia/graficos",
        "nombres": [
            "elec01-mapa-cambio-izquierda-narino",
            "elec02-mapa-coca-narino-2023",
            "elec03-mapa-cambio-izquierda-y-coca",
            "elec04-dispersion-coca-relativa-cambio-electoral",
            "elec05-mapa-violencia-narino-2025",
            "elec06-dispersion-violencia-cambio-electoral",
            "elec07-promedios-subregion",
            "elec08-mapa-cambio-coca-violencia",
        ],
        # Dos figuras salieron del original con textos superpuestos. Se recorta
        # solo la banda ilegible y ese contenido se lleva a la leyenda HTML,
        # donde se lee bien y además queda seleccionable. Los originales no se
        # tocan: el recorte se aplica únicamente a la copia web.
        #
        #   elec07: el título chocaba con su subtítulo (filas 0-41).
        #   elec03: la línea de fuente al pie chocaba con el crédito del autor
        #           (filas 979 en adelante). La nota de la figura, que está
        #           encima, sí se conserva.
        "recortes": {
            "elec07-promedios-subregion": {"arriba": 42},
            "elec03-mapa-cambio-izquierda-y-coca": {"abajo": 979},
        },
    },
}


def orden_imagenes(z):
    """Rutas de las imágenes en el orden en que aparecen en el texto."""
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


def procesar(clave, cfg):
    docx = os.path.join(RAIZ, cfg["docx"])
    orig = os.path.join(RAIZ, cfg["originales"])
    nombres = cfg["nombres"]
    recortes = cfg.get("recortes", {})

    if not os.path.exists(docx):
        print(f"  ! no está {cfg['docx']}, se omite")
        return

    print(f"\n— {clave} —")
    os.makedirs(orig, exist_ok=True)
    os.makedirs(WEB, exist_ok=True)

    with zipfile.ZipFile(docx) as z:
        rutas = orden_imagenes(z)
        assert len(rutas) == len(nombres), \
            f"{clave}: esperaba {len(nombres)} figuras, el documento trae {len(rutas)}"
        for ruta, nombre in zip(rutas, nombres):
            with z.open(ruta) as f, open(os.path.join(orig, nombre + ".png"), "wb") as g:
                shutil.copyfileobj(f, g)

    total_o = total_w = 0
    for nombre in nombres:
        origen = os.path.join(orig, nombre + ".png")
        im = Image.open(origen).convert("RGB")  # los gráficos son opacos sobre blanco

        if nombre in recortes:
            r = recortes[nombre]
            im = im.crop((0, r.get("arriba", 0), im.width, r.get("abajo", im.height)))

        if im.width > ANCHO_MAX:
            alto = round(im.height * ANCHO_MAX / im.width)
            im = im.resize((ANCHO_MAX, alto), Image.LANCZOS)

        png = os.path.join(WEB, nombre + ".png")
        webp = os.path.join(WEB, nombre + ".webp")
        im.save(png, "PNG", optimize=True)
        im.save(webp, "WEBP", quality=92, method=6)

        total_o += os.path.getsize(origen)
        total_w += min(os.path.getsize(png), os.path.getsize(webp))
        marca = "  (recortada)" if nombre in recortes else ""
        print(f"  {nombre:48s} {im.width}x{im.height}  "
              f"png {os.path.getsize(png)//1024:4d} KB   "
              f"webp {os.path.getsize(webp)//1024:4d} KB{marca}")

    print(f"  originales {total_o//1024} KB  ->  web {total_w//1024} KB")


def main():
    pedidas = sys.argv[1:] or list(NOTAS)
    for clave in pedidas:
        if clave not in NOTAS:
            print(f"  ! nota desconocida: {clave}. Opciones: {', '.join(NOTAS)}")
            continue
        procesar(clave, NOTAS[clave])


if __name__ == "__main__":
    main()
