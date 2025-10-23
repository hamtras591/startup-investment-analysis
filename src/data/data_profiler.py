"""
Data Profiler Module
====================
Generador automático de informes estadísticos para cualquier dataset.

PROPÓSITO:
    Proporcionar una visión completa y estandarizada de cualquier DataFrame,
    detectando problemas comunes y facilitando el análisis exploratorio inicial.

DEPENDENCIAS:
    - data_loader.py: Para cargar datasets automáticamente
    - config.py: Para rutas estandarizadas

FUNCIONALIDADES:
    1. Carga automática de datasets (usando data_loader)
    2. Dimensiones y uso de memoria
    3. Tipos de datos y valores nulos
    4. Detección de duplicados
    5. Estadísticas descriptivas numéricas
    6. Correlaciones entre variables
    7. Frecuencias de variables categóricas
    8. Detección de columnas constantes
    9. Detección de alta cardinalidad
    10. Guardado opcional de reportes

UBICACIÓN EN EL PROYECTO:
    src/data/data_profiler.py

AUTOR: Anderson Sebastian Rubio Pacheco
VERSIÓN: 2.1.0
FECHA: Octubre 2025
CAMBIOS v2.1.0:
    - ✅ Integración CON data_loader.py
    - ✅ Función profile_from_file() para cargar + analizar en 1 paso
    - Mejoras en formato de salida
    - Detección automática de problemas
    - Opción de guardar reportes
"""

# ============================================================
# SECCIÓN 1: IMPORTACIONES
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime

# ============================================================
# Importar data_loader (DEPENDENCIA PRINCIPAL)
# ============================================================
try:
    from src.data.data_loader import load_raw, UniversalDataLoader
    LOADER_AVAILABLE = True
except ImportError:
    print("⚠️  Advertencia: No se pudo importar data_loader.py")
    print("   El módulo funcionará solo con DataFrames ya cargados.")
    LOADER_AVAILABLE = False

# ============================================================
# Importar configuración para guardar reportes
# ============================================================
try:
    from src.data.config import REPORTS_DIRECTORY
    CONFIG_AVAILABLE = True
except ImportError:
    REPORTS_DIRECTORY = Path('./reports/')
    CONFIG_AVAILABLE = False


# ============================================================
# FUNCIÓN PRINCIPAL: generate_profile
# ============================================================

