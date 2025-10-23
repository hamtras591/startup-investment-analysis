"""
test_pipeline.py
================
Script para probar la integración completa:
    1. config.py (rutas centralizadas)
    2. kaggle_downloader.py (descarga de Kaggle)
    3. data_loader.py (lectura de datos)

DATASET: Big Startup Success/Fail Dataset from Crunchbase
OBJETIVO: Preparar datos para análisis de inversión en startups

UBICACIÓN: tests/test_pipeline.py o notebooks/00_data_setup.ipynb
"""

# ============================================================
# PASO 1: IMPORTACIONES
# ============================================================

print("\n" + "=" * 70)
print("🚀 PIPELINE DE DATOS: DESCARGA Y LECTURA")
print("=" * 70)

# Importar módulos del proyecto
from src.data.kaggle_downloader import download_from_kaggle
from src.data.data_loader import load_raw
from src.data.config import show_config
import pandas as pd

# ============================================================
# PASO 2: VERIFICAR CONFIGURACIÓN DEL PROYECTO
# ============================================================

print("\n📋 PASO 1: Verificando configuración del proyecto...\n")
show_config()

# ============================================================
# PASO 3: DESCARGAR DATASET DE KAGGLE
# ============================================================

print("\n📥 PASO 2: Descargando dataset de Kaggle...\n")

#! Dataset de Crunchbase con información de startups - Cambio acá
DATASET_ID = 'sidraaazam/analyzing-student-stress-factors'

# Descargar (se salta si ya existe)
try:
    dataset_path = download_from_kaggle(DATASET_ID)
    print(f"\n✅ Dataset disponible en: {dataset_path}")
except Exception as e:
    print(f"\n❌ Error descargando dataset: {e}")
    print("\n💡 SOLUCIÓN:")
    print("   1. Verifica tu conexión a internet")
    print("   2. Ejecuta: verify_kaggle_setup()")
    exit(1)

# ============================================================
# PASO 4: CARGAR DATOS CON data_loader
# ============================================================

print("\n📊 PASO 3: Cargando datos en memoria...\n")

#! Nombre del archivo principal del dataset
FILENAME = 'Student Stress Factors (2).csv'

try:
    # Cargar usando load_raw (búsqueda recursiva en data/raw/)
    df_startups = load_raw(FILENAME)

    print("\n" + "=" * 70)
    print("✅ DATOS CARGADOS EXITOSAMENTE")
    print("=" * 70)

except FileNotFoundError as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Archivos disponibles en data/raw/:")
    from pathlib import Path
    from src.data.config import RAW_DATA_DIRECTORY

    for file in RAW_DATA_DIRECTORY.rglob('*.csv'):
        print(f"   • {file.relative_to(RAW_DATA_DIRECTORY)}")
    exit(1)

# ============================================================
# PASO 5: INSPECCIÓN INICIAL DE LOS DATOS
# ============================================================

print("\n📈 PASO 4: Información básica del dataset\n")

# Dimensiones
print(f"📏 Dimensiones:")
print(f"   Filas (startups): {df_startups.shape[0]:,}")
print(f"   Columnas (variables): {df_startups.shape[1]}")

# Columnas disponibles
print(f"\n📋 Columnas disponibles ({df_startups.shape[1]}):")
for i, col in enumerate(df_startups.columns, 1):
    print(f"   {i:2d}. {col}")

# Tipos de datos
print(f"\n🔢 Tipos de datos:")
print(df_startups.dtypes)

# Valores nulos
print(f"\n❓ Valores nulos por columna:")
nulls = df_startups.isnull().sum()
nulls_pct = (nulls / len(df_startups) * 100).round(2)
null_summary = pd.DataFrame({
    'Nulos': nulls,
    'Porcentaje': nulls_pct
}).sort_values('Nulos', ascending=False)
print(null_summary[null_summary['Nulos'] > 0])

# Primeras filas
print(f"\n👀 Primeras 5 filas del dataset:")
print(df_startups.head())

# Información de memoria
memory_mb = df_startups.memory_usage(deep=True).sum() / (1024 ** 2)
print(f"\n💾 Uso de memoria: {memory_mb:.2f} MB")

# ============================================================
# PASO 6: RESUMEN FINAL
# ============================================================

print("\n" + "=" * 70)
print("🎯 RESUMEN DEL PIPELINE")
print("=" * 70)
print(f"✅ Dataset descargado: {DATASET_ID}")
print(f"✅ Archivo cargado: {FILENAME}")
print(f"✅ Registros disponibles: {len(df_startups):,} startups")
print(f"✅ Variables disponibles: {df_startups.shape[1]}")
print("\n💡 Variable 'df_startups' lista para análisis")
print("=" * 70)

# ============================================================
# PASO 7: GUARDAR REFERENCIA PARA ANÁLISIS
# ============================================================

print("\n📌 El DataFrame está disponible como: df_startups")
print("🚦 Esperando instrucciones para análisis de insights...\n")