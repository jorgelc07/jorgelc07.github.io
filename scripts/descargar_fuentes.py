#!/usr/bin/env python3
"""
Descarga las tipografías (Source Serif 4 + Inter) desde Google Fonts y las deja
auto-alojadas en docs/assets/fuentes/, junto con un fuentes.css de rutas relativas.

Se hace una sola vez. Auto-alojar evita depender de un tercero en cada visita,
elimina peticiones externas y hace la web más rápida y más privada.
Solo se conservan los subconjuntos latin y latin-ext (suficiente para español).

Uso:  python3 scripts/descargar_fuentes.py
"""
import os
import re
import subprocess

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "docs", "assets", "fuentes")

API = (
    "https://fonts.googleapis.com/css2"
    "?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400"
    "&family=Inter:wght@400;500;600"
    "&display=swap"
)
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SUBCONJUNTOS = {"latin", "latin-ext"}


def descargar(url):
    # Se usa curl (y no urllib) porque el Python de python.org en macOS no trae
    # el bundle de certificados raíz y falla la verificación TLS.
    r = subprocess.run(
        ["curl", "-sSfL", "-A", UA, url], capture_output=True, timeout=120
    )
    if r.returncode != 0:
        raise RuntimeError(f"error descargando {url}: {r.stderr.decode()}")
    return r.stdout


def main():
    os.makedirs(DESTINO, exist_ok=True)
    css = descargar(API).decode("utf-8")

    # Cada bloque va precedido de un comentario con el nombre del subconjunto.
    bloques = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
    salida, descargados = [], {}

    for subconjunto, bloque in bloques:
        if subconjunto not in SUBCONJUNTOS:
            continue
        familia = re.search(r"font-family:\s*'([^']+)'", bloque).group(1)
        estilo = re.search(r"font-style:\s*(\w+)", bloque).group(1)
        url = re.search(r"url\((https://[^)]+)\)", bloque).group(1)

        nombre = "%s-%s-%s.woff2" % (
            familia.lower().replace(" ", "-"),
            estilo,
            subconjunto,
        )
        if nombre not in descargados:
            datos = descargar(url)
            with open(os.path.join(DESTINO, nombre), "wb") as f:
                f.write(datos)
            descargados[nombre] = len(datos)
            print(f"  {nombre:42s} {len(datos)//1024:4d} KB")

        salida.append(
            re.sub(r"url\(https://[^)]+\)", "url(%s)" % nombre, bloque).strip()
        )

    cabecera = (
        "/* Tipografías auto-alojadas. Generado por scripts/descargar_fuentes.py.\n"
        "   Source Serif 4 y Inter: SIL Open Font License 1.1.\n"
        "   No editar a mano: se regenera con el script. */\n\n"
    )
    with open(os.path.join(DESTINO, "fuentes.css"), "w") as f:
        f.write(cabecera + "\n\n".join(salida) + "\n")

    print(f"\n{len(descargados)} archivos, {sum(descargados.values())//1024} KB en total")


if __name__ == "__main__":
    main()
