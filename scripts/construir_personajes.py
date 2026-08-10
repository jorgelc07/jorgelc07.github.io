#!/usr/bin/env python3
"""
Convierte el resultado de scripts/verificar_personajes.py en la estructura de
datos que consume el generador: content/personajes.json.

Solo se marcan como publicables las entradas cuya autoría quedó verificada por
la firma en el cuerpo del artículo. Las demás se conservan en el archivo con
autoria_verificada=false para no perder el trabajo hecho: quedan como
candidatas, el generador las ignora y aparecen en el informe como pendientes.

El nombre de la persona y su oficio se deducen del título, que en esta serie
sigue siempre la forma:

    «<oficio>, <Nombre de la persona>, es “El/La personaje 10 del día”»

Uso:  python3 scripts/construir_personajes.py
"""
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, "pruebas", "verificacion_personajes.json")
SALIDA = os.path.join(RAIZ, "content", "personajes.json")

# Cola del título, que se descarta: «, es “El personaje 10 del día”» y variantes.
COLA = re.compile(
    r"\s*,?\s*[“\"']?\s*es\s+[“\"']?\s*(?:el|la)\s+personaje\s*10.*$",
    re.I)


def partir_titulo(titulo):
    """Devuelve (persona, oficio) a partir del título de la nota."""
    t = COLA.sub("", titulo).strip().strip(",").strip()
    if "," in t:
        oficio, persona = t.rsplit(",", 1)
        persona, oficio = persona.strip(), oficio.strip()
        # Si al cortar por la última coma la "persona" queda demasiado larga o
        # con minúscula inicial, probablemente el título no sigue el patrón.
        if persona and persona[0].isupper() and len(persona.split()) <= 6:
            return persona, oficio[0].upper() + oficio[1:] if oficio else None
    return t, None


def main():
    with open(ENTRADA, encoding="utf8") as f:
        crudo = json.load(f)

    personajes = []
    for d in crudo:
        if d.get("http") != 200 or not d.get("titulo"):
            continue
        persona, oficio = partir_titulo(d["titulo"])
        personajes.append({
            "persona": persona,
            "descriptor": oficio,
            "titulo": d["titulo"],
            "fecha": d.get("fecha"),
            "anio": d.get("anio"),
            "url": d["url"],
            "fuente": "Página10.com",
            "serie": "Personaje 10",
            "autoria_verificada": bool(d.get("autoria_verificada")),
            "verificada_en": d.get("verificada_en"),
            "evidencia_autoria": d.get("evidencia"),
        })

    personajes.sort(key=lambda x: (x["fecha"] or "", x["persona"]), reverse=True)

    salida = {
        "_comentario": (
            "Colección «Personajes». Cada entrada enlaza al artículo original en "
            "Página10.com: este sitio NO reproduce esos textos. El generador "
            "publica únicamente las entradas con autoria_verificada=true. "
            "Se regenera con scripts/construir_personajes.py a partir de "
            "pruebas/verificacion_personajes.json."),
        "serie": "Personaje 10",
        "fuente": "Página10.com",
        "personajes": personajes,
    }
    with open(SALIDA, "w", encoding="utf8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    ok = sum(1 for p in personajes if p["autoria_verificada"])
    print(f"  {len(personajes)} entradas · {ok} publicables · "
          f"{len(personajes) - ok} pendientes de verificar")
    print(f"  escrito en {os.path.relpath(SALIDA, RAIZ)}\n")
    for p in personajes:
        marca = "✓" if p["autoria_verificada"] else "·"
        print(f"  {marca} {p['anio']}  {p['persona']:38s} {(p['descriptor'] or '')[:52]}")


if __name__ == "__main__":
    main()
