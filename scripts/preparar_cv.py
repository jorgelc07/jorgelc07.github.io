#!/usr/bin/env python3
"""
Genera la copia pública del CV: la misma hoja, pero sin el número de teléfono.

Usa redacción real de PyMuPDF (add_redact_annot + apply_redactions), que borra
los glifos del contenido del PDF. No es un rectángulo encima: si alguien copia
el texto o lo pasa por un extractor, el número ya no está.

El PDF original no se toca: queda en originales/.

Uso:  python3 scripts/preparar_cv.py
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
    print(f"  copia pública en docs/assets/documentos/ "
          f"({os.path.getsize(DESTINO) // 1024} KB)")


if __name__ == "__main__":
    main()
