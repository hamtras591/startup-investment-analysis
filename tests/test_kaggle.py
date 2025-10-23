"""
Quick Load + Profile Template
"""

from src.data.kaggle_downloader import download_from_kaggle
from src.data.data_loader import load_raw
from src.data.data_profiler import generate_profile, profile_from_file

DATASET_ID = 'ayeshaimran123/data-science-student-marks'
FILENAME = 'data_science_student_marks.csv'

# ============================================================
# OPCIÓN 1: Pipeline Manual (3 pasos)
# ============================================================
download_from_kaggle(DATASET_ID)
df = load_raw(FILENAME)
generate_profile(df, dataset_name="Estudiantes Ciencia de Datos")
