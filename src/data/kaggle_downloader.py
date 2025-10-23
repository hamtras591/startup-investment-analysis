"""
Kaggle Downloader - Versión Simple
===================================
Descarga automática de datasets desde Kaggle.

REQUISITOS:
1. Tener kaggle.json en ~/.kaggle/ (Windows: C:\\Users\\TU_USUARIO\\.kaggle\\)
2. pip install kaggle
"""

import os
from pathlib import Path
from typing import Union
import zipfile
import shutil

try:
    from kaggle.api.kaggle_api_extended import KaggleApi

    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False


class KaggleDownloader:
    """
    Descargador de datasets de Kaggle
    """

    def __init__(self, download_dir: Union[str, Path] = None):
        """
        Inicializa el descargador

        Args:
            download_dir: Dónde descargar (default: data/raw)
        """
        # Verificar que Kaggle está instalado
        if not KAGGLE_AVAILABLE:
            raise ImportError(
                "\n❌ Kaggle API no está instalada.\n"
                "   Instala con: pip install kaggle\n"
            )

        # Verificar que kaggle.json existe
        self._check_credentials()

        # Autenticar
        self.api = KaggleApi()
        self.api.authenticate()

        # Configurar directorio de descarga
        if download_dir is None:
            from src.data.config import RAW_DATA_DIR
            download_dir = RAW_DATA_DIR

        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        print("✅ Kaggle API autenticada correctamente")
        print(f"📂 Descargas irán a: {self.download_dir}")

    def _check_credentials(self):
        """Verifica que kaggle.json existe"""
        home = Path.home()
        kaggle_json = home / '.kaggle' / 'kaggle.json'

        if not kaggle_json.exists():
            raise FileNotFoundError(
                f"\n❌ No se encontró kaggle.json\n"
                f"   Debería estar en: {kaggle_json}\n\n"
                f"   PASOS PARA CONFIGURARLO:\n"
                f"   1. Ve a: https://www.kaggle.com/settings\n"
                f"   2. En la sección 'API', haz clic en 'Create New API Token'\n"
                f"   3. Descarga kaggle.json\n"
                f"   4. Colócalo en: {kaggle_json}\n"
                f"   5. En Linux/Mac, ejecuta: chmod 600 {kaggle_json}\n"
            )

    def download(
            self,
            dataset_identifier: str,
            unzip: bool = True,
            force: bool = False
    ) -> Path:
        """
        Descarga un dataset de Kaggle

        Args:
            dataset_identifier: ID del dataset (ej: 'carrie1/ecommerce-data')
            unzip: Descomprimir automáticamente
            force: Forzar descarga aunque ya exista

        Returns:
            Path donde se descargó

        Ejemplo:
            >>> downloader = KaggleDownloader()
            >>> downloader.download('carrie1/ecommerce-data')
        """
        print(f"\n{'=' * 70}")
        print(f"📥 DESCARGANDO DATASET DE KAGGLE")
        print(f"{'=' * 70}")
        print(f"Dataset: {dataset_identifier}")
        print(f"Destino: {self.download_dir}")

        # Nombre del dataset
        dataset_name = dataset_identifier.split('/')[-1]

        # Verificar si ya existe
        existing_files = list(self.download_dir.glob(f"{dataset_name}*"))
        if existing_files and not force:
            print(f"\n✅ Dataset ya existe en: {self.download_dir}")
            print(f"   Archivos encontrados:")
            for file in existing_files:
                print(f"   • {file.name}")
            print(f"\n💡 Para forzar descarga, usa: force=True")
            return self.download_dir

        # Descargar
        print(f"\n⏳ Descargando... (esto puede tardar)")

        try:
            self.api.dataset_download_files(
                dataset_identifier,
                path=self.download_dir,
                unzip=unzip,
                quiet=False
            )

            print(f"\n✅ Descarga completada")

            # Mostrar archivos descargados
            print(f"\n📂 Archivos en {self.download_dir}:")
            for file in sorted(self.download_dir.iterdir()):
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"   • {file.name} ({size_mb:.2f} MB)")

            return self.download_dir

        except Exception as e:
            print(f"\n❌ Error al descargar: {e}")
            print(f"\n💡 POSIBLES SOLUCIONES:")
            print(f"   1. Verifica que el identificador es correcto: {dataset_identifier}")
            print(f"   2. Verifica tu conexión a internet")
            print(f"   3. Verifica que kaggle.json es válido")
            raise

    def search(self, query: str, max_results: int = 10):
        """
        Busca datasets en Kaggle

        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados

        Ejemplo:
            >>> downloader = KaggleDownloader()
            >>> downloader.search('retail sales')
        """
        print(f"\n🔍 Buscando en Kaggle: '{query}'")
        print(f"{'=' * 70}")

        try:
            # CORRECCIÓN: Usar max_size en lugar de page_size
            datasets = self.api.dataset_list(search=query, max_size=max_results)

            if not datasets:
                print(f"❌ No se encontraron datasets para: '{query}'")
                return []

            print(f"\n📊 Encontrados {len(datasets)} datasets:\n")

            for i, dataset in enumerate(datasets, 1):
                print(f"{i}. {dataset.ref}")
                print(f"   📌 Título: {dataset.title}")
                print(f"   📦 Tamaño: {dataset.size}")
                print(f"   👥 Descargas: {dataset.downloadCount:,}")
                print(f"   ⭐ Votos: {dataset.voteCount}")
                print()

            return datasets

        except Exception as e:
            print(f"\n❌ Error al buscar: {e}")
            print(f"\n💡 Verifica:")
            print(f"   • Tu conexión a internet")
            print(f"   • Que kaggle.json sea válido")
            return []

    def list_files(self, dataset_identifier: str):
        """
        Lista archivos de un dataset sin descargarlo

        Args:
            dataset_identifier: ID del dataset

        Ejemplo:
            >>> downloader = KaggleDownloader()
            >>> downloader.list_files('carrie1/ecommerce-data')
        """
        print(f"\n📋 Archivos en '{dataset_identifier}':")
        print(f"{'=' * 70}")

        try:
            files = self.api.dataset_list_files(dataset_identifier).files

            for file in files:
                size_mb = file.totalBytes / (1024 * 1024)
                print(f"   • {file.name} ({size_mb:.2f} MB)")

            return [file.name for file in files]

        except Exception as e:
            print(f"❌ Error: {e}")
            return []


