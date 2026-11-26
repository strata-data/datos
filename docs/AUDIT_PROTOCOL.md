# Protocolo de integridad y verificación

**Proyecto:** Strata Data Engine · **Contacto:** strata.data@outlook.com

## 1. Controles
| Control | Cómo funciona |
|---|---|
| Verificación contra la fuente | Cada dataset se compara con el archivo oficial de su institución: fila por fila cuando es posible, o contra los totales que publica la institución. Las cifras de informes técnicos se comprueban en la página citada del documento. |
| Huella de cada dataset | `src/data/checksums_sha256.txt` guarda la huella SHA-256 de cada CSV publicado. |
| Compuerta de privacidad | Antes de generar las huellas, `build-logic/privacidad.py` revisa todos los CSV. Si encuentra datos personales, la exportación se detiene y no se generan huellas. |
| Huella de los archivos originales | Cada archivo descargado de una institución se registra con su URL, su fecha de descarga y su huella SHA-256. |

## 2. Cómo verificar un dataset descargado
En Linux, macOS o Git Bash:
```bash
sha256sum src/data/csv/*.csv
```
En Windows (PowerShell):
```powershell
Get-FileHash -Algorithm SHA256 .\src\data\csv\*.csv
```
Si cada resultado coincide con `src/data/checksums_sha256.txt`, el archivo es idéntico al publicado.

## 3. Alcance de la huella
La huella SHA-256 prueba que un archivo no cambió. No prueba que la cifra oficial sea correcta: la exactitud respecto de la fuente se controla con la verificación de la sección 1. Los errores de origen corresponden a la institución emisora.
