"""
test_vistas_publicas.py — Construye la base publica completa y comprueba que cada
vista de sql/views_publicas.sql funcione y cuadre con su tabla de origen.
"""

from decimal import Decimal
import importlib.util
import sqlite3
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("build_engine", BASE_DIR / "build_engine.py")
build_engine = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_engine)

DATA_DIR = BASE_DIR / "src" / "data" / "csv"
SCHEMA = BASE_DIR / "src" / "schema" / "current" / "strata.schema.sql"
VIEWS = BASE_DIR / "sql" / "views_publicas.sql"


@pytest.fixture(scope="module")
def conn(tmp_path_factory):
    db = tmp_path_factory.mktemp("vistas") / "strata_public.db"
    assert build_engine.build_sqlite(db, SCHEMA, VIEWS, DATA_DIR, {})
    c = sqlite3.connect(db)
    yield c
    c.close()


def uno(conn, sql):
    return conn.execute(sql).fetchone()


def test_toda_vista_definida_se_puede_consultar(conn):
    vistas = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='view'")]
    assert len(vistas) == 2
    for v in vistas:
        assert uno(conn, f"SELECT COUNT(*) FROM {v}")[0] > 0, v


def test_bce_solo_meses_en_vista(conn):
    n_vista = uno(conn, "SELECT COUNT(*) FROM vw_public_bce_exportaciones_mensuales")[0]
    n_tabla = uno(conn, "SELECT COUNT(*) FROM bce_exportaciones_mensuales WHERE tipo_periodo='MES'")[0]
    assert n_vista == n_tabla == 1116


def test_wb_vista_completa(conn):
    assert uno(conn, "SELECT COUNT(*) FROM vw_public_wb_precio_oro_cobre")[0] == 282
