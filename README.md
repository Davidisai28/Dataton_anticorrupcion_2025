[![Ver en Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)](https://codifikados-datatonanticorrupcion2025-8u6mrjovxpzpf5ezsntfny.streamlit.app/)

# 🔍 PatrimonIA  
**Sistema de Detección de Riesgo en Declaraciones Patrimoniales**  
Datatón SESNA 2025 – México 🇲🇽

---

## 🧠 ¿Qué es PatrimonIA?

**PatrimonIA** es un dashboard interactivo construido en **Streamlit** que permite analizar declaraciones patrimoniales de personas servidoras públicas para identificar **riesgos de posible corrupción** a través de:

- Un **modelo de riesgo** (`riesgo_score`, `riesgo_modelo`, `score_riesgo_total`)
- Un conjunto de **reglas expertas** (R1–R10)
- Indicadores derivados de ingresos, patrimonio, anomalías y comparaciones con pares

El objetivo es aportar una herramienta abierta, transparente y replicable para apoyar el trabajo del **Sistema Nacional Anticorrupción (SNA)** y, en particular, la **SESNA**, en el contexto del **Datatón Anticorrupción 2025**.

---

## 🔗 Demo en vivo

👉 Prueba el dashboard aquí:  
[🌐 PatrimonIA en Streamlit](https://codifikados-datatonanticorrupcion2025-8u6mrjovxpzpf5ezsntfny.streamlit.app/)

> ⏱ **Nota:** debido al tamaño del conjunto de datos (cientos de miles de declaraciones) y a que el CSV se descarga desde almacenamiento externo, **la página puede tardar algunos segundos en cargar**. 

---

## ✨ Funcionalidades principales

- 📊 **Dashboard interactivo en Streamlit**:
  - Distribución de niveles de riesgo (Bajo / Medio / Alto)
  - Histogramas de score de riesgo
  - Boxplots de ingresos por nivel de riesgo
  - Análisis por institución / dependencia
  - Top casos de mayor riesgo

- 🎯 **Reglas expertas anticorrupción**:
  - Reglas R1–R10 basadas en:
    - proporción de otros ingresos,
    - inconsistencias en la declaración,
    - relación ingresos–patrimonio,
    - outliers extremos vs. pares, etc.
  - Score de reglas (`score_reglas`) y score combinado (`score_riesgo_total`)

- 🏛️ **Análisis por dependencia**:
  - Score de riesgo promedio por institución
  - Porcentaje de casos en alto riesgo por dependencia
  - Ranking de dependencias priorizado

- 🔍 **Búsqueda de personas servidoras públicas**:
  - Búsqueda por nombre y apellidos
  - Ficha detallada de:
    - institución, cargo, nivel de gobierno, año,
    - ingresos desglosados,
    - patrimonio,
    - score total y score por reglas / modelo,
    - reglas activadas.

- 🧮 **Métricas globales**:
  - Total de declaraciones analizadas
  - Distribución de riesgo (alto/medio/bajo)
  - Cobertura patrimonial
  - Ingreso promedio
  - Anomalías detectadas por Isolation Forest (`anomaly_iforest`)

---

## 🧱 Arquitectura / Tecnologías

- **Frontend / Dashboard**: [Streamlit](https://streamlit.io/)
- **Análisis y manipulación de datos**: `pandas`, `numpy`
- **Visualización**: `plotly` (gráficos interactivos)
- **Modelo y reglas de riesgo**:
  - Score de modelo (`riesgo_modelo`)
  - Score de reglas (`score_reglas`)
  - Score combinado (`score_riesgo_total`)
  - Reglas R1–R10 integradas como variables binarias

El dashboard está optimizado para manejar un dataset grande (~700k filas) mediante:

- Caché de datos con `@st.cache_data`
- Muestreo automático en algunos gráficos (histograma y boxplot)
- Límite de resultados detallados en búsquedas

---

## 📁 Estructura del repositorio

```text
.
├─ dashboard.py               # App principal de Streamlit (PatrimonIA)
├─ metadatos_analisis.json    # Metadatos del análisis (fecha, cobertura, umbrales, etc.)
├─ requirements.txt           # Dependencias de Python
├─ analisis_modelo.ipynb      # Notebook de análisis / modelado en Colab/Jupyter
└─ README.md                  # Este archivo
