"""
Kaggle Downloader Module
=========================
Módulo para descarga automática de datasets desde Kaggle.

PROPÓSITO:
    Facilitar la descarga de datasets de Kaggle de forma programática,
    integrándose con la estructura de carpetas del proyecto (data/raw/).

FUNCIONALIDADES:
    1. Descarga de datasets públicos
    2. Descarga de datos de competencias
    3. Búsqueda de datasets por palabras clave
    4. Listado de archivos sin descargar
    5. Verificación de credenciales

UBICACIÓN EN EL PROYECTO:
    src/data/kaggle_downloader.py

    Estructura relacionada:
    proyecto/
    ├── src/
    │   └── data/
    │       ├── config.py           ← Define rutas (RAW_DATA_DIRECTORY)
    │       └── kaggle_downloader.py ← Este archivo
    └── data/
        └── raw/                     ← Destino de descargas

REQUISITOS PREVIOS:
    1. pip install kaggle
    2. Cuenta en Kaggle (https://www.kaggle.com)
    3. API Token descargado (kaggle.json)
    4. Token ubicado en ~/.kaggle/kaggle.json

AUTOR: Anderson Sebastian Rubio Pacheco
VERSIÓN: 2.1.0
FECHA: Octubre 2025
CAMBIOS v2.1.0: Integración con config.py para rutas centralizadas
"""

# ============================================================
# SECCIÓN 1: IMPORTACIONES
# ============================================================

import os                    # Para operaciones del sistema operativo
from pathlib import Path     # Para manejo moderno de rutas (Pythonic)
from typing import Union, Optional, List  # Para type hints (tipado)
import zipfile              # Para descomprimir archivos .zip
import shutil               # Para operaciones de archivos (mover, copiar)

# ============================================================
# Importar configuración centralizada del proyecto
# ============================================================
try:
    # Intentar importar la ruta de data/raw/ desde config.py
    from src.data.config import RAW_DATA_DIRECTORY
    CONFIG_AVAILABLE = True
except ImportError:
    # Si falla (ej: ejecutando fuera del proyecto)
    RAW_DATA_DIRECTORY = None
    CONFIG_AVAILABLE = False

# ============================================================
# Intentar importar la API de Kaggle
# ============================================================
# IMPORTANTE: Este try-except permite que el módulo se importe
# incluso si 'kaggle' no está instalado, para mostrar un error amigable.

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    KAGGLE_AVAILABLE = True  # Bandera: Kaggle está instalado
except ImportError:
    KAGGLE_AVAILABLE = False  # Bandera: Kaggle NO está instalado


# ============================================================
# CLASE PRINCIPAL: KaggleDownloader
# ============================================================

