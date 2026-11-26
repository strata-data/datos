# Strata Data Engine — Datos públicos de la minería en Ecuador

[![Datos: CC BY 4.0](https://img.shields.io/badge/Datos-CC%20BY%204.0-lightgrey.svg)](DATA_LICENSE.md)
[![Código: MIT](https://img.shields.io/badge/C%C3%B3digo-MIT-lightgrey.svg)](LICENSE)

Strata Data Engine reúne en una base relacional reproducible los datos públicos verificados sobre la minería en Ecuador y sus precios internacionales de referencia. Cada cifra procede de una publicación oficial identificable, se normaliza y puede rastrearse hasta su documento de origen.

Web del proyecto: [https://stratadata.app](https://stratadata.app)

> Proyecto técnico independiente, sin fines de lucro y sin afiliación con el Estado ni con empresas mineras. Los datos se presentan tal como los publican sus instituciones y conservan sus términos de uso. Ver [docs/PRIVACY.md](docs/PRIVACY.md) y [docs/DISCLAIMER.md](docs/DISCLAIMER.md).

## 1. Principios
- **La fuente oficial manda.** Toda cifra sale de un documento oficial identificable. Lo que no está en un documento no se estima ni se interpola.
- **Trazabilidad.** Cada dataset indica su institución, documento de origen y huella SHA-256 del archivo oficial en `manifest.json`.
- **Integridad.** Cada archivo publicado tiene su huella SHA-256 verificable en `src/data/checksums_sha256.txt`.
- **Privacidad.** No se publican datos de personas naturales. Ver [docs/PRIVACY.md](docs/PRIVACY.md).

## 2. Inicio rápido: construir la base de datos local

Cualquier persona puede reconstruir la base relacional en local de forma determinista, validando matemáticamente cada archivo contra su huella SHA-256 oficial:

```bash
git clone https://github.com/strata-data/datos.git
cd datos
python build_engine.py
```

Esto genera el archivo `strata_public.db` (SQLite) con las 3 tablas normalizadas y las vistas analíticas públicas.

Opciones del CLI:
```bash
python build_engine.py --verify-only      # Solo valida los checksums SHA-256 sin modificar nada
python build_engine.py --target postgres  # Ingesta en un servidor PostgreSQL local o remoto
python build_engine.py --db-path mi_bd.db # Especifica una ruta personalizada para la base SQLite
```

## 3. Datasets (v2026.11.0)
En `src/data/csv/`:

| Dataset | Institución | Período | Filas | Estado |
|---|---|---|---:|---|
| `bce_exportaciones_mensuales.csv` | Banco Central del Ecuador (BCE) | 2021–2025 anual y ene 2024–jul 2026 mensual | 1.296 | Verificado contra la fuente |
| `bce_exportaciones_mineras_rubro.csv` | Banco Central del Ecuador (BCE) | 2025-T1 a 2026-T2 | 20 | Verificado contra la fuente |
| `wb_precio_oro_cobre_mensual.csv` | Banco Mundial (World Bank) | ene 2015 a sep 2026 | 282 | Verificado contra la fuente |

"Verificado contra la fuente" significa que el dataset se comparó, fila por fila o contra los totales publicados, frente al documento oficial de la institución emisora.

### Vistas públicas
`build_engine.py` aplica `sql/views_publicas.sql` sobre las tablas cargadas. Las pruebas de `tests/test_vistas_publicas.py` comprueban cada vista contra su tabla de origen:

| Vista | Origen | Qué hace |
|---|---|---|
| `vw_public_bce_exportaciones_mensuales` | `bce_exportaciones_mensuales` | Filtra las filas mensuales (`tipo_periodo = 'MES'`). |
| `vw_public_wb_precio_oro_cobre` | `wb_precio_oro_cobre_mensual` | Expone la serie mensual internacional de precios de oro y cobre. |

## 4. Cómo comprobar una huella SHA-256

Cada archivo CSV en `src/data/csv/` tiene su huella registrada en `src/data/checksums_sha256.txt` y en `manifest.json` (y en el verificador de [https://stratadata.app](https://stratadata.app)).

En Linux o macOS:
```bash
sha256sum src/data/csv/*.csv
```

En Windows (PowerShell):
```powershell
Get-FileHash -Algorithm SHA256 src\data\csv\*.csv
```

O mediante el verificador incluido:
```bash
python build_engine.py --verify-only
```

Compare la salida obtenida con `src/data/checksums_sha256.txt`. Si un solo carácter o número cambia, la huella cambia por completo. Ver también [docs/CADENA_DE_CUSTODIA.md](docs/CADENA_DE_CUSTODIA.md) y [docs/AUDIT_PROTOCOL.md](docs/AUDIT_PROTOCOL.md).

## 5. Estructura
```text
datos/
├── build_engine.py                 # CLI de ingesta y construcción local (SQLite / PostgreSQL)
├── docs/                           # AUDIT_PROTOCOL, CADENA_DE_CUSTODIA, DISCLAIMER, METHODOLOGY, PRIVACY
├── sql/                            # Vistas SQL públicas
├── src/
│   ├── data/csv/                   # Datasets normalizados en UTF-8 (LF)
│   ├── data/checksums_sha256.txt   # Huellas SHA-256 oficiales
│   └── schema/current/strata.schema.sql
├── tests/                          # Pruebas automáticas de integridad y vistas
├── CHANGELOG.md
├── DATA_LICENSE.md                 # CC BY 4.0 (datos y esquema)
├── LICENSE                         # MIT (código)
└── manifest.json                   # Linaje oficial y huellas de la versión
```

## 6. Licencia y cita
- **Datos y esquema:** CC BY 4.0. Ver [DATA_LICENSE.md](DATA_LICENSE.md), que explica cómo citar.
- **Código:** MIT. Ver [LICENSE](LICENSE).
- **Datos de instituciones públicas:** conservan los términos de su institución emisora.
