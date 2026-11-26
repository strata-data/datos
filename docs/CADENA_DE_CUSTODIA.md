# Cadena de custodia criptográfica

**Cómo Strata garantiza que nadie puede alterar un dato sin que se note, ni siquiera Strata.**

Contacto: strata.data@outlook.com

---

## 1. El problema que resuelve
Una base de datos normal tiene un punto débil: quien la administra puede cambiar una cifra antigua y nadie se entera. Si mañana alguien modifica las exportaciones de un año anterior, o el precio de un mes, el lector no tiene cómo saberlo.

En datos públicos sobre minería, donde hay intereses económicos, ambientales y políticos, eso no es aceptable. Strata resuelve este problema con criptografía: **cada dato queda sellado, y cualquier cambio deja una huella imposible de borrar.**

## 2. La huella digital (SHA-256)
Una huella SHA-256 es un código de 64 caracteres que se calcula a partir del contenido de un archivo. Funciona como una huella dactilar:

- **El mismo archivo siempre da la misma huella.** Cualquier persona, en cualquier computadora, obtiene el mismo resultado.
- **Si cambia una sola letra, un solo número o una coma, la huella cambia por completo.** No se parece en nada a la anterior.
- **No se puede fabricar un archivo distinto que tenga la misma huella.** Es un estándar internacional (FIPS 180-4) y lo usan los bancos, los gobiernos y la firma electrónica.

Ejemplo con el precio del oro de septiembre de 2026 del CSV del Banco Mundial (`4319.00 USD/oz`, puede comprobarlo con cualquier calculadora SHA-256 sobre el texto en UTF-8):

| Contenido | Huella SHA-256 (primeros 8 caracteres) |
|---|---|
| `Oro 2026-09: 4319.00 USD/oz` | `22bad39e…` |
| `Oro 2026-09: 4319.01 USD/oz` | `8eac9e26…` (un centavo de diferencia: otra huella) |

Strata calcula la huella de **cada archivo oficial descargado** (del BCE, el Banco Mundial, etc.) y de **cada dataset que publica**.

## 3. La cadena de bloques
Cada vez que Strata incorpora datos (una "carga"), registra un **bloque** con:

| Campo | Qué guarda |
|---|---|
| Fuente | La institución y el documento oficial (por ejemplo, el cuadro IEM-3.1.2 del BCE) |
| Huella del original | La huella SHA-256 del archivo tal como lo publicó la institución |
| Resultado | Cuántas filas se cargaron y la suma de control de sus valores |
| Estado | ACTIVO, ANULADO o CORRECTIVO (ver la sección 4) |
| Huella del bloque anterior | La huella del bloque previo de la cadena |
| Huella del bloque | La huella de todo lo anterior junto |

La clave es la penúltima fila. **Cada bloque contiene la huella del anterior.** Por eso los bloques forman una cadena:

```
[ Bloque 1 ] ──► [ Bloque 2 ] ──► [ Bloque 3 ] ──► [ Bloque 4 ]
  huella A         contiene A       contiene B       contiene C
                   huella B         huella C         huella D
```

Si alguien altera el bloque 2, su huella cambia. Entonces el bloque 3 ya no coincide, y tampoco el 4. **La alteración se nota en toda la cadena, desde el punto donde ocurrió.** Para esconderla habría que rehacer todos los bloques siguientes, y eso también se detecta (ver la sección 5).

## 4. Correcciones sin borrar: ACTIVO, ANULADO y CORRECTIVO
Las instituciones corrigen sus cifras; por ejemplo, el BCE publica primero cifras provisionales y luego las definitivas. Strata **nunca borra ni sobrescribe** un dato publicado. Lo que hace es dejar constancia:

1. **ACTIVO:** el bloque original, con la cifra que publicó la institución.
2. **ANULADO:** cuando la institución rectifica, se agrega un bloque nuevo que anula al anterior. Indica cuál anula y **por qué**, citando el documento oficial de la rectificación.
3. **CORRECTIVO:** un bloque nuevo con la cifra corregida, que remite a los dos anteriores.

```
[ ACTIVO ]  Exportaciones julio: 545,3 M  (boletín provisional)
     │
     ▼
[ ANULADO ] Anula el bloque anterior. Motivo: boletín definitivo del BCE
     │
     ▼
[ CORRECTIVO ] Exportaciones julio: 548,1 M  (boletín definitivo)
```

(Cifras ilustrativas.) Los datasets vigentes usan la cifra corregida, pero **la historia completa queda a la vista**: cualquier persona puede reconstruir qué se publicó, cuándo cambió y con qué documento oficial.

## 5. Anclaje público: prueba de fecha
Una cadena guardada solo en Strata podría, en teoría, rehacerse completa. Para impedirlo, Strata **ancla** periódicamente la huella del último bloque en una blockchain pública (la de Bitcoin), mediante el protocolo abierto **OpenTimestamps**.

Esto produce una prueba, un archivo `.ots`, que demuestra que **esa cadena exacta existía en esa fecha**. Nadie puede cambiar esa prueba, tampoco Strata. Si alguien rehiciera la cadena después, su huella ya no coincidiría con la anclada.

## 6. Cómo verificarlo usted mismo
No hace falta confiar en Strata. Cualquier persona puede comprobarlo:

1. **Un dataset publicado:** calcule su huella y compárela con `src/data/checksums_sha256.txt`.
   ```bash
   sha256sum src/data/csv/*.csv
   ```
2. **Un archivo oficial:** descárguelo desde la dirección de la institución que registra el bloque, calcule su huella y compárela con la del bloque.
3. **La cadena:** recalcule la huella de cada bloque y compruebe que cada uno contiene la del anterior. Un script del repositorio lo hace en un solo paso.
4. **La fecha:** verifique el archivo `.ots` con cualquier verificador de OpenTimestamps.

Si todo coincide, los datos son exactamente los que Strata registró, en la fecha anclada, y no se tocaron.

## 7. Qué garantiza y qué no
- **Garantiza** que ningún dato se alteró después de registrarse, que las correcciones quedan documentadas y que la fecha de registro es verificable.
- **No garantiza** que la cifra oficial sea correcta: si una institución publica un error, Strata registra fielmente ese error, hasta que la institución lo rectifique. Eso se controla con la verificación de cada dataset contra su fuente.

## 8. Por qué importa
Con esto, los datos públicos de la minería dejan de depender de la confianza en quien los administra. Pasan a ser **verificables por cualquiera**: un periodista, un investigador, una comunidad, una empresa o el propio Estado.

Si trabaja en datos, transparencia, minería o registros verificables y quiere conversar sobre este enfoque, escríbanos a **strata.data@outlook.com**.