class KaggleDownloader:
    """
    Descargador automático de datasets de Kaggle

    RESPONSABILIDADES:
        - Autenticar con la API de Kaggle
        - Buscar datasets por palabras clave
        - Descargar datasets a data/raw/
        - Gestionar archivos comprimidos
        - Validar credenciales del usuario

    ATRIBUTOS:
        api (KaggleApi): Cliente autenticado de Kaggle
        download_dir (Path): Directorio de destino (data/raw/)
        verbose (bool): Controla si mostrar mensajes detallados

    EJEMPLO DE USO:
        >>> downloader = KaggleDownloader()
        >>> downloader.download('carrie1/ecommerce-data')
        >>> downloader.search('startup investment')
    """

    # ========================================================
    # MÉTODO: __init__ (Constructor)
    # ========================================================
    def __init__(
        self,
        download_dir: Optional[Union[str, Path]] = None,  # Ruta personalizada
        verbose: bool = True  # Mostrar mensajes por defecto
    ):
        """
        Inicializa el descargador de Kaggle

        FLUJO DE INICIALIZACIÓN:
            1. Verificar que 'kaggle' esté instalado
            2. Verificar que kaggle.json exista
            3. Autenticar con la API
            4. Configurar directorio de descarga (usando config.py)
            5. Crear carpetas si no existen

        Args:
            download_dir: Directorio personalizado de descarga.
                         Si es None, usa RAW_DATA_DIRECTORY de config.py
            verbose: Si True, imprime mensajes detallados del proceso

        Raises:
            ImportError: Si 'kaggle' no está instalado
            FileNotFoundError: Si kaggle.json no existe
        """
        # ----------------------------------------------------
        # 1. Guardar configuración de verbosidad
        # ----------------------------------------------------
        self.verbose = verbose
        # Esta bandera controla todos los prints del módulo

        # ----------------------------------------------------
        # 2. Verificar instalación de Kaggle
        # ----------------------------------------------------
        if not KAGGLE_AVAILABLE:
            # Si la bandera es False, 'kaggle' no se pudo importar
            raise ImportError(
                "\n❌ Kaggle API no está instalada.\n"
                "   Instala con: pip install kaggle\n"
            )
        # Si llegamos aquí, 'kaggle' está instalado ✅

        # ----------------------------------------------------
        # 3. Verificar credenciales (kaggle.json)
        # ----------------------------------------------------
        self._verify_credentials()
        # Método privado que verifica la existencia de kaggle.json
        # Si falla, lanza FileNotFoundError con instrucciones

        # ----------------------------------------------------
        # 4. Autenticar con la API de Kaggle
        # ----------------------------------------------------
        self.api = KaggleApi()  # Crear instancia del cliente
        self.api.authenticate()  # Leer kaggle.json y autenticar
        # Si falla, Kaggle lanzará una excepción automáticamente

        # ----------------------------------------------------
        # 5. Configurar directorio de descarga
        # ✅ CAMBIO v2.1.0: Usar config.py como fuente principal
        # ----------------------------------------------------
        if download_dir is None:
            # Si no se especificó ruta personalizada
            if CONFIG_AVAILABLE and RAW_DATA_DIRECTORY is not None:
                # ✅ PRIORIDAD 1: Usar configuración de config.py
                download_dir = RAW_DATA_DIRECTORY
                if self.verbose:
                    print(f"📂 Usando RAW_DATA_DIRECTORY de config.py")
            else:
                # ⚠️ FALLBACK: Si config.py no está disponible
                download_dir = Path('./data/raw/')
                if self.verbose:
                    print(f"⚠️ config.py no disponible, usando: {download_dir}")

        # Convertir a objeto Path (para operaciones modernas)
        self.download_dir = Path(download_dir)

        # Crear directorio si no existe (parents=True crea padres)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # ----------------------------------------------------
        # 6. Mensajes de confirmación
        # ----------------------------------------------------
        if self.verbose:
            print("✅ Kaggle API autenticada correctamente")
            print(f"📂 Descargas irán a: {self.download_dir}")

    # ========================================================
    # MÉTODO PRIVADO: _verify_credentials
    # ========================================================
    def _verify_credentials(self):
        """
        Verifica que kaggle.json existe en la ubicación correcta

        UBICACIONES ESPERADAS:
            - Windows: C:\\Users\\<usuario>\\.kaggle\\kaggle.json
            - Linux/Mac: ~/.kaggle/kaggle.json

        CONTENIDO DE kaggle.json:
            {
              "username": "tu_usuario_kaggle",
              "key": "tu_api_key_secreta"
            }

        VERIFICA:
            1. Existencia del archivo
            2. Permisos correctos (600 en Linux/Mac)

        Raises:
            FileNotFoundError: Si kaggle.json no existe
        """
        # ----------------------------------------------------
        # 1. Construir ruta esperada de kaggle.json
        # ----------------------------------------------------
        home = Path.home()  # Obtiene directorio home del usuario
        # En Windows: C:\Users\Anderson
        # En Linux: /home/anderson

        kaggle_json = home / '.kaggle' / 'kaggle.json'
        # Ruta final: ~/.kaggle/kaggle.json

        # ----------------------------------------------------
        # 2. Verificar si el archivo existe
        # ----------------------------------------------------
        if not kaggle_json.exists():
            # Si NO existe, lanzar error con instrucciones completas
            raise FileNotFoundError(
                f"\n{'='*70}\n"
                f"❌ NO SE ENCONTRÓ EL ARCHIVO kaggle.json\n"
                f"{'='*70}\n\n"
                f"📍 Ubicación esperada:\n"
                f"   {kaggle_json}\n\n"
                f"🔧 CÓMO CONFIGURARLO:\n\n"
                f"1️⃣ Ve a tu perfil de Kaggle:\n"
                f"   https://www.kaggle.com/settings\n\n"
                f"2️⃣ En la sección 'API', haz clic en:\n"
                f"   'Create New API Token'\n\n"
                f"3️⃣ Se descargará el archivo 'kaggle.json'\n\n"
                f"4️⃣ Colócalo en la ubicación correcta:\n"
                f"   • Windows: C:\\Users\\TU_USUARIO\\.kaggle\\kaggle.json\n"
                f"   • Linux/Mac: ~/.kaggle/kaggle.json\n\n"
                f"5️⃣ En Linux/Mac, ejecuta:\n"
                f"   chmod 600 ~/.kaggle/kaggle.json\n\n"
                f"{'='*70}\n"
            )
        # Si llegamos aquí, el archivo existe ✅

        # ----------------------------------------------------
        # 3. Verificar permisos (solo Linux/Mac)
        # ----------------------------------------------------
        if os.name != 'nt':  # 'nt' = Windows
            # En Linux/Mac, los permisos deben ser 600 (solo el usuario)
            import stat

            # Obtener permisos actuales del archivo
            perms = oct(kaggle_json.stat().st_mode)[-3:]
            # stat().st_mode devuelve algo como: 0o100600
            # oct() lo convierte a: '0o100600'
            # [-3:] extrae solo: '600'

            if perms != '600':
                # Advertencia si los permisos son incorrectos
                print(
                    f"\n⚠️ ADVERTENCIA: Permisos incorrectos en kaggle.json\n"
                    f"   Permisos actuales: {perms}\n"
                    f"   Permisos requeridos: 600\n"
                    f"   Ejecuta: chmod 600 {kaggle_json}\n"
                )
                # NOTA: No lanzamos error, solo advertencia
                # Kaggle puede funcionar, pero es menos seguro

    # ========================================================
    # MÉTODO PRINCIPAL: download
    # ========================================================
    def download(
        self,
        dataset_identifier: str,         # 'usuario/nombre-dataset'
        unzip: bool = True,              # Descomprimir automáticamente
        force: bool = False,             # Forzar descarga si ya existe
        destination_folder: Optional[str] = None  # Subcarpeta personalizada
    ) -> Path:
        """
        Descarga un dataset de Kaggle

        FLUJO DE DESCARGA:
            1. Validar parámetros
            2. Determinar directorio de destino
            3. Verificar si ya existe (skip si force=False)
            4. Descargar a directorio temporal
            5. Descomprimir si unzip=True
            6. Mover al directorio final
            7. Limpiar archivos temporales
            8. Mostrar resumen de archivos descargados

        Args:
            dataset_identifier: ID del dataset en formato 'usuario/nombre'
                               Ejemplo: 'carrie1/ecommerce-data'
            unzip: Si True, descomprime archivos .zip automáticamente
            force: Si True, descarga aunque ya exista localmente
            destination_folder: Nombre de subcarpeta en data/raw/
                               Si None, usa el nombre del dataset

        Returns:
            Path: Directorio donde se descargaron los archivos

        Raises:
            ValueError: Si el formato del identificador es inválido
            Exception: Si falla la descarga (conexión, permisos, etc.)

        Ejemplos:
            >>> downloader = KaggleDownloader()
            >>> # Descarga estándar
            >>> downloader.download('carrie1/ecommerce-data')
            >>> # Descarga a subcarpeta personalizada
            >>> downloader.download('hospital-data', destination_folder='hospital')
        """
        # ----------------------------------------------------
        # 1. Validar formato del identificador
        # ✅ MEJORA v2.1.0: Validación de parámetros
        # ----------------------------------------------------
        if '/' not in dataset_identifier:
            raise ValueError(
                f"\n❌ Formato inválido: '{dataset_identifier}'\n"
                f"   Debe ser: 'usuario/nombre-dataset'\n"
                f"   Ejemplo: 'carrie1/ecommerce-data'"
            )

        parts = dataset_identifier.split('/')
        if len(parts) != 2:
            raise ValueError(
                f"\n❌ El identificador debe tener exactamente un '/'\n"
                f"   Recibido: '{dataset_identifier}'"
            )

        # ----------------------------------------------------
        # 2. Mostrar banner de inicio
        # ----------------------------------------------------
        if self.verbose:
            print("\n" + "="*70)
            print("📥 DESCARGANDO DATASET DE KAGGLE")
            print("="*70)
            print(f"Dataset: {dataset_identifier}")

        # ----------------------------------------------------
        # 3. Determinar directorio de destino
        # ----------------------------------------------------
        if destination_folder:
            # Si se especificó subcarpeta, usarla
            target_dir = self.download_dir / destination_folder
            # Ejemplo: data/raw/hospital/
        else:
            # Si no, usar el nombre del dataset
            dataset_name = dataset_identifier.split('/')[-1]
            # 'carrie1/ecommerce-data' → 'ecommerce-data'
            target_dir = self.download_dir / dataset_name
            # Ejemplo: data/raw/ecommerce-data/

        # Crear directorio (parents=True crea padres si no existen)
        target_dir.mkdir(parents=True, exist_ok=True)

        if self.verbose:
            print(f"Destino: {target_dir}")

        # ----------------------------------------------------
        # 4. Verificar si ya existe
        # ----------------------------------------------------
        existing_files = list(target_dir.glob('*'))
        # .glob('*') retorna todos los archivos y carpetas
        # list() convierte el generador a lista

        if existing_files and not force:
            # Si hay archivos Y no se forzó la descarga
            if self.verbose:
                print(f"\n✅ Dataset ya existe ({len(existing_files)} archivos)")
                print(f"\n📂 Archivos encontrados:")

                # Mostrar primeros 5 archivos
                for file in existing_files[:5]:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    # .stat().st_size obtiene tamaño en bytes
                    # / (1024 * 1024) convierte a MB
                    print(f"   • {file.name} ({size_mb:.2f} MB)")

                # Si hay más de 5, mostrar conteo
                if len(existing_files) > 5:
                    print(f"   ... y {len(existing_files) - 5} archivos más")

                print(f"\n💡 Para forzar descarga, usa: force=True")

            # Retornar directorio existente sin descargar
            return target_dir

        # ----------------------------------------------------
        # 5. Iniciar descarga
        # ----------------------------------------------------
        if self.verbose:
            print(f"\n⏳ Descargando... (esto puede tardar varios minutos)")

        try:
            # ------------------------------------------------
            # 5.1. Crear directorio temporal
            # ------------------------------------------------
            temp_dir = self.download_dir / f"_temp_{dataset_identifier.split('/')[-1]}"
            # Ejemplo: data/raw/_temp_ecommerce-data/
            temp_dir.mkdir(exist_ok=True)

            # ------------------------------------------------
            # 5.2. Descargar usando API de Kaggle
            # ------------------------------------------------
            self.api.dataset_download_files(
                dataset_identifier,   # 'usuario/nombre-dataset'
                path=temp_dir,       # Descargar aquí temporalmente
                unzip=unzip,         # Descomprimir si es True
                quiet=not self.verbose  # Silenciar si verbose=False
            )
            # Esta llamada descarga y (opcionalmente) descomprime

            # ------------------------------------------------
            # 5.3. Mover archivos al directorio final
            # ------------------------------------------------
            for item in temp_dir.iterdir():
                # .iterdir() itera sobre archivos/carpetas
                dest = target_dir / item.name
                # Construir ruta destino

                if dest.exists():
                    # Si ya existe, eliminarlo primero
                    dest.unlink()

                # Mover archivo de temp a destino final
                shutil.move(str(item), str(dest))
                # shutil.move() requiere strings, no Path

            # ------------------------------------------------
            # 5.4. Limpiar directorio temporal
            # ------------------------------------------------
            temp_dir.rmdir()  # Eliminar carpeta vacía

            # ------------------------------------------------
            # 5.5. Mostrar resumen de descarga
            # ------------------------------------------------
            if self.verbose:
                print(f"\n✅ Descarga completada")

                # Listar archivos descargados
                files = list(target_dir.glob('*'))
                print(f"\n📂 Archivos descargados ({len(files)}):")

                for file in sorted(files):
                    if file.is_file():  # Solo archivos (no carpetas)
                        size_mb = file.stat().st_size / (1024 * 1024)
                        print(f"   • {file.name} ({size_mb:.2f} MB)")

                print(f"\n📍 Ubicación: {target_dir}")

            return target_dir

        except Exception as e:
            # ------------------------------------------------
            # 6. Manejo de errores
            # ------------------------------------------------
            if self.verbose:
                print(f"\n❌ Error al descargar: {e}")
                print(f"\n💡 POSIBLES SOLUCIONES:")
                print(f"   1. Verifica el identificador: {dataset_identifier}")
                print(f"   2. Verifica tu conexión a internet")
                print(f"   3. Verifica que kaggle.json es válido")
                print(f"   4. Intenta acceder al dataset en el navegador:")
                print(f"      https://www.kaggle.com/datasets/{dataset_identifier}")

            # Re-lanzar la excepción para que el código llamador la maneje
            raise

    # ========================================================
    # MÉTODO: search
    # ========================================================
    def search(
        self,
        query: str,              # Palabras clave de búsqueda
        max_results: int = 10,   # Número máximo de resultados
        sort_by: str = 'hottest' # Criterio de ordenamiento
    ) -> List:
        """
        Busca datasets en Kaggle por palabras clave

        CASOS DE USO:
            - Encontrar datasets antes de descargar
            - Explorar qué datos están disponibles
            - Verificar que un dataset existe

        Args:
            query: Palabras clave de búsqueda
                   Ejemplo: 'ecommerce retail', 'startup investment'
            max_results: Número máximo de resultados a retornar (1-100)
            sort_by: Criterio de ordenamiento:
                    - 'hottest': Más populares actualmente
                    - 'votes': Más votados
                    - 'updated': Actualizados recientemente
                    - 'active': Más activos (con discusión)

        Returns:
            List: Lista de objetos Dataset de Kaggle
                  Cada objeto tiene: .ref, .title, .size, .downloadCount, etc.

        Ejemplo:
            >>> downloader = KaggleDownloader()
            >>> results = downloader.search('ecommerce retail', max_results=5)
            >>> for dataset in results:
            ...     print(f"{dataset.ref} - {dataset.title}")
        """
        # ----------------------------------------------------
        # 1. Mostrar banner de búsqueda
        # ----------------------------------------------------
        if self.verbose:
            print(f"\n🔍 Buscando en Kaggle: '{query}'")
            print("="*70)

        try:
            # ------------------------------------------------
            # 2. Ejecutar búsqueda usando API
            # ------------------------------------------------
            datasets = self.api.dataset_list(
                search=query,        # Palabras clave
                max_size=max_results, # Límite de resultados
                sort_by=sort_by      # Criterio de orden
            )
            # Retorna lista de objetos Dataset

            # ------------------------------------------------
            # 3. Validar resultados
            # ------------------------------------------------
            if not datasets:
                # Si no se encontró nada
                if self.verbose:
                    print(f"❌ No se encontraron datasets para: '{query}'")
                return []  # Lista vacía

            # ------------------------------------------------
            # 4. Mostrar resultados (si verbose=True)
            # ------------------------------------------------
            if self.verbose:
                print(f"\n📊 Encontrados {len(datasets)} datasets:\n")

                for i, dataset in enumerate(datasets, 1):
                    # enumerate(datasets, 1) da: (1, dataset1), (2, dataset2), ...
                    print(f"{i}. {dataset.ref}")
                    # .ref es el identificador: 'usuario/nombre-dataset'

                    print(f"   📌 {dataset.title}")
                    # .title es el nombre descriptivo

                    print(f"   📦 Tamaño: {dataset.size}")
                    # .size es el tamaño legible: '500 MB'

                    print(f"   👥 Descargas: {dataset.downloadCount:,}")
                    # .downloadCount número de descargas
                    # :, formatea con comas: 1000 → 1,000

                    print(f"   ⭐ Votos: {dataset.voteCount}")
                    # .voteCount número de votos positivos

                    print(f"   🔗 https://www.kaggle.com/datasets/{dataset.ref}")
                    # URL directa al dataset

                    print()  # Línea en blanco entre resultados

            return datasets

        except Exception as e:
            # ------------------------------------------------
            # 5. Manejo de errores
            # ------------------------------------------------
            if self.verbose:
                print(f"\n❌ Error al buscar: {e}")
            return []  # Retornar lista vacía en caso de error

    # ========================================================
    # MÉTODO: list_files
    # ========================================================
    def list_files(
        self,
        dataset_identifier: str
    ) -> List[str]:
        """
        Lista archivos de un dataset sin descargarlo

        UTILIDAD:
            - Ver qué archivos contiene antes de descargar
            - Verificar tamaños
            - Decidir si descargar o no

        Args:
            dataset_identifier: ID del dataset ('usuario/nombre')

        Returns:
            List[str]: Lista de nombres de archivos

        Ejemplo:
            >>> downloader = KaggleDownloader()
            >>> files = downloader.list_files('carrie1/ecommerce-data')
            >>> print(files)
            ['data.csv', 'readme.txt']
        """
        # ----------------------------------------------------
        # 1. Mostrar banner
        # ----------------------------------------------------
        if self.verbose:
            print(f"\n📋 Archivos en '{dataset_identifier}':")
            print("="*70)

        try:
            # ------------------------------------------------
            # 2. Obtener lista de archivos usando API
            # ------------------------------------------------
            files_info = self.api.dataset_list_files(dataset_identifier).files
            # Retorna objeto con lista de archivos y sus propiedades

            # ------------------------------------------------
            # 3. Procesar y mostrar información
            # ------------------------------------------------
            filenames = []
            for file in files_info:
                # Calcular tamaño en MB
                size_mb = file.totalBytes / (1024 * 1024)
                # .totalBytes tiene el tamaño en bytes

                # Agregar nombre a la lista
                filenames.append(file.name)

                # Mostrar información si verbose=True
                if self.verbose:
                    print(f"   • {file.name} ({size_mb:.2f} MB)")

            return filenames

        except Exception as e:
            # ------------------------------------------------
            # 4. Manejo de errores
            # ------------------------------------------------
            if self.verbose:
                print(f"❌ Error: {e}")
            return []  # Retornar lista vacía

    # ========================================================
    # MÉTODO: download_competition
    # ========================================================
    def download_competition(
        self,
        competition_name: str,
        force: bool = False
    ) -> Path:
        """
        Descarga datos de una competencia de Kaggle

        NOTA: Requiere aceptar las reglas de la competencia en kaggle.com

        Args:
            competition_name: Nombre de la competencia (ej: 'titanic')
            force: Forzar descarga aunque ya exista

        Returns:
            Path: Directorio con los archivos descargados

        Ejemplo:
            >>> downloader = KaggleDownloader()
            >>> downloader.download_competition('titanic')
        """
        # ----------------------------------------------------
        # 1. Mostrar banner
        # ----------------------------------------------------
        if self.verbose:
            print(f"\n🏆 Descargando competencia: {competition_name}")

        # ----------------------------------------------------
        # 2. Configurar directorio de destino
        # ----------------------------------------------------
        target_dir = self.download_dir / f"competition_{competition_name}"
        target_dir.mkdir(exist_ok=True)

        # ----------------------------------------------------
        # 3. Verificar si ya existe
        # ----------------------------------------------------
        if list(target_dir.glob('*')) and not force:
            if self.verbose:
                print(f"✅ Competencia ya descargada en: {target_dir}")
            return target_dir

        # ----------------------------------------------------
        # 4. Descargar
        # ----------------------------------------------------
        try:
            self.api.competition_download_files(
                competition_name,
                path=target_dir,
                quiet=not self.verbose
            )

            # ------------------------------------------------
            # 5. Descomprimir archivos zip
            # ------------------------------------------------
            for zip_file in target_dir.glob('*.zip'):
                if self.verbose:
                    print(f"📦 Descomprimiendo: {zip_file.name}")

                # Descomprimir usando zipfile
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)

                # Eliminar el .zip después de extraer
                zip_file.unlink()

            if self.verbose:
                print(f"✅ Competencia descargada en: {target_dir}")

            return target_dir

        except Exception as e:
            # ------------------------------------------------
            # 6. Manejo de errores
            # ------------------------------------------------
            if self.verbose:
                print(f"❌ Error: {e}")
                print(f"\n💡 IMPORTANTE:")
                print(f"   Debes aceptar las reglas de la competencia en:")
                print(f"   https://www.kaggle.com/competitions/{competition_name}")
            raise


