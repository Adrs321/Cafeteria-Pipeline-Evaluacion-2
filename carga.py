import os
import pandas as pd
import sqlite3
import logging

# Mantenemos el archivo de logs para el hito final (Trazabilidad)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/errors/pipeline.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def ejecutar_carga(path_validated, db_name="cafe_data.db"):
    logging.info("=== INICIANDO ETAPA 4: CARGA A BASE DE DATOS ===")
    
    if not os.path.exists(path_validated):
        logging.error(f"No se encontró el archivo validado en: {path_validated}")
        return
        
    df = pd.read_csv(path_validated)
    
    # 1. Conexión a la Base de Datos SQLite
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    logging.info(f"Conexión exitosa a la base de datos: {db_name}")
    
    try:
        # 2. Crear la estructura de la tabla (Esquema con PK)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas_cafe (
                transaction_id TEXT PRIMARY KEY,
                item TEXT,
                quantity INTEGER,
                price_per_unit REAL,
                total_spent_calculado REAL,
                payment_method TEXT,
                location TEXT,
                transaction_date TEXT
            )
        """)
        
        # Limpiar la tabla por si acaso corres el script varias veces (evitar colisiones de PK)
        cursor.execute("DELETE FROM ventas_cafe")
        
        # 3. Preparar la inserción masiva
        query_insert = """
            INSERT INTO ventas_cafe (
                transaction_id, item, quantity, price_per_unit, 
                total_spent_calculado, payment_method, location, transaction_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Transformar el DataFrame en una lista de tuplas para SQLite
        datos_a_insertar = [
            (
                row['Transaction ID'], row['Item'], int(row['Quantity']), float(row['Price Per Unit']),
                float(row['Total_Spent_Calculado']), row['Payment Method'], row['Location'], row['Transaction Date']
            )
            for idx, row in df.iterrows()
        ]
        
        # Ejecutar la carga dentro de una transacción ACID
        cursor.executemany(query_insert, datos_a_insertar)
        
        # Si todo fue exitoso, hacemos COMMIT
        conn.commit()
        logging.info(f"Transacción EXITOSA. Se cargaron {len(datos_a_insertar)} registros mediante COMMIT.")
        
    except sqlite3.Error as e:
        # Si algo falla (ej. Primary Key duplicada), hacemos ROLLBACK absoluto
        conn.rollback()
        logging.error(f"Transacción RECHAZADA por la BD. Se aplicó ROLLBACK. Error: {e}")
        conn.close()
        return

    # 4. VERIFICACIÓN SQL (Requisito obligatorio de la Rúbrica)
    logging.info("Ejecutando consultas SQL de verificación...")
    
    print("\n" + "="*50)
    print("      VERIFICACIÓN DESDE LA BASE DE DATOS (SQL)")
    print("="*50)
    
    # Consulta 1: Conteo Total
    cursor.execute("SELECT COUNT(*) FROM ventas_cafe")
    total_filas_bd = cursor.fetchone()[0]
    print(f"Resultado de 'SELECT COUNT(*)': {total_filas_bd} registros en la tabla.")
    
    # Consulta 2: Group By (Top 3 productos más vendidos)
    query_group = """
        SELECT item, SUM(quantity) as total_vendido 
        FROM ventas_cafe 
        GROUP BY item 
        ORDER BY total_vendido DESC 
        LIMIT 3
    """
    cursor.execute(query_group)
    top_productos = cursor.fetchall()
    
    print("\nResultado de 'GROUP BY' (Top 3 productos más vendidos):")
    for prod, cant in top_productos:
        print(f" - {prod}: {cant} unidades")
    print("="*50 + "\n")
    
    # Cerrar la conexión de forma segura
    conn.close()
    logging.info("=== ETAPA 4 FINALIZADA CON ÉXITO ===")

if __name__ == "__main__":
    PATH_VALIDATED = "data/validated/cafe_sales_validated.csv"
    ejecutar_carga(PATH_VALIDATED)