def generate_profile(
    df: pd.DataFrame,
    dataset_name: str = "Dataset",
    show_correlations: bool = True,
    show_categories: bool = True,
    save_report: bool = False,
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Genera informe estadístico completo para cualquier DataFrame

    SECCIONES DEL INFORME:
        1. Dimensiones y memoria
        2. Tipos de datos y valores nulos
        3. Valores duplicados
        4. Estadísticas descriptivas numéricas
        5. Correlaciones (opcional)
        6. Frecuencias categóricas (opcional)
        7. Detección de problemas

    Args:
        df: DataFrame a analizar
        dataset_name: Nombre descriptivo del dataset
        show_correlations: Mostrar matriz de correlación
        show_categories: Mostrar frecuencias de categóricas
        save_report: Guardar reporte en archivo
        output_file: Nombre del archivo (default: auto-generado)

    Returns:
        dict: Resumen con métricas clave

    Ejemplo:
        >>> from src.data.data_profiler import generate_profile
        >>> generate_profile(df, dataset_name="Startups")
        >>> generate_profile(df, save_report=True, output_file='analisis.txt')
    """

    # ========================================================
    # VALIDACIÓN INICIAL
    # ========================================================
    if df.empty:
        print(f"❌ El {dataset_name} está vacío. No se puede generar el perfil.")
        return {'error': 'DataFrame vacío'}

    # Variable para capturar el reporte si se va a guardar
    report_lines = []

    def print_and_save(text: str):
        """Imprime y guarda en buffer si save_report=True"""
        print(text)
        if save_report:
            report_lines.append(text)

    # ========================================================
    # ENCABEZADO
    # ========================================================
    print_and_save("\n" + "="*80)
    print_and_save(f"📊 INFORME DE PERFILADO ESTADÍSTICO: {dataset_name.upper()}")
    print_and_save("="*80)
    print_and_save(f"📅 Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ========================================================
    # 1. DIMENSIONES Y MEMORIA
    # ========================================================
    print_and_save("\n" + "─"*80)
    print_and_save("📏 1. DIMENSIONES DEL DATASET")
    print_and_save("─"*80)

    n_rows = df.shape[0]
    n_cols = df.shape[1]
    mem_usage_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)

    print_and_save(f"   Filas (observaciones):  {n_rows:,}")
    print_and_save(f"   Columnas (variables):   {n_cols:,}")
    print_and_save(f"   Uso de memoria:         {mem_usage_mb:.2f} MB")
    print_and_save(f"   Celdas totales:         {n_rows * n_cols:,}")

    # ========================================================
    # 2. TIPOS DE DATOS Y VALORES NULOS
    # ========================================================
    print_and_save("\n" + "─"*80)
    print_and_save("🏷️  2. TIPOS DE DATOS Y VALORES NULOS")
    print_and_save("─"*80)

    # Resumen de tipos
    dtype_summary = df.dtypes.astype(str).value_counts()
    print_and_save("\n   Distribución de tipos:")
    for dtype, count in dtype_summary.items():
        print_and_save(f"      • {dtype}: {count} columnas")

    # Tabla detallada por columna
    null_counts = df.isnull().sum()
    null_percentages = (null_counts / len(df)) * 100

    summary_df = pd.DataFrame({
        'Tipo': df.dtypes.astype(str),
        'No Nulos': df.count(),
        'Nulos': null_counts,
        '% Nulos': null_percentages.round(2)
    })

    print_and_save("\n   Detalle por columna:")
    # Mostrar solo columnas con problemas + primeras 10
    problematic = summary_df[summary_df['Nulos'] > 0]
    if len(problematic) > 0:
        print_and_save(f"\n   ⚠️  Columnas con valores nulos ({len(problematic)}):")
        print_and_save(str(problematic.sort_values('% Nulos', ascending=False)))
    else:
        print_and_save("\n   ✅ No hay valores nulos en el dataset")

    # ========================================================
    # 3. VALORES DUPLICADOS
    # ========================================================
    print_and_save("\n" + "─"*80)
    print_and_save("👯 3. VALORES DUPLICADOS")
    print_and_save("─"*80)

    total_duplicates = df.duplicated().sum()
    duplicate_pct = (total_duplicates / len(df)) * 100

    print_and_save(f"   Filas duplicadas:       {total_duplicates:,} ({duplicate_pct:.2f}%)")

    if total_duplicates > 0:
        print_and_save(f"   ⚠️  Considerar eliminar duplicados con: df.drop_duplicates()")

    # ========================================================
    # 4. ESTADÍSTICAS DESCRIPTIVAS NUMÉRICAS
    # ========================================================
    print_and_save("\n" + "─"*80)
    print_and_save("🔢 4. ESTADÍSTICAS DESCRIPTIVAS (VARIABLES NUMÉRICAS)")
    print_and_save("─"*80)

    num_df = df.select_dtypes(include=[np.number])

    if not num_df.empty:
        print_and_save(f"\n   Variables numéricas encontradas: {len(num_df.columns)}")

        # Estadísticas descriptivas
        desc = num_df.describe().T
        desc['rango'] = desc['max'] - desc['min']
        desc['cv'] = (desc['std'] / desc['mean']) * 100  # Coeficiente de variación

        print_and_save("\n" + str(desc.round(2)))

        # Detectar columnas constantes (sin variación)
        constant_cols = num_df.columns[num_df.std() == 0].tolist()
        if constant_cols:
            print_and_save(f"\n   ⚠️  Columnas constantes (sin variación): {constant_cols}")
            print_and_save(f"       Considerar eliminarlas (no aportan información)")
    else:
        print_and_save("\n   ℹ️  No se encontraron columnas numéricas")

    # ========================================================
    # 5. CORRELACIONES BÁSICAS
    # ========================================================
    if show_correlations and not num_df.empty:
        print_and_save("\n" + "─"*80)
        print_and_save("🔗 5. CORRELACIONES ENTRE VARIABLES NUMÉRICAS")
        print_and_save("─"*80)

        corr_matrix = num_df.corr()

        # Extraer triángulo inferior (sin diagonal)
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        corr_lower = corr_matrix.mask(mask)

        # Top 10 correlaciones más fuertes (positivas y negativas)
        corr_pairs = corr_lower.stack().sort_values(key=abs, ascending=False)

        if len(corr_pairs) > 0:
            print_and_save("\n   Top 10 correlaciones más fuertes:")
            for idx, (pair, corr_value) in enumerate(corr_pairs.head(10).items(), 1):
                emoji = "🔴" if abs(corr_value) > 0.7 else "🟡" if abs(corr_value) > 0.4 else "🟢"
                print_and_save(f"      {emoji} {idx:2d}. {pair[0]:20s} ↔ {pair[1]:20s} : {corr_value:+.3f}")

            # Advertencias
            strong_corr = corr_pairs[abs(corr_pairs) > 0.9]
            if len(strong_corr) > 0:
                print_and_save(f"\n   ⚠️  {len(strong_corr)} pares con correlación muy alta (>0.9)")
                print_and_save(f"       Posible multicolinealidad - considerar eliminar variables redundantes")
        else:
            print_and_save("\n   ℹ️  No hay suficientes variables para calcular correlaciones")

    # ========================================================
    # 6. FRECUENCIAS DE VARIABLES CATEGÓRICAS
    # ========================================================
    if show_categories:
        print_and_save("\n" + "─"*80)
        print_and_save("🏷️  6. FRECUENCIAS DE VARIABLES CATEGÓRICAS")
        print_and_save("─"*80)

        cat_cols = df.select_dtypes(include=['object', 'category']).columns

        if len(cat_cols) > 0:
            print_and_save(f"\n   Variables categóricas encontradas: {len(cat_cols)}")

            for col in cat_cols[:10]:  # Limitar a 10 columnas
                n_unique = df[col].nunique()
                cardinality_pct = (n_unique / len(df)) * 100

                print_and_save(f"\n   📌 {col}")
                print_and_save(f"      Valores únicos: {n_unique:,} ({cardinality_pct:.1f}% del total)")

                # Advertencia para alta cardinalidad
                if n_unique > len(df) * 0.5:
                    print_and_save(f"      ⚠️  Alta cardinalidad (>50% único) - posible ID o texto libre")

                # Mostrar top 5
                print_and_save(f"      Top 5 más frecuentes:")
                value_counts = df[col].value_counts(dropna=False).head(5)
                for val, count in value_counts.items():
                    pct = (count / len(df)) * 100
                    val_str = str(val) if pd.notna(val) else "NaN"
                    print_and_save(f"         • {val_str:30s}: {count:6,} ({pct:5.1f}%)")

            if len(cat_cols) > 10:
                print_and_save(f"\n   ℹ️  ... y {len(cat_cols) - 10} columnas categóricas más")
        else:
            print_and_save("\n   ℹ️  No se encontraron columnas categóricas")

    # ========================================================
    # 7. DETECCIÓN DE PROBLEMAS POTENCIALES
    # ========================================================
    print_and_save("\n" + "─"*80)
    print_and_save("🚨 7. DETECCIÓN DE PROBLEMAS POTENCIALES")
    print_and_save("─"*80)

    problems = []

    # Problema 1: Muchos valores nulos
    high_null_cols = summary_df[summary_df['% Nulos'] > 50].index.tolist()
    if high_null_cols:
        problems.append(f"❌ {len(high_null_cols)} columnas con >50% nulos: {high_null_cols}")

    # Problema 2: Duplicados significativos
    if duplicate_pct > 5:
        problems.append(f"❌ {duplicate_pct:.1f}% de filas duplicadas")

    # Problema 3: Columnas constantes
    if num_df is not None and not num_df.empty:
        constant_cols = num_df.columns[num_df.std() == 0].tolist()
        if constant_cols:
            problems.append(f"❌ Columnas sin variación: {constant_cols}")

    # Problema 4: Alta cardinalidad en categóricas
    if len(cat_cols) > 0:
        high_card = [col for col in cat_cols if df[col].nunique() > len(df) * 0.8]
        if high_card:
            problems.append(f"⚠️  Columnas con cardinalidad muy alta: {high_card}")

    # Problema 5: Uso excesivo de memoria
    if mem_usage_mb > 1000:
        problems.append(f"⚠️  Dataset grande ({mem_usage_mb:.0f} MB) - considerar optimización")

    if problems:
        print_and_save("\n   Problemas detectados:")
        for i, problem in enumerate(problems, 1):
            print_and_save(f"      {i}. {problem}")
    else:
        print_and_save("\n   ✅ No se detectaron problemas significativos")

    # ========================================================
    # RESUMEN FINAL
    # ========================================================
    print_and_save("\n" + "="*80)
    print_and_save("📋 RESUMEN EJECUTIVO")
    print_and_save("="*80)
    print_and_save(f"   Dataset:           {dataset_name}")
    print_and_save(f"   Tamaño:            {n_rows:,} filas × {n_cols:,} columnas")
    print_and_save(f"   Memoria:           {mem_usage_mb:.2f} MB")
    print_and_save(f"   Duplicados:        {total_duplicates:,} ({duplicate_pct:.1f}%)")
    print_and_save(f"   Columnas nulas:    {len(high_null_cols)}")
    print_and_save(f"   Problemas:         {len(problems)}")
    print_and_save("="*80 + "\n")

    # ========================================================
    # GUARDAR REPORTE (OPCIONAL)
    # ========================================================
    if save_report:
        # Generar nombre de archivo si no se proporcionó
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"data_profile_{dataset_name.lower().replace(' ', '_')}_{timestamp}.txt"

        # Determinar ruta completa
        if CONFIG_AVAILABLE:
            output_path = REPORTS_DIRECTORY / output_file
            REPORTS_DIRECTORY.mkdir(exist_ok=True)
        else:
            output_path = Path(output_file)

        # Guardar archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"💾 Reporte guardado en: {output_path}")

    # ========================================================
    # RETORNAR RESUMEN
    # ========================================================
    return {
        'n_rows': n_rows,
        'n_cols': n_cols,
        'memory_mb': mem_usage_mb,
        'duplicates': total_duplicates,
        'null_cols': len(high_null_cols),
        'problems': len(problems)
    }


# ============================================================
# FUNCIÓN NUEVA: profile_from_file
# ✅ USA data_loader.py PARA CARGAR Y ANALIZAR EN 1 PASO
# ============================================================

def profile_from_file(
    filename: str,
    dataset_name: Optional[str] = None,
    location: str = 'raw',
    show_correlations: bool = True,
    show_categories: bool = True,
    save_report: bool = False,
    **loader_kwargs
) -> Dict[str, Any]:
    """
    Carga un archivo Y genera perfil automáticamente

    VENTAJA:
        Combina load_raw() + generate_profile() en 1 función.
        Aprovecha todo el poder de data_loader.py (detección de encoding, etc.)

    Args:
        filename: Nombre del archivo (ej: 'startups.csv')
        dataset_name: Nombre descriptivo (si None, usa filename)
        location: 'raw' o 'processed'
        show_correlations: Mostrar correlaciones
        show_categories: Mostrar frecuencias
        save_report: Guardar reporte
        **loader_kwargs: Argumentos adicionales para load_raw()

    Returns:
        dict: Resumen con métricas clave

    Ejemplo:
        >>> from src.data.data_profiler import profile_from_file
        >>>
        >>> # Cargar + Analizar en 1 línea
        >>> profile_from_file('startups.csv', dataset_name='Startups 2025')
        >>>
        >>> # Con opciones de loader
        >>> profile_from_file('data.csv', sep=';', encoding='latin-1')
        >>>
        >>> # Guardar reporte
        >>> profile_from_file('data.csv', save_report=True)
    """

    # ========================================================
    # VALIDAR QUE data_loader ESTÁ DISPONIBLE
    # ========================================================
    if not LOADER_AVAILABLE:
        raise ImportError(
            "\n❌ data_loader.py no está disponible.\n"
            "   profile_from_file() requiere data_loader.py para funcionar.\n"
            "   Usa generate_profile(df) si ya tienes el DataFrame cargado."
        )

    # ========================================================
    # CARGAR ARCHIVO USANDO data_loader
    # ========================================================
    print(f"📂 Cargando archivo: {filename}")
    print(f"   (usando data_loader.py con detección automática de encoding)")

    if location == 'raw':
        # Usar load_raw() que busca recursivamente en data/raw/
        df = load_raw(filename, **loader_kwargs)
    else:
        # Para otros casos, usar UniversalDataLoader
        loader = UniversalDataLoader()
        from src.data.config import PROCESSED_DATA_DIRECTORY
        filepath = PROCESSED_DATA_DIRECTORY / filename
        df = loader.load(filepath, **loader_kwargs)

    print(f"✅ Archivo cargado: {len(df):,} filas × {df.shape[1]} columnas\n")

    # ========================================================
    # GENERAR PERFIL DEL DATAFRAME CARGADO
    # ========================================================

    # Si no se especificó nombre, usar el filename sin extensión
    if dataset_name is None:
        dataset_name = Path(filename).stem  # 'data.csv' → 'data'

    # Llamar a generate_profile con el DataFrame cargado
    return generate_profile(
        df,
        dataset_name=dataset_name,
        show_correlations=show_correlations,
        show_categories=show_categories,
        save_report=save_report
    )


# ============================================================
# FUNCIÓN DE CONVENIENCIA: quick_profile
# ============================================================

def quick_profile(df: pd.DataFrame, name: str = "Dataset") -> None:
    """
    Perfil rápido sin correlaciones ni categóricas (más rápido)

    Ejemplo:
        >>> from src.data.data_profiler import quick_profile
        >>> quick_profile(df, "Startups")
    """
    generate_profile(
        df,
        dataset_name=name,
        show_correlations=False,
        show_categories=False
    )


# ============================================================
# EXPORTACIONES
# ============================================================

__all__ = [
    'generate_profile',      # Analizar DataFrame ya cargado
    'profile_from_file',     # ✅ Cargar + Analizar (USA data_loader)
    'quick_profile'          # Versión rápida
]


# ============================================================
# PRUEBA (solo si se ejecuta directamente)
# ============================================================

if __name__ == '__main__':
    print("\n🧪 Modo de prueba de data_profiler.py\n")

    # Opción 1: Usar profile_from_file (RECOMENDADO)
    if LOADER_AVAILABLE:
        print("✅ data_loader disponible - probando profile_from_file():\n")
        try:
            # Intentar cargar y analizar un archivo real
            profile_from_file(
                'big_startup_secsees_dataset.csv',
                dataset_name='Startups Demo',
                save_report=True
            )
        except FileNotFoundError:
            print("⚠️  Archivo de prueba no encontrado.")
            print("   Generando dataset sintético...\n")

    # Opción 2: Dataset sintético
    print("🧪 Generando dataset sintético para demostración...\n")

    np.random.seed(42)
    test_data = {
        'edad': np.random.randint(18, 65, 100),
        'salario': np.random.randint(30000, 150000, 100),
        'ciudad': np.random.choice(['Madrid', 'Barcelona', 'Valencia', 'Sevilla'], 100),
        'departamento': np.random.choice(['Ventas', 'IT', 'RRHH', 'Marketing'], 100),
        'años_empresa': np.random.randint(0, 20, 100),
        'satisfaccion': np.random.choice([1, 2, 3, 4, 5], 100),
        'id_empleado': range(1, 101)
    }

    df_test = pd.DataFrame(test_data)
    df_test.loc[0:5, 'salario'] = np.nan
    df_test = pd.concat([df_test, df_test.iloc[0:3]], ignore_index=True)

    generate_profile(df_test, dataset_name="Empleados (Demo)", save_report=False)