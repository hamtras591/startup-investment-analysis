"""
Universal Data Loader Module
============================
Módulo reutilizable para cargar cualquier tipo de datos sin problemas de encoding.

PROPÓSITO:
    Cargar y guardar datos en múltiples formatos (CSV, Excel, JSON, Parquet)
    con detección automática de encoding y manejo robusto de errores.

FUNCIONALIDADES:
    1. Detección automática de encoding (UTF-8, Latin-1, etc.)
    2. Detección automática de delimitadores (CSV)
    3. Soporte para múltiples formatos
    4. Caché en memoria para archivos cargados
    5. Validación de corrupción de caracteres
    6. Integración con config.py para rutas estandarizadas

UBICACIÓN EN EL PROYECTO:
    src/data/data_loader.py

AUTOR: Anderson Sebastian Rubio Pacheco
VERSIÓN: 2.0.0
FECHA: Octubre 2025
CAMBIOS v2.0.0: Integración completa con config.py
"""

# ============================================================
# SECCIÓN 1: IMPORTACIONES
# ============================================================

import pandas as pd  # Manipulación de datos
from pathlib import Path  # Manejo moderno de rutas
import chardet  # Detección de encoding
import logging  # Sistema de logs
from typing import Optional, Dict, Any, Union

# ============================================================
# Importar configuración centralizada del proyecto
# ============================================================
try:
    # Importar rutas desde config.py
    from src.data.config import (
        RAW_DATA_DIRECTORY,  # data/raw/
        PROCESSED_DATA_DIRECTORY  # data/processed/
    )

    CONFIG_AVAILABLE = True
except ImportError:
    # Fallback si config.py no está disponible
    RAW_DATA_DIRECTORY = Path('./data/raw/')
    PROCESSED_DATA_DIRECTORY = Path('./data/processed/')
    CONFIG_AVAILABLE = False

# ============================================================
# Configurar logging
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# CLASE PRINCIPAL: UniversalDataLoader
# ============================================================

