import json
from pathlib import Path
from typing import Dict, Any

# ============================================================
# Detección automática de la raíz del proyecto
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
        # Hacemos un print para verificar que la ruta en la que está el archivo
        print(f"📑 La ruta donde esta este archivo es: {start_path}")

    # Declaración de variable iterable = current (actual)
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

    # Le dice que suba un máximo de 5 niveles
    for i in range(5):
        # Revisa cada una de las pistas de los posibles archivos en la raíz del proyecto
        for marker in root_markers:
            if (current / marker).exists():
                print(f"✅ Raíz del proyecto detectada: {current}")
                print(f"🔑 Marcador encontrado: {marker}")
                return current
        #? Si el for no encuentra ninguno de los archivos posibles, subimos 1 carpeta con el método parent() de la librería pathlib
        parent = current.parent

        #! Si llegamos a la raíz del sistema, detenernos
        if parent == current:
            break

        current = parent
        print(f"📁 Ruta buscada: {current}")
        # Si no encontramos marcadores, asumir que estamos 3 niveles abajo
        # proyecto/src/data/config.py → proyecto
    fallback = Path(__file__).resolve().parent.parent.parent
    print(f"⚠️ No se encontró marcador de raíz. Usando: {fallback}")
    return fallback


# ============================================================
# Carga de configuración del Json
# ============================================================

def load_config_json(config_path: Path = None) -> Dict[str, Any]:
    """
    Carga la configuración desde el archivo JSON

    Args:
        config_path: Ruta al JSON (default: config/project_config.json)

    Returns:
        dict: Configuración cargada
    """
    if config_path is None:
        project_root = find_project_root()
        config_path = project_root / 'config' / 'project_config.json'

    if not config_path.exists():
        raise FileNotFoundError(
            f"\n{'=' * 70}\n"
            f"❌ NO SE ENCONTRÓ EL ARCHIVO DE CONFIGURACIÓN\n"
            f"{'=' * 70}\n\n"
            f"📍 Se esperaba en: {config_path}\n\n"
            f"🔧 SOLUCIÓN:\n"
            f"1. Crea la carpeta 'config/' en la raíz del proyecto\n"
            f"2. Crea el archivo 'project_config.json'\n"
            f"3. Copia el contenido del template\n\n"
            f"💡 Ver ejemplo en: config/README.md\n"
            f"{'=' * 70}\n"
        )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print(f"✅ Configuración cargada desde: {config_path.name}")
        return config

    except json.JSONDecodeError as e:
        raise ValueError(
            f"\n{'=' * 70}\n"
            f"❌ ERROR EN EL ARCHIVO JSON\n"
            f"{'=' * 70}\n\n"
            f"📍 Archivo: {config_path}\n"
            f"❌ Error: {e}\n\n"
            f"🔧 SOLUCIÓN:\n"
            f"1. Verifica que el JSON tenga formato correcto\n"
            f"2. Usa un validador: https://jsonlint.com\n"
            f"3. Verifica comas, comillas y llaves\n\n"
            f"{'=' * 70}\n"
        )

# ============================================================
# Configuración de rutas del proyecto
# ============================================================

# Detectar raíz del proyecto
PROJECT_ROOT_FOLDER = find_project_root()

# Cargar configuración
try:
    CONFIG = load_config_json()
except Exception as e:
    print(f"\n⚠️ Error al cargar configuración: {e}")
    print("⚠️ Usando configuración por defecto vacía")
    CONFIG = {
        "input_files": {},
        "output_files": {},
        "kaggle_datasets": {}
    }

# Estructura estándar de carpetas para Data Science
standar_structures = {
    'data': PROJECT_ROOT_FOLDER / 'data',
    'data/raw': PROJECT_ROOT_FOLDER / 'data' / 'raw',
    'data/processed': PROJECT_ROOT_FOLDER / 'data' / 'processed',
    'data/external': PROJECT_ROOT_FOLDER / 'data' / 'external',
    'data/interim': PROJECT_ROOT_FOLDER / 'data' / 'interim',
    'notebooks': PROJECT_ROOT_FOLDER / 'notebooks',
    'reports': PROJECT_ROOT_FOLDER / 'reports',
    'reports/figures': PROJECT_ROOT_FOLDER / 'reports' / 'figures',
    'src': PROJECT_ROOT_FOLDER / 'src',
    'tests': PROJECT_ROOT_FOLDER / 'tests',
    'docs': PROJECT_ROOT_FOLDER / 'docs',
    'config': PROJECT_ROOT_FOLDER / 'config',
    'scripts': PROJECT_ROOT_FOLDER / 'scripts'
}

