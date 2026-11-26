"""
test_data_checksums.py — Valida que el 100% de los CSV coincida con checksums_sha256.txt
"""

import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "src" / "data" / "csv"
CHECKSUMS_FILE = BASE_DIR / "src" / "data" / "checksums_sha256.txt"

EXPECTED_FILES = {
    "wb_precio_oro_cobre_mensual.csv",
    "bce_exportaciones_mensuales.csv",
    "bce_exportaciones_mineras_rubro.csv",
}


def calculate_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_checksums_exist_and_match():
    assert CHECKSUMS_FILE.exists(), "El archivo checksums_sha256.txt no existe"

    expected_hashes = {}
    with open(CHECKSUMS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=1)
            assert len(parts) == 2, f"Linea invalida en checksums: {line}"
            expected_hashes[parts[1].strip()] = parts[0].strip()

    assert set(expected_hashes.keys()) == EXPECTED_FILES, (
        f"Datasets esperados: {sorted(EXPECTED_FILES)}, encontrados: {sorted(expected_hashes.keys())}"
    )

    for filename, expected_sha in expected_hashes.items():
        filepath = CSV_DIR / filename
        assert filepath.exists(), f"El archivo dataset no existe: {filename}"
        actual_sha = calculate_sha256(filepath)
        assert actual_sha.lower() == expected_sha.lower(), (
            f"Hash discrepante para {filename}: esperado {expected_sha}, obtenido {actual_sha}"
        )