# ============================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================

def download_from_kaggle(dataset_identifier: str) -> Path:
    """
    Función rápida para descargar un dataset

    Ejemplo:
        >>> from src.kaggle_downloader import download_from_kaggle
        >>> download_from_kaggle('carrie1/ecommerce-data')
    """
    downloader = KaggleDownloader()
    return downloader.download(dataset_identifier)


def search_kaggle(query: str):
    """
    Función rápida para buscar datasets

    Ejemplo:
        >>> from src.kaggle_downloader import search_kaggle
        >>> search_kaggle('retail sales')
    """
    downloader = KaggleDownloader()
    return downloader.search(query)


def verify_kaggle_setup():
    """
    Verifica que Kaggle está configurado correctamente

    Ejemplo:
        >>> from src.kaggle_downloader import verify_kaggle_setup
        >>> verify_kaggle_setup()
    """
    print("\n🔍 VERIFICANDO CONFIGURACIÓN DE KAGGLE")
    print("=" * 70)

    # 1. Verificar instalación
    print("\n1️⃣ Verificando instalación de kaggle...")
    if KAGGLE_AVAILABLE:
        print("   ✅ Librería 'kaggle' instalada")
    else:
        print("   ❌ Librería 'kaggle' NO instalada")
        print("   Instala con: pip install kaggle")
        return False

    # 2. Verificar kaggle.json
    print("\n2️⃣ Verificando archivo kaggle.json...")
    home = Path.home()
    kaggle_json = home / '.kaggle' / 'kaggle.json'

    if kaggle_json.exists():
        print(f"   ✅ Archivo encontrado: {kaggle_json}")

        # Verificar permisos en Linux/Mac
        if os.name != 'nt':  # No Windows
            import stat
            perms = oct(kaggle_json.stat().st_mode)[-3:]
            if perms == '600':
                print(f"   ✅ Permisos correctos: {perms}")
            else:
                print(f"   ⚠️ Permisos incorrectos: {perms}")
                print(f"   Ejecuta: chmod 600 {kaggle_json}")
    else:
        print(f"   ❌ Archivo NO encontrado: {kaggle_json}")
        print(f"\n   PASOS PARA CREAR kaggle.json:")
        print(f"   1. Ve a: https://www.kaggle.com/settings")
        print(f"   2. Sección 'API' → 'Create New API Token'")
        print(f"   3. Guarda el archivo en: {kaggle_json}")
        return False

    # 3. Probar autenticación
    print("\n3️⃣ Probando autenticación...")
    try:
        api = KaggleApi()
        api.authenticate()
        print("   ✅ Autenticación exitosa")

        # Obtener usuario
        print(f"\n👤 Usuario autenticado correctamente")

    except Exception as e:
        print(f"   ❌ Error de autenticación: {e}")
        return False

    print("\n" + "=" * 70)
    print("✅ CONFIGURACIÓN COMPLETA Y FUNCIONANDO")
    print("=" * 70)
    print("\n💡 Ahora puedes descargar datasets con:")
    print("   from src.kaggle_downloader import download_from_kaggle")
    print("   download_from_kaggle('carrie1/ecommerce-data')")

    return True


__all__ = [
    'KaggleDownloader',
    'download_from_kaggle',
    'search_kaggle',
    'verify_kaggle_setup'
]