# Rutas principales (shortcuts)
DATA_DIRECTORY = standar_structures['data']
RAW_DATA_DIRECTORY = standar_structures['data/raw']
PROCESSED_DATA_DIRECTORY = standar_structures['data/processed']
EXTERNAL_DATA_DIRECTORY = standar_structures['data/external']
INTERMEDIATE_DATA_DIRECTORY = standar_structures['data/interim']

NOTEBOOKS_DIRECTORY = standar_structures['notebooks']
REPORTS_DIRECTORY = standar_structures['reports']
FIGURES_DIRECTORY = standar_structures['reports/figures']
SRC_DIRECTORY = standar_structures['src'] #? src -> "Source Code"
TEST_DIRECTORY = standar_structures['tests']
DOCUMENTS_DIRECTORY = standar_structures['docs']
CONFIG_DIRECTORY = standar_structures['config']
SCRIPTS_DIRECTORY = standar_structures['scripts']

# Extraer del JSON
INPUT_FILES = CONFIG.get('input_files', {})
OUTPUT_FILES = CONFIG.get('output_files', {})
KAGGLE_DATASETS = CONFIG.get('kaggle_datasets', {})
APIS_CONFIG = CONFIG.get('apis', {})
PROCESSING_CONFIG = CONFIG.get('processing', {})
VISUALIZATION_CONFIG = CONFIG.get('visualization', {})

# ============================================================
# Funciones de gestión de estructura
# ============================================================

# 1. función para verificar que las carpetas existen
def check_structure_exists() -> dict:
    """
    Verifica qué carpetas de la estructura ya existen

    Returns:
        dict: {nombre_carpeta: existe (bool)}
    """
    status = {}
    for name, path in standar_structures.items():
        status[name] = path.exists()
    return status

# 2. función para crear las carpetas faltantes
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
        print("🔍 Verificando estructura de carpetas del proyecto")
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
                print(f"📁 {name}/")

    # Crear carpetas faltantes
    carpetas_creadas = []
    missing = [name for name, exists in status.items() if not exists]

    if missing:
        if verbose:
            print(f"\n📁 Creando {len(missing)} carpetas faltantes:")

        for name in missing:
            path = standar_structures[name]
            path.mkdir(parents=True, exist_ok=True)
            carpetas_creadas.append(name)
            if verbose:
                print(f"📁 {name}/")

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

# 3. Función para mostrar la estructura del proyecto
def show_structure(show_files: bool = False):
    """
    Muestra la estructura del proyecto en formato árbol

    Args:
        show_files: Mostrar también archivos (no solo carpetas)
    """
    print("\n" + "="*70)
    print("📂 Estructura del proyecto")
    print("="*70)
    print(f"\n{PROJECT_ROOT_FOLDER.name}/")

    # Carpetas principales en orden
    main_folders = ['data', 'src', 'notebooks', 'reports', 'tests', 'docs']

    for folder in main_folders:
        folder_path = PROJECT_ROOT_FOLDER / folder
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

# 4. Función para obtener ruta de archivo en data/raw/
def get_raw_path(file_key: str) -> Path:
    """Obtiene ruta de archivo en data/raw/"""
    if file_key not in INPUT_FILES:
        available = ', '.join(INPUT_FILES.keys()) if INPUT_FILES else 'ninguno'
        raise ValueError(
            f"\n❌ Archivo '{file_key}' no encontrado.\n"
            f"   Disponibles: {available}\n"
            f"   Agrégalo en: config/project_config.json → input_files"
        )

    return RAW_DATA_DIRECTORY / INPUT_FILES[file_key]

# 5. Función para obtener ruta de archivo en data/processed/
def get_processed_path(file_key: str) -> Path:
    """Obtiene ruta de archivo en data/processed/"""
    if file_key not in OUTPUT_FILES:
        available = ', '.join(OUTPUT_FILES.keys()) if OUTPUT_FILES else 'ninguno'
        raise ValueError(
            f"\n❌ Archivo '{file_key}' no encontrado.\n"
            f"   Disponibles: {available}\n"
            f"   Agrégalo en: config/project_config.json → output_files"
        )

    return PROCESSED_DATA_DIRECTORY / OUTPUT_FILES[file_key]

