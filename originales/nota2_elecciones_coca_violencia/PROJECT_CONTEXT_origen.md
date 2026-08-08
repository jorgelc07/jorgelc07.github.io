# PROJECT_CONTEXT.md — Análisis Coca, Violencia y Voto en Nariño

> **Última actualización del documento:** 2026-06-09
> **Última actividad del proyecto:** 2026-06-05 17:06 (PDF / DOCX final del artículo)
> **Estado:** Producto editorial finalizado (artículo + nota corta + mapas v3/v4/v5). Pendiente: publicar en Página10 y revisar mapa 09 final.
> **Tipo de proyecto:** Análisis territorial + visualización + nota periodística

---

## 1. Qué es este proyecto

Análisis territorial municipal de Nariño que cruza tres dimensiones:

1. **Cambio electoral de la izquierda** entre la primera vuelta presidencial 2022 (Petro) y la primera vuelta presidencial 2026 (Cepeda).
2. **Coca cultivada** por municipio en 2023 (SIMCI/UNODC).
3. **Tasa de homicidios** municipal en 2025 (PONAL / SIPC MinJusticia).

Produce mapas editoriales, gráficos de dispersión, tablas y un texto periodístico para **Página10.com**.

**Pregunta central:** ¿Coincide territorialmente el voto por la izquierda con la presencia de coca y de violencia? ¿O hay subregiones distintas?

**Conclusión robusta de los datos:**
- El Pacífico cocalero **mejora** la izquierda (Tumaco +14,4 pp; promedio subregional +5,2 pp).
- La cordillera y el piedemonte **pierden** izquierda fuerte (La Llanada −21,3; promedio −10,2 pp).
- Coca por sí sola no predice el voto (r ≈ 0,12 con log ha, n.s.).
- Tasa de homicidios 2025 sí correlaciona, **negativamente**, con el cambio electoral (r ≈ −0,50, p < 0,001).
- Esto es **descriptivo, no causal**. Insiste en lenguaje prudente en el texto.

---

## 2. Ubicación

**Carpeta del proyecto (ruta absoluta):**
```
/Users/jorgeluis/Library/CloudStorage/OneDrive-UniversidaddelosAndes/Escritorio/Otros/Pagina 10/analisis_coca_violencia_elecciones_narino
```

**Carpeta padre** (con el Excel electoral fuente y otros artefactos del proyecto Página 10):
```
/Users/jorgeluis/Library/CloudStorage/OneDrive-UniversidaddelosAndes/Escritorio/Otros/Pagina 10
```

**Git:** NO es repositorio git (`git status` falla). No hay control de versiones; las "versiones" son carpetas `version_*/`.

---

## 3. Productos finales (los más actualizados)

### 3.1 Artículo / nota editorial

| Archivo | Ruta | Descripción |
|---|---|---|
| **Artículo extenso (PDF)** | `Elecciones_coca_violencia_narino.pdf` | Versión final con todas las figuras. Listo para enviar (Jun 5 16:59). |
| **Artículo extenso (DOCX)** | `Elecciones_coca_violencia_narino.docx` | Versión Word (Jun 5 17:06). |
| **Artículo extenso (TeX)** | `articulo_elecciones_coca_violencia_narino.tex` | Fuente LaTeX que compila el PDF anterior. |
| **Nota corta (PDF)** | `nota_coca_violencia_voto_narino.pdf` | Versión más breve, ~Jun 5 11:35. |
| **Nota corta (TeX)** | `nota_coca_violencia_voto_narino.tex` | Fuente LaTeX. |
| Texto markdown v2 (legado) | `texto_analisis_coca_violencia_narino_actualizado_v2.md` | Borrador editorial v2. Reemplazado por las versiones TeX/PDF. |

### 3.2 Mapas y gráficos finales (versiones más recientes)

