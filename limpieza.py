import os
import pandas as pd
import numpy as np
import logging

# Seguimos usando el mismo archivo de logs para mantener la trazabilidad (10 pts)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/errors/pipeline.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def ejecutar_limpieza(path_raw, carpeta_destino):
    logging.info("=== INICIANDO ETAPA 2: LIMPIEZA Y TRANSFORMACIÓN ===")
    
    # 1. Cargar el dataset de la etapa anterior
    df = pd.read_csv(path_raw)
    filas_iniciales = len(df)
    
    # 2. Reemplazar "Falsos Nulos" de texto por NaN reales
    falsos_nulos = ['ERROR', 'UNKNOWN', 'error', 'unknown']
    df = df.replace(falsos_nulos, np.nan)
    
    # 3. Limpieza de filas críticas (Item)
    df = df.dropna(subset=['Item'])
    logging.info(f"Se eliminaron {filas_iniciales - len(df)} filas por no tener un 'Item' válido.")
    
    # 4. Convertir tipos de datos a numéricos para poder operar (forzando errores a NaN)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['Price Per Unit'] = pd.to_numeric(df['Price Per Unit'], errors='coerce')
    
    # Imputar precios faltantes (agrupando por Item y sacando el valor más común o la media)
    df['Price Per Unit'] = df.groupby('Item')['Price Per Unit'].transform(lambda x: x.fillna(x.mode()[0] if not x.mode().empty else 0))
    
    # Imputar nulos en columnas categóricas
    df['Payment Method'] = df['Payment Method'].fillna('No Especificado')
    df['Location'] = df['Location'].fillna('No Especificado')
    df['Quantity'] = df['Quantity'].fillna(1) # Si no hay cantidad, asumimos mínimo 1
    
    # --- APLICANDO LAS 3 TRANSFORMACIONES REQUERIDAS ---
    
    # Transformación 1: Columna Derivada (Total Real Calculado)
    df['Total_Spent_Calculado'] = df['Quantity'] * df['Price Per Unit']
    logging.info("Transformación 1 aplicada: Columna derivada 'Total_Spent_Calculado' creada.")
    
    # Transformación 2: Normalización de cadenas de texto
    df['Item'] = df['Item'].astype(str).str.strip().str.title()
    logging.info("Transformación 2 aplicada: Texto en columna 'Item' normalizado (Strip + Title).")
    
    # Transformación 3: Estandarización de formato de Fechas
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], errors='coerce')
    # Eliminar registros con fechas completamente corruptas irreparables
    df = df.dropna(subset=['Transaction Date'])
    logging.info("Transformación 3 aplicada: Columna 'Transaction Date' convertida a formato DateTime homogéneo.")
    
    # 5. Guardar el dataset limpio en /data/clean/
    os.makedirs(carpeta_destino, exist_ok=True)
    path_destino_final = os.path.join(carpeta_destino, "cafe_sales_clean.csv")
    df.to_csv(path_destino_final, index=False, encoding='utf-8')
    
    print("\n" + "="*50)
    print("      RESUMEN DE LA LIMPIEZA (ETAPA 2)")
    print("="*50)
    print(f"Filas originales recibidas: {filas_iniciales}")
    print(f"Filas limpias resultantes:  {len(df)}")
    print(f"Filas descartadas en total: {filas_iniciales - len(df)}")
    print(f"Nulos actuales en el dataframe:\n{df.isnull().sum()}")
    print("="*50 + "\n")
    
    logging.info(f"Dataset limpio guardado en: {path_destino_final}")
    logging.info("=== ETAPA 2 FINALIZADA CON ÉXITO ===\n")
    
    return df

if __name__ == "__main__":
    # Ejecución en modo individual para pruebas
    PATH_RAW = "data/raw/dirty_cafe_sales.csv"
    CARPETA_CLEAN = "data/clean/"
    ejecutar_limpieza(PATH_RAW, CARPETA_CLEAN)