class UniversalDataLoader:
    """
    Cargador universal de datos con detección automática

    RESPONSABILIDADES:
        - Detectar encoding automáticamente
        - Detectar delimitadores en CSVs
        - Cargar múltiples formatos (CSV, Excel, JSON, Parquet)
        - Validar integridad de datos
        - Cachear archivos en memoria
        - Guardar datos en formatos limpios

    FORMATOS SOPORTADOS:
        - CSV (.csv, .txt, .tsv)
        - Excel (.xlsx, .xls)
        - JSON (.json)
        - Parquet (.parquet)

    ATRIBUTOS:
        verbose (bool): Controla mensajes detallados
        _cache (dict): Caché de DataFrames cargados

    EJEMPLO DE USO:
        >>> loader = UniversalDataLoader()
        >>> df = loader.load('data.csv')
        >>> loader.save_data(df, 'clean_data.csv', location='processed')
    """

    # ========================================================
    # MÉTODO: __init__ (Constructor)
    # ========================================================
    def __init__(self, verbose: bool = True):
        """
        Inicializa el cargador universal

        Args:
            verbose: Si True, muestra mensajes detallados del proceso
        """
        self.verbose = verbose  # Controla verbosidad
        self._cache = {}  # Diccionario para cachear DataFrames

    # ========================================================
    # MÉTODO PRIVADO: _log
    # ========================================================
    def _log(self, message: str, level=logging.INFO):
        """
        Registra mensaje en el logger si verbose está activo

        Args:
            message: Mensaje a mostrar
            level: Nivel de logging (INFO, WARNING, ERROR)
        """
        if self.verbose:
            logger.log(level, message)

    # ========================================================
    # MÉTODOS DE DETECCIÓN
    # ========================================================

    def _detect_encoding(self, filepath: Path, sample_size: int = 100000) -> tuple:
        """
        Detecta el encoding del archivo usando chardet

        ESTRATEGIA:
            1. Lee los primeros N bytes del archivo
            2. Usa chardet para detectar el encoding
            3. Retorna encoding y nivel de confianza

        Args:
            filepath: Ruta del archivo a analizar
            sample_size: Número de bytes a leer para la muestra

        Returns:
            tuple: (encoding, confianza)
                  Ejemplo: ('utf-8', 0.99)
        """
        try:
            # Abrir archivo en modo binario
            with open(filepath, 'rb') as file:
                # Leer muestra de bytes
                raw_data = file.read(sample_size)

                # Detectar encoding con chardet
                result = chardet.detect(raw_data)
                # result = {'encoding': 'utf-8', 'confidence': 0.99, ...}

                return result['encoding'], result['confidence']

        except Exception:
            # Si falla la detección, usar UTF-8 por defecto
            self._log("⚠️ Fallback: Usando utf-8 por defecto.", logging.WARNING)
            return 'utf-8', 0.5

    def _detect_delimiter(self, filepath: Path) -> str:
        """
        Detecta el delimitador del archivo CSV

        ESTRATEGIA:
            1. Lee la primera línea del archivo
            2. Cuenta ocurrencias de delimitadores comunes
            3. Retorna el más frecuente

        DELIMITADORES COMUNES:
            - ',' (comma) - Estándar internacional
            - ';' (semicolon) - Común en Europa/Latinoamérica
            - '\t' (tab) - TSV (Tab-Separated Values)
            - '|' (pipe) - Usado en bases de datos

        Args:
            filepath: Ruta del archivo CSV

        Returns:
            str: Delimitador detectado (',', ';', '\t', '|')
        """
        # Abrir archivo con encoding tolerante a errores
        with open(filepath, 'r', encoding='latin-1', errors='ignore') as file:
            first_line = file.readline()  # Leer primera línea

        # Contar ocurrencias de cada delimitador
        delimiters = {
            ',': first_line.count(','),  # Comas
            ';': first_line.count(';'),  # Punto y coma
            '\t': first_line.count('\t'),  # Tabulaciones
            '|': first_line.count('|')  # Pipes
        }

        # Retornar el delimitador con más ocurrencias
        return max(delimiters, key=delimiters.get)
        # max(..., key=...) encuentra la clave con el valor máximo

    def _check_corruption(self, df: pd.DataFrame) -> bool:
        """
        Verifica si hay caracteres corruptos en el DataFrame

        PATRONES DE CORRUPCIÓN COMUNES:
            Cuando un archivo UTF-8 se lee como Latin-1:
            - 'ñ' se corrompe a: 'Ã±'
            - 'á' se corrompe a: 'Ã¡'
            - 'é' se corrompe a: 'Ã©'
            - '£' se corrompe a: 'Â£'

        Args:
            df: DataFrame a verificar

        Returns:
            bool: True si se detecta corrupción, False si está limpio
        """
        # Patrones que indican corrupción de encoding
        corruption_patterns = ['Ã', 'Â£', 'Ã±', 'Ã¡', 'Ã©', 'Â']

        # Revisar solo columnas de texto (object dtype)
        for col in df.select_dtypes(include=['object']).columns:
            # Tomar muestra de las primeras 100 filas
            sample = df[col].astype(str).head(100).str.cat(sep=' ')
            # .str.cat(sep=' ') concatena todas las filas con espacio

            # Verificar si algún patrón de corrupción está presente
            if any(pattern in sample for pattern in corruption_patterns):
                return True  # Corrupción detectada

        return False  # No hay corrupción

    # ========================================================
    # MÉTODOS DE CARGA POR FORMATO
    # ========================================================

    def _load_csv(self, filepath: Path, **kwargs) -> pd.DataFrame:
        """
        Carga archivos CSV con detección automática

        PROCESO:
            1. Detectar delimitador si no se especificó
            2. Detectar encoding si no se especificó
            3. Intentar cargar con configuración detectada
            4. Si falla, usar fallback robusto
            5. Validar corrupción de caracteres

        Args:
            filepath: Ruta del archivo CSV
            **kwargs: Argumentos adicionales para pd.read_csv()

        Returns:
            pd.DataFrame: Datos cargados
        """
        # ----------------------------------------------------
        # 1. Detectar separador si no se especificó
        # ----------------------------------------------------
        if 'sep' not in kwargs and 'delimiter' not in kwargs:
            kwargs['sep'] = self._detect_delimiter(filepath)
            self._log(f"📊 Separador detectado: '{kwargs['sep']}'")

        # ----------------------------------------------------
        # 2. Detectar encoding si no se especificó
        # ----------------------------------------------------
        if 'encoding' not in kwargs:
            encoding, confidence = self._detect_encoding(filepath)
            kwargs['encoding'] = encoding
            self._log(f"🔤 Encoding detectado: {encoding} ({confidence:.1%} confianza)")

        # ----------------------------------------------------
        # 3. Intentar cargar con configuración detectada
        # ----------------------------------------------------
        try:
            df = pd.read_csv(filepath, **kwargs)
            self._log(f"✅ CSV cargado: {df.shape[0]:,} filas × {df.shape[1]} columnas")

        # ----------------------------------------------------
        # 4. Manejo de errores comunes
        # ----------------------------------------------------
        except UnicodeDecodeError:
            # Error de encoding: intentar con Latin-1
            self._log("⚠️ Error de encoding, intentando con latin-1")
            kwargs['encoding'] = 'latin-1'
            df = pd.read_csv(filepath, **kwargs)

        except Exception:
            # Cualquier otro error: usar método de respaldo
            df = self._fallback_csv_load(filepath)

        # ----------------------------------------------------
        # 5. Validar integridad de los datos
        # ----------------------------------------------------
        if self._check_corruption(df):
            self._log("⚠️ Posible corrupción de caracteres detectada", logging.WARNING)

        return df

    def _load_excel(self, filepath: Path, **kwargs) -> pd.DataFrame:
        """
        Carga archivos Excel (.xlsx, .xls)

        Args:
            filepath: Ruta del archivo Excel
            **kwargs: Argumentos para pd.read_excel()
                     (sheet_name, usecols, etc.)

        Returns:
            pd.DataFrame: Datos cargados
        """
        try:
            df = pd.read_excel(filepath, **kwargs)
            self._log(f"✅ Excel cargado: {df.shape[0]:,} filas × {df.shape[1]} columnas")
            return df
        except Exception as e:
            self._log(f"❌ Error cargando Excel: {e}", logging.ERROR)
            raise

    def _load_json(self, filepath: Path, **kwargs) -> pd.DataFrame:
        """
        Carga archivos JSON con detección de orientación

        ORIENTACIONES SOPORTADAS:
            - 'records': [{col1: val, col2: val}, ...]
            - 'index': {index: {col: val, ...}, ...}
            - 'columns': {col: {index: val, ...}, ...}
            - 'values': [[val1, val2, ...], ...]

        Args:
            filepath: Ruta del archivo JSON
            **kwargs: Argumentos para pd.read_json()

        Returns:
            pd.DataFrame: Datos cargados
        """
        try:
            # Intentar con configuración proporcionada
            df = pd.read_json(filepath, **kwargs)
            self._log(f"✅ JSON cargado: {df.shape[0]:,} filas × {df.shape[1]} columnas")
            return df

        except Exception as e:
            # Si falla, probar diferentes orientaciones
            self._log("⚠️ Intentando con orientaciones diferentes para JSON")

            for orient in ['records', 'index', 'columns', 'values']:
                try:
                    df = pd.read_json(filepath, orient=orient)
                    self._log(f"✅ JSON cargado con orient='{orient}'")
                    return df
                except:
                    continue  # Probar siguiente orientación

            # Si ninguna funcionó, lanzar el error original
            self._log(f"❌ Falló la carga de JSON: {e}", logging.ERROR)
            raise

    def _load_parquet(self, filepath: Path, **kwargs) -> pd.DataFrame:
        """
        Carga archivos Parquet (formato columnar eficiente)

        VENTAJAS DE PARQUET:
            - Compresión eficiente (archivos más pequeños)
            - Lectura rápida (formato columnar)
            - Preserva tipos de datos
            - Soporta esquemas complejos

        REQUISITO: pip install pyarrow

        Args:
            filepath: Ruta del archivo Parquet
            **kwargs: Argumentos para pd.read_parquet()

        Returns:
            pd.DataFrame: Datos cargados
        """
        try:
            df = pd.read_parquet(filepath, **kwargs)
            self._log(f"✅ Parquet cargado: {df.shape[0]:,} filas × {df.shape[1]} columnas")
            return df
        except ImportError:
            self._log("❌ Instala 'pyarrow' para leer Parquet", logging.ERROR)
            raise

    def _fallback_csv_load(self, filepath: Path) -> pd.DataFrame:
        """
        Método de respaldo para CSVs problemáticos

        CONFIGURACIÓN ROBUSTA:
            - encoding='latin-1': Encoding tolerante
            - sep=None: Detección automática de separador
            - engine='python': Motor más flexible (no C)
            - on_bad_lines='skip': Ignora líneas malformadas
            - encoding_errors='ignore': Ignora errores de encoding

        Args:
            filepath: Ruta del archivo CSV problemático

        Returns:
            pd.DataFrame: Datos cargados (puede tener filas faltantes)
        """
        self._log("⚠️ Usando configuración robusta de fallback")

        return pd.read_csv(
            filepath,
            encoding='latin-1',  # Encoding tolerante
            sep=None,  # Auto-detectar separador
            engine='python',  # Motor flexible
            on_bad_lines='skip',  # Omitir líneas con errores
            encoding_errors='ignore'  # Ignorar errores de encoding
        )

    # ========================================================
    # MÉTODO PRINCIPAL: load
    # ========================================================

    def load(self,
             filepath: Union[str, Path],
             force_reload: bool = False,
             **kwargs) -> pd.DataFrame:
        """
        Método principal - carga cualquier archivo automáticamente

        FLUJO DE CARGA:
            1. Verificar caché (si force_reload=False)
            2. Detectar tipo de archivo por extensión
            3. Llamar al método de carga apropiado
            4. Guardar en caché
            5. Agregar metadata al DataFrame
            6. Retornar DataFrame

        Args:
            filepath: Ruta del archivo (str o Path)
            force_reload: Si True, ignora caché y recarga
            **kwargs: Argumentos específicos del formato

        Returns:
            pd.DataFrame: Datos cargados con metadata

        Raises:
            ValueError: Si el formato no es soportado

        Ejemplo:
            >>> loader = UniversalDataLoader()
            >>> df = loader.load('data.csv')
            >>> df = loader.load('data.xlsx', sheet_name='Hoja1')
            >>> df = loader.load('data.json', orient='records')
        """
        # ----------------------------------------------------
        # 1. Convertir a Path para operaciones modernas
        # ----------------------------------------------------
        filepath = Path(filepath)

        # ----------------------------------------------------
        # 2. Verificar caché
        # ----------------------------------------------------
        cache_key = str(filepath.absolute())
        # .absolute() da la ruta absoluta completa

        if not force_reload and cache_key in self._cache:
            self._log("📦 Cargando desde caché")
            return self._cache[cache_key]

        # ----------------------------------------------------
        # 3. Detectar tipo de archivo y cargar
        # ----------------------------------------------------
        file_extension = filepath.suffix.lower()
        # .suffix obtiene la extensión: 'archivo.csv' → '.csv'
        # .lower() normaliza a minúsculas

        # Delegar a método específico según extensión
        if file_extension in ['.csv', '.txt', '.tsv']:
            df = self._load_csv(filepath, **kwargs)

        elif file_extension in ['.xlsx', '.xls']:
            df = self._load_excel(filepath, **kwargs)

        elif file_extension == '.json':
            df = self._load_json(filepath, **kwargs)

        elif file_extension == '.parquet':
            df = self._load_parquet(filepath, **kwargs)

        else:
            # Formato no reconocido
            raise ValueError(f"Formato no soportado: {file_extension}")

        # ----------------------------------------------------
        # 4. Guardar en caché
        # ----------------------------------------------------
        self._cache[cache_key] = df

        # ----------------------------------------------------
        # 5. Agregar metadata al DataFrame
        # ----------------------------------------------------
        df.attrs['source_file'] = str(filepath)
        # .attrs es un diccionario de metadata del DataFrame
        df.attrs['load_timestamp'] = pd.Timestamp.now()

        return df

    # ========================================================
    # MÉTODO: save_data
    # ✅ INTEGRADO CON config.py
    # ========================================================

    def save_data(self,
                  df: pd.DataFrame,
                  filename: str,
                  location: str = 'processed',
                  format: str = 'auto',
                  index: bool = False) -> Path:
        """
        Guarda DataFrame usando rutas de config.py

        UBICACIONES VÁLIDAS:
            - 'raw': data/raw/ (RAW_DATA_DIRECTORY)
            - 'processed': data/processed/ (PROCESSED_DATA_DIRECTORY)

        FORMATOS SOPORTADOS:
            - 'csv': CSV con UTF-8
            - 'excel': Excel (.xlsx)
            - 'parquet': Parquet (requiere pyarrow)
            - 'auto': Detectar por extensión

        Args:
            df: DataFrame a guardar
            filename: Nombre del archivo (con extensión)
            location: 'raw' o 'processed'
            format: Formato de guardado
            index: Incluir índice del DataFrame

        Returns:
            Path: Ruta donde se guardó el archivo

        Ejemplo:
            >>> loader = UniversalDataLoader()
            >>> loader.save_data(df, 'clean.csv', location='processed')
            >>> loader.save_data(df, 'backup.parquet', location='raw')
        """
        # ----------------------------------------------------
        # 1. Determinar directorio usando config.py
        # ✅ CAMBIO v2.0.0: Usar variables importadas
        # ----------------------------------------------------
        if location.lower() == 'raw':
            target_dir = RAW_DATA_DIRECTORY
        elif location.lower() == 'processed':
            target_dir = PROCESSED_DATA_DIRECTORY
        else:
            raise ValueError("location debe ser 'raw' o 'processed'")

        # Construir ruta completa
        output_path = target_dir / filename

        # ----------------------------------------------------
        # 2. Detectar formato si es 'auto'
        # ----------------------------------------------------
        if format == 'auto':
            # Usar la extensión del archivo
            format = output_path.suffix[1:] if output_path.suffix else 'csv'
            # .suffix[1:] elimina el punto: '.csv' → 'csv'

        # ----------------------------------------------------
        # 3. Mensaje informativo
        # ----------------------------------------------------
        self._log(f"💾 Guardando en {target_dir.name}/{filename} como {format.upper()}")

        # ----------------------------------------------------
        # 4. Guardar según formato
        # ----------------------------------------------------
        if format == 'csv':
            df.to_csv(output_path, encoding='utf-8', index=index)

        elif format == 'excel':
            df.to_excel(output_path, index=index)

        elif format == 'parquet':
            df.to_parquet(output_path, index=index)

        else:
            raise ValueError(f"Formato no soportado: {format}")

        self._log(f"✅ Guardado exitoso: {output_path}")
        return output_path