# ============================================================
# FUNCIONES DE CONVENIENCIA (Shortcuts)
# ============================================================
# Estas funciones simplifican el uso del módulo para casos comunes

def download_from_kaggle(
    dataset_identifier: str,
    destination_folder: Optional[str] = None
) -> Path:
    """
    Función rápida para descargar un dataset con una sola línea

    VENTAJAS:
        - No necesitas crear instancia de KaggleDownloader
        - Configuración automática
        - Ideal para scripts rápidos

    Args:
        dataset_identifier: ID del dataset ('usuario/nombre')
        destination_folder: Subcarpeta opcional en data/raw/

    Returns:
        Path: Directorio con archivos descargados

    Ejemplo:
        >>> from src.data.kaggle_downloader import download_from_kaggle
        >>> # Descarga rápida
        >>> download_from_kaggle('carrie1/ecommerce-data')
        >>> # Con subcarpeta
        >>> download_from_kaggle('hospital-data', destination_folder='hospital')
    """
    # Crear instancia (configuración automática usando config.py)
    downloader = KaggleDownloader()

    # Ejecutar descarga y retornar resultado
    return downloader.download(
        dataset_identifier,
        destination_folder=destination_folder
    )


def search_kaggle(query: str, max_results: int = 10):
    """
    Función rápida para buscar datasets

    Args:
        query: Palabras clave de búsqueda
        max_results: Número de resultados (default: 10)

    Returns:
        List: Datasets encontrados

    Ejemplo:
        >>> from src.data.kaggle_downloader import search_kaggle
        >>> results = search_kaggle('startup investment', max_results=5)
        >>> for dataset in results:
        ...     print(dataset.ref)
    """
    downloader = KaggleDownloader()
    return downloader.search(query, max_results)


