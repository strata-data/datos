-- ==============================================================================
-- STRATA DATA ENGINE — VISTAS PUBLICAS CURADAS Y AUDITADAS (SQL VIEWS)
-- Version: v2026.11.0
-- Proposito: Servir como capa analitica sobre las 3 tablas publicas verificadas.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. VISTA: COMERCIO EXTERIOR MENSUAL (BANCO CENTRAL DEL ECUADOR, IEM-3.1.2)
-- ------------------------------------------------------------------------------

DROP VIEW IF EXISTS vw_public_bce_exportaciones_mensuales;

CREATE VIEW vw_public_bce_exportaciones_mensuales AS
SELECT
    periodo,
    tipo_periodo,
    categoria,
    tipo,
    valor,
    unidad,
    observacion,
    ubicacion,
    archivo,
    archivo_sha256
FROM bce_exportaciones_mensuales
WHERE tipo_periodo = 'MES';

-- ------------------------------------------------------------------------------
-- 2. VISTA: PRECIOS DE REFERENCIA INTERNACIONALES (BANCO MUNDIAL)
-- ------------------------------------------------------------------------------

DROP VIEW IF EXISTS vw_public_wb_precio_oro_cobre;

CREATE VIEW vw_public_wb_precio_oro_cobre AS
SELECT
    periodo,
    mineral_codigo,
    producto,
    unidad,
    valor,
    ubicacion,
    archivo,
    archivo_sha256
FROM wb_precio_oro_cobre_mensual;