**Bloque coca (v3, 04-jun 21:14):**
- `02_coca_narino_2023_v3_verde_notas_limpias.png` — paleta verde (no naranja).
- `04_cambio_izquierda_y_coca_narino_2023_v3_leyenda_limpia.png` — leyenda sin solapamientos.
- `07A_dispersion_ha_coca_log_cambio_electoral_2023_v3.png`
- `07B_dispersion_share_coca_cambio_electoral_2023_v3.png`

**Bloque homicidios con tasa oficial SIPC (v3, 04-jun 21:39):**
- `03_violencia_narino_2025_v3_tasa_fuente_notas_limpias.png`
- `05_cambio_izquierda_y_violencia_narino_2025_v3_rombos_azules.png` — rombos azules (cambio de color desde el rojo vino v2).
- `06_resumen_subregional_narino_actualizado_v3_notas_limpias.png`
- `08_dispersion_violencia_cambio_electoral_2025_v3_tasa_fuente.png`

**Mapa combinado (más reciente):**
- `09_cambio_izquierda_coca_homicidios_narino_v5_tumaco_homicidios_visible.png` (Jun 5 11:32) — versión v5 del mapa triple Δ + coca + homicidios.

**Mapa 01 (sin cambios desde v2):**
- `01_cambio_izquierda_narino.png` (Jun 4 12:55, geometría GADM detallada).

### 3.3 Tablas y datos finales (más recientes)

| Archivo | Descripción |
|---|---|
| `tabla_municipios_coca_violencia_elecciones_actualizada_v3.csv` | Tabla completa 64 mpios × variables (Jun 4 21:39). |
| `resumen_subregional_actualizado_v3.csv` | Promedios por 5 subregiones. |
| `ranking_municipios_interes_actualizado_v3.csv` | Top de mpios por categoría (sube+coca alta, etc.). |
| `tasa_homicidio_sipc_narino_2025.csv` | **Tasa oficial SIPC** descargada desde PowerBI MinJusticia. Validada (Policarpa = 114,99). |
| `tasa_homicidio_sipc_narino_2025.xlsx` | Misma tabla en Excel. |
| `validacion_tasa_sipc_2025.csv` | Comparación tasa SIPC vs tasa recalculada con DANE 2025. |
| `validacion_tasas_homicidio_2025.csv` | Comparación tasa CEDE 2023 (v1) vs DANE 2025 (v2). |
| `poblacion_dane_2025_narino.csv` | Proyecciones DANE 2025 por municipio (insumo). |
| `homicidios_narino_2025.csv` | Conteo de homicidios PONAL 2025 desde Datos Abiertos Colombia. |

---

## 4. Scripts (orden de aparición)

| Script | Fecha | Rol |
|---|---|---|
| `script_coca_violencia_elecciones_narino.py` | Jun 1 | **v1**: versión original 2022 (coca + violencia CEDE 2022, geometría GADM). |
| `script_coca_violencia_elecciones_narino_actualizado.py` | Jun 3 | **v1.5**: actualización a coca 2023 + homicidios 2025 PONAL. Usó shapefile DIVIPOLA (simplificado). Tasa con pobl_tot CEDE 2023. |
| `script_coca_violencia_elecciones_narino_actualizado_v2.py` | Jun 4 | **v2**: volvió a GADM 4.1 detallado; denominador DANE 2025; mapa 09 combinado; rombos en violencia; área directamente proporcional en coca. |
| `script_ajustes_v3_coca.py` | Jun 4 21:14 | **v3 coca**: paleta verde para mapa 02; leyenda mapa 04 limpia; ajustes en scatter 07A/07B. |
| `script_ajustes_v3_homicidios.py` | Jun 4 21:39 | **v3 homicidios**: usa `tasa_homicidio_sipc_narino_2025.csv` (oficial SIPC); regenera 03, 05, 06, 08; produce tablas v3. |
| `script_ajuste_v4_mapa09.py` | Jun 4 21:51 | **v4 mapa 09**: reordena capas (círculos coca encima de rombos homicidios) y leyendas (abajo lado a lado). |

> **Nota:** No hay un script v5 visible. El archivo `09_..._v5_tumaco_homicidios_visible.png` (Jun 5 11:32) probablemente se generó modificando `script_ajuste_v4_mapa09.py` antes de compilar el artículo. **Pendiente por confirmar.**

