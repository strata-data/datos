#!/usr/bin/env python3
"""
build_engine.py — Strata Data Engine Public Database Loader

Reconstruye de forma autonoma y determinista la base de datos relacional
publica de mineria en Ecuador (SQLite o PostgreSQL) a partir de los datasets
CSV oficiales y el esquema DDL versionado, validando matematicamente cada
archivo contra su huella criptografica SHA-256.

Uso:
    python build_engine.py                    # Construye strata_public.db (SQLite)
    python build_engine.py --verify-only      # Solo valida integridad SHA-256
    python build_engine.py --target postgres  # Construye en PostgreSQL
"""

import argparse
import csv
import hashlib
import os
import sqlite3
import sys
import time
from pathlib import Path

# Definicion del mapeo canonico: archivo CSV -> tabla SQL
CSV_TABLE_MAP = {
    "wb_precio_oro_cobre_mensual.csv": "wb_precio_oro_cobre_mensual",
    "bce_exportaciones_mensuales.csv": "bce_exportaciones_mensuales",
    "bce_exportaciones_mineras_rubro.csv": "bce_exportaciones_mineras_rubro",
}

def calculate_sha256(filepath):
    """Calcula el hash SHA-256 de un archivo en bloques de 64 KB."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def verify_checksums(data_dir, checksums_file):
    """
    Verifica que cada archivo CSV en data_dir coincida exactamente
    con su hash registrado en checksums_sha256.txt.
    """
    if not checksums_file.exists():
        print(f"ERROR: Archivo de checksums no encontrado: {checksums_file}", file=sys.stderr)
        return False, {}

    expected_hashes = {}
    with open(checksums_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                sha, filename = parts[0].strip(), parts[1].strip()
                expected_hashes[filename] = sha

    print(f"Verificando integridad SHA-256 de {len(expected_hashes)} datasets...")
    all_ok = True
    verified = {}

    for filename, expected_sha in sorted(expected_hashes.items()):
        filepath = data_dir / filename
        if not filepath.exists():
            print(f"  FALLA: Archivo faltante: {filename}", file=sys.stderr)
            all_ok = False
            continue

        actual_sha = calculate_sha256(filepath)
        if actual_sha.lower() != expected_sha.lower():
            print(f"  FALLA: Hash discrepante en {filename}", file=sys.stderr)
            print(f"    Esperado: {expected_sha}", file=sys.stderr)
            print(f"    Obtenido: {actual_sha}", file=sys.stderr)
            all_ok = False
        else:
            verified[filename] = actual_sha
            print(f"  OK: {filename:<45} [{actual_sha[:16]}...]")

    return all_ok, verified

def load_csv_rows(filepath):
    """Lee un archivo CSV convirtiendo cadenas vacias a None (NULL)."""
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = []
        for r in reader:
            rows.append([None if val == "" else val for val in r])
    return header, rows

def build_sqlite(db_path, schema_path, views_path, data_dir, verified_files):
    """Construye la base de datos SQLite y carga todos los datasets."""
    # Si la base previa existe, se remueve para garantizar reproducibilidad limpia
    if db_path.exists():
        try:
            os.remove(db_path)
        except OSError as e:
            print(f"ERROR: No se pudo eliminar la base existente: {e}", file=sys.stderr)
            return False

    print(f"\nCreando base SQLite: {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")

    # 1. Aplicar esquema DDL
    print(f"Aplicando esquema DDL: {schema_path}...")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cur.executescript(schema_sql)

    # 2. Ingestar cada dataset CSV
    print("\nIngestando datasets...")
    stats = []

    for filename, table_name in CSV_TABLE_MAP.items():
        filepath = data_dir / filename
        if not filepath.exists():
            print(f"  ALERTA: Archivo no encontrado, saltando: {filename}", file=sys.stderr)
            continue

        header, rows = load_csv_rows(filepath)
        cols_str = ", ".join(header)
        placeholders = ", ".join(["?"] * len(header))
        sql = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"

        t0 = time.time()
        cur.executemany(sql, rows)
        elapsed = time.time() - t0

        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        inserted_count = cur.fetchone()[0]

        if inserted_count != len(rows):
            print(f"ERROR: Discrepancia en {table_name}: {len(rows)} leidas vs {inserted_count} insertadas", file=sys.stderr)
            conn.close()
            return False

        stats.append((table_name, filename, len(rows), elapsed))
        print(f"  Cargado: {table_name:<42} | {len(rows):>6} filas | {elapsed:.3f}s")

    conn.commit()

    # 3. Aplicar vistas SQL si el archivo existe
    if views_path and views_path.exists():
        print(f"\nAplicando vistas publicas: {views_path}...")
        with open(views_path, "r", encoding="utf-8") as f:
            views_sql = f.read()
        cur.executescript(views_sql)
        conn.commit()

    # 4. Estadisticas finales
    db_size_mb = db_path.stat().st_size / (1024 * 1024)
    conn.close()

    print("\n" + "=" * 80)
    print("RESUMEN DE CONSTRUCCION EXITOSA (STRATA DATA ENGINE)")
    print("=" * 80)
    total_filas = sum(s[2] for s in stats)
    for tbl, f_csv, rows, elap in stats:
        print(f"  - Tabla: {tbl:<40} Filas: {rows:>7}  ({f_csv})")
    print("-" * 80)
    print(f"  Total tablas pobladas: {len(stats)}")
    print(f"  Total registros cargados: {total_filas:,}")
    print(f"  Tamano de base de datos: {db_size_mb:.2f} MB")
    print(f"  Destino SQLite: {db_path.resolve()}")
    print("=" * 80)
    return True

def build_postgres(pg_url, schema_path, views_path, data_dir, verified_files):
    """Construye la base de datos en PostgreSQL."""
    try:
        import psycopg2
    except ImportError:
        print("ERROR: El conector 'psycopg2' no esta instalado.", file=sys.stderr)
        print("Instalalo con: pip install psycopg2-binary", file=sys.stderr)
        return False

    print(f"\nConectando a PostgreSQL: {pg_url}...")
    try:
        conn = psycopg2.connect(pg_url)
    except Exception as e:
        print(f"ERROR: No se pudo conectar a PostgreSQL: {e}", file=sys.stderr)
        return False

    cur = conn.cursor()

    # Adaptar DDL basico para Postgres (ej. AUTOINCREMENT -> SERIAL)
    print(f"Aplicando esquema DDL: {schema_path}...")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # Adaptaciones minimas de sintaxis SQLite a PostgreSQL
    schema_pg = schema_sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    cur.execute(schema_pg)
    conn.commit()

    print("\nIngestando datasets en PostgreSQL...")
    stats = []

    for filename, table_name in CSV_TABLE_MAP.items():
        filepath = data_dir / filename
        if not filepath.exists():
            continue

        header, rows = load_csv_rows(filepath)
        cols_str = ", ".join(header)
        placeholders = ", ".join(["%s"] * len(header))
        sql = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"

        t0 = time.time()
        cur.executemany(sql, rows)
        elapsed = time.time() - t0

        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        inserted_count = cur.fetchone()[0]

        stats.append((table_name, filename, len(rows), elapsed))
        print(f"  Cargado: {table_name:<42} | {len(rows):>6} filas | {elapsed:.3f}s")

    conn.commit()

    if views_path and views_path.exists():
        print(f"\nAplicando vistas publicas: {views_path}...")
        with open(views_path, "r", encoding="utf-8") as f:
            views_sql = f.read()
        cur.execute(views_sql)
        conn.commit()

    cur.close()
    conn.close()

    print("\n" + "=" * 80)
    print("CONSTRUCCION EN POSTGRESQL COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    return True

def main():
    base_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Strata Data Engine: Motor de Ingesta y Loader Publico de Datos Mineros de Ecuador"
    )
    parser.add_argument(
        "--target",
        choices=["sqlite", "postgres"],
        default="sqlite",
        help="Motor de base de datos destino (default: sqlite)"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Valida los checksums SHA-256 de los CSV y finaliza sin construir la base"
    )
    parser.add_argument(
        "--db-path",
        default=str(base_dir / "strata_public.db"),
        help="Ruta del archivo SQLite destino (default: strata_public.db en la raiz del repo)"
    )
    parser.add_argument(
        "--pg-url",
        default=os.environ.get("STRATA_PG_URL", "postgresql://localhost:5432/strata_public"),
        help="URL de conexion PostgreSQL (default: variable STRATA_PG_URL o localhost)"
    )
    parser.add_argument(
        "--data-dir",
        default=str(base_dir / "src" / "data" / "csv"),
        help="Directorio con los archivos CSV oficiales"
    )
    parser.add_argument(
        "--checksums",
        default=str(base_dir / "src" / "data" / "checksums_sha256.txt"),
        help="Archivo con los hashes SHA-256 de referencia"
    )
    parser.add_argument(
        "--schema",
        default=str(base_dir / "src" / "schema" / "current" / "strata.schema.sql"),
        help="Archivo DDL del esquema relacional"
    )
    parser.add_argument(
        "--views",
        default=str(base_dir / "sql" / "views_publicas.sql"),
        help="Archivo SQL con las vistas analiticas y de saneamiento"
    )

    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    checksums_file = Path(args.checksums)
    schema_path = Path(args.schema)
    views_path = Path(args.views)
    db_path = Path(args.db_path)

    print("=" * 80)
    print("STRATA DATA ENGINE — LOADER Y CONSTRUCTOR DETERMINISTA")
    print("=" * 80)

    # Paso 1: Verificacion matematica obligatoria de Checksums SHA-256
    ok, verified = verify_checksums(data_dir, checksums_file)
    if not ok:
        print("\nERROR CRITICO: Verificacion de integridad SHA-256 fallida. Proceso abortado.", file=sys.stderr)
        sys.exit(1)

    print("Verificacion de integridad SHA-256 exitosa en todos los datasets.")

    if args.verify_only:
        print("\nModo --verify-only completado. Base de datos no modificada.")
        sys.exit(0)

    # Paso 2: Construccion segun el motor elegido
    if args.target == "sqlite":
        success = build_sqlite(db_path, schema_path, views_path, data_dir, verified)
    else:
        success = build_postgres(args.pg_url, schema_path, views_path, data_dir, verified)

    if not success:
        print("\nERROR: La construccion de la base de datos no pudo completarse.", file=sys.stderr)
        sys.exit(1)

    print("\nProceso finalizado con codigo de salida 0.")

if __name__ == "__main__":
    main()
