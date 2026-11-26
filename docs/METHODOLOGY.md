# Metodología

**Proyecto:** Strata Data Engine · **Contacto:** strata.data@outlook.com

## 1. Principios
1. **La fuente oficial manda.** Toda cifra publicada sale de un documento oficial identificable. Lo que no está en un documento queda vacío: no se estima ni se interpola.
2. **Extracción determinista.** Las cifras se leen de las tablas o archivos de la institución, con el mismo resultado cada vez que se ejecuta el proceso.
3. **Rectificaciones oficiales.** Si una institución corrige una cifra, se publica la nueva y se registra el documento de la rectificación en `CHANGELOG.md`.

## 2. Tratamiento por fuente
### Banco Central del Ecuador (BCE), comercio exterior y exportaciones mineras
- Fuente: Información Estadística Mensual (`IEM-312-e.xlsx`, cuadro IEM-3.1.2) y Reporte de Minería (`ReporteMinero072026.pdf`).
- Se conservan los valores publicados en miles o millones de dólares según la unidad oficial de cada tabla, junto con la marca de cifras provisionales en `observacion`.
- En `bce_exportaciones_mensuales.csv`, `tipo_periodo` distingue las series anuales (`ANIO`, 2021–2025) de las mensuales (`MES`, ene 2024–jul 2026).

### Banco Mundial (World Bank), precios internacionales de referencia
- Fuente: serie mensual de commodities (`CMO-Historical-Data-Monthly.xlsx`, Pink Sheet).
- Se publican los precios mensuales de referencia para oro (`ORO`, USD/troy oz) y cobre (`COBRE`, USD/mt) desde enero de 2015 hasta septiembre de 2026.

## 3. Privacidad
Ver `docs/PRIVACY.md`.