def verify_kaggle_setup() -> bool:
    """
    Verifica que Kaggle está configurado correctamente

    VERIFICA:
        1. Librería 'kaggle' instalada
        2. Archivo kaggle.json existe
        3. Permisos correctos (Linux/Mac)
        4. Autenticación funciona
        5. config.py detectado correctamente

    Returns:
        bool: True si todo está configurado correctamente

    Ejemplo:
        >>> from src.data.kaggle_downloader import verify_kaggle_setup
        >>> if verify_kaggle_setup():
        ...     print("✅ Listo para descargar datasets")
        ... else:
        ...     print("❌ Configuración incompleta")
    """
    # ----------------------------------------------------
    # Banner de inicio
    # ----------------------------------------------------
    print("\n" + "="*70)
    print("🔍 VERIFICANDO CONFIGURACIÓN DE KAGGLE")
    print("="*70)

    # ----------------------------------------------------
    # 1. Verificar instalación de 'kaggle'
    # ----------------------------------------------------
    print("\n1️⃣ Verificando instalación de 'kaggle'...")

    if not KAGGLE_AVAILABLE:
        # Si la bandera global es False
        print("   ❌ Librería 'kaggle' NO instalada")
        print("   Instala con: pip install kaggle")
        return False  # Falló verificación

    print("   ✅ Librería 'kaggle' instalada")

    # ----------------------------------------------------
    # 2. Verificar kaggle.json
    # ----------------------------------------------------
    print("\n2️⃣ Verificando archivo kaggle.json...")

    home = Path.home()
    kaggle_json = home / '.kaggle' / 'kaggle.json'

    if not kaggle_json.exists():
        # Archivo no encontrado
        print(f"   ❌ Archivo NO encontrado: {kaggle_json}")
        print(f"\n   📝 CÓMO OBTENERLO:")
        print(f"   1. Ve a: https://www.kaggle.com/settings")
        print(f"   2. Sección 'API' → 'Create New API Token'")
        print(f"   3. Guarda kaggle.json en: {kaggle_json}")
        return False

    print(f"   ✅ Archivo encontrado: {kaggle_json}")

    # Verificar permisos (Linux/Mac)
    if os.name != 'nt':  # No es Windows
        import stat
        perms = oct(kaggle_json.stat().st_mode)[-3:]

        if perms == '600':
            print(f"   ✅ Permisos correctos: {perms}")
        else:
            print(f"   ⚠️ Permisos incorrectos: {perms}")
            print(f"   Ejecuta: chmod 600 {kaggle_json}")

    # ----------------------------------------------------
    # 3. Probar autenticación
    # ----------------------------------------------------
    print("\n3️⃣ Probando autenticación...")

    try:
        api = KaggleApi()
        api.authenticate()
        print("   ✅ Autenticación exitosa")
    except Exception as e:
        print(f"   ❌ Error de autenticación: {e}")
        return False

    # ----------------------------------------------------
    # 4. Verificar integración con config.py
    # ✅ NUEVO en v2.1.0
    # ----------------------------------------------------
    print("\n4️⃣ Verificando integración con config.py...")

    if CONFIG_AVAILABLE and RAW_DATA_DIRECTORY is not None:
        print(f"   ✅ config.py detectado correctamente")
        print(f"   ✅ RAW_DATA_DIRECTORY: {RAW_DATA_DIRECTORY}")
    else:
        print(f"   ⚠️ config.py no disponible (usando fallback)")

    # ----------------------------------------------------
    # 5. Crear instancia de prueba
    # ----------------------------------------------------
    print("\n5️⃣ Probando inicialización...")

    try:
        downloader = KaggleDownloader(verbose=False)
        print(f"   ✅ Directorio de descarga: {downloader.download_dir}")
    except Exception as e:
        print(f"   ⚠️ Advertencia: {e}")

    # ----------------------------------------------------
    # 6. Resumen final
    # ----------------------------------------------------
    print("\n" + "="*70)
    print("✅ CONFIGURACIÓN COMPLETA Y FUNCIONANDO")
    print("="*70)
    print("\n💡 Ahora puedes descargar datasets:")
    print("   from src.data.kaggle_downloader import download_from_kaggle")
    print("   download_from_kaggle('carrie1/ecommerce-data')")

    return True  # Todo OK ✅


# ============================================================
# EXPORTACIONES (para imports limpios)
# ============================================================
__all__ = [
    'KaggleDownloader',      # Clase principal
    'download_from_kaggle',  # Shortcut para descargar
    'search_kaggle',         # Shortcut para buscar
    'verify_kaggle_setup'    # Verificación de setup
]