"""
Script para probar configuración con JSON
"""

from src.data.config import (
    show_config,
    get_raw_path,
    get_kaggle_dataset,
    INPUT_FILES,
    OUTPUT_FILES,
    KAGGLE_DATASETS,
    reload_config
)

print("="*70)
print("🧪 PRUEBA DE CONFIGURACIÓN CON JSON")
print("="*70)

# Mostrar configuración
show_config()

# Probar acceso a archivos
print("\n🔍 PROBANDO ACCESO A RUTAS:")

if INPUT_FILES:
    primer_archivo = list(INPUT_FILES.keys())[0]
    print(f"\n📥 Ruta de '{primer_archivo}':")
    print(f"   {get_raw_path(primer_archivo)}")

if KAGGLE_DATASETS:
    primer_dataset = list(KAGGLE_DATASETS.keys())[0]
    print(f"\n🌐 Dataset '{primer_dataset}':")
    print(f"   {get_kaggle_dataset(primer_dataset)}")

print("\n✅ Prueba completada")
print("\n💡 Para editar configuración:")
print("   Edita: config/project_config.json")
print("   Y ejecuta: reload_config()")