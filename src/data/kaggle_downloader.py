"""
Kaggle Downloader Module
=========================
Descarga automática de datasets desde Kaggle.
Diseñado para estructura: src/data/kaggle_downloader.py

Autor: Anderson Sebastian Rubio Pacheco
Versión: 2.0.0
"""

import os
from pathlib import Path
from typing import Union, Optional, List
import zipfile
import shutil

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False


class KaggleDownloader:
    """
    Descargador automático de datasets de Kaggle

    Requisitos:
    1. pip install kaggle
    2. Archivo kaggle.json en ~/.kaggle/ (o C:\\Users\\USER\\.kaggle\\ en Windows)
    3. Permisos 600 en kaggle.json (Linux/Mac)
    """

    def __init__(
        self,
        download_dir: Optional[Union[str, Path]] = None,
        verbose: bool = True
    ):
        """
        Inicializa el descargador de Kaggle

        Args:
            download_dir: Directorio de descarga (default: data/raw/)
            verbose: Mostrar mensajes detallados
        """
        self.verbose = verbose

        # Verificar instalación de Kaggle
        if not KAGGLE_AVAILABLE:
            raise ImportError(
                "\n❌ Kaggle API no está instalada.\n"
                "   Instala con: pip install kaggle\n"
            )

        # Verificar credenciales
        self._verify_credentials()

        # Autenticar API
        self.api = KaggleApi()
        self.api.authenticate()

        # Configurar directorio de descarga
        if download_dir is None:
            # Detectar automáticamente data/raw/
            download_dir = self._find_raw_directory()

        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        if self.verbose:
            print("✅ Kaggle API autenticada correctamente")
            print(f"📂 Descargas irán a: {self.download_dir}")

    def _verify_credentials(self):
        """Verifica que kaggle.json existe en la ubicación correcta"""
        home = Path.home()
        kaggle_json = home / '.kaggle' / 'kaggle.json'

        if not kaggle_json.exists():
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

        # Verificar permisos en Linux/Mac
        if os.name != 'nt':  # No es Windows
            import stat
            perms = oct(kaggle_json.stat().st_mode)[-3:]
            if perms != '600':
                print(
                    f"\n⚠️ ADVERTENCIA: Permisos incorrectos en kaggle.json\n"
                    f"   Permisos actuales: {perms}\n"
                    f"   Permisos requeridos: 600\n"
                    f"   Ejecuta: chmod 600 {kaggle_json}\n"
                )

    def _find_raw_directory(self) -> Path:
        """
        Encuentra automáticamente la carpeta data/raw/

        Busca desde la ubicación de este archivo hacia arriba:
        src/data/kaggle_downloader.py → proyecto/data/raw/
        """
        # Este archivo está en: proyecto/src/data/kaggle_downloader.py
        current = Path(__file__).resolve().parent  # src/data/

        # Subir hasta encontrar la raíz del proyecto
        for _ in range(5):
            # Verificar si existe data/raw/
            candidate = current.parent / 'data' / 'raw'

            if candidate.exists():
                if self.verbose:
                    print(f"📂 Directorio data/raw/ detectado: {candidate}")
                return candidate

            # Subir un nivel
            current = current.parent

            # Si llegamos a la raíz del sistema, detenernos
            if current == current.parent:
                break

        # Si no encontramos, crear en la ubicación estándar
        # proyecto/src/data/ → proyecto/data/raw/
        project_root = Path(__file__).resolve().parent.parent.parent
        default_raw = project_root / 'data' / 'raw'

        if self.verbose:
            print(f"⚠️ No se encontró data/raw/, usando: {default_raw}")

        return default_raw

    def download(
        self,
        dataset_identifier: str,
        unzip: bool = True,
        force: bool = False,
        destination_folder: Optional[str] = None
    ) -> Path:
        """
        Descarga un dataset de Kaggle

        Args:
            dataset_identifier: ID del dataset (formato: 'usuario/nombre-dataset')
            unzip: Descomprimir automáticamente archivos zip
            force: Forzar descarga aunque ya exista
            destination_folder: Subcarpeta dentro de data/raw/ (opcional)

        Returns:
            Path: Directorio donde se descargaron los archivos

        Ejemplos:
            >>> downloader = KaggleDownloader()
            >>> downloader.download('carrie1/ecommerce-data')
            >>> downloader.download('jaderz/hospital-beds-management', destination_folder='hospital')
        """
        if self.verbose:
            print("\n" + "="*70)
            print("📥 DESCARGANDO DATASET DE KAGGLE")
            print("="*70)
            print(f"Dataset: {dataset_identifier}")

        # Determinar directorio de destino
        if destination_folder:
            target_dir = self.download_dir / destination_folder
        else:
            # Usar el nombre del dataset
            dataset_name = dataset_identifier.split('/')[-1]
            target_dir = self.download_dir / dataset_name

        target_dir.mkdir(parents=True, exist_ok=True)

        if self.verbose:
            print(f"Destino: {target_dir}")

        # Verificar si ya existe
        existing_files = list(target_dir.glob('*'))
        if existing_files and not force:
            if self.verbose:
                print(f"\n✅ Dataset ya existe ({len(existing_files)} archivos)")
                print(f"\n📂 Archivos encontrados:")
                for file in existing_files[:5]:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"   • {file.name} ({size_mb:.2f} MB)")
                if len(existing_files) > 5:
                    print(f"   ... y {len(existing_files) - 5} archivos más")
                print(f"\n💡 Para forzar descarga, usa: force=True")
            return target_dir

        # Descargar
        if self.verbose:
            print(f"\n⏳ Descargando... (esto puede tardar varios minutos)")

        try:
            # Descargar a directorio temporal
            temp_dir = self.download_dir / f"_temp_{dataset_identifier.split('/')[-1]}"
            temp_dir.mkdir(exist_ok=True)

            self.api.dataset_download_files(
                dataset_identifier,
                path=temp_dir,
                unzip=unzip,
                quiet=not self.verbose
            )

            # Mover archivos al directorio final
            for item in temp_dir.iterdir():
                dest = target_dir / item.name
                if dest.exists():
                    dest.unlink()
                shutil.move(str(item), str(dest))

            # Limpiar directorio temporal
            temp_dir.rmdir()

            if self.verbose:
                print(f"\n✅ Descarga completada")

                # Mostrar archivos descargados
                files = list(target_dir.glob('*'))
                print(f"\n📂 Archivos descargados ({len(files)}):")
                for file in sorted(files):
                    if file.is_file():
                        size_mb = file.stat().st_size / (1024 * 1024)
                        print(f"   • {file.name} ({size_mb:.2f} MB)")

                print(f"\n📍 Ubicación: {target_dir}")

            return target_dir

        except Exception as e:
            if self.verbose:
                print(f"\n❌ Error al descargar: {e}")
                print(f"\n💡 POSIBLES SOLUCIONES:")
                print(f"   1. Verifica el identificador: {dataset_identifier}")
                print(f"   2. Verifica tu conexión a internet")
                print(f"   3. Verifica que kaggle.json es válido")
                print(f"   4. Intenta acceder al dataset en el navegador:")
                print(f"      https://www.kaggle.com/datasets/{dataset_identifier}")
            raise

    def search(
        self,
        query: str,
        max_results: int = 10,
        sort_by: str = 'hottest'
    ) -> List:
        """
        Busca datasets en Kaggle

        Args:
            query: Término de búsqueda (palabras clave)
            max_results: Número máximo de resultados (1-100)
            sort_by: Ordenar por 'hottest', 'votes', 'updated', 'active'

        Returns:
            Lista de datasets encontrados

        Ejemplo:
            >>> downloader = KaggleDownloader()
            >>> results = downloader.search('ecommerce retail')
            >>> for dataset in results:
            ...     print(dataset.ref, dataset.title)
        """
        if self.verbose:
            print(f"\n🔍 Buscando en Kaggle: '{query}'")
            print("="*70)

        try:
            datasets = self.api.dataset_list(
                search=query,
                max_size=max_results,
                sort_by=sort_by
            )

            if not datasets:
                if self.verbose:
                    print(f"❌ No se encontraron datasets para: '{query}'")
                return []

            if self.verbose:
                print(f"\n📊 Encontrados {len(datasets)} datasets:\n")

                for i, dataset in enumerate(datasets, 1):
                    print(f"{i}. {dataset.ref}")
                    print(f"   📌 {dataset.title}")
                    print(f"   📦 Tamaño: {dataset.size}")
                    print(f"   👥 Descargas: {dataset.downloadCount:,}")
                    print(f"   ⭐ Votos: {dataset.voteCount}")
                    print(f"   🔗 https://www.kaggle.com/datasets/{dataset.ref}")
                    print()

            return datasets

        except Exception as e:
            if self.verbose:
                print(f"\n❌ Error al buscar: {e}")
            return []

    def list_files(
        self,
        dataset_identifier: str
    ) -> List[str]:
        """
        Lista archivos de un dataset sin descargarlo

        Args:
            dataset_identifier: ID del dataset

        Returns:
            Lista de nombres de archivos

        Ejemplo:
            >>> downloader = KaggleDownloader()
            >>> files = downloader.list_files('carrie1/ecommerce-data')
            >>> print(files)
            ['data.csv', 'readme.txt']
        """
        if self.verbose:
            print(f"\n📋 Archivos en '{dataset_identifier}':")
            print("="*70)

        try:
            files_info = self.api.dataset_list_files(dataset_identifier).files

            filenames = []
            for file in files_info:
                size_mb = file.totalBytes / (1024 * 1024)
                filenames.append(file.name)

                if self.verbose:
                    print(f"   • {file.name} ({size_mb:.2f} MB)")

            return filenames

        except Exception as e:
            if self.verbose:
                print(f"❌ Error: {e}")
            return []

    def download_competition(
        self,
        competition_name: str,
        force: bool = False
    ) -> Path:
        """
        Descarga datos de una competencia de Kaggle

        Args:
            competition_name: Nombre de la competencia (ej: 'titanic')
            force: Forzar descarga

        Returns:
            Path: Directorio con los archivos

        Ejemplo:
            >>> downloader = KaggleDownloader()
            >>> downloader.download_competition('titanic')
        """
        if self.verbose:
            print(f"\n🏆 Descargando competencia: {competition_name}")

        target_dir = self.download_dir / f"competition_{competition_name}"
        target_dir.mkdir(exist_ok=True)

        if list(target_dir.glob('*')) and not force:
            if self.verbose:
                print(f"✅ Competencia ya descargada en: {target_dir}")
            return target_dir

        try:
            self.api.competition_download_files(
                competition_name,
                path=target_dir,
                quiet=not self.verbose
            )

            # Descomprimir archivos zip
            for zip_file in target_dir.glob('*.zip'):
                if self.verbose:
                    print(f"📦 Descomprimiendo: {zip_file.name}")
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
                zip_file.unlink()

            if self.verbose:
                print(f"✅ Competencia descargada en: {target_dir}")

            return target_dir

        except Exception as e:
            if self.verbose:
                print(f"❌ Error: {e}")
            raise


