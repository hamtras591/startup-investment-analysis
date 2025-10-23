# data_loader.py

import pandas as pd
from pathlib import Path
import chardet
import logging
from typing import Optional, Dict, Any, Union, List

# 💡 IMPORTAMOS LAS RUTAS DE CONFIGURACIÓN
try:
    from config import RAW_DATA_DIR, PROCESSED_DATA_DIR
except ImportError:
    # Fallback si config.py no está en la ruta
    logging.error("❌ No se pudo importar RAW_DATA_DIR/PROCESSED_DATA_DIR de config.py.")
    RAW_DATA_DIR = Path('./data/raw/')
    PROCESSED_DATA_DIR = Path('./data/processed/')


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UniversalDataLoader:
    """
    Cargador universal de datos que maneja automáticamente:
    - Detección de encoding
    - Múltiples formatos (CSV, Excel, JSON, Parquet)
    - Caché de archivos
    """

    def __init__(self, verbose: bool = True):
        """Inicializa el cargador universal"""
        self.verbose = verbose
        self._cache = {}

    def _log(self, message: str, level=logging.INFO):
        """Usa el sistema de logging si verbose está activo"""
        if self.verbose:
            logger.log(level, message)

    # =====================================================================
    # ⚙️ MÉTODOS DE LECTURA DE ARCHIVOS (Mantenidos del notebook)
    # =====================================================================

    def _detect_encoding(self, filepath: Path, sample_size: int = 100000) -> tuple:
        """Detecta el encoding del archivo"""
        try:
            with open(filepath, 'rb') as file:
                raw_data = file.read(sample_size)
                result = chardet.detect(raw_data)
                return result['encoding'], result['confidence']
        except Exception:
            self._log("⚠️ Fallback: Usando utf-8 por defecto.", logging.WARNING)
            return 'utf-8', 0.5

    def _detect_delimiter(self, filepath: Path) -> str:
        """Detecta el delimitador del CSV"""
        with open(filepath, 'r', encoding='latin-1', errors='ignore') as file:
            first_line = file.readline()

        # Contar ocurrencias de posibles delimitadores
        delimiters = {',': first_line.count(','), ';': first_line.count(';'), '\t': first_line.count('\t'), '|': first_line.count('|')}

        # Devuelve el delimitador con más ocurrencias
        return max(delimiters, key=delimiters.get)

    def _check_corruption(self, df: pd.DataFrame) -> bool:
        """Verifica si hay caracteres corruptos en el DataFrame"""
        corruption_patterns = ['Ã', 'Â£', 'Ã±', 'Ã¡', 'Ã©', 'Â']
        for col in df.select_dtypes(include=['object']).columns:
            sample = df[col].astype(str).head(100).str.cat(sep=' ')
            if any(pattern in sample for pattern in corruption_patterns):
                return True
        return False

    def _fallback_csv_load(self, filepath: Path) -> pd.DataFrame:
        """Método de respaldo para CSVs problemáticos"""
        self._log("⚠️ Error, intentando con configuración robusta")
        return pd.read_csv(
            filepath,
            encoding='latin-1',
            sep=None,
            engine='python',
            on_bad_lines='skip',
            encoding_errors='ignore'
        )

    # ---------------------------------------------------------------------
    # MÉTODOS DE CARGA POR FORMATO
    # ---------------------------------------------------------------------

    def _load_csv(self, filepath: Path, **kwargs) -> pd.DataFrame:
        """Carga archivos CSV con detección automática de encoding y delimitador"""
        # (Lógica de detección de separador y encoding del notebook)
        if 'sep' not in kwargs and 'delimiter' not in kwargs:
            kwargs['sep'] = self._detect_delimiter(filepath)
            self._log(f"📊 Separador detectado: '{kwargs['sep']}'")
        if 'encoding' not in kwargs:
            encoding, confidence = self._detect_encoding(filepath)
            kwargs['encoding'] = encoding
            self._log(f"🔤 Encoding detectado: {encoding} ({confidence:.1%} confianza)")

        try:
            df = pd.read_csv(filepath, **kwargs)
            self._log(f"✅ CSV cargado: {df.shape[0]:,} filas × {df.shape[1]} columnas")
        except UnicodeDecodeError:
            self._log("⚠️ Error de encoding, intentando con latin-1")
            kwargs['encoding'] = 'latin-1'
            df = pd.read_csv(filepath, **kwargs)
        except Exception:
            df = self._fallback_csv_load(filepath)

        if self._check_corruption(df):
            self._log("⚠️ Posible corrupción de caracteres detectada", logging.WARNING)
        return df

    def _load_excel(self, filepath: Path, **kwargs) -> pd.DataFrame:
        """Carga archivos Excel"""
        try:
            df = pd.read_excel(filepath, **kwargs)
            self._log(f"✅ Excel cargado: {df.shape[0]:,} filas × {df.shape[1]} columnas")
            return df
        except Exception as e:
            self._log(f"❌ Error cargando Excel: {e}", logging.ERROR)
            raise

    def _load_json(self, filepath: Path, **kwargs) -> pd.DataFrame:
        """Carga archivos JSON"""
        try:
            df = pd.read_json(filepath, **kwargs)
            self._log(f"✅ JSON cargado: {df.shape[0]:,} filas × {df.shape[1]} columnas")
            return df
        except Exception as e:
            self._log("⚠️ Intentando con orientaciones diferentes para JSON")
            for orient in ['records', 'index', 'columns', 'values']:
                try:
                    df = pd.read_json(filepath, orient=orient)
                    self._log(f"✅ JSON cargado con orient='{orient}'")
                    return df
                except:
                    continue
            self._log(f"❌ Falló la carga de JSON en todas las orientaciones: {e}", logging.ERROR)
            raise

    def _load_parquet(self, filepath: Path, **kwargs) -> pd.DataFrame:
        """Carga archivos Parquet (formato eficiente)"""
        try:
            df = pd.read_parquet(filepath, **kwargs)
            self._log(f"✅ Parquet cargado: {df.shape[0]:,} filas × {df.shape[1]} columnas")
            return df
        except ImportError:
            self._log("❌ Instala 'pyarrow' para leer archivos Parquet", logging.ERROR)
            raise

    # =====================================================================
    # ⬆️ MÉTODO PRINCIPAL: LOAD
    # =====================================================================

    def load(self,
             filepath: Union[str, Path],
             force_reload: bool = False,
             **kwargs) -> pd.DataFrame:
        """Método principal - carga cualquier archivo automáticamente"""
        filepath = Path(filepath)

        # Verificar caché
        cache_key = str(filepath.absolute())
        if not force_reload and cache_key in self._cache:
            self._log("📦 Cargando desde caché")
            return self._cache[cache_key]

        # Detectar tipo de archivo y cargar
        file_extension = filepath.suffix.lower()

        if file_extension in ['.csv', '.txt', '.tsv']:
            df = self._load_csv(filepath, **kwargs)
        elif file_extension in ['.xlsx', '.xls']:
            df = self._load_excel(filepath, **kwargs)
        elif file_extension == '.json':
            df = self._load_json(filepath, **kwargs)
        elif file_extension == '.parquet':
            df = self._load_parquet(filepath, **kwargs)
        else:
            raise ValueError(f"Formato no soportado: {file_extension}")

        # Guardar en caché y metadata
        self._cache[cache_key] = df
        df.attrs['source_file'] = str(filepath)
        df.attrs['load_timestamp'] = pd.Timestamp.now()

        return df

    # =====================================================================
    # 💾 NUEVO MÉTODO DE GUARDADO INTEGRADO CON CONFIG.PY
    # =====================================================================

    def save_data(self,
                  df: pd.DataFrame,
                  filename: str,
                  location: str = 'processed',
                  format: str = 'auto',
                  index: bool = False) -> Path:
        """
        Guarda el DataFrame en las carpetas de destino definidas en config.py.

        Args:
            df: El DataFrame a guardar.
            filename: Nombre del archivo (ej: 'datos_limpios.parquet').
            location: 'raw' o 'processed'. Por defecto, 'processed'.
            format: Formato ('csv', 'excel', 'parquet', 'auto').
            index: Incluir el índice del DataFrame.
        """

        # 1. Determinar la carpeta de destino usando config.py
        if location.lower() == 'raw':
            target_dir = RAW_DATA_DIR
        elif location.lower() == 'processed':
            target_dir = PROCESSED_DATA_DIR
        else:
            raise ValueError("La ubicación debe ser 'raw' o 'processed'")

        output_path = target_dir / filename

        if format == 'auto':
            format = output_path.suffix[1:] if output_path.suffix else 'csv'

        self._log(f"💾 Guardando data en {target_dir.name}/{filename} como {format.upper()}")

        # 2. Guardar
        if format == 'csv':
            df.to_csv(output_path, encoding='utf-8', index=index)
        elif format == 'excel':
            df.to_excel(output_path, index=index)
        elif format == 'parquet':
            df.to_parquet(output_path, index=index)
        else:
            raise ValueError(f"Formato no soportado: {format}")

        return output_path

