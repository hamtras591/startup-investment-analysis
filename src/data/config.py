"""
CONFIGURACIÓN INTELIGENTE DEL PROYECTO
=======================================
Este archivo:
1. Detecta automáticamente la estructura del proyecto
2. Verifica si ya existen las carpetas necesarias
3. Si existen, las usa
4. Si NO existen, las crea
5. Siempre garantiza que los archivos vayan al lugar correcto

Autor: Anderson Sebastian Rubio Pacheco
Versión: 2.0.0
"""

from pathlib import Path
import sys

# ============================================================
# DETECCIÓN AUTOMÁTICA DE LA RAÍZ DEL PROYECTO
# ============================================================

def find_project_root(start_path: Path = None) -> Path:
    """
    Encuentra la raíz del proyecto buscando hacia arriba

    La raíz se identifica por tener alguno de estos archivos/carpetas:
    - .git/
    - .venv/
    - requirements.txt
    - setup.py
    - README.md

    Args:
        start_path: Punto de inicio (default: ubicación de este archivo)

    Returns:
        Path: Ruta de la raíz del proyecto
    """
    if start_path is None:
        # Este archivo está en: proyecto/src/data/config.py
        start_path = Path(__file__).resolve().parent

    current = start_path

    # Marcadores que indican la raíz del proyecto
    root_markers = [
        '.git',
        '.venv',
        'venv',
        'requirements.txt',
        'setup.py',
        'README.md',
        '.gitignore'
    ]

    # Subir máximo 5 niveles
    for _ in range(5):
        # Verificar si algún marcador existe en este nivel
        for marker in root_markers:
            if (current / marker).exists():
                print(f"✅ Raíz del proyecto detectada: {current}")
                print(f"   Marcador encontrado: {marker}")
                return current

        # Subir un nivel
        parent = current.parent

        # Si llegamos a la raíz del sistema, detenernos
        if parent == current:
            break

        current = parent

    # Si no encontramos marcadores, asumir que estamos 3 niveles abajo
    # proyecto/src/data/config.py → proyecto
    fallback = Path(__file__).resolve().parent.parent.parent
    print(f"⚠️ No se encontró marcador de raíz. Usando: {fallback}")
    return fallback


# ============================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================

# Detectar raíz del proyecto
BASE_DIR = find_project_root()

# Estructura estándar de carpetas para Data Science
STANDARD_STRUCTURE = {
    'data': BASE_DIR / 'data',
    'data/raw': BASE_DIR / 'data' / 'raw',
    'data/processed': BASE_DIR / 'data' / 'processed',
    'data/external': BASE_DIR / 'data' / 'external',
    'data/interim': BASE_DIR / 'data' / 'interim',
    'notebooks': BASE_DIR / 'notebooks',
    'reports': BASE_DIR / 'reports',
    'reports/figures': BASE_DIR / 'reports' / 'figures',
    'src': BASE_DIR / 'src',
    'tests': BASE_DIR / 'tests',
    'docs': BASE_DIR / 'docs',
}

# Rutas principales (shortcuts)
DATA_DIR = STANDARD_STRUCTURE['data']
RAW_DATA_DIR = STANDARD_STRUCTURE['data/raw']
PROCESSED_DATA_DIR = STANDARD_STRUCTURE['data/processed']
EXTERNAL_DATA_DIR = STANDARD_STRUCTURE['data/external']
INTERIM_DATA_DIR = STANDARD_STRUCTURE['data/interim']

NOTEBOOKS_DIR = STANDARD_STRUCTURE['notebooks']
REPORTS_DIR = STANDARD_STRUCTURE['reports']
FIGURES_DIR = STANDARD_STRUCTURE['reports/figures']
SRC_DIR = STANDARD_STRUCTURE['src']
TESTS_DIR = STANDARD_STRUCTURE['tests']
DOCS_DIR = STANDARD_STRUCTURE['docs']


# ============================================================
# ⚙️ ARCHIVOS DE ENTRADA (data/raw/)
# ============================================================

INPUT_FILES = {
    'hospital': 'hospital_data.csv',
    'startups': 'startups_investment.csv',

    # ⬇️ AGREGA TUS ARCHIVOS AQUÍ ⬇️
}


# ============================================================
# ⚙️ ARCHIVOS DE SALIDA (data/processed/)
# ============================================================

OUTPUT_FILES = {
    'hospital_clean': 'hospital_data_clean.csv',
    'startups_clean': 'startups_investment_clean.csv',

    # ⬇️ AGREGA TUS ARCHIVOS DE SALIDA AQUÍ ⬇️
}


