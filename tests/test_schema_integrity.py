"""
test_schema_integrity.py — Valida que el DDL cree todas las tablas y vistas sin error
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_FILE = BASE_DIR / "src" / "schema" / "current" / "strata.schema.sql"
VIEWS_FILE = BASE_DIR / "sql" / "views_publicas.sql"

EXPECTED_TABLES = [
    "strata_ledger",
    "wb_precio_oro_cobre_mensual",
    "bce_exportaciones_mensuales",
    "bce_exportaciones_mineras_rubro",
]

EXPECTED_VIEWS = [
    "vw_public_bce_exportaciones_mensuales",
    "vw_public_wb_precio_oro_cobre",
]


def test_schema_creates_tables_and_indices():
    assert SCHEMA_FILE.exists(), "El archivo strata.schema.sql no existe"
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.executescript(schema_sql)

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    created_tables = {r[0] for r in cur.fetchall()}

    for tbl in EXPECTED_TABLES:
        assert tbl in created_tables, f"Tabla esperada no fue creada: {tbl}"

    cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
    created_indices = {r[0] for r in cur.fetchall()}
    assert len(created_indices) >= 6, "Se esperaban al menos 6 indices creados"

    conn.close()


def test_views_apply_cleanly():
    assert VIEWS_FILE.exists(), "El archivo views_publicas.sql no existe"
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    with open(VIEWS_FILE, "r", encoding="utf-8") as f:
        views_sql = f.read()

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.executescript(schema_sql)
    cur.executescript(views_sql)

    cur.execute("SELECT name FROM sqlite_master WHERE type='view'")
    created_views = {r[0] for r in cur.fetchall()}

    for vw in EXPECTED_VIEWS:
        assert vw in created_views, f"Vista esperada no fue creada: {vw}"

    conn.close()
