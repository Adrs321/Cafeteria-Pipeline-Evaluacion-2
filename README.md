Pipeline de Datos ETL: Cafe Sales
Este proyecto implementa un pipeline de datos ETL (Extracción, Transformación y Carga) automatizado en Python para procesar, limpiar, validar y cargar datos de ventas de una cafetería desde un archivo CSV original (dirty_cafe_sales.csv) hasta una base de datos relacional SQLite (cafe_data.db).

Arquitectura del Proyecto
El flujo de procesamiento se ejecuta de manera secuencial a través de módulos especializados:

ingesta.py ──> limpieza.py ──> validacion.py ──> carga.py
Estructura de Directorios
El sistema organiza los datos en la carpeta /data/ de acuerdo con su estado de madurez en el pipeline:

├── data/
│   ├── raw/         # Copia exacta del archivo origen CSV recibido.
│   ├── clean/       # Datos transformados, imputados y normalizados.
│   ├── validated/   # Registros que aprobaron todas las reglas de calidad de datos.
│   └── errors/      # Registros rechazados por validación y archivo centralizado de logs.
├── ingesta.py       # Módulo de carga inicial y estadísticas descriptivas.
├── limpieza.py      # Módulo de normalización, limpieza e imputación de nulos.
├── validacion.py    # Módulo de validación estructural (Pandera) y semántica (Negocio).
├── carga.py         # Módulo de inserción transaccional en la base de datos SQLite.
├── main.py          # Orquestador del pipeline completo de extremo a extremo.
└── dirty_cafe_sales.csv # Archivo fuente original (Input).
Componentes del Pipeline
1. Ingesta (ingesta.py)
Función: Carga el archivo fuente original dirty_cafe_sales.csv.

Operaciones: * Verifica la existencia del archivo origen.

Calcula y despliega estadísticas iniciales por consola (dimensiones, tipos de datos, conteo de nulos y primeras filas).

Salida: Guarda el dataset sin modificaciones en data/raw/dirty_cafe_sales.csv.

2. Limpieza y Transformación (limpieza.py)
Función: Purifica el dataset crudo y genera variables calculadas.

Operaciones:

Reemplaza cadenas de texto que actúan como falsos nulos ('ERROR', 'UNKNOWN') por valores NaN reales.

Elimina registros críticos que no poseen un valor válido en la columna Item.

Convierte las columnas Quantity y Price Per Unit a tipo numérico de manera forzada.

Imputa valores faltantes en Price Per Unit basándose en la moda del tipo de Item.

Completa valores nulos categóricos con valores por defecto ('No Especificado' y cantidad mínima de 1).

Transformación 1: Crea la columna derivada Total_Spent_Calculado (Quantity * Price Per Unit).

Transformación 2: Normaliza el texto de la columna Item aplicando eliminación de espacios en blanco (strip) y formato de título (title).

Transformación 3: Homogeneiza la columna Transaction Date al tipo DateTime, descartando filas con fechas irreparables.

Salida: Guarda el archivo resultante en data/clean/cafe_sales_clean.csv.

3. Validación Estructural y Semántica (validacion.py)
Función: Evalúa la calidad de los datos registro por registro mediante validaciones multinivel.

Operaciones:

Validación Estructural (Pandera): Aplica un esquema estricto mediante la librería Pandera que comprueba:

Transaction ID: Debe coincidir con la expresión regular ^TXN_\d+$ y no ser nulo.

Quantity: Debe ser estrictamente mayor a 0 y de tipo flotante/numérico.

Price Per Unit: Debe ser mayor o igual a 0 y de tipo flotante/numérico.

Validación Semántica (Reglas de Negocio):

Regla 1: Comprueba que el valor de Total_Spent_Calculado sea idéntico a la multiplicación de la cantidad por el precio unitario, aplicando una tolerancia decimal de 0.01.

Regla 2: Si el monto total calculado supera los $50.0, rechaza transacciones donde la locación figure como 'No Especificado'.

Salida: Separa el flujo de datos en dos archivos:

Aprobados: data/validated/cafe_sales_validated.csv

Rechazados: data/errors/cafe_sales_errors.csv (añade la columna Motivo_Error detallando la falla).

4. Carga a Base de Datos (carga.py)
Función: Almacena los registros validados de forma permanente bajo un modelo relacional.

Operaciones:

Establece conexión con la base de datos local SQLite cafe_data.db.

Crea la estructura de la tabla ventas_cafe definiendo restricciones de tipos y asignando transaction_id como clave primaria (PRIMARY KEY).

Limpia los registros preexistentes de la tabla para evitar duplicidad de llaves en ejecuciones continuas.

Procesa la inserción de datos de manera masiva utilizando executemany bajo una arquitectura transaccional ACID. Si ocurre un error, aplica un ROLLBACK total; si finaliza correctamente, consolida los datos mediante un COMMIT.

Ejecuta consultas SQL de verificación automáticas (COUNT para cuadratura de registros y un GROUP BY para obtener el Top 3 de productos más vendidos).

Trazabilidad y Monitoreo (Logs)
El sistema integra un mecanismo centralizado de logging a través de la librería estándar logging de Python. Todos los módulos comparten la misma configuración, lo que garantiza el seguimiento unificado del proceso.

Destinos: Los eventos se emiten de forma simultánea en la consola estándar del sistema (StreamHandler) y se registran en un archivo físico (FileHandler).

Ruta del Archivo de Log: data/errors/pipeline.log

Formato de Registro: AAAA-MM-DD HH:MM:SS,mmm - LEVEL - Mensaje de proceso

Nivel mínimo configurado: INFO (Registra hitos de inicio, confirmaciones de almacenamiento, estadísticas operacionales, advertencias y excepciones del sistema).

Ejecución del Sistema
Prerrequisitos
Es necesario contar con las librerías de Python requeridas instaladas en el entorno:

Bash
pip install pandas numpy pandera
Ejecución Integral
Para lanzar el proceso ETL completo de forma secuencial, automatizada y con control de errores por etapas, ejecute el archivo orquestador central:

Bash
python main.py
Ejecución Individual
Cada componente está diseñado con un punto de entrada autónomo, permitiendo realizar pruebas unitarias o ejecuciones aisladas sobre sus respectivas carpetas de datos:

Bash
python ingesta.py
python limpieza.py
python validacion.py
python carga.py
