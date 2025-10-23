# data_acquisition.ipynb - Celda de Lectura

# 1. Configuración y Obtención de la Ruta (Importación)
# ESTO es lo que resuelve la ruta absoluta correctamente.
from src.data.config import RAW_DATA_DIR
from src.data.data_loader import load_raw

FILE_TO_LOAD = 'investments_VC.csv'

# ----------------------------------------------------
# 2. Cargar forzando la ruta absoluta (¡Solución!)
# ----------------------------------------------------

print(f"Buscando '{FILE_TO_LOAD}' recursivamente dentro de: {RAW_DATA_DIR.resolve()}")

# 💡 USAMOS el argumento search_dir=RAW_DATA_DIR
# Esto garantiza que rglob() busque en: D:\...\data\raw
df_raw = load_raw(
    FILE_TO_LOAD,
    search_dir=RAW_DATA_DIR
)

print(f"✅ Lectura finalizada. Filas: {df_raw.shape[0]}, Columnas: {df_raw.shape[1]}")


print(df_raw.head())