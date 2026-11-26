-- ==============================================================================
-- STRATA DATA ENGINE — RELATIONAL SCHEMA DEFINITION (DDL)
-- Version: current (v2026.11.0)
-- License: Creative Commons Attribution 4.0 International (CC BY 4.0)
-- Author: Strata Data Core (https://github.com/strata-data/datos)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. DOMINIO: CADENA DE CUSTODIA Y AUDITORIA CRIPTOGRAFICA (HASH-CHAINING)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS strata_ledger (
    block_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity VARCHAR(50) NOT NULL,
    dataset_name VARCHAR(100) NOT NULL,
    period_label VARCHAR(20) NOT NULL,
    source_document_url TEXT NOT NULL,
    raw_document_sha256 CHAR(64) NOT NULL,
    records_count INTEGER NOT NULL,
    control_sum_usd NUMERIC(16,2),
    status VARCHAR(16) DEFAULT 'ACTIVE',
    ref_block_id INTEGER REFERENCES strata_ledger(block_id),
    void_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prev_hash CHAR(64) NOT NULL,
    block_hash CHAR(64) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ledger_source ON strata_ledger(source_entity);
CREATE INDEX IF NOT EXISTS idx_ledger_status ON strata_ledger(status);

-- ------------------------------------------------------------------------------
-- 2. DOMINIO: PRECIOS DE REFERENCIA INTERNACIONALES (BANCO MUNDIAL)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS wb_precio_oro_cobre_mensual (
    periodo VARCHAR(10) NOT NULL,
    mineral_codigo VARCHAR(20) NOT NULL,
    producto VARCHAR(50) NOT NULL,
    unidad VARCHAR(30) NOT NULL,
    valor NUMERIC(16,6) NOT NULL,
    ubicacion VARCHAR(100) NOT NULL,
    archivo TEXT NOT NULL,
    archivo_sha256 CHAR(64) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_wb_precio_periodo ON wb_precio_oro_cobre_mensual(periodo);
CREATE INDEX IF NOT EXISTS idx_wb_precio_mineral ON wb_precio_oro_cobre_mensual(mineral_codigo);

-- ------------------------------------------------------------------------------
-- 3. DOMINIO: MACROECONOMIA Y COMERCIO EXTERIOR (BANCO CENTRAL DEL ECUADOR)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS bce_exportaciones_mensuales (
    periodo VARCHAR(10) NOT NULL,
    tipo_periodo VARCHAR(10) NOT NULL,
    categoria TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    valor NUMERIC(18,6) NOT NULL,
    unidad VARCHAR(20) NOT NULL,
    observacion VARCHAR(50),
    ubicacion VARCHAR(100) NOT NULL,
    archivo TEXT NOT NULL,
    archivo_sha256 CHAR(64) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bce_mensuales_periodo ON bce_exportaciones_mensuales(periodo);
CREATE INDEX IF NOT EXISTS idx_bce_mensuales_tipo ON bce_exportaciones_mensuales(tipo_periodo);

CREATE TABLE IF NOT EXISTS bce_exportaciones_mineras_rubro (
    periodo VARCHAR(10) NOT NULL,
    tipo_periodo VARCHAR(15) NOT NULL,
    categoria TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    valor NUMERIC(18,6) NOT NULL,
    unidad VARCHAR(20) NOT NULL,
    observacion VARCHAR(50),
    ubicacion VARCHAR(150) NOT NULL,
    archivo TEXT NOT NULL,
    archivo_sha256 CHAR(64) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bce_rubro_periodo ON bce_exportaciones_mineras_rubro(periodo);
CREATE INDEX IF NOT EXISTS idx_bce_rubro_categoria ON bce_exportaciones_mineras_rubro(categoria);