---

## 5. Archivos fuente / insumos externos

| Recurso | Ruta | Descripción |
|---|---|---|
| Excel electoral | `/Users/jorgeluis/Library/CloudStorage/OneDrive-UniversidaddelosAndes/Escritorio/Otros/Pagina 10/cepeda26-vs-petro22_bol67.xlsx`, hoja `Municipios` | Datos Cepeda 2026 vs Petro 2022 (boletín #67). |
| Stata `.dta` coca + pobl_CEDE | `/Users/jorgeluis/Library/CloudStorage/OneDrive-UniversidaddelosAndes(2)/Uniandes/Jorge/Tesis/Regresiones/Regresiones Stata/Regresiones 2026/Material replicable TESIS-final/01_version_interna_completa/01_data/master/Base_master_2026_robustez.dta` | 76 MB. Coca 2023 + población CEDE. Se copia a `/tmp/Base_master_2026_robustez.dta` por OneDrive Files-On-Demand. |
| Shapefile DIVIPOLA (no se usa en v2/v3) | mismo proyecto Stata, carpeta `01_data/ancillary/shp_municipios_divipola/` | Solo 58 vértices/mpio. **Reemplazado por GADM**. |
| GADM 4.1 | `/tmp/gadm41_COL_2.json` | Geometría detallada (134 vértices/mpio). Usado por v1, v2, v3. |
| DANE proyecciones | `/tmp/DANE_proyecciones_mpio_2018_2042.xlsx` (descarga directa DANE) | Población municipal 2025. |
| Datos Abiertos Colombia | `https://www.datos.gov.co/resource/m8fd-ahd9.json` | Dataset HOMICIDIO (PONAL). Endpoint Socrata. |
| Tasa SIPC PowerBI | descarga manual desde [dashboard MinJusticia](https://app.powerbi.com/view?r=eyJrIjoiNTg1YTNkMGMtNzQ3Yi00ZDcxLWJkNmItYmMxNGVhMjEzZWUzIiwidCI6ImZiMWVmYmNkLWJlMzctNDIzOC04NGQyLTRmYWMyYzc1NTFkYyIsImMiOjR9) | Eventualmente sí se logró extraer (cómo: **pendiente por confirmar**, probablemente "Exportar datos" del visual). Resultado: `tasa_homicidio_sipc_narino_2025.csv`. |

---

## 6. Subregiones (clasificación territorial usada en todos los gráficos)

5 subregiones de Nariño, por código DIVIPOLA oficial DANE 2025:

| Subregión | n mpios | Color en gráficos |
|---|---:|---|
| Pacífico | 10 | `#2166AC` azul oscuro |
| Telembí-Piedemonte | 2 | `#74ADD1` azul claro |
| Cordillera | 12 | `#D73027` rojo |
| Centro-Pasto | 17 | `#FDB863` naranja |
| Sur-Frontera | 23 | `#ABDDA4` verde claro |

El dict `SUBREGIONES` en el script v2 fue corregido respecto a las versiones anteriores (Sandoná, Sapuyes, Guaitarilla, Consacá pasaron a Sur-Frontera donde corresponden geográficamente).

---

## 7. Decisiones técnicas tomadas (importante para retomar)

### 7.1 Geometría
- **Usar GADM 4.1** (`/tmp/gadm41_COL_2.json`), **no** el shapefile DIVIPOLA del proyecto Stata. Razón: GADM tiene 2,3× más vértices y conserva los bordes curvos del Pacífico que la edición simplificada del DIVIPOLA pierde.
- **No** aplicar `simplify()`, `tolerance`, `preserve_topology=False`, ni reproyectar con CRS que reduzca detalle.

### 7.2 Tasa de homicidios 2025
- **Final (v3): usar tasa SIPC oficial** desde `tasa_homicidio_sipc_narino_2025.csv` (extraída del PowerBI MinJusticia). Policarpa = 114,99 ✓.
- v2 alternativa (recalculada con DANE 2025): conteo PONAL ÷ DANE × 100.000. Da Policarpa = 131,73 (diferencia 16,7 pp con SIPC porque SIPC usa proyecciones poblacionales internas distintas y/o conteo 12 vs 13). Solo usar como fallback si no hay acceso a la cifra SIPC.
- v1 (recalculada con pobl_tot CEDE 2023): **deprecada** porque sobreestima ~15 % respecto a SIPC.

### 7.3 Símbolos en los mapas combinados
- **Mapa 04 (coca)**: círculos rojos (`#E63946` con borde `#7A1F1F`, alpha 0,55). Área directamente proporcional a hectáreas: `s = ha * 0.06`. Tumaco ≈ 2,5× más grande que El Charco.
- **Mapa 05 (violencia)**: **rombos** (`marker="D"`) en color **azul** en v3 (en v2 era vino oscuro `#5C0E1A`). Área proporcional a la tasa. El cambio a azul fue parte de los "ajustes v3" para diferenciar mejor coca y violencia.
- **Mapa 09 (triple combinado)**: capas reordenadas en v4 (rombos detrás, círculos delante). Leyendas abajo lado a lado.

### 7.4 Lenguaje editorial
- **NUNCA** afirmar causalidad: "la coca explica el voto", "la violencia tumbó a la izquierda", "los municipios cocaleros votaron por X".
- **SÍ** decir: "coincidencia territorial", "patrón regional", "los datos abren preguntas", "no se puede inferir causalidad con estos datos descriptivos".

### 7.5 Memoria recordatoria sobre OneDrive
> El usuario ya tiene en su memoria global este recordatorio:
> **"Copiar archivos a /tmp antes de OCR/proceso largo: OneDrive desaloja a la nube a mitad de corrida (PermissionError)"**.
> Aplica a `Base_master_2026_robustez.dta` y al Excel DANE; **siempre** copiar a `/tmp/` antes de procesar.

---

## 8. Errores resueltos en el camino (para no repetir)

| Problema | Cómo se resolvió |
|---|---|
| PowerBI MinJusticia no scrapeable por WebFetch (JS-rendered) | Fallback a Socrata `m8fd-ahd9` + DANE 2025 (v2). Luego eventualmente se descargó la tasa SIPC directamente (v3). |
| SSL CertVerificationError al llamar a `datos.gov.co` | Usar `ssl.create_default_context()` con `check_hostname=False` y `verify_mode=ssl.CERT_NONE`. |
| Catastrophic regex backtracking al consolidar archivos | (Era del proyecto Tesis, no de Nariño). Reemplazar regex DOTALL por procesamiento línea a línea. |
| GADM no trae `cod_mpio` numérico | Construir `GADM_TO_DIVIPOLA` con nombres normalizados validados contra DANE. |
| Tumaco no cruzaba electoral ↔ Stata | El alias `ELEC_KEY_ALIAS` debe convertir `"SANANDRESDETUMACO"` → `"TUMACO"`. También `CUASPUDCARLOSAMA` y `ELTABLONDEGOMEZ`. |
| Round 1 v1 reportó Pacífico +5,2 pp; ronda intermedia bajó a +4,2 al perderse Tumaco en el merge | Resuelto al añadir los 3 alias de arriba. Vuelve a +5,2 pp. |
| Códigos DIVIPOLA mal asignados (Consacá, Sapuyes, Guaitarilla) en el script original | Reemplazado por dict oficial DANE en v2. |

---

## 9. Qué NO tocar / precauciones

- **NO borrar** ninguna carpeta `version_*/`. Son backups intencionales:
  - `version_anterior_2022/` — análisis original con datos 2022.
  - `version_actual_antes_ajustes_geometria_simbolos/` — antes de v2 (geometría detallada + DANE).
  - `version_antes_ajustes_finales_notas_fuentes/` — antes de v3 (leyendas/fuentes finales).
- **NO modificar** el Excel electoral fuente `/Users/jorgeluis/.../cepeda26-vs-petro22_bol67.xlsx`. Es lectura solamente.
- **NO modificar** la base Stata `Base_master_2026_robustez.dta` (es de la tesis; archivo distinto y crítico).
- **NO** asumir que GADM trae `cod_mpio` — solo nombres. Usar el dict `GADM_TO_DIVIPOLA` validado.
- **NO** confiar en los nombres del shapefile DIVIPOLA viejo del script original: tenía códigos desfasados (52203/52378/52694 estaban mal).
- **NO** publicar afirmaciones causales en la nota.

---

## 10. Pendientes (al cerrar esta sesión)

1. **Pendiente por confirmar**: cómo exactamente se descargó la tasa oficial SIPC del PowerBI (no hay script automatizado visible; probablemente fue manual desde el botón "Exportar datos" del visual). Documentar el procedimiento para que sea reproducible.
2. **Pendiente por confirmar**: si el mapa 09 v5 (`_v5_tumaco_homicidios_visible.png`) sustituye al v4 en el artículo final. Buscar en `articulo_elecciones_coca_violencia_narino.tex` qué archivo se inserta.
3. Publicar el artículo en Página10.com (no hay evidencia de publicación en el proyecto).
4. Considerar si hace falta un texto markdown v3 explícito; actualmente el más reciente es v2 (Jun 4 14:25) y el editorial final vive en `.tex/.pdf/.docx`.

---

## 11. Comandos útiles para retomar

```sh
# 1. Ir a la carpeta del proyecto
cd "/Users/jorgeluis/Library/CloudStorage/OneDrive-UniversidaddelosAndes/Escritorio/Otros/Pagina 10/analisis_coca_violencia_elecciones_narino"

# 2. Ver últimos archivos modificados
ls -lt | head -20

# 3. Copiar insumos pesados a /tmp (OneDrive descarga bajo demanda)
cp "/Users/jorgeluis/Library/CloudStorage/OneDrive-UniversidaddelosAndes(2)/Uniandes/Jorge/Tesis/Regresiones/Regresiones Stata/Regresiones 2026/Material replicable TESIS-final/01_version_interna_completa/01_data/master/Base_master_2026_robustez.dta" /tmp/

# 4. Re-correr v3 coca (si hace falta regenerar mapas de coca)
python3 script_ajustes_v3_coca.py

# 5. Re-correr v3 homicidios (si hace falta regenerar mapas de violencia con tasa SIPC)
python3 script_ajustes_v3_homicidios.py

# 6. Re-correr el mapa 09 ajustado v4 (capas y leyendas)
python3 script_ajuste_v4_mapa09.py

# 7. Recompilar el artículo final
pdflatex articulo_elecciones_coca_violencia_narino.tex
pdflatex articulo_elecciones_coca_violencia_narino.tex   # segunda pasada

# 8. Recompilar nota corta
pdflatex nota_coca_violencia_voto_narino.tex
```

---

## 12. Dependencias Python (versión 3.13 probada)

```
pandas
numpy
matplotlib
scipy
geopandas
shapely
fiona
openpyxl
```

Para Stata `.dta` se usa `pandas.read_stata` (ya viene con pandas). No requiere Stata instalado.

---

## 13. Instrucción para reabrir el proyecto en Claude Code

Cuando vuelvas, abre Claude Code y di:

> "Vamos a continuar con el proyecto de Nariño. Lee `PROJECT_CONTEXT.md` en `/Users/jorgeluis/Library/CloudStorage/OneDrive-UniversidaddelosAndes/Escritorio/Otros/Pagina 10/analisis_coca_violencia_elecciones_narino/`. Dime cuál es el último archivo modificado y cuál es el siguiente paso recomendado."

Claude debería:
1. Leer este `PROJECT_CONTEXT.md`.
2. Hacer `ls -lt` para ver el último archivo modificado.
3. Confirmar el estado del artículo final y proponer si se publica, se ajusta el mapa 09 v5, o se hace alguna nueva iteración.
