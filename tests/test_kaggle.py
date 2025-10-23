"""
Test para verificar que Kaggle funciona
"""

from src.data.kaggle_downloader import verify_kaggle_setup, search_kaggle, download_from_kaggle

# Verificar configuración
verify_kaggle_setup()
# Buscar Dataset
download_from_kaggle('jaderz/hospital-beds-management')