# ============================================================
# FUNCIONES DE CONVENIENCIA (Shortcuts)
# ============================================================

def load_raw(filename: str, **kwargs) -> pd.DataFrame:
    """
    Carga archivo desde data/raw/ con búsqueda recursiva

    BÚSQUEDA RECURSIVA:
        Busca el archivo en data/raw/ y todas sus subcarpetas.
        Ejemplo:
            data/raw/
            ├── archivo.csv          ← Encuentra esto
            ├── carpeta1/
            │   └── archivo.csv      ← O esto
            └── carpeta2/
                └── sub/
                    └── archivo.csv  ← O esto

    Args:
        filename: Nombre exacto del archivo
        **kwargs: Argumentos para el loader

    Returns:
        pd.DataFrame: Datos cargados

    Raises:
        FileNotFoundError: Si el archivo no existe

    Ejemplo:
        >>> from src.data.data_loader import load_raw
        >>> df = load_raw('investments.csv')
        >>> df = load_raw('data.xlsx', sheet_name='Sheet1')
    """
    # ----------------------------------------------------
    # 1. Crear instancia del loader
    # ----------------------------------------------------
    loader = UniversalDataLoader()

    # ----------------------------------------------------
    # 2. Buscar archivo recursivamente
    # ✅ USA RAW_DATA_DIRECTORY de config.py
    # ----------------------------------------------------
    search_results = list(RAW_DATA_DIRECTORY.rglob(filename))
    # .rglob() busca recursivamente (r = recursive)
    # Ejemplo: RAW_DATA_DIRECTORY.rglob('*.csv') busca todos los CSVs

    # ----------------------------------------------------
    # 3. Validar resultados
    # ----------------------------------------------------
    if not search_results:
        # Archivo no encontrado
        raise FileNotFoundError(
            f"❌ Archivo '{filename}' no encontrado en {RAW_DATA_DIRECTORY}\n"
            f"   Buscar en subdirectorios también.\n"
            f"   Verifica el nombre exacto del archivo."
        )

    # ----------------------------------------------------
    # 4. Usar primer resultado encontrado
    # ----------------------------------------------------
    filepath = search_results[0]

    # ----------------------------------------------------
    # 5. Advertir si hay múltiples coincidencias
    # ----------------------------------------------------
    if len(search_results) > 1:
        logging.warning(
            f"⚠️ Múltiples archivos '{filename}' encontrados. "
            f"Usando: {filepath.relative_to(RAW_DATA_DIRECTORY)}"
        )
        # .relative_to() muestra ruta relativa: data/raw/carpeta/archivo.csv → carpeta/archivo.csv

    # ----------------------------------------------------
    # 6. Cargar y retornar
    # ----------------------------------------------------
    logging.info(f"📁 Cargando: {filepath.relative_to(RAW_DATA_DIRECTORY)}")
    return loader.load(filepath, **kwargs)


