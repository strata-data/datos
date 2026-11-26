"""
test_deterministic_build.py — Valida que dos ejecuciones sucesivas del build generen bases identicas
"""

import sqlite3
import tempfile
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from build_engine import build_sqlite, verify_checksums, CSV_TABLE_MAP

EXPECTED_COUNTS = {
    "wb_precio_oro_cobre_mensual": 282,
    "bce_exportaciones_mensuales": 1296,
    "bce_exportaciones_mineras_rubro": 20,
}


def test_deterministic_build_twice():
    data_dir = BASE_DIR / "src" / "data" / "csv"
    checksums_file = BASE_DIR / "src" / "data" / "checksums_sha256.txt"
    schema_path = BASE_DIR / "src" / "schema" / "current" / "strata.schema.sql"
    views_path = BASE_DIR / "sql" / "views_publicas.sql"

    ok, verified = verify_checksums(data_dir, checksums_file)
    assert ok, "Fallo la verificacion de checksums previa al build"

    with tempfile.TemporaryDirectory() as tmpdir:
        db1 = Path(tmpdir) / "run1.db"
        db2 = Path(tmpdir) / "run2.db"

        success1 = build_sqlite(db1, schema_path, views_path, data_dir, verified)
        assert success1, "El primer build fallo"

        success2 = build_sqlite(db2, schema_path, views_path, data_dir, verified)
        assert success2, "El segundo build fallo"

        conn1 = sqlite3.connect(db1)
        conn2 = sqlite3.connect(db2)

        cur1 = conn1.cursor()
        cur2 = conn2.cursor()

        for _filename, table_name in CSV_TABLE_MAP.items():
            cur1.execute(f"SELECT COUNT(*) FROM {table_name}")
            cnt1 = cur1.fetchone()[0]
            cur2.execute(f"SELECT COUNT(*) FROM {table_name}")
            cnt2 = cur2.fetchone()[0]
            assert cnt1 == cnt2, f"Conteo distinto en {table_name}: run1={cnt1}, run2={cnt2}"
            assert cnt1 == EXPECTED_COUNTS[table_name], (
                f"Conteo inesperado en {table_name}: {cnt1} vs {EXPECTED_COUNTS[table_name]}"
            )

        cur1.execute(
            "SELECT * FROM bce_exportaciones_mensuales ORDER BY periodo, tipo_periodo, categoria, tipo, ubicacion"
        )
        rows1 = cur1.fetchall()
        cur2.execute(
            "SELECT * FROM bce_exportaciones_mensuales ORDER BY periodo, tipo_periodo, categoria, tipo, ubicacion"
        )
        rows2 = cur2.fetchall()
        assert rows1 == rows2, "Discrepancia en contenido de bce_exportaciones_mensuales"

        conn1.close()
        conn2.close()
