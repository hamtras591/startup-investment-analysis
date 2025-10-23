"""
Script de prueba para verificar config.py
"""

# Esto importará y ejecutará la verificación automáticamente
from src.data.config import (
    show_structure,
    show_config,
    BASE_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR
)

print("\n" + "="*70)
print("🧪 PRUEBA DE CONFIGURACIÓN")
print("="*70)

# Mostrar estructura
show_structure(show_files=True)

# Mostrar configuración
show_config()

# Verificar rutas
print("\n🔍 VERIFICACIÓN DE RUTAS:")
print(f"   BASE_DIR existe: {BASE_DIR.exists()}")
print(f"   RAW_DATA_DIR existe: {RAW_DATA_DIR.exists()}")
print(f"   PROCESSED_DATA_DIR existe: {PROCESSED_DATA_DIR.exists()}")

print("\n✅ Prueba completada")