def save_processed(df: pd.DataFrame, filename: str, **kwargs) -> Path:
    """
    Guarda DataFrame en data/processed/

    Args:
        df: DataFrame a guardar
        filename: Nombre del archivo
        **kwargs: Argumentos para save_data()

    Returns:
        Path: Ruta donde se guardó

    Ejemplo:
        >>> from src.data.data_loader import save_processed
        >>> save_processed(df_clean, 'clean_data.csv')
        >>> save_processed(df_clean, 'backup.parquet')
    """
    loader = UniversalDataLoader()
    return loader.save_data(df, filename, location='processed', **kwargs)


def load_and_clean(filepath: Union[str, Path]) -> pd.DataFrame:
    """
    Carga y limpia automáticamente

    LIMPIEZA AUTOMÁTICA:
        1. Elimina filas completamente vacías
        2. Elimina columnas completamente vacías
        3. Elimina duplicados exactos

    Args:
        filepath: Ruta del archivo

    Returns:
        pd.DataFrame: Datos cargados y limpiados

    Ejemplo:
        >>> from src.data.data_loader import load_and_clean
        >>> df = load_and_clean('messy_data.csv')
    """
    loader = UniversalDataLoader(verbose=True)
    df = loader.load(filepath)

    # Guardar shape inicial
    initial_shape = df.shape

    # Limpieza automática básica
    df = df.dropna(how='all')  # Eliminar filas vacías
    df = df.dropna(axis=1, how='all')  # Eliminar columnas vacías
    df = df.drop_duplicates()  # Eliminar duplicados

    final_shape = df.shape

    # Mostrar resumen de limpieza
    if initial_shape != final_shape:
        print(f"🧹 Limpieza: {initial_shape} → {final_shape}")
        rows_removed = initial_shape[0] - final_shape[0]
        cols_removed = initial_shape[1] - final_shape[1]
        print(f"   Filas eliminadas: {rows_removed}")
        print(f"   Columnas eliminadas: {cols_removed}")

    return df


# ============================================================
# EXPORTACIONES (para imports limpios)
# ============================================================
__all__ = [
    'UniversalDataLoader',  # Clase principal
    'load_raw',  # Cargar desde data/raw/
    'save_processed',  # Guardar en data/processed/
    'load_and_clean'  # Cargar + limpiar
]