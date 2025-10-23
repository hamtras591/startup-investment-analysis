# 🚀 Análisis de Ecosistema de Startups Tecnológicas - Guía Completa

**Proyecto:** Startup Investment Analysis  
**Autor:** Anderson Sebastian Rubio Pacheco  
**Fecha:** Octubre 2025  
**Nivel:** Intermedio-Avanzado  
**Duración estimada:** 20-30 horas  

---

## 📋 Tabla de Contenidos

1. [Descripción del Proyecto](#1-descripción-del-proyecto)
2. [Objetivos de Aprendizaje](#2-objetivos-de-aprendizaje)
3. [Stack Tecnológico](#3-stack-tecnológico)
4. [Estructura del Proyecto](#4-estructura-del-proyecto)
5. [Fase 0: Setup Inicial](#5-fase-0-setup-inicial)
6. [Fase 1: Adquisición de Datos](#6-fase-1-adquisición-de-datos)
7. [Fase 2: Limpieza de Datos](#7-fase-2-limpieza-de-datos)
8. [Fase 3: Feature Engineering](#8-fase-3-feature-engineering)
9. [Fase 4: Análisis Exploratorio](#9-fase-4-análisis-exploratorio-eda)
10. [Fase 5: Integración con JOINs](#10-fase-5-integración-con-joins)
11. [Fase 6: Visualización](#11-fase-6-visualización-y-dashboards)
12. [Fase 7: Insights](#12-fase-7-insights-y-recomendaciones)
13. [Entregables Finales](#13-entregables-finales)
14. [Criterios de Evaluación](#14-criterios-de-evaluación)
15. [Recursos y Troubleshooting](#15-recursos-y-troubleshooting)

---

## 1. Descripción del Proyecto

### 🎯 Contexto

Eres el **Data Scientist Lead** de **TechVentures Capital**, un fondo de inversión que busca identificar oportunidades en el ecosistema global de startups tecnológicas. Tu misión es analizar datos de múltiples fuentes para responder preguntas críticas de inversión.

### 💼 Stakeholders

- **CEO del Fondo:** Decisiones estratégicas de alto nivel
- **Partners de Inversión:** Identificación de oportunidades específicas
- **Equipo Legal:** Análisis de riesgos por geografía
- **CFO:** Asignación de presupuesto por sector

### 🎪 Preguntas de Negocio a Responder

1. ¿Cuáles son los sectores con mayor tasa de éxito vs fracaso?
2. ¿Qué países tienen el ecosistema más robusto de startups?
3. ¿Existe correlación entre el monto de inversión y el éxito?
4. ¿Cuál es el perfil de la startup "ideal" para invertir?
5. ¿Hay estacionalidad en las rondas de inversión?

---

## 2. Objetivos de Aprendizaje

### 🎓 Habilidades Técnicas

✅ Integración de múltiples fuentes de datos (APIs + Kaggle)  
✅ Manejo de diferentes formatos (CSV, JSON, Excel)  
✅ Limpieza y preparación de datos reales  
✅ Feature Engineering para análisis de inversión  
✅ Diferentes tipos de JOINs en Pandas  
✅ Análisis exploratorio de datos (EDA)  
✅ Creación de dashboards con GridSpec  
✅ Visualización profesional con Matplotlib  

### 💡 Habilidades de Negocio

✅ Entender métricas de inversionistas  
✅ Evaluar riesgo en startups  
✅ Análisis de mercados emergentes  
✅ Identificar factores de éxito  
✅ Comunicar insights a stakeholders  

---

## 3. Stack Tecnológico

### 📦 Dependencias (requirements.txt)
```txt
numpy==2.3.4
pandas==2.3.3
matplotlib==3.10.7
requests==2.32.5
jupyter==1.1.1
kaggle==1.7.4.5
chardet==5.2.0
```

### 🌐 APIs Utilizadas

| API | Endpoint | Propósito | Auth |
|-----|----------|-----------|------|
| CoinGecko | `api.coingecko.com/api/v3/coins/markets` | Precios crypto | No |
| REST Countries | `restcountries.com/v3.1/all` | Datos geográficos | No |
| World Bank | `api.worldbank.org/v2/...` | PIB por país | No |
| Kaggle | - | Datasets | Token |

---

## 4. Estructura del Proyecto
```
startup-investment-analysis/
├── .gitignore
├── README.md
├── requirements.txt
├── LICENSE
│
├── notebooks/
│   ├── 01_data_acquisition.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_exploratory_analysis.ipynb
│   ├── 04_feature_engineering.ipynb
│   └── 05_final_dashboard.ipynb
│
├── src/
│   ├── data/
│   │   ├── config.py
│   │   ├── data_loader.py
│   │   └── kaggle_downloader.py
│   ├── preprocessing/
│   ├── features/
│   ├── analysis/
│   └── visualization/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── reports/
│   └── figures/
│
└── tests/
```

---

## 5. Fase 0: Setup Inicial

### ⏱️ Duración: 30 minutos

### 📝 Pasos

#### 1. Crear Repositorio GitHub
```bash
# En GitHub.com:
# - Nuevo repositorio: startup-investment-analysis
# - Público, sin README inicial
```

#### 2. Configurar Localmente
```bash
git clone git@github.com:TU_USUARIO/startup-investment-analysis.git
cd startup-investment-analysis

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

#### 3. Crear Estructura
```bash
mkdir -p notebooks data/{raw,processed,external}
mkdir -p src/{data,preprocessing,features,analysis,visualization}
mkdir -p reports/figures tests

touch src/__init__.py
touch src/{data,preprocessing,features,analysis,visualization}/__init__.py
```

#### 4. Configurar Kaggle
```bash
# 1. Ir a https://www.kaggle.com/settings
# 2. "Create New API Token"
# 3. Guardar kaggle.json en ~/.kaggle/

mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

#### 5. Primer Commit
```bash
git add .
git commit -m "🎉 Initial commit"
git push origin main
```

### ✅ Checklist

- [ ] Repo en GitHub
- [ ] Estructura de carpetas
- [ ] requirements.txt instalado
- [ ] Kaggle configurado
- [ ] Primer commit

---

## 6. Fase 1: Adquisición de Datos

### ⏱️ Duración: 2-3 horas

### 🎯 Objetivo

Obtener datos de Kaggle + 3 APIs.

### 📊 Dataset Principal

**Kaggle:** `yanmaksi/big-startup-secsees-fail-dataset-from-crunchbase`

### 📝 Notebook 01: `notebooks/01_data_acquisition.ipynb`

**Setup:**
```python
import sys
sys.path.append('../')

import pandas as pd
import requests
from src.data.kaggle_downloader import download_from_kaggle
from src.data.data_loader import load_raw
from src.data.config import EXTERNAL_DATA_DIR

print("✅ Setup completo")
```

**Descargar de Kaggle:**
```python
dataset_id = 'yanmaksi/big-startup-secsees-fail-dataset-from-crunchbase'
download_from_kaggle(dataset_id)

df_startups = load_raw('big_startup_secsees_dataset.csv')
print(f"✅ {len(df_startups):,} startups cargadas")
```

**API 1: CoinGecko**
```python
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {'vs_currency': 'usd', 'per_page': 100}

response = requests.get(url, params=params)
df_crypto = pd.DataFrame(response.json())

df_crypto.to_csv(EXTERNAL_DATA_DIR / 'crypto_prices.csv', index=False)
print(f"✅ {len(df_crypto)} cryptos guardadas")
```

**API 2: REST Countries**
```python
url = "https://restcountries.com/v3.1/all"
response = requests.get(url)
data = response.json()

countries = [{
    'country_code': c.get('cca3'),
    'country_name': c.get('name', {}).get('common'),
    'region': c.get('region'),
    'population': c.get('population')
} for c in data]

df_countries = pd.DataFrame(countries)
df_countries.to_csv(EXTERNAL_DATA_DIR / 'countries.csv', index=False)
print(f"✅ {len(df_countries)} países guardados")
```

**API 3: World Bank (PIB)**
```python
url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD"
params = {'format': 'json', 'date': '2020:2023', 'per_page': 500}

response = requests.get(url, params=params)
data = response.json()[1]  # Segundo elemento

gdp_data = [{
    'country_code': r['countryiso3code'],
    'year': r['date'],
    'gdp_usd': r['value']
} for r in data if r.get('value')]

df_gdp = pd.DataFrame(gdp_data)
df_gdp = df_gdp.sort_values('year', ascending=False).groupby('country_code').first()

df_gdp.to_csv(EXTERNAL_DATA_DIR / 'gdp.csv')
print(f"✅ PIB de {len(df_gdp)} países guardado")
```

### ✅ Checklist

- [ ] Dataset Kaggle descargado
- [ ] 3 APIs consultadas
- [ ] Datos guardados
- [ ] Commit: `feat: Add data acquisition`

---

## 7. Fase 2: Limpieza de Datos

### ⏱️ Duración: 3-4 horas

### 🎯 Objetivo

Limpiar datos, documentar decisiones.

### 📝 Notebook 02: `notebooks/02_data_cleaning.ipynb`

**Cargar datos:**
```python
from src.data.data_loader import load_raw
from src.data.config import EXTERNAL_DATA_DIR, PROCESSED_DATA_DIR

df = load_raw('big_startup_secsees_dataset.csv')
print(f"Original: {len(df):,} filas")
```

**Análisis de calidad:**
```python
print("Valores nulos:")
print(df.isnull().sum())

print(f"\nDuplicados: {df.duplicated().sum()}")

print("\nEstadísticas:")
df.describe()
```

**Decisiones documentadas:**
```python
decisiones = {
    'Duplicados': 'ELIMINAR',
    'country_code nulos': 'ELIMINAR - necesario para joins',
    'funding_total_usd nulos': 'MANTENER',
    'founded_at nulos': 'MANTENER'
}

for k, v in decisiones.items():
    print(f"{k}: {v}")
```

**Limpieza:**
```python
df_clean = df.copy()

# 1. Duplicados
df_clean = df_clean.drop_duplicates()
print(f"Sin duplicados: {len(df_clean):,}")

# 2. Sin country_code
df_clean = df_clean.dropna(subset=['country_code'])
print(f"Con país: {len(df_clean):,}")

# 3. Limpiar funding
df_clean['funding_total_usd'] = df_clean['funding_total_usd'].replace('-', np.nan)
df_clean['funding_total_usd'] = pd.to_numeric(df_clean['funding_total_usd'], errors='coerce')

# 4. Fechas
for col in ['founded_at', 'first_funding_at', 'last_funding_at']:
    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')

print(f"\n✅ Limpieza completa: {len(df_clean):,} filas")
```

**Guardar:**
```python
output = PROCESSED_DATA_DIR / 'startups_cleaned.csv'
df_clean.to_csv(output, index=False)
print(f"💾 Guardado: {output}")
```

### ✅ Checklist

- [ ] Calidad analizada
- [ ] Decisiones documentadas
- [ ] Datos limpios guardados
- [ ] Commit: `feat: Add cleaning`

---

## 8. Fase 3: Feature Engineering

### ⏱️ Duración: 4-5 horas

### 🎯 Objetivo

Crear 5+ features de valor.

### 📝 Features Obligatorias

#### 1. age_years
```python
from datetime import datetime

df['age_years'] = (datetime.now() - df['founded_at']).dt.days / 365.25
df['age_years'] = df['age_years'].round(1)
```

#### 2. success_rate_sector
```python
success = df.groupby('category_list').apply(
    lambda x: (x['status'] == 'operating').sum() / len(x) * 100
)
df = df.merge(success.rename('success_rate_sector'), on='category_list', how='left')
```

#### 3. funding_stage
```python
def stage(amount):
    if pd.isna(amount): return 'Unfunded'
    elif amount < 1e6: return 'Seed'
    elif amount < 10e6: return 'Series A-B'
    elif amount < 50e6: return 'Series C+'
    else: return 'Late Stage'

df['funding_stage'] = df['funding_total_usd'].apply(stage)
```

#### 4. country_score
```python
scores = df[df['status'] == 'operating'].groupby('country_code').size()
scores = (scores / scores.max()) * 100
df['country_score'] = df['country_code'].map(scores).fillna(0)
```

#### 5. funding_velocity
```python
df['funding_velocity'] = (df['last_funding_at'] - df['first_funding_at']).dt.days
df['funding_per_day'] = df['funding_total_usd'] / df['funding_velocity']
```

### ✅ Checklist

- [ ] 5 features creadas
- [ ] Validadas sin errores
- [ ] Dataset guardado
- [ ] Commit: `feat: Add features`

---

## 9. Fase 4: Análisis Exploratorio (EDA)

### ⏱️ Duración: 4-5 horas

### 🎯 Preguntas a Responder

#### Pregunta 1: Sectores con Mayor Tasa de Éxito
```python
sector_success = df.groupby('category_list').agg({
    'status': lambda x: (x == 'operating').sum(),
    'name': 'count'
}).rename(columns={'status': 'exitosas', 'name': 'total'})

sector_success['tasa_exito'] = (sector_success['exitosas'] / sector_success['total']) * 100
sector_success = sector_success.sort_values('tasa_exito', ascending=False).head(10)

print(sector_success)
```

#### Pregunta 2: Países con Ecosistema Robusto
```python
country_analysis = df[df['status'] == 'operating'].groupby('country_code').agg({
    'name': 'count',
    'funding_total_usd': 'sum'
}).sort_values('name', ascending=False).head(10)

print(country_analysis)
```

#### Pregunta 3: Correlación Inversión-Éxito
```python
# Comparar funding promedio entre exitosas y cerradas
comparison = df.groupby('status')['funding_total_usd'].agg(['mean', 'median', 'count'])
print(comparison)

# Correlación
from scipy.stats import pearsonr
df_numeric = df[df['funding_total_usd'].notna()]
corr, pval = pearsonr(
    df_numeric['funding_total_usd'],
    (df_numeric['status'] == 'operating').astype(int)
)
print(f"Correlación: {corr:.3f}, p-value: {pval:.3f}")
```

#### Pregunta 4: Perfil Ideal de Startup
```python
ideal = df[df['status'] == 'operating'].describe()
print("Perfil de startup exitosa:")
print(f"Edad promedio: {ideal.loc['mean', 'age_years']:.1f} años")
print(f"Funding promedio: ${ideal.loc['mean', 'funding_total_usd']:,.0f}")
print(f"Rondas promedio: {ideal.loc['mean', 'funding_rounds']:.1f}")
```

#### Pregunta 5: Estacionalidad
```python
df['funding_month'] = df['first_funding_at'].dt.month
monthly_funding = df.groupby('funding_month').size()

print("Rondas por mes:")
print(monthly_funding.sort_values(ascending=False))
```

### ✅ Checklist

- [ ] 5 preguntas respondidas
- [ ] Análisis documentado
- [ ] Commit: `feat: Add EDA`

---

## 10. Fase 5: Integración con JOINs

### ⏱️ Duración: 2-3 horas

### 🎯 Objetivo

Integrar datos externos usando 3 tipos de JOINs.

### 📝 JOIN 1: LEFT JOIN (Startups + Países)
```python
df_countries = pd.read_csv(EXTERNAL_DATA_DIR / 'countries.csv')

df_enriched = df.merge(
    df_countries,
    on='country_code',
    how='left'
)

print(f"✅ LEFT JOIN: {len(df_enriched)} filas")
print(f"Nulos en country_name: {df_enriched['country_name'].isnull().sum()}")
```

### 📝 JOIN 2: INNER JOIN (Solo Blockchain + Crypto)
```python
df_crypto = pd.read_csv(EXTERNAL_DATA_DIR / 'crypto_prices.csv')

# Filtrar solo blockchain startups
df_blockchain = df[df['category_list'].str.contains('blockchain|crypto', case=False, na=False)]

# JOIN con precios crypto (simulado por nombre)
df_blockchain_enriched = df_blockchain.merge(
    df_crypto[['name', 'current_price']],
    left_on='name',
    right_on='name',
    how='inner'
)

print(f"✅ INNER JOIN: {len(df_blockchain_enriched)} startups blockchain con precio")
```

### 📝 JOIN 3: LEFT JOIN (Países + PIB)
```python
df_gdp = pd.read_csv(EXTERNAL_DATA_DIR / 'gdp.csv')

df_final = df_enriched.merge(
    df_gdp[['country_code', 'gdp_usd']],
    on='country_code',
    how='left'
)

print(f"✅ LEFT JOIN con PIB: {len(df_final)} filas")
print(f"Países con PIB: {df_final['gdp_usd'].notna().sum()}")
```

### 📊 Análisis Post-JOIN
```python
# Correlación: PIB del país vs éxito de startups
country_success = df_final.groupby('country_code').agg({
    'status': lambda x: (x == 'operating').sum(),
    'name': 'count',
    'gdp_usd': 'first'
}).dropna()

country_success['success_rate'] = (country_success['status'] / country_success['name']) * 100

print("Top 10 países por PIB vs tasa de éxito:")
print(country_success.sort_values('gdp_usd', ascending=False).head(10))
```

### ✅ Checklist

- [ ] 3 tipos de JOIN usados
- [ ] Cada JOIN documentado
- [ ] Dataset final guardado
- [ ] Commit: `feat: Add data integration`

---

## 11. Fase 6: Visualización y Dashboards

### ⏱️ Duración: 5-6 horas

### 🎯 Objetivo

Crear dashboard ejecutivo con GridSpec.

### 📝 Dashboard Principal
```python
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# Crear grid 2x2 con proporciones personalizadas
gs = gridspec.GridSpec(2, 2, height_ratios=[2, 1], width_ratios=[1, 1])
fig = plt.figure(figsize=(16, 12))
fig.suptitle('📊 Dashboard Ejecutivo - Ecosistema de Startups', 
             fontsize=18, fontweight='bold')

# ========== GRÁFICO 1: Distribución Éxito/Fracaso por Sector ==========
ax1 = fig.add_subplot(gs[0, :])  # Toda la fila superior

top_sectors = df.groupby('category_list').size().sort_values(ascending=False).head(10)
success_data = df[df['category_list'].isin(top_sectors.index)].groupby(['category_list', 'status']).size().unstack(fill_value=0)

success_data.plot(kind='barh', stacked=False, ax=ax1, color=['#4ECDC4', '#FF6B6B', '#95E1D3'])
ax1.set_title('Top 10 Sectores: Distribución por Status', fontsize=14, fontweight='bold')
ax1.set_xlabel('Número de Startups')
ax1.legend(title='Status')
ax1.grid(True, alpha=0.3, axis='x')

# ========== GRÁFICO 2: Mapa de Calor de Países ==========
ax2 = fig.add_subplot(gs[1, 0])

top_countries = df.groupby('country_code').size().sort_values(ascending=False).head(10)
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_countries)))

ax2.barh(top_countries.index, top_countries.values, color=colors, edgecolor='black')
ax2.set_title('Top 10 Países por Startups', fontsize=12, fontweight='bold')
ax2.set_xlabel('Número de Startups')
ax2.invert_yaxis()
ax2.grid(True, alpha=0.3, axis='x')

# ========== GRÁFICO 3: Distribución de Funding ==========
ax3 = fig.add_subplot(gs[1, 1])

funding_stages = df['funding_stage'].value_counts()
colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

ax3.pie(funding_stages.values, labels=funding_stages.index, autopct='%1.1f%%',
        startangle=90, colors=colors_pie)
ax3.set_title('Distribución por Etapa de Funding', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('reports/figures/dashboard_executive.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Dashboard guardado en reports/figures/")
```

### 📊 Visualizaciones Adicionales

**Evolución Temporal:**
```python
plt.figure(figsize=(14, 6))

# Funding por año
yearly = df.groupby(df['founded_at'].dt.year)['funding_total_usd'].sum() / 1e9

plt.plot(yearly.index, yearly.values, marker='o', linewidth=2, markersize=8)
plt.fill_between(yearly.index, yearly.values, alpha=0.3)

plt.title('Evolución del Funding Total por Año', fontsize=14, fontweight='bold')
plt.xlabel('Año')
plt.ylabel('Funding Total (Billones USD)')
plt.grid(True, alpha=0.3)
plt.savefig('reports/figures/funding_evolution.png', dpi=300)
plt.show()
```

### ✅ Checklist

- [ ] Dashboard con GridSpec
- [ ] Mínimo 4 visualizaciones
- [ ] Figuras guardadas en `reports/figures/`
- [ ] Commit: `feat: Add dashboards`

---

## 12. Fase 7: Insights y Recomendaciones

### ⏱️ Duración: 2-3 horas

### 🎯 Objetivo

Generar insights accionables para stakeholders.

### 📝 Framework de Insights
```python
print("="*80)
print("📊 INFORME EJECUTIVO DE INSIGHTS")
print("="*80)

print("\n🔴 INSIGHT 1: SECTORES DE OPORTUNIDAD")
print("-"*80)
print("Observación:")
print(f"  - Top 3 sectores por tasa de éxito: FinTech (42%), HealthTech (38%), AI/ML (35%)")
print("\nRecomendaciones:")
print("  1. Priorizar inversión en FinTech y HealthTech")
print("  2. Reservar 30% del capital para AI/ML (alto riesgo, alto retorno)")
print("  3. Evitar sectores con <20% de tasa de éxito")

print("\n\n💰 INSIGHT 2: GEOGRAFÍA")
print("-"*80)
print("Observación:")
print(f"  - USA: 45% startups exitosas, UK: 18%, India: 12%")
print("\nRecomendaciones:")
print("  1. Mantener 60% de capital en USA")
print("  2. Expandir a UK e Israel (ecosistemas emergentes)")
print("  3. Considerar India para etapas tempranas (Seed)")

print("\n\n📈 INSIGHT 3: PERFIL IDEAL")
print("-"*80)
print("Perfil de startup con mayor probabilidad de éxito:")
print("  ✓ Sector: FinTech o HealthTech")
print("  ✓ Ubicación: USA o UK")
print("  ✓ Etapa: Series A ($5M-$15M)")
print("  ✓ Edad: 2-4 años desde fundación")
print("  ✓ Equipo: 10-50 empleados")
print("  ✓ Country Score: >75/100")

print("\n" + "="*80)
```

### 📄 Crear `reports/executive_summary.md`
```markdown
# Resumen Ejecutivo - Análisis de Startups

## 🎯 Objetivo del Análisis

Identificar oportunidades de inversión en el ecosistema global de startups tecnológicas.

## 📊 Hallazgos Clave

### 1. Sectores Estratégicos

- **FinTech:** 42% tasa de éxito, $8.5M inversión promedio
- **HealthTech:** 38% tasa de éxito, $12.3M inversión promedio
- **AI/ML:** 35% tasa de éxito, $15.7M inversión promedio

### 2. Geografía Prioritaria

| País | % Startups Exitosas | Ecosistema |
|------|---------------------|------------|
| USA | 45% | Maduro |
| UK | 18% | Robusto |
| India | 12% | Emergente |

### 3. Perfil Ideal de Inversión
```
Sector: FinTech/HealthTech
Stage: Series A ($5-15M)
Location: USA/UK
Age: 2-4 años
Team Size: 10-50
Score: >75/100
```

## 💼 Recomendaciones

### Corto Plazo (0-6 meses)

1. Invertir $50M en portafolio FinTech USA
2. Abrir oficina en UK para deal flow
3. Contratar especialista en HealthTech

### Medio Plazo (6-12 meses)

1. Expandir a Israel y Singapore
2. Lanzar fondo específico para AI/ML
3. Establecer relaciones con aceleradoras top

### Largo Plazo (12+ meses)

1. Evaluar mercados emergentes (India, Brasil)
2. Desarrollar tesis de inversión por vertical
3. Construir red de co-inversionistas

## 📈 Métricas de Éxito

- ROI objetivo: 3.2x en 5 años
- Tasa de éxito portafolio: >40%
- Tiempo promedio a exit: 4-6 años
```

### ✅ Checklist

- [ ] Insights documentados
- [ ] Framework aplicado
- [ ] Resumen ejecutivo creado
- [ ] Commit: `docs: Add insights`

---

## 13. Entregables Finales

### 📦 Checklist Completo

#### Código y Notebooks

- [ ] 5 notebooks completos y ejecutables
- [ ] Código modular en `src/`
- [ ] Tests básicos en `tests/`
- [ ] Sin errores al ejecutar end-to-end

#### Documentación

- [ ] README.md completo
- [ ] Executive summary
- [ ] Data dictionary
- [ ] API documentation

#### Visualizaciones

- [ ] Dashboard ejecutivo (GridSpec)
- [ ] Mínimo 6 visualizaciones guardadas
- [ ] Todas en `reports/figures/`

#### Git/GitHub

- [ ] Mínimo 20 commits descriptivos
- [ ] README con badges
- [ ] .gitignore configurado
- [ ] Repositorio público

---

## 14. Criterios de Evaluación

### 📊 Rúbrica de Evaluación (Total: 100 puntos)

| Categoría | Peso | Criterios | Puntos |
|-----------|------|-----------|--------|
| **Uso de APIs** | 20% | - 3 APIs funcionando correctamente (15 pts)<br>- Manejo de errores robusto (5 pts) | 20 |
| **JOINs en Pandas** | 15% | - 3 tipos diferentes de JOIN (9 pts)<br>- Justificación de cada tipo (6 pts) | 15 |
| **Feature Engineering** | 15% | - Mínimo 5 features creadas (10 pts)<br>- Features aportan valor al negocio (5 pts) | 15 |
| **Visualizaciones** | 20% | - Dashboard con GridSpec (10 pts)<br>- Mínimo 6 visualizaciones profesionales (10 pts) | 20 |
| **Insights de Negocio** | 20% | - 5 preguntas respondidas (10 pts)<br>- Recomendaciones accionables (10 pts) | 20 |
| **Documentación** | 10% | - README completo (3 pts)<br>- Executive summary (4 pts)<br>- Código comentado (3 pts) | 10 |

### ✅ Puntaje Mínimo para Aprobar: 70/100

### 🏆 Niveles de Logro

| Rango | Nivel | Descripción |
|-------|-------|-------------|
| 90-100 | **Excelente** | Listo para portfolio profesional |
| 80-89 | **Muy Bueno** | Proyecto sólido, mejoras menores |
| 70-79 | **Bueno** | Cumple requisitos, necesita refinamiento |
| <70 | **Insuficiente** | Requiere completar elementos faltantes |

---

## 15. Recursos y Troubleshooting

### 📚 Documentación Oficial

- **Pandas:** https://pandas.pydata.org/docs/
- **Matplotlib:** https://matplotlib.org/stable/gallery/
- **Kaggle API:** https://www.kaggle.com/docs/api
- **CoinGecko:** https://www.coingecko.com/en/api/documentation
- **REST Countries:** https://restcountries.com/
- **World Bank:** https://datahelpdesk.worldbank.org/knowledgebase/articles/889392

### 🐛 Troubleshooting Común

#### Problema 1: Kaggle API no funciona
```bash
# Solución:
# 1. Verificar kaggle.json existe
ls ~/.kaggle/kaggle.json

# 2. Verificar permisos (Linux/Mac)
chmod 600 ~/.kaggle/kaggle.json

# 3. Probar autenticación
python -c "from kaggle.api.kaggle_api_extended import KaggleApi; api = KaggleApi(); api.authenticate(); print('✅ OK')"
```

#### Problema 2: Error de encoding al cargar CSV
```python
# Solución: Usar data_loader.py que maneja encoding automáticamente
from src.data.data_loader import load_raw

df = load_raw('archivo.csv')  # Detecta encoding automáticamente
```

#### Problema 3: APIs con rate limit
```python
# Solución: Agregar delays entre requests
import time

for i in range(10):
    response = requests.get(url)
    time.sleep(1)  # Esperar 1 segundo entre llamadas
```

#### Problema 4: Error en JOINs
```python
# Solución: Verificar antes y después del merge
print(f"Antes: df1={len(df1)}, df2={len(df2)}")

result = pd.merge(df1, df2, on='key', how='left')

print(f"Después: {len(result)}")
print(f"Nulos creados: {result.isnull().sum()}")
```

#### Problema 5: GridSpec no muestra bien
```python
# Solución: Usar tight_layout() y tamaños adecuados
fig = plt.figure(figsize=(16, 12))  # Tamaño grande
# ... crear subplots ...
plt.tight_layout()
plt.subplots_adjust(top=0.95)  # Ajustar para título
plt.show()
```

### 💡 Tips Profesionales

#### Tip 1: Commits Frecuentes
```bash
# Commit después de cada fase completada
git add .
git commit -m "✨ feat: Completada Fase 1 - Data Acquisition"
git push
```

#### Tip 2: Prueba Incremental
```python
# No esperes a tener todo el código para probar
# Prueba cada función inmediatamente

def mi_funcion(x):
    return x * 2

# Probar inmediatamente
assert mi_funcion(5) == 10
print("✅ Función funciona")
```

#### Tip 3: Documentación en el Momento
```python
# Documenta MIENTRAS escribes código, no después
def calcular_tasa_exito(df, sector):
    """
    Calcula la tasa de éxito de startups en un sector.
    
    Args:
        df: DataFrame con columnas 'sector' y 'status'
        sector: Nombre del sector a analizar
        
    Returns:
        float: Porcentaje de éxito (0-100)
    """
    # Tu código aquí
```

#### Tip 4: Usa Variables Descriptivas
```python
# ❌ MAL
df1 = df[df['c'] == 'x']
df2 = df1.groupby('y')['z'].sum()

# ✅ BIEN
operating_startups = df[df['status'] == 'operating']
funding_by_sector = operating_startups.groupby('sector')['funding_usd'].sum()
```

#### Tip 5: Manejo de Errores Siempre
```python
# ✅ Siempre usar try-except en llamadas a APIs
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.Timeout:
    print("⏰ Timeout - intenta de nuevo")
except requests.exceptions.HTTPError as e:
    print(f"❌ Error HTTP: {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
```

### 🚀 Optimizaciones Avanzadas

#### Para Datasets Grandes (>1GB)
```python
# Leer CSV en chunks
chunks = []
for chunk in pd.read_csv('huge_file.csv', chunksize=10000):
    # Procesar chunk
    chunk_processed = chunk[chunk['status'] == 'operating']
    chunks.append(chunk_processed)

df_final = pd.concat(chunks, ignore_index=True)
```

#### Caché de APIs
```python
import pickle
from pathlib import Path

def fetch_with_cache(url, cache_file):
    """Fetch con caché local"""
    cache_path = Path(cache_file)
    
    if cache_path.exists():
        print("📦 Cargando desde caché")
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
    
    print("🌐 Descargando de API")
    response = requests.get(url)
    data = response.json()
    
    with open(cache_path, 'wb') as f:
        pickle.dump(data, f)
    
    return data
```

---

## 🎓 Recursos de Aprendizaje Adicionales

### 📖 Lecturas Recomendadas

1. **"Python for Data Analysis" - Wes McKinney**
   - Capítulos 7-8: Data Cleaning and Preparation
   - Capítulos 9-10: Data Aggregation and Group Operations

2. **Kaggle Learn:**
   - Pandas Course: https://www.kaggle.com/learn/pandas
   - Data Visualization: https://www.kaggle.com/learn/data-visualization

3. **Real Python:**
   - Working with APIs: https://realpython.com/api-integration-in-python/
   - Pandas GroupBy: https://realpython.com/pandas-groupby/

### 🎥 Videos Recomendados

1. **Data School (YouTube):**
   - Pandas Best Practices
   - Data Cleaning Workflow

2. **Corey Schafer:**
   - Matplotlib Tutorial Series
   - Pandas Tutorial Series

### 💼 Proyectos Similares para Inspiración

1. **Kaggle Notebooks:**
   - Buscar: "startup analysis", "venture capital analysis"
   - Filtrar por: Most Votes

2. **GitHub:**
   - Buscar: "startup investment analysis python"
   - Estudiar estructura de proyectos con muchas ⭐

---

## 🎯 Plan de Trabajo Sugerido

### Semana 1: Fundamentos

- **Lunes:** Setup + Fase 0 (2h)
- **Martes:** Fase 1 - APIs (3h)
- **Miércoles:** Fase 1 - Kaggle (2h)
- **Jueves:** Fase 2 - Limpieza (4h)
- **Viernes:** Repaso y consolidación (2h)

### Semana 2: Análisis

- **Lunes:** Fase 3 - Feature Engineering (4h)
- **Martes:** Fase 3 - Validación (2h)
- **Miércoles:** Fase 4 - EDA parte 1 (3h)
- **Jueves:** Fase 4 - EDA parte 2 (3h)
- **Viernes:** Fase 5 - JOINs (3h)

### Semana 3: Visualización

- **Lunes:** Fase 6 - Dashboard base (4h)
- **Martes:** Fase 6 - Visualizaciones adicionales (3h)
- **Miércoles:** Fase 7 - Insights (3h)
- **Jueves:** Documentación (3h)
- **Viernes:** Refinamiento y entrega (4h)

---

## 📝 Plantillas Útiles

### Template: Celda de Markdown Inicial
```markdown
# [Número]. [Título de la Sección]

**Objetivo:** [Qué vamos a lograr]

**Entrada:** [Qué datos/archivos necesitamos]

**Salida:** [Qué vamos a producir]

**Duración estimada:** [X minutos]
```

### Template: Commit Message
```bash
# Formato: <tipo>: <descripción>

# Tipos:
# ✨ feat: Nueva funcionalidad
# 🐛 fix: Corrección de bug
# 📝 docs: Documentación
# 🎨 style: Formato (no afecta código)
# ♻️ refactor: Refactorización
# 🧪 test: Agregar tests
# 🔧 chore: Mantenimiento

# Ejemplos:
git commit -m "✨ feat: Add CoinGecko API integration"
git commit -m "🐛 fix: Handle missing country_code in merge"
git commit -m "📝 docs: Add executive summary"
```

### Template: Función Documentada
```python
def nombre_funcion(param1: tipo1, param2: tipo2) -> tipo_retorno:
    """
    [Descripción breve de una línea]
    
    [Descripción extendida opcional con más detalles
    sobre el propósito y comportamiento de la función]
    
    Args:
        param1: Descripción del primer parámetro
        param2: Descripción del segundo parámetro
        
    Returns:
        Descripción de lo que retorna
        
    Raises:
        ErrorType: Cuándo y por qué se levanta este error
        
    Example:
        >>> resultado = nombre_funcion(valor1, valor2)
        >>> print(resultado)
        Salida esperada
    """
    # Implementación
    pass
```

---

## 🏁 Checklist Final Pre-Entrega

### ✅ Código

- [ ] Todos los notebooks ejecutan sin errores
- [ ] Código en `src/` es modular y reutilizable
- [ ] No hay imports sin usar
- [ ] Variables tienen nombres descriptivos
- [ ] Funciones tienen docstrings

### ✅ Datos

- [ ] `data/raw/` tiene datos originales
- [ ] `data/processed/` tiene datos limpios
- [ ] `data/external/` tiene datos de APIs
- [ ] `.gitignore` excluye archivos grandes

### ✅ Análisis

- [ ] 5 preguntas de negocio respondidas
- [ ] Mínimo 5 features creadas
- [ ] 3 tipos de JOINs usados y documentados
- [ ] EDA completo con hallazgos

### ✅ Visualización

- [ ] Dashboard ejecutivo creado
- [ ] Mínimo 6 visualizaciones
- [ ] Todas guardadas en `reports/figures/`
- [ ] Figuras de alta resolución (300 DPI)

### ✅ Documentación

- [ ] README.md completo
- [ ] Executive summary escrito
- [ ] Data dictionary creado
- [ ] Código comentado adecuadamente

### ✅ Git/GitHub

- [ ] Mínimo 20 commits descriptivos
- [ ] Repositorio público (o privado si prefieres)
- [ ] README con badges
- [ ] LICENSE incluida

### ✅ Presentación (Opcional)

- [ ] Slides ejecutivos (10-15 diapositivas)
- [ ] Video demo (5-10 minutos)
- [ ] Blog post explicando el proyecto

---

## 🎉 ¡Felicitaciones!

Si llegaste hasta aquí y completaste todos los pasos, has creado un proyecto de **nivel profesional** que puedes:

✅ Agregar a tu **portfolio**  
✅ Mostrar en **entrevistas de trabajo**  
✅ Compartir en **LinkedIn**  
✅ Usar como **referencia** para futuros proyectos  

### 🚀 Próximos Pasos

1. **Publicar el proyecto:**
   - Escribe un post en LinkedIn
   - Comparte en comunidades de Data Science
   - Agrega al README badges de Python, Pandas, etc.

2. **Expandir el proyecto:**
   - Agregar modelos de ML para predicción
   - Dashboard interactivo con Plotly/Dash
   - API REST con FastAPI
   - Automatización con Airflow

3. **Aprender más:**
   - SQL para bases de datos
   - Spark para Big Data
   - Machine Learning con scikit-learn
   - Deep Learning con TensorFlow

---

## 📞 Soporte y Comunidad

### 💬 Dónde Pedir Ayuda

- **Stack Overflow:** Tag `pandas`, `matplotlib`, `python`
- **Reddit:** r/datascience, r/learnpython
- **Discord:** Python Discord Server
- **Kaggle Forums:** Discussions sobre datasets

### 🤝 Contribuir al Proyecto

Si mejoras este proyecto, considera:
- Hacer un fork y enviar Pull Request
- Documentar mejoras en el README
- Compartir tus insights

---

## 📄 Licencia

Este proyecto educativo está bajo licencia MIT. Eres libre de:
- ✅ Usar el código
- ✅ Modificarlo
- ✅ Distribuirlo
- ✅ Usarlo comercialmente

**Única condición:** Mantener el aviso de copyright.

---

## 👤 Autor

**Anderson Sebastian Rubio Pacheco**
- GitHub: [@hamtrass59](https://github.com/hamtrass59)
- Email: hamtrass59@hotmail.com
- LinkedIn: [Tu perfil]

---

## 🙏 Agradecimientos

- **Platzi** por el bootcamp de Data Science
- **Kaggle** por los datasets públicos
- **Comunidad de Python** por las librerías open source
- **APIs públicas** por facilitar acceso a datos

---

**Última actualización:** Octubre 2025  
**Versión del documento:** 1.0.0  

---

## 📌 Notas Finales

### ⚠️ Advertencias Importantes

1. **No uses datos sensibles:** Este es un proyecto educativo con datos públicos
2. **Respeta rate limits:** No abuses de las APIs
3. **No versiones archivos grandes:** Usa `.gitignore` correctamente
4. **Cita tus fuentes:** Da crédito a datasets y APIs usadas

### 💡 Consejos de un Data Scientist Senior

1. **"Perfect is the enemy of done"** - Entrega algo funcional primero, refina después
2. **Documenta mientras programas** - No dejes la documentación para el final
3. **Git commit frecuente** - Mejor muchos commits pequeños que uno grande
4. **Pregunta cuando te atores** - No pierdas 2 horas en algo que alguien te puede explicar en 5 minutos
5. **Portfolio > Certificados** - Un proyecto bien hecho vale más que 10 certificados

### 🎯 Meta Final

Al completar este proyecto, habrás demostrado:
- ✅ Capacidad de trabajar con datos reales
- ✅ Integración de múltiples fuentes
- ✅ Pensamiento analítico de negocio
- ✅ Comunicación de insights
- ✅ Buenas prácticas de programación

**¡Ahora ve y construye algo increíble! 🚀**

---

_"Data is the new oil, but only if you know how to refine it."_  
_— Anónimo_