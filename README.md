# Pipeline de Datos Completo: Ingesta → Limpieza → Validación → Carga 
**Asignatura:** Gestión De Datos Para IA  
**Evaluación:** Evaluación Grupal — Unidad 2  

---

## 1. Dominio Elegido y Contexto
El proyecto se enmarca en el dominio de **E-Commerce y Retail**, específicamente enfocado en las transacciones comerciales de una cafetería utilizando el dataset `dirty_cafe_sales.csv`. 

El objetivo de este pipeline es automatizar el procesamiento de los registros de ventas masivas (10,000 filas), los cuales presentan fuentes de contaminación críticas (valores nulos, formatos inconsistentes, errores de texto y fallas semánticas). El pipeline asegura que solo la información con calidad empresarial sea integrada en el repositorio analítico final.

---

## 2. Decisiones Técnicas y Arquitectura

El pipeline fue construido utilizando **Python** y se divide en 4 módulos independientes orquestados por un archivo central, garantizando modularidad y mantenibilidad.

### Etapa 1: Ingesta (`ingesta.py`)
* **Decisión:** Carga el archivo fuente en bruto y genera un reporte estadístico inicial (`shape`, `dtypes`, conteo de nulos) por consola de forma automatizada.
* **Resguardo:** Guarda una copia exacta e intacta en la ruta organizada `/data/raw/` antes de aplicar cualquier alteración, asegurando la idempotencia del proceso.

### Etapa 2: Limpieza y Transformación (`limpieza.py`)
* **Tratamiento de Errores:** Se identificó que los campos numéricos y de fechas venían tipificados como cadenas de texto (`object`) debido a la presencia de "falsos nulos" escritos como strings (`'ERROR'`, `'UNKNOWN'`). Se reemplazaron por `NaN` reales de NumPy para su correcta manipulación.
* **Criterio de Nulos:** Se eliminaron las filas con el campo `Item` nulo por ser una variable crítica de negocio. Los precios faltantes se imputaron dinámicamente utilizando la moda (`mode()`) del precio de cada producto correspondiente. Las variables categóricas vacías se rellenaron con la etiqueta `"No Especificado"`.
* **Transformaciones Aplicadas (Mínimo 3 requeridas):**
  1. *Columna Derivada:* Creación de `Total_Spent_Calculado` mediante la operación matemática estricta `Quantity * Price Per Unit`.
  2. *Normalización de Texto:* Aplicación de métodos `.str.strip().str.title()` sobre la columna `Item` para unificar criterios tipográficos.
  3. *Estandarización de Fechas:* Conversión de la columna `Transaction Date` a formato homogéneo `DateTime` (`AAAA-MM-DD`).

### Etapa 3: Validación Estructural y Semántica (`validacion.py`)
* **Validación Estructural (Pandera):** Se implementó un esquema estricto de control de calidad que valida:
  1. Que `Transaction ID` responda estrictamente a la expresión regular (Regex) `^TXN_\d+$`.
  2. Que `Quantity` sea una variable numérica estrictamente mayor a 0.
  3. Que `Price Per Unit` sea un valor flotante no negativo ($\geq 0$).
* **Validación Semántica (Reglas de Negocio):**
  1. *Regla 1:* Verificación de que el gasto total registrado en la plataforma original no difiera de nuestra columna derivada calculada matemática.
  2. *Regla 2:* Control de seguridad; toda transacción con un monto mayor a \$50 exige obligatoriamente una ubicación (`Location`) válida, rechazando los valores por defecto (`"No Especificado"`).
* **Segregación:** Los registros aprobados se exportan a `/data/validated/`, mientras que los rechazados se envían a `/data/errors/cafe_sales_errors.csv` agregando una columna descriptiva con el motivo exacto del fallo.

### Etapa 4: Carga a Base de Datos (`carga.py`)
* **Decisión:** Se utilizó **SQLite** como motor relacional por su portabilidad y cumplimiento de estándares SQL. Se definió un esquema estructurado con tipos de datos nativos e indexación, estableciendo `transaction_id` como **Primary Key (PK)**.
* **Transacciones ACID:** La inserción masiva se ejecuta encapsulada en un bloque `try-except`. Si el proceso tiene éxito se aplica un `COMMIT` definitivo. Ante cualquier fallo de integridad (como colisión de PK o tipos), se gatilla un `ROLLBACK` absoluto para salvaguardar la consistencia de los datos.
* **Verificación:** Al finalizar la carga, el script realiza consultas SQL de agregación (`SELECT COUNT` y `GROUP BY`) directo en la base de datos para auditar el resultado del proceso de forma transparente.

---

## 📁 Estructura del Proyecto

```text
├── 📁 data/
│   ├── 📁 raw/            # Copia del dataset original intacto
│   ├── 📁 clean/          # Dataset tras la Etapa de Limpieza
│   ├── 📁 validated/      # Registros que aprobaron el control de calidad
│   └── 📁 errors/         # Registros rechazados y archivo .log analítico
├── 📄 dirty_cafe_sales.csv # Dataset original (Fuente)
├── 🐍 ingesta.py          # Script de la Etapa 1
├── 🐍 limpieza.py         # Script de la Etapa 2
├── 🐍 validacion.py       # Script de la Etapa 3
├── 🐍 carga.py            # Script de la Etapa 4
├── 🐍 main.py             # Orquestador maestro del pipeline
└── 📄 README.md           # Documentación técnica del proyecto