# ============================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================

def download_from_kaggle(
    dataset_identifier: str,
    destination_folder: Optional[str] = None
) -> Path:
    """
    Función rápida para descargar un dataset

    Args:
        dataset_identifier: ID del dataset (usuario/nombre)
        destination_folder: Subcarpeta en data/raw/ (opcional)

    Returns:
        Path: Directorio con los archivos descargados

    Ejemplo:
        >>> from src.data.kaggle_downloader import download_from_kaggle
        >>> path = download_from_kaggle('carrie1/ecommerce-data')
        >>> path = download_from_kaggle('hospital-data', destination_folder='hospital')
    """
    downloader = KaggleDownloader()
    return downloader.download(dataset_identifier, destination_folder=destination_folder)


def search_kaggle(query: str, max_results: int = 10):
    """
    Función rápida para buscar datasets

    Args:
        query: Palabras clave de búsqueda
        max_results: Número máximo de resultados

    Returns:
        Lista de datasets encontrados

    Ejemplo:
        >>> from src.data.kaggle_downloader import search_kaggle
        >>> results = search_kaggle('startup investment')
    """
    downloader = KaggleDownloader()
    return downloader.search(query, max_results)


def verify_kaggle_setup() -> bool:
    """
    Verifica que Kaggle está configurado correctamente

    Returns:
        bool: True si todo está correcto

    Ejemplo:
        >>> from src.data.kaggle_downloader import verify_kaggle_setup
        >>> if verify_kaggle_setup():
        ...     print("✅ Kaggle listo para usar")
    """
    print("\n" + "="*70)
    print("🔍 VERIFICANDO CONFIGURACIÓN DE KAGGLE")
    print("="*70)

    # 1. Verificar instalación
    print("\n1️⃣ Verificando instalación de 'kaggle'...")
    if not KAGGLE_AVAILABLE:
        print("   ❌ Librería 'kaggle' NO instalada")
        print("   Instala con: pip install kaggle")
        return False
    print("   ✅ Librería 'kaggle' instalada")

    # 2. Verificar kaggle.json
    print("\n2️⃣ Verificando archivo kaggle.json...")
    home = Path.home()
    kaggle_json = home / '.kaggle' / 'kaggle.json'

    if not kaggle_json.exists():
        print(f"   ❌ Archivo NO encontrado: {kaggle_json}")
        print(f"\n   📝 CÓMO OBTENERLO:")
        print(f"   1. Ve a: https://www.kaggle.com/settings")
        print(f"   2. Sección 'API' → 'Create New API Token'")
        print(f"   3. Guarda kaggle.json en: {kaggle_json}")
        return False

    print(f"   ✅ Archivo encontrado: {kaggle_json}")

    # Verificar permisos (Linux/Mac)
    if os.name != 'nt':
        import stat
        perms = oct(kaggle_json.stat().st_mode)[-3:]
        if perms == '600':
            print(f"   ✅ Permisos correctos: {perms}")
        else:
            print(f"   ⚠️ Permisos incorrectos: {perms}")
            print(f"   Ejecuta: chmod 600 {kaggle_json}")

    # 3. Probar autenticación
    print("\n3️⃣ Probando autenticación...")
    try:
        api = KaggleApi()
        api.authenticate()
        print("   ✅ Autenticación exitosa")
    except Exception as e:
        print(f"   ❌ Error de autenticación: {e}")
        return False

    # 4. Detectar data/raw/
    print("\n4️⃣ Detectando directorio data/raw/...")
    try:
        downloader = KaggleDownloader(verbose=False)
        print(f"   ✅ Directorio detectado: {downloader.download_dir}")
    except Exception as e:
        print(f"   ⚠️ Advertencia: {e}")

    print("\n" + "="*70)
    print("✅ CONFIGURACIÓN COMPLETA Y FUNCIONANDO")
    print("="*70)
    print("\n💡 Ahora puedes descargar datasets:")
    print("   from src.data.kaggle_downloader import download_from_kaggle")
    print("   download_from_kaggle('carrie1/ecommerce-data')")

    return True


__all__ = [
    'KaggleDownloader',
    'download_from_kaggle',
    'search_kaggle',
    'verify_kaggle_setup'
]