import os
import logging
from ingesta import ejecutar_ingesta
from limpieza import ejecutar_limpieza
from validacion import ejecutar_validacion
from carga import ejecutar_carga

# Configuración centralizada de logs para el pipeline completo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/errors/pipeline.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("==================================================")
    logging.info("INICIANDO EJECUCIÓN DEL PIPELINE AUTOMATIZADO")
    logging.info("==================================================")
    
    # Ruta de origen inicial
    ruta_origen_csv = "dirty_cafe_sales.csv"
    
    # 1. ETAPA 1: INGESTA
    df_raw = ejecutar_ingesta(path_origen=ruta_origen_csv, carpeta_destino="data/raw/")
    if df_raw is None:
        logging.error("Pipeline detenido en la Etapa 1 (Ingesta).")
        return

    # 2. ETAPA 2: LIMPIEZA Y TRANSFORMACIÓN
    df_clean = ejecutar_limpieza(path_raw="data/raw/dirty_cafe_sales.csv", carpeta_destino="data/clean/")
    if df_clean is None:
        logging.error("Pipeline detenido en la Etapa 2 (Limpieza).")
        return

    # 3. ETAPA 3: VALIDACIÓN ESTRUCTURAL Y SEMÁNTICA
    df_validated = ejecutar_validacion(
        path_clean="data/clean/cafe_sales_clean.csv", 
        carpeta_validated="data/validated/", 
        carpeta_errors="data/errors/"
    )
    if df_validated is None:
        logging.error("Pipeline detenido en la Etapa 3 (Validación).")
        return

    # 4. ETAPA 4: CARGA A BASE DE DATOS
    ejecutar_carga(path_validated="data/validated/cafe_sales_validated.csv", db_name="cafe_data.db")

    logging.info("==================================================")
    logging.info("¡PIPELINE EJECUTADO CON ÉXITO DE EXTREMO A EXTREMO!")
    logging.info("==================================================")

if __name__ == "__main__":
    # Asegurar que la estructura de carpetas exista antes de arrancar
    os.makedirs("data/errors", exist_ok=True)
    main()