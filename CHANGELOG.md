# Registro de versiones

Versionado por calendario (CalVer), `YYYY.MM.MICRO`:
- `YYYY.MM`: año y mes de la versión.
- `MICRO`: corrección dentro del mismo mes (0, 1, 2…).

Cuando una institución rectifica una cifra ya publicada, la rectificación se anota aquí con el documento oficial que la respalda.

## v2026.11.0
Primera versión pública verificada.

- **Comercio exterior del BCE (`bce_exportaciones_mensuales.csv`):** exportaciones anuales (2021–2025) y mensuales (ene 2024–jul 2026), 1.296 filas.
- **Exportaciones mineras por rubro del BCE (`bce_exportaciones_mineras_rubro.csv`):** desglose por producto y escala (2025-T1 a 2026-T2), 20 filas.
- **Precios internacionales de referencia del Banco Mundial (`wb_precio_oro_cobre_mensual.csv`):** serie mensual de oro y cobre (ene 2015–sep 2026), 282 filas.
- **Integridad y reproducibilidad:** huellas SHA-256 en `src/data/checksums_sha256.txt`, manifiesto con linaje oficial en `manifest.json`, esquema SQL en `src/schema/current/strata.schema.sql`, vistas públicas en `sql/views_publicas.sql` y pruebas automáticas en `tests/`.