# =====================================================================
# FUNCIONES DE CONVENIENCIA (Shortcuts)
# =====================================================================

def load_raw(filename: str, **kwargs) -> pd.DataFrame:
    """
    Carga un archivo directamente desde la carpeta data/raw/, buscando
    recursivamente en cualquier subcarpeta con una sola línea de código.

    Args:
        filename: El nombre exacto del archivo (ej: 'online_retail.csv').

    Returns:
        DataFrame de pandas.
    """

    # 1. 🔑 SOLUCIÓN: Importamos la ruta base en tiempo de ejecución.
    #    Esto resuelve la ruta absoluta correcta (D:\...\data\raw) usando el sys.path del notebook.
    try:
        # Importación absoluta que funciona cuando 'src' está en el sys.path
        from src.data.config import RAW_DATA_DIR
    except ImportError as e:
        # Si esta importación falla, es un error fatal de estructura de proyecto.
        logger.error(f"❌ Error fatal: No se pudo importar RAW_DATA_DIR desde src.data.config.")
        raise ImportError(
            f"No se pudo resolver la ruta base: Asegúrese de que 'src' esté en el sys.path de su notebook. Error original: {e}")

    loader = UniversalDataLoader()

    # 2. 🔍 BÚSQUEDA RECURSIVA: RAW_DATA_DIR ya es la ruta absoluta correcta.
    search_results = list(RAW_DATA_DIR.rglob(filename))

    if not search_results:
        # ❌ Caso 1: Archivo no encontrado
        raise FileNotFoundError(
            f"❌ Archivo '{filename}' no encontrado en {RAW_DATA_DIR.resolve()} ni en sus subcarpetas. "
            f"Verifique el nombre exacto del archivo."
        )

    # 3. ✔️ Cargar el archivo encontrado
    filepath = search_results[0]

    if len(search_results) > 1:
        logger.warning(
            f"⚠️ Múltiples archivos encontrados con el nombre '{filename}'. "
            f"Cargando el primero: {filepath.relative_to(RAW_DATA_DIR)}"
        )

    logger.info(f"📁 Archivo encontrado en subcarpeta. Cargando: {filepath.relative_to(RAW_DATA_DIR)}")
    return loader.load(filepath, **kwargs)

    logger.info(f"📁 Archivo encontrado en subcarpeta. Cargando: {filepath.relative_to(search_dir)}")  # Usa search_dir
    return loader.load(filepath, **kwargs)

def save_processed(df: pd.DataFrame, filename: str, **kwargs) -> Path:
    """Guarda un DataFrame en la carpeta data/processed/"""
    loader = UniversalDataLoader()
    # Usamos el nuevo método save_data
    return loader.save_data(df, filename, location='processed', **kwargs)