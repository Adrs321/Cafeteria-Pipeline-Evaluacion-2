import os
import pandas as pd
import logging

# Configuración básica del sistema de logs (Trazabilidad)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/errors/pipeline.log", encoding='utf-8'), # Guarda registros aquí
        logging.StreamHandler() # Muestra logs también por consola
    ]
)

def ejecutar_ingesta(path_origen, carpeta_destino):
    """
    Carga el dataset, calcula estadísticas iniciales y guarda una copia raw.
    """
    logging.info("=== INICIANDO ETAPA 1: INGESTA DE DATOS ===")
    
    # Verificar que el archivo original existe
    if not os.path.exists(path_origen):
        logging.error(f"No se encontró el archivo de origen en: {path_origen}")
        return None

    # 1. Cargar el dataset desde la fuente original (CSV)
    logging.info(f"Cargando datos desde: {path_origen}")
    df = pd.read_csv(path_origen)
    
    # 2. Calcular y mostrar estadísticas iniciales 
    logging.info("Calculando estadísticas iniciales del Raw Dataset...")
    
    print("\n" + "="*50)
    print("      ESTADÍSTICAS INICIALES (RAW DATA)")
    print("="*50)
    print(f"Dimensiones del dataset (Shape): {df.shape[0]} filas, {df.shape[1]} columnas")
    print("\n--- Tipos de Datos (dtypes) ---")
    print(df.dtypes)
    print("\n--- Conteo de Valores Nulos por Columna ---")
    print(df.isnull().sum())
    print("\n--- Primeras 3 filas del dataset ---")
    print(df.head(3))
    print("="*50 + "\n")
    
    
    os.makedirs(carpeta_destino, exist_ok=True)
    path_destino_final = os.path.join(carpeta_destino, "dirty_cafe_sales.csv")
    
    df.to_csv(path_destino_final, index=False, encoding='utf-8')
    logging.info(f"Copia del Raw Dataset guardada exitosamente en: {path_destino_final}")
    logging.info("=== ETAPA 1 FINALIZADA CON ÉXITO ===\n")
    
    return df

if __name__ == "__main__":
    # Asegurar que exista la carpeta de errores para guardar el archivo .log inicial
    os.makedirs("data/errors", exist_ok=True)
    
    # Definición de rutas de archivos
    RUTA_ORIGEN = "dirty_cafe_sales.csv"
    CARPETA_RAW = "data/raw/"
    
    # Ejecutar la función
    df_raw = ejecutar_ingesta(RUTA_ORIGEN, CARPETA_RAW)