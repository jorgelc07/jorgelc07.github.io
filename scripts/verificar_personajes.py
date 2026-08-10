#!/usr/bin/env python3
"""
Consulta las notas de la serie «Personaje 10» en Página10.com y comprueba la
autoría antes de enlazarlas desde el sitio.

Por qué hace falta: Página10 publica estas notas con el autor genérico
«Columnista Invitado» en los metadatos. La firma real está dentro del cuerpo,
en una línea del tipo «Por: Jorge Luis Congacha Yunda». Este script busca esa
firma y solo marca como verificada la nota que la lleva.

De cada URL extrae: estado HTTP, título, fecha de publicación, sección, el
autor declarado en los metadatos y la firma encontrada en el cuerpo.

Es deliberadamente lento (una petición cada PAUSA segundos, en serie) para no
castigar un sitio ajeno.

Uso:  python3 scripts/verificar_personajes.py             (lee urls_personajes.txt)
      python3 scripts/verificar_personajes.py URL [URL…]
"""
import html
import json
import os
import re
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTA = os.path.join(RAIZ, "content", "urls_personajes.txt")
SALIDA = os.path.join(RAIZ, "pruebas", "verificacion_personajes.json")

PAUSA = 2.5          # segundos entre peticiones a Página10
PAUSA_ARCHIVO = 4    # segundos entre sondeos al Internet Archive
ANIOS_ARCHIVO = ("2019", "2020", "2021", "2018", "2022", "2023", "2025")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Variantes inequívocas del nombre. Se exige que aparezcan precedidas de una
# marca de firma ("Por:", "Escrito por", …) para no dar por buena una simple
# mención dentro del texto.
NOMBRE = r"Jorge\s+Luis\s+Congacha(?:\s+Yunda)?"
FIRMA = re.compile(
    r"(?:Por|POR|Escrito por|Redacci[óo]n de|Texto de)\s*:?\s*(" + NOMBRE + r")",
    re.I)
MENCION = re.compile(NOMBRE, re.I)


def pedir(url):
    r = subprocess.run(
        ["curl", "-sS", "-L", "-A", UA, "-w", "\n@@HTTP:%{http_code}", url],
        capture_output=True, timeout=90)
    salida = r.stdout.decode("utf8", "ignore")
    estado = 0
    m = re.search(r"@@HTTP:(\d+)\s*$", salida)
    if m:
        estado = int(m.group(1))
        salida = salida[:m.start()]
    return estado, salida


def texto_plano(h):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def meta(h, patron):
    m = re.search(patron, h, re.I)
    return html.unescape(m.group(1)).strip() if m else None


def analizar(url):
    estado, h = pedir(url)
    d = {"url": url, "http": estado}
    if estado != 200 or not h:
        d["error"] = f"respuesta HTTP {estado}"
        return d

    d["titulo"] = (meta(h, r'<meta property="og:title" content="([^"]*)"')
                   or meta(h, r"<title>([^<]*)</title>") or "").split(" | ")[0].strip()
    fecha = meta(h, r'<meta property="article:published_time" content="([^"]*)"')
    if fecha:
        d["fecha"] = fecha[:10]
        d["anio"] = int(fecha[:4])
    d["seccion"] = meta(h, r'<meta property="article:section" content="([^"]*)"')
    d["autor_metadatos"] = meta(h, r'<meta name="author" content="([^"]*)"')

    t = texto_plano(h)
    firma = FIRMA.search(t)
    if firma:
        d.update(comprobante(t, firma, "página en vivo"))
        return d

    # Desde 2026 Página10 dejó estas notas tras un muro de pago y solo muestra
    # el primer párrafo. La firma va al FINAL del artículo, así que en el
    # extracto público no aparece. Se recurre al Internet Archive, que guardó
    # las páginas completas de 2019, antes del muro. Es gratuito y público.
    hw, detalle = captura_wayback(url)
    if hw:
        d["archivo_consultado"] = detalle
        tw = texto_plano(hw)
        firma_w = FIRMA.search(tw)
        if firma_w:
            d.update(comprobante(tw, firma_w, f"Internet Archive, {detalle}"))
            return d
        d["motivo_sin_verificar"] = f"la {detalle} no lleva firma"
    else:
        d["motivo_sin_verificar"] = detalle

    d["firma_en_cuerpo"] = None
    d["autoria_verificada"] = False
    d["evidencia"] = ("el nombre aparece en la página, pero no como firma"
                      if MENCION.search(t) else None)
    return d


def comprobante(t, firma, origen):
    ini = max(0, firma.start() - 70)
    return {
        "firma_en_cuerpo": firma.group(1),
        "autoria_verificada": True,
        "verificada_en": origen,
        "evidencia": "…" + t[ini:firma.end() + 15].strip() + "…",
    }


def captura_wayback(url):
    """
    Devuelve (html, descripcion) de una captura archivada, o (None, motivo).

    Se pide directamente https://web.archive.org/web/<año>id_/<url>, que
    redirige a la captura más cercana a ese año. Se probó primero la API CDX,
    pero limita con dureza y, en vez de un error, devuelve una lista vacía
    idéntica a «esta página nunca se archivó»: con eso se descartaban notas que
    sí existían. Este camino distingue bien los dos casos, porque una URL no
    archivada responde 404 de verdad.

    El orden de los años empieza por los cercanos a la publicación, que es
    cuando es más probable que exista captura.
    """
    for anio in ANIOS_ARCHIVO:
        estado, h = pedir(f"https://web.archive.org/web/{anio}id_/{url}")
        if estado == 200 and len(h) > 2000:
            return h, f"captura de {anio}"
        time.sleep(PAUSA_ARCHIVO)
    return None, "no hay ninguna captura en el Internet Archive"


def main():
    urls = sys.argv[1:]
    if not urls:
        with open(LISTA, encoding="utf8") as f:
            urls = [l.strip() for l in f
                    if l.strip() and not l.startswith("#")]

    print(f"Consultando {len(urls)} URL, una cada {PAUSA}s\n")
    res = []
    for i, url in enumerate(urls, 1):
        if i > 1:
            time.sleep(PAUSA)
        d = analizar(url)
        res.append(d)
        marca = "✓" if d.get("autoria_verificada") else ("·" if d["http"] == 200 else "✗")
        origen = d.get("verificada_en", "")
        print(f"  {marca} [{i:2d}/{len(urls)}] {d['http']}  {d.get('anio','----')}  "
              f"{(d.get('titulo') or url)[:60]}")
        if d.get("autoria_verificada"):
            print(f"       firma «{d['firma_en_cuerpo']}» · vía {origen}")
        elif d["http"] == 200:
            print(f"       SIN VERIFICAR · metadatos: {d.get('autor_metadatos')}"
                  f" · {d.get('motivo_sin_verificar','')}")

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    ok = sum(1 for d in res if d.get("autoria_verificada"))
    vivo = sum(1 for d in res if d.get("verificada_en") == "página en vivo")
    arch = sum(1 for d in res if (d.get("verificada_en") or "").startswith("Internet"))
    print(f"\n  {ok}/{len(res)} con autoría verificada por firma en el cuerpo"
          f"  ({vivo} en la página en vivo, {arch} vía Internet Archive)")
    print(f"  detalle en {os.path.relpath(SALIDA, RAIZ)}")


if __name__ == "__main__":
    main()
