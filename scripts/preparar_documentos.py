#!/usr/bin/env python3
"""
Prepara los PDF que se publican en el sitio.

1. CV: copia sin el número de teléfono. Usa redacción real de PyMuPDF
   (add_redact_annot + apply_redactions), que borra los glifos del contenido
   del PDF. No es un rectángulo encima: si alguien copia el texto o lo pasa por
   un extractor, el número ya no está. Después lo verifica.

2. PDF de cada nota: se limpian los metadatos, que delatan la versión exacta
   del sistema operativo y el software con que se exportó.

Los PDF originales no se tocan: quedan en originales/.

Uso:  python3 scripts/preparar_documentos.py
"""
import os
import re
import sys

import fitz  # PyMuPDF

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(RAIZ, "originales", "CV - Jorge Luis Congacha.pdf")
DESTINO = os.path.join(RAIZ, "docs", "assets", "documentos", "cv-jorge-luis-congacha.pdf")

# Lo que no debe quedar en la copia pública.
PATRON_TELEFONO = re.compile(r"\+?\d[\d\s\-().]{8,}\d")


# PDF de notas: origen en originales/ -> copia publicada en docs/
NOTAS = [
    ("narino_paz_territorial_coca_otros.pdf",
     "narino-paz-territorial-homicidios-coca.pdf",
     "Nariño: paz territorial, homicidios, coca y otros indicadores"),
    ("nota2_elecciones_coca_violencia/Elecciones_coca_violencia_narino.pdf",
     "elecciones-coca-violencia-mapa-electoral-narino.pdf",
     "Elecciones, coca y violencia: mapa electoral de Nariño"),
]


def limpiar_notas():
    """Quita los metadatos que revelan sistema operativo y software."""
    for origen, destino, titulo in NOTAS:
        ruta_origen = os.path.join(RAIZ, "originales", origen)
        ruta_destino = os.path.join(RAIZ, "docs", "assets", "documentos", destino)
        if not os.path.exists(ruta_origen):
            print(f"  ! no está {origen}, se omite")
            continue
        doc = fitz.open(ruta_origen)
        doc.set_metadata({
            "title": titulo,
            "author": "Jorge Luis Congacha",
            "subject": "Análisis",
            "keywords": "",
            "creator": "",
            "producer": "",
        })
        doc.save(ruta_destino, garbage=4, deflate=True, clean=True)
        doc.close()
        print(f"  {destino}: metadatos limpios "
              f"({os.path.getsize(ruta_destino) // 1024} KB)")


def main():
    doc = fitz.open(ORIGEN)
    borrados = []

    for pagina in doc:
        texto = pagina.get_text()
        for candidato in set(PATRON_TELEFONO.findall(texto)):
            # Evita borrar años, códigos postales o cifras del propio CV.
            digitos = re.sub(r"\D", "", candidato)
            if len(digitos) < 9:
                continue
            for rect in pagina.search_for(candidato.strip()):
                pagina.add_redact_annot(rect, fill=(1, 1, 1))
                borrados.append(candidato.strip())
        pagina.apply_redactions()

    # Metadatos: se conserva lo útil y se limpia lo que delata rutas o software.
    doc.set_metadata({
        "title": "CV — Jorge Luis Congacha",
        "author": "Jorge Luis Congacha",
        "subject": "Hoja de vida",
        "keywords": "economía, investigación, análisis de datos",
        "creator": "",
        "producer": "",
    })

    doc.save(DESTINO, garbage=4, deflate=True, clean=True)
    doc.close()

    # Comprobación: el teléfono no debe poder extraerse de la copia publicada.
    publicado = fitz.open(DESTINO)
    texto_publicado = "".join(p.get_text() for p in publicado)
    publicado.close()

    for numero in set(borrados):
        if re.sub(r"\D", "", numero) in re.sub(r"\D", "", texto_publicado):
            print(f"  ✗ el número {numero} todavía es extraíble", file=sys.stderr)
            sys.exit(1)

    if borrados:
        print(f"  {len(set(borrados))} número(s) de teléfono eliminados: "
              + ", ".join(sorted(set(borrados))))
    else:
        print("  no se encontró ningún teléfono que eliminar")
    print(f"  cv-jorge-luis-congacha.pdf: copia pública "
          f"({os.path.getsize(DESTINO) // 1024} KB)")
    limpiar_notas()


if __name__ == "__main__":
    main()
