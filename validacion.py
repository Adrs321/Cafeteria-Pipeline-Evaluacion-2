import os
import pandas as pd
import numpy as np
import pandera as pa
from pandera import Check, Column, DataFrameSchema
import logging

# Seguimos usando el mismo archivo de logs para la trazabilidad (10 pts)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/errors/pipeline.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def ejecutar_validacion(path_clean, carpeta_validated, carpeta_errors):
    logging.info("=== INICIANDO ETAPA 3: VALIDACIÓN ESTRUCTURAL Y SEMÁNTICA ===")
    
    # 1. Cargar el dataset limpio de la etapa anterior
    if not os.path.exists(path_clean):
        logging.error(f"No se encontró el archivo limpio en: {path_clean}")
        return None, None
        
    df = pd.read_csv(path_clean)
    logging.info(f"Dataset cargado para validación. Registros a evaluar: {len(df)}")

    # 2. Definición del Esquema Estructural con Pandera (Requisito Etapa 3a)
    schema = DataFrameSchema({
        "Transaction ID": Column(str, Check.str_matches(r"^TXN_\d+$"), nullable=False), # Validación 1 (Regex)
        "Quantity": Column(float, Check(lambda s: s > 0), nullable=False),             # Validación 2 (Rango > 0)
        "Price Per Unit": Column(float, Check(lambda s: s >= 0), nullable=False)        # Validación 3 (Rango >= 0)
    }, coerce=True)

    # 3. Listas para separar los registros válidos de los inválidos (Requisito Etapa 3b)
    registros_validos = []
    registros_invalidos = []

    # Iteramos fila por fila para aplicar las validaciones estructurales y semánticas
    for idx, row in df.iterrows():
        fila_valida = True
        motivo_error = ""
        
        # --- A. VALIDACIÓN ESTRUCTURAL ---
        try:
            # Convertimos la fila en un DataFrame temporal para que Pandera la evalúe
            schema.validate(pd.DataFrame([row]))
        except Exception as e:
            fila_valida = False
            motivo_error = f"Falla Estructural (Pandera): {str(e).splitlines()[0]}"

        # --- B. VALIDACIÓN SEMÁNTICA (Reglas de Negocio) ---
        if fila_valida:
            # Regla Semántica 1: El Total Spent registrado debe cuadrar con la multiplicación matemática
            # Margen de tolerancia de 0.01 por temas de redondeo decimal
            diferencia = abs(row['Total_Spent_Calculado'] - (row['Quantity'] * row['Price Per Unit']))
            if diferencia > 0.01:
                fila_valida = False
                motivo_error = f"Falla Semántica: El total calculado ({row['Total_Spent_Calculado']}) no coincide con Quantity * Price."

            # Regla Semántica 2: Si la venta es sospechosamente alta (ej: más de $50), la locación no puede ser "No Especificado"
            if row['Total_Spent_Calculado'] > 50.0 and row['Location'] == "No Especificado":
                fila_valida = False
                motivo_error = "Falla Semántica: Transacción mayor a $50 requiere una 'Location' válida."

        # Separar la fila según el resultado del control de calidad
        row_dict = row.to_dict()
        if fila_valida:
            registros_validos.append(row_dict)
        else:
            row_dict['Motivo_Error'] = motivo_error
            registros_invalidos.append(row_dict)

    # 4. Crear los DataFrames de salida
    df_validos = pd.DataFrame(registros_validos)
    df_invalidos = pd.DataFrame(registros_invalidos)

    # 5. Guardar archivos en sus respectivas carpetas obligatorias
    os.makedirs(carpeta_validated, exist_ok=True)
    os.makedirs(carpeta_errors, exist_ok=True)
    
    path_validos = os.path.join(carpeta_validated, "cafe_sales_validated.csv")
    path_invalidos = os.path.join(carpeta_errors, "cafe_sales_errors.csv")
    
    df_validos.to_csv(path_validos, index=False, encoding='utf-8')
    df_invalidos.to_csv(path_invalidos, index=False, encoding='utf-8')

    # Imprimir estadísticas en consola para las Slides de la PPT
    print("\n" + "="*50)
    print("      RESULTADO DE VALIDACIONES (ETAPA 3)")
    print("="*50)
    print(f"Registros VÁLIDOS (Aprobados):   {len(df_validos)}")
    print(f"Registros INVÁLIDOS (Rechazados): {len(df_invalidos)}")
    print(f"Porcentaje de éxito:             {(len(df_validos)/len(df))*100:.2f}%")
    print("="*50 + "\n")

    logging.info(f"Registros válidos guardados en: {path_validos}")
    logging.info(f"Registros con errores guardados en: {path_invalidos}")
    logging.info("=== ETAPA 3 FINALIZADA CON ÉXITO ===\n")

    return df_validos

if __name__ == "__main__":
    PATH_CLEAN = "data/clean/cafe_sales_clean.csv"
    CARPETA_VALIDATED = "data/validated/"
    CARPETA_ERRORS = "data/errors/"
    ejecutar_validacion(PATH_CLEAN, CARPETA_VALIDATED, CARPETA_ERRORS)