# 6. Función para obtener
def get_kaggle_dataset(dataset_key: str) -> str:
    """Obtiene identificador de dataset de Kaggle"""
    if dataset_key not in KAGGLE_DATASETS:
        available = ', '.join(KAGGLE_DATASETS.keys()) if KAGGLE_DATASETS else 'ninguno'
        raise ValueError(
            f"\n❌ Dataset '{dataset_key}' no encontrado.\n"
            f"   Disponibles: {available}\n"
            f"   Agrégalo en: config/project_config.json → kaggle_datasets"
        )

    return KAGGLE_DATASETS[dataset_key]

def reload_config():
    """Recarga la configuración del JSON (útil si se editó)"""
    global CONFIG, INPUT_FILES, OUTPUT_FILES, KAGGLE_DATASETS

    CONFIG = load_config_json()
    INPUT_FILES = CONFIG.get('input_files', {})
    OUTPUT_FILES = CONFIG.get('output_files', {})
    KAGGLE_DATASETS = CONFIG.get('kaggle_datasets', {})

    print("✅ Configuración recargada desde JSON")

# 7. Función para mostrar la configuración del archivo
def show_config():
    """Muestra la configuración actual"""
    print("\n" + "="*70)
    print("⚙️ CONFIGURACIÓN ACTUAL")
    print("="*70)

    print(f"\n📂 Rutas principales:")
    print(f"   BASE_DIR:      {PROJECT_ROOT_FOLDER}")
    print(f"   DATA_DIR:      {DATA_DIRECTORY}")
    print(f"   RAW_DATA_DIR:  {RAW_DATA_DIRECTORY}")
    print(f"   PROCESSED_DIR: {PROCESSED_DATA_DIRECTORY}")

    print(f"\n📥 Archivos de entrada ({len(INPUT_FILES)}):")
    for key, filename in INPUT_FILES.items():
        path = RAW_DATA_DIRECTORY / filename
        exists = "✅" if path.exists() else "❌"
        size = f"({path.stat().st_size / 1024:.1f} KB)" if path.exists() else ""
        print(f"   {exists} '{key}' → {filename} {size}")

    print(f"\n📤 Archivos de salida ({len(OUTPUT_FILES)}):")
    for key, filename in OUTPUT_FILES.items():
        path = PROCESSED_DATA_DIRECTORY / filename
        exists = "✅" if path.exists() else "❌"
        size = f"({path.stat().st_size / 1024:.1f} KB)" if path.exists() else ""
        print(f"   {exists} '{key}' → {filename} {size}")

    print(f"\n🌐 Datasets de Kaggle ({len(KAGGLE_DATASETS)}):")
    for key, dataset_id in KAGGLE_DATASETS.items():
        print(f"   • '{key}' → {dataset_id}")

    print("\n" + "="*70)


# ============================================================
# Inicialización del proyecto automática
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

print(f"\n📂 Datos se guardarán en: {RAW_DATA_DIRECTORY}")
print(f"📊 Resultados se guardarán en: {PROCESSED_DATA_DIRECTORY}")

# ============================================================
# EXPORTAR (IMPORTANTE: Debe estar al final)
# ============================================================

__all__ = [
    # Rutas principales
    'PROJECT_ROOT_FOLDER',
    'DATA_DIRECTORY',
    'RAW_DATA_DIRECTORY',
    'PROCESSED_DATA_DIRECTORY',
    'EXTERNAL_DATA_DIRECTORY',
    'INTERMEDIATE_DATA_DIRECTORY',
    'NOTEBOOKS_DIRECTORY',
    'REPORTS_DIRECTORY',
    'FIGURES_DIRECTORY',
    'SRC_DIRECTORY',
    'TEST_DIRECTORY',
    'DOCUMENTS_DIRECTORY',
    'CONFIG_DIRECTORY',
    'SCRIPTS_DIRECTORY',
    'standar_structures',

    # Configuraciones del JSON
    'CONFIG',
    'INPUT_FILES',
    'OUTPUT_FILES',
    'KAGGLE_DATASETS',
    'APIS_CONFIG',
    'PROCESSING_CONFIG',
    'VISUALIZATION_CONFIG',

    # Funciones principales
    'get_raw_path',
    'get_processed_path',
    'get_kaggle_dataset',
    'reload_config',
    'show_config',

    # Funciones de estructura
    'verify_and_create_structure',
    'check_structure_exists',

    # Funciones auxiliares
    'load_config_json',
    'find_project_root',
]