# ============================================================
# ⚙️ DATASETS DE KAGGLE
# ============================================================

KAGGLE_DATASETS = {
    'hospital': 'jaderz/hospital-beds-management',
    'startups': 'yanmaksi/big-startup-secsees-fail-dataset-from-crunchbase',

    # ⬇️ AGREGA TUS DATASETS AQUÍ ⬇️
}


# ============================================================
# FUNCIONES DE GESTIÓN DE ESTRUCTURA
# ============================================================

def check_structure_exists() -> dict:
    """
    Verifica qué carpetas de la estructura ya existen

    Returns:
        dict: {nombre_carpeta: existe (bool)}
    """
    status = {}
    for name, path in STANDARD_STRUCTURE.items():
        status[name] = path.exists()
    return status


def verify_and_create_structure(verbose: bool = True) -> tuple:
    """
    Verifica la estructura y crea solo las carpetas faltantes

    Args:
        verbose: Mostrar mensajes detallados

    Returns:
        tuple: (estructura_existia, carpetas_creadas)
    """
    if verbose:
        print("\n" + "="*70)
        print("🔍 VERIFICANDO ESTRUCTURA DEL PROYECTO")
        print("="*70)

    # Verificar estado actual
    status = check_structure_exists()

    # Contar cuántas carpetas ya existen
    existing_count = sum(status.values())
    total_count = len(status)

    estructura_existia = existing_count > 0

    if verbose:
        print(f"\n📊 Estado: {existing_count}/{total_count} carpetas encontradas")

    # Mostrar carpetas existentes
    if verbose and existing_count > 0:
        print("\n✅ Carpetas existentes:")
        for name, exists in status.items():
            if exists:
                print(f"   ✓ {name}/")

    # Crear carpetas faltantes
    carpetas_creadas = []
    missing = [name for name, exists in status.items() if not exists]

    if missing:
        if verbose:
            print(f"\n📁 Creando {len(missing)} carpetas faltantes:")

        for name in missing:
            path = STANDARD_STRUCTURE[name]
            path.mkdir(parents=True, exist_ok=True)
            carpetas_creadas.append(name)
            if verbose:
                print(f"   ✓ {name}/")

    if verbose:
        print("\n" + "="*70)
        if estructura_existia and not carpetas_creadas:
            print("✅ ESTRUCTURA COMPLETA - No se crearon carpetas")
        elif estructura_existia and carpetas_creadas:
            print(f"✅ ESTRUCTURA COMPLETADA - Se crearon {len(carpetas_creadas)} carpetas")
        else:
            print(f"✅ ESTRUCTURA CREADA - Se crearon {len(carpetas_creadas)} carpetas")
        print("="*70)

    return estructura_existia, carpetas_creadas


def show_structure(show_files: bool = False):
    """
    Muestra la estructura del proyecto en formato árbol

    Args:
        show_files: Mostrar también archivos (no solo carpetas)
    """
    print("\n" + "="*70)
    print("📂 ESTRUCTURA DEL PROYECTO")
    print("="*70)
    print(f"\n{BASE_DIR.name}/")

    # Carpetas principales en orden
    main_folders = ['data', 'src', 'notebooks', 'reports', 'tests', 'docs']

    for folder in main_folders:
        folder_path = BASE_DIR / folder
        if folder_path.exists():
            print(f"├── {folder}/")

            # Mostrar subcarpetas
            if folder == 'data':
                subfolders = ['raw', 'processed', 'external', 'interim']
                for i, subfolder in enumerate(subfolders):
                    sub_path = folder_path / subfolder
                    if sub_path.exists():
                        is_last = (i == len(subfolders) - 1)
                        prefix = "└──" if is_last else "├──"
                        print(f"│   {prefix} {subfolder}/")

                        # Mostrar archivos si se solicita
                        if show_files:
                            files = list(sub_path.glob('*'))
                            for j, file in enumerate(files[:5]):  # Máximo 5 archivos
                                is_last_file = (j == len(files) - 1) or (j == 4)
                                file_prefix = "    └──" if is_last_file else "    ├──"
                                print(f"│   {file_prefix} {file.name}")
                            if len(files) > 5:
                                print(f"│       └── ... ({len(files) - 5} más)")

            elif folder == 'reports':
                sub_path = folder_path / 'figures'
                if sub_path.exists():
                    print(f"│   └── figures/")

    print("│")
    print("├── .gitignore")
    print("├── requirements.txt")
    print("├── README.md")
    print("└── LICENSE")
    print("\n" + "="*70)


# ============================================================
# FUNCIONES DE ACCESO A RUTAS
# ============================================================

def get_raw_path(file_key: str) -> Path:
    """
    Obtiene ruta completa de archivo en data/raw/

    Args:
        file_key: Clave del archivo en INPUT_FILES

    Returns:
        Path: Ruta completa del archivo

    Ejemplo:
        >>> path = get_raw_path('hospital')
        >>> print(path)
        /home/user/proyecto/data/raw/hospital_data.csv
    """
    if file_key not in INPUT_FILES:
        available = ', '.join(INPUT_FILES.keys())
        raise ValueError(
            f"\n❌ Archivo '{file_key}' no encontrado.\n"
            f"   Archivos disponibles: {available}\n"
            f"   Agrégalo en INPUT_FILES en config.py"
        )

    return RAW_DATA_DIR / INPUT_FILES[file_key]


def get_processed_path(file_key: str) -> Path:
    """
    Obtiene ruta completa de archivo en data/processed/

    Args:
        file_key: Clave del archivo en OUTPUT_FILES

    Returns:
        Path: Ruta completa del archivo
    """
    if file_key not in OUTPUT_FILES:
        available = ', '.join(OUTPUT_FILES.keys())
        raise ValueError(
            f"\n❌ Archivo '{file_key}' no encontrado.\n"
            f"   Archivos disponibles: {available}\n"
            f"   Agrégalo en OUTPUT_FILES en config.py"
        )

    return PROCESSED_DATA_DIR / OUTPUT_FILES[file_key]


def get_kaggle_dataset(dataset_key: str) -> str:
    """
    Obtiene identificador de dataset de Kaggle

    Args:
        dataset_key: Clave del dataset en KAGGLE_DATASETS

    Returns:
        str: Identificador del dataset (usuario/nombre)
    """
    if dataset_key not in KAGGLE_DATASETS:
        available = ', '.join(KAGGLE_DATASETS.keys())
        raise ValueError(
            f"\n❌ Dataset '{dataset_key}' no encontrado.\n"
            f"   Datasets disponibles: {available}\n"
            f"   Agrégalo en KAGGLE_DATASETS en config.py"
        )

    return KAGGLE_DATASETS[dataset_key]


def show_config():
    """Muestra la configuración actual"""
    print("\n" + "="*70)
    print("⚙️ CONFIGURACIÓN ACTUAL")
    print("="*70)

    print(f"\n📂 Rutas principales:")
    print(f"   BASE_DIR:      {BASE_DIR}")
    print(f"   DATA_DIR:      {DATA_DIR}")
    print(f"   RAW_DATA_DIR:  {RAW_DATA_DIR}")
    print(f"   PROCESSED_DIR: {PROCESSED_DATA_DIR}")

    print(f"\n📥 Archivos de entrada ({len(INPUT_FILES)}):")
    for key, filename in INPUT_FILES.items():
        path = RAW_DATA_DIR / filename
        exists = "✅" if path.exists() else "❌"
        size = f"({path.stat().st_size / 1024:.1f} KB)" if path.exists() else ""
        print(f"   {exists} '{key}' → {filename} {size}")

    print(f"\n📤 Archivos de salida ({len(OUTPUT_FILES)}):")
    for key, filename in OUTPUT_FILES.items():
        path = PROCESSED_DATA_DIR / filename
        exists = "✅" if path.exists() else "❌"
        size = f"({path.stat().st_size / 1024:.1f} KB)" if path.exists() else ""
        print(f"   {exists} '{key}' → {filename} {size}")

    print(f"\n🌐 Datasets de Kaggle ({len(KAGGLE_DATASETS)}):")
    for key, dataset_id in KAGGLE_DATASETS.items():
        print(f"   • '{key}' → {dataset_id}")

    print("\n" + "="*70)


# ============================================================
# INICIALIZACIÓN AUTOMÁTICA
# ============================================================

# Al importar este módulo, verificar y crear estructura si es necesario
estructura_existia, carpetas_creadas = verify_and_create_structure(verbose=True)

# Mensaje de bienvenida
if not estructura_existia:
    print("\n🎉 ¡Proyecto inicializado!")
    print("   Puedes empezar a trabajar en tus notebooks o scripts.")
elif carpetas_creadas:
    print(f"\n✨ Estructura completada con {len(carpetas_creadas)} carpetas nuevas.")
else:
    print("\n👍 Usando estructura existente del proyecto.")

print(f"\n📂 Datos se guardarán en: {RAW_DATA_DIR}")
print(f"📊 Resultados se guardarán en: {PROCESSED_DATA_DIR}")