# quick_load_template.py

# Importamos las funciones de las herramientas que hemos creado
# Usamos 'load_raw' que es la función correcta de tu data_loader.
from src.data.kaggle_downloader import download_from_kaggle
from src.data.data_loader import load_raw
from src.data.data_profiler import generate_profile # <-- Importamos el perfilador

# --- 🔧 CONFIGURACIÓN ---
# Define el dataset de Kaggle y el nombre del archivo CSV dentro de ese dataset.
DATASET_ID = 'sidraaazam/analyzing-student-stress-factors'
FILENAME = 'Student Stress Factors (2).csv'

# Definimos una clave única que usará el cargador.
# Esta clave DEBE estar mapeada al FILENAME en tu archivo config.py (sección INPUT_FILES).
FILE_KEY = 'student_stress'


# --- 🚀 EJECUTAR LA PRUEBA ---
print("--- INICIANDO PRUEBA DE CARGA Y PERFILADO ---")

try:
    # 1. Descargar el dataset (si no existe)
    print(f"\n1. Descargando o verificando dataset: {DATASET_ID}...")
    # Asegúrate de que 'download_from_kaggle' pueda manejar la descarga o verificación correctamente.
    download_from_kaggle(DATASET_ID, file_key=FILE_KEY)

    # 2. Cargar los datos usando el método correcto: load_raw
    print(f"\n2. Cargando archivo: {FILENAME} usando load_raw...")
    # Le pasamos el nombre del archivo directamente, como en tu ejemplo,
    # asumiendo que load_raw espera el nombre del archivo.
    # NOTA: Si 'load_raw' solo espera la CLAVE, usa 'df = load_raw(FILE_KEY)'
    df = load_raw(FILENAME)

    # 3. Mostrar resumen básico
    print("\n" + "=" * 50)
    print(f"✅ ¡CARGA EXITOSA!")
    print(f"   Filas (Observaciones): {len(df):,}")
    print(f"   Columnas (Variables):  {df.shape[1]}")
    print("=" * 50)

    # 4. Generar el perfil estadístico
    print("\n3. Generando el Perfil Estadístico Completo...")
    generate_profile(df, dataset_name=FILENAME)

except Exception as e:
    print("\n❌ ¡ERROR DURANTE LA EJECUCIÓN DE LA PRUEBA!")
    print(f"   Por favor, verifica tu configuración en config.py y las dependencias.")
    print(f"   Detalle del error: {e}")