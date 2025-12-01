"""
DASHBOARD INTERACTIVO - PatrimonIA
Sistema de Detección de Riesgo Anticorrupción
Datatón SESNA 2025

Para ejecutar:
streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

CSV_URL = "https://www.dropbox.com/scl/fi/v7y2qfi7yee97i15fp78j/resultados_anticorrupcion.csv?rlkey=je634a217ga8a5psh4j2ulyum&st=liqyz188&dl=1"

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================

st.set_page_config(
    page_title="PatrimonIA - Sistema Anticorrupción",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS personalizados
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .risk-high {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }
    .risk-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }
    .risk-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================
# FUNCIONES DE CARGA Y PROCESAMIENTO
# ============================================



@st.cache_data
def cargar_datos():
    """
    Carga los resultados del análisis y metadatos desde la URL pública de Dropbox.
    Cualquiera que entre a la app usará este mismo CSV.
    """
    # 1) Leer CSV grande desde la URL pública
    df = pd.read_csv(CSV_URL)

    # Convertir columnas numéricas importantes
    num_cols = [
        "total_ingresos",
        "ingreso_cargo",
        "otros_ingresos",
        "patrimonio_bruto",
        "prop_otros_ingresos",
        "riesgo_score",
        "riesgo_modelo",
        "score_reglas",
        "score_riesgo_total",
        "ingreso_financiero",
        "inmuebles_total",
        "vehiculos_total",
        "muebles_total",
        "adeudos_total",
        "num_campos_patrimonio",
        "ratio_patrimonio_ingresos",
        "dif_total_vs_componentes",
        "zscore_ingresos_vs_pares",
        "zscore_patrimonio_vs_pares",
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 2) Cargar metadatos (este sí va dentro del repo)
    try:
        with open("metadatos_analisis.json", "r", encoding="utf-8") as f:
            metadatos = json.load(f)
    except FileNotFoundError:
        metadatos = {}

    return df, metadatos

def calcular_metricas(df):
    """Cálculo de métricas globales."""
    total = len(df)

    # 1. Conteo de Riesgos
    # 👇 Preferimos el modelo original 'riesgo_nivel'
    if "riesgo_nivel" in df.columns:
        col = "riesgo_nivel"
    elif "categoria_riesgo" in df.columns:
        col = "categoria_riesgo"
    else:
        col = None

    if col is not None:
        alto = (df[col] == "Alto").sum()
        medio = (df[col] == "Medio").sum()
        bajo = (df[col] == "Bajo").sum()
    else:
        alto = medio = bajo = 0

    # 2. Cobertura patrimonial: porcentaje con patrimonio > 0
    if "patrimonio_bruto" in df.columns:
        con_patrimonio = (df["patrimonio_bruto"] > 0).sum()
        cobertura = con_patrimonio / total if total > 0 else 0
    else:
        cobertura = 0

    # 3. Ingreso promedio
    if "total_ingresos" in df.columns:
        ingreso_prom = df["total_ingresos"].mean()
    else:
        ingreso_prom = 0

    return {
        "total": total,
        "alto": alto,
        "medio": medio,
        "bajo": bajo,
        "cobertura_patrimonial": cobertura,
        "ingreso_promedio": ingreso_prom,
    }


def columna_score_total(df):
    """Devuelve la columna de score 'total' a usar."""
    if "score_riesgo_total" in df.columns:
        return "score_riesgo_total"
    elif "riesgo_score" in df.columns:
        return "riesgo_score"
    else:
        return None


def generar_grafico_distribucion(df):
    """Pie chart de distribución de niveles de riesgo."""
    if "riesgo_nivel" not in df.columns:
        return go.Figure()

    distribucion = df["riesgo_nivel"].value_counts()

    fig = go.Figure(
        data=[
            go.Pie(
                labels=distribucion.index,
                values=distribucion.values,
                hole=0.4,
                marker=dict(
                    colors=["#ef4444", "#f59e0b", "#10b981"],
                    line=dict(color="white", width=2),
                ),
                textinfo="label+percent",
                textfont_size=14,
            )
        ]
    )

    fig.update_layout(
        title="Distribución de Niveles de Riesgo",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
    )

    return fig


def generar_grafico_histograma_score(df):
    """Histograma del score de riesgo."""
    score_col = columna_score_total(df)
    if score_col is None or "riesgo_nivel" not in df.columns:
        return go.Figure()

    fig = px.histogram(
        df,
        x=score_col,
        nbins=50,
        color="riesgo_nivel",
        color_discrete_map={
            "Alto": "#ef4444",
            "Medio": "#f59e0b",
            "Bajo": "#10b981",
        },
        labels={score_col: "Score de Riesgo"},
        title="Distribución del Score de Riesgo",
    )

    # Umbrales clásicos
    fig.add_vline(
        x=0.5,
        line_dash="dash",
        line_color="orange",
        annotation_text="Umbral Medio",
    )
    fig.add_vline(
        x=0.75,
        line_dash="dash",
        line_color="red",
        annotation_text="Umbral Alto",
    )

    fig.update_layout(height=400)
    return fig


def generar_grafico_boxplot_ingresos(df):
    """Boxplot de ingresos por categoría de riesgo."""
    if "total_ingresos" not in df.columns or "riesgo_nivel" not in df.columns:
        return go.Figure()

    fig = px.box(
        df,
        x="riesgo_nivel",
        y="total_ingresos",
        color="riesgo_nivel",
        color_discrete_map={
            "Alto": "#ef4444",
            "Medio": "#f59e0b",
            "Bajo": "#10b981",
        },
        labels={
            "riesgo_nivel": "Categoría de Riesgo",
            "total_ingresos": "Total de Ingresos (MXN)",
        },
        title="Distribución de Ingresos por Categoría de Riesgo",
        log_y=True,
    )

    fig.update_layout(height=400, showlegend=False)
    return fig


def generar_grafico_reglas(df):
    """Gráfico de barras de reglas más activadas en casos de riesgo alto."""
    if "riesgo_nivel" not in df.columns:
        return None

    reglas_cols = [c for c in df.columns if c.startswith("R")]
    if not reglas_cols:
        return None

    altos = df[df["riesgo_nivel"] == "Alto"]
    if altos.empty:
        return None

    activaciones = altos[reglas_cols].mean().sort_values(ascending=True)

    fig = go.Figure(
        data=[
            go.Bar(
                y=activaciones.index,
                x=activaciones.values * 100,
                orientation="h",
                marker=dict(
                    color=activaciones.values,
                    colorscale="Reds",
                    showscale=True,
                    colorbar=dict(title="Activación %"),
                ),
                text=[f"{v:.1f}%" for v in activaciones.values * 100],
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        title="Reglas Más Activadas en Casos de Riesgo Alto",
        xaxis_title="Porcentaje de Activación (%)",
        yaxis_title="Regla",
        height=500,
        showlegend=False,
    )

    return fig


def generar_tabla_top_riesgo(df, n=20):
    """Top N casos de mayor riesgo (usando score total si existe)."""
    score_col = columna_score_total(df)
    if score_col is None:
        return pd.DataFrame()

    cols_display = [
        "id",
        "nombre",
        "primerApellido",
        "institucion",
        "cargo",
        "total_ingresos",
        "patrimonio_bruto",
        score_col,
        "riesgo_nivel",
    ]
    cols_display = [c for c in cols_display if c in df.columns]

    top_df = df.nlargest(n, score_col)[cols_display].copy()

    # Formatear columnas numéricas
    if "total_ingresos" in top_df.columns:
        top_df["total_ingresos"] = top_df["total_ingresos"].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) else "-"
        )
    if "patrimonio_bruto" in top_df.columns:
        top_df["patrimonio_bruto"] = top_df["patrimonio_bruto"].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) else "No declarado"
        )
    if score_col in top_df.columns:
        top_df[score_col] = top_df[score_col].apply(
            lambda x: f"{x:.3f}" if pd.notna(x) else "-"
        )

    return top_df


def generar_grafico_dependencias(df):
    """Análisis de riesgo por dependencia usando % de casos de Riesgo Alto."""
    if "institucion" not in df.columns or "riesgo_nivel" not in df.columns:
        return None

    score_col = columna_score_total(df)
    if score_col is None:
        return None

    # Agrupamos por institución
    agg = df.groupby("institucion").agg(
        score_promedio=(score_col, "mean"),
        total_servidores=("id", "count"),
        porcentaje_alto=("riesgo_nivel", lambda x: (x == "Alto").mean()),
    )

    # Filtramos dependencias con al menos 5 servidores
    agg = agg[agg["total_servidores"] >= 5]

    # Ordenamos por % de alto riesgo
    agg = agg.sort_values("porcentaje_alto", ascending=False).head(15)

    # Construimos la gráfica: eje X = % alto, color = % alto
    fig = go.Figure(
        data=[
            go.Bar(
                x=agg["porcentaje_alto"] * 100,
                y=agg.index,
                orientation="h",
                marker=dict(
                    color=agg["porcentaje_alto"],
                    colorscale="RdYlGn_r",  # rojo = más alto
                    showscale=True,
                    colorbar=dict(title="% Riesgo Alto"),
                ),
                text=[f"{v*100:.1f}%" for v in agg["porcentaje_alto"]],
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        title="Top 15 Dependencias por % de Casos en Riesgo Alto",
        xaxis_title="% de casos en Riesgo Alto",
        yaxis_title="Dependencia",
        height=600,
        showlegend=False,
    )

    return fig


# ============================================
# CARGA DE DATOS
# ============================================

df, metadatos = cargar_datos()
metricas = calcular_metricas(df)

# ============================================
# HEADER
# ============================================

st.markdown('<h1 class="main-header">🔍 PatrimonIA</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Sistema Inteligente de Detección de Riesgo Anticorrupción | Datatón SESNA 2025</p>',
    unsafe_allow_html=True,
)

# ============================================
# SIDEBAR - FILTROS
# ============================================

st.sidebar.title("⚙️ Filtros y Configuración")

# Filtro de nivel de riesgo
niveles_default = ["Alto", "Medio", "Bajo"]
riesgo_filter = st.sidebar.multiselect(
    "Nivel de Riesgo",
    options=niveles_default,
    default=niveles_default,
)

# Filtro de rango de ingresos (usando percentiles para evitar outliers locos)
rango_ingresos = None
if "total_ingresos" in df.columns:
    ingresos_validos = (
        df["total_ingresos"].replace([np.inf, -np.inf], np.nan).dropna()
    )
    if not ingresos_validos.empty:
        q_low, q_high = ingresos_validos.quantile([0.01, 0.99])
        ingreso_min = float(q_low)
        ingreso_max = float(q_high)
    else:
        ingreso_min = ingreso_max = 0.0

    rango_ingresos = st.sidebar.slider(
        "Rango de Ingresos (MXN)",
        min_value=ingreso_min,
        max_value=ingreso_max,
        value=(ingreso_min, ingreso_max),
        format="$%d",
    )

# Filtro de institución
institucion_filter = None
if "institucion" in df.columns:
    instituciones = ["Todas"] + sorted(
        df["institucion"].dropna().unique().tolist()
    )
    institucion_filter = st.sidebar.selectbox(
        "Institución",
        options=instituciones,
    )

# Aplicar filtros
df_filtered = df.copy()

if "riesgo_nivel" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["riesgo_nivel"].isin(riesgo_filter)]

if "total_ingresos" in df_filtered.columns and rango_ingresos is not None:
    df_filtered = df_filtered[
        (df_filtered["total_ingresos"] >= rango_ingresos[0])
        & (df_filtered["total_ingresos"] <= rango_ingresos[1])
    ]

if (
    "institucion" in df_filtered.columns
    and institucion_filter is not None
    and institucion_filter != "Todas"
):
    df_filtered = df_filtered[df_filtered["institucion"] == institucion_filter]

st.sidebar.markdown("---")
st.sidebar.info(
    f"📊 Mostrando {len(df_filtered):,} de {len(df):,} declaraciones"
)

# ============================================
# MÉTRICAS PRINCIPALES
# ============================================

st.markdown("## 📈 Métricas Principales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card risk-high">
            <h3>🚨 Riesgo Alto</h3>
            <h1>{metricas['alto']:,}</h1>
            <p>{(metricas['alto']/metricas['total']*100 if metricas['total']>0 else 0):.1f}% del total</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card risk-medium">
            <h3>⚠️ Riesgo Medio</h3>
            <h1>{metricas['medio']:,}</h1>
            <p>{(metricas['medio']/metricas['total']*100 if metricas['total']>0 else 0):.1f}% del total</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card risk-low">
            <h3>✅ Riesgo Bajo</h3>
            <h1>{metricas['bajo']:,}</h1>
            <p>{(metricas['bajo']/metricas['total']*100 if metricas['total']>0 else 0):.1f}% del total</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <h3>📋 Total Declaraciones</h3>
            <h1>{metricas['total']:,}</h1>
            <p>Analizadas en el sistema</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ============================================
# VISUALIZACIONES PRINCIPALES
# ============================================

st.markdown("## 📊 Análisis Visual")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Distribución General",
        "🎯 Análisis de Reglas",
        "🏛️ Por Dependencia",
        "🔝 Top Riesgos",
    ]
)

with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.plotly_chart(
            generar_grafico_distribucion(df_filtered),
            use_container_width=True,
        )

    with col_b:
        st.plotly_chart(
            generar_grafico_histograma_score(df_filtered),
            use_container_width=True,
        )

    st.plotly_chart(
        generar_grafico_boxplot_ingresos(df_filtered),
        use_container_width=True,
    )

    # Estadísticas adicionales
    st.markdown("### 📌 Estadísticas Clave")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Cobertura Patrimonial",
            f"{metricas['cobertura_patrimonial']:.1%}",
            delta="de declaraciones con patrimonio",
        )

    with c2:
        st.metric(
            "Ingreso Promedio",
            f"${metricas['ingreso_promedio']:,.0f}",
            delta="MXN anuales",
        )

    with c3:
        if "anomaly_iforest" in df.columns:
            anomalias = (df["anomaly_iforest"] == -1).sum()
            st.metric(
                "Anomalías Detectadas",
                f"{anomalias:,}",
                delta=f"{(anomalias/len(df)*100 if len(df)>0 else 0):.1f}% del total",
            )

with tab2:
    st.markdown("### 🎯 Reglas Anticorrupción Más Activadas")

    fig_reglas = generar_grafico_reglas(df_filtered)
    if fig_reglas:
        st.plotly_chart(fig_reglas, use_container_width=True)
    else:
        st.info("No hay datos de reglas disponibles")

    # Tabla de explicación de reglas
    st.markdown("### 📖 Explicación de Reglas")

    reglas_explicacion = {
        "R1_otros_ingresos_moderados": "30-50% de ingresos de fuentes no relacionadas al cargo",
        "R2_inconsistencia_menor": "Diferencia menor entre total declarado y componentes",
        "R3_otros_ingresos_alto": ">50% de ingresos de fuentes no relacionadas al cargo",
        "R4_alto_ingreso_sin_patrimonio": "Top 10% ingresos sin patrimonio declarado",
        "R5_inconsistencia_grave": "Diferencia significativa entre total y componentes",
        "R6_patrimonio_fragmentado": "Muchos bienes pero valor total bajo",
        "R7_solo_pasivos": "Declara deudas pero no activos",
        "R8_rendimientos_imposibles": "Ingresos financieros >15% del patrimonio",
        "R9_outlier_extremo": "Outlier significativo vs pares en mismo nivel",
        "R10_ratio_anormal": "Ratio patrimonio/ingresos anormal (>20 años o <2 años)",
    }

    reglas_df = pd.DataFrame(
        [{"Regla": k, "Descripción": v} for k, v in reglas_explicacion.items()]
    )

    st.dataframe(reglas_df, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("### 🏛️ Análisis por Dependencia")

    fig_dep = generar_grafico_dependencias(df_filtered)
    if fig_dep:
        st.plotly_chart(fig_dep, use_container_width=True)
    else:
        st.info("No hay suficientes datos por dependencia")

    # Tabla de ranking
    if (
        "institucion" in df_filtered.columns
        and "riesgo_nivel" in df_filtered.columns
        and columna_score_total(df_filtered) is not None
    ):
        st.markdown("### 📋 Ranking de Dependencias")

        score_col = columna_score_total(df_filtered)

        agg_dict = {score_col: "mean"}
        if "id" in df_filtered.columns:
            agg_dict["id"] = "count"

        ranking = df_filtered.groupby("institucion").agg(agg_dict)

        if "id" in ranking.columns:
            ranking = ranking.rename(columns={"id": "Total Servidores"})
        else:
            ranking["Total Servidores"] = 1

        ranking["Casos Riesgo Alto"] = df_filtered.groupby("institucion")[
            "riesgo_nivel"
        ].apply(lambda x: (x == "Alto").sum())

        ranking = ranking.sort_values(score_col, ascending=False)

        ranking["Score Promedio"] = ranking[score_col].apply(
            lambda x: f"{x:.3f}"
        )
        ranking = ranking.drop(columns=[score_col])

        st.dataframe(ranking.head(20), use_container_width=True)
    else:
        st.info("No hay información suficiente para el ranking por dependencia.")

with tab4:
    st.markdown("### 🔝 Top Casos de Mayor Riesgo")

    num_casos = st.slider(
        "Número de casos a mostrar", min_value=10, max_value=50, value=20, step=5
    )

    top_tabla = generar_tabla_top_riesgo(df_filtered, n=num_casos)
    st.dataframe(top_tabla, use_container_width=True, hide_index=True)

    # Opción de descarga
    if not top_tabla.empty:
        csv = top_tabla.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 Descargar Top Casos (CSV)",
            data=csv,
            file_name=f"top_{num_casos}_casos_riesgo.csv",
            mime="text/csv",
        )

# ============================================
# BÚSQUEDA INDIVIDUAL
# ============================================

st.markdown("---")
st.markdown("## 🔍 Búsqueda de Servidor Público")

col_bus1, col_bus2 = st.columns([3, 1])

with col_bus1:
    nombre_busqueda = st.text_input(
        "Buscar por nombre o apellido",
        placeholder="Ej: Juan Pérez",
    )

with col_bus2:
    st.markdown("<br>", unsafe_allow_html=True)
    buscar_btn = st.button(
        "🔎 Buscar", type="primary", use_container_width=True
    )

if buscar_btn and nombre_busqueda:
    # Búsqueda en nombre completo
    mask = pd.Series(False, index=df.index)

    for col in ["nombre", "primerApellido", "segundoApellido"]:
        if col in df.columns:
            mask = mask | df[col].str.contains(
                nombre_busqueda, case=False, na=False
            )

    resultados = df[mask]

    if len(resultados) > 0:
        st.success(f"✅ Se encontraron {len(resultados)} resultado(s)")

        # Nos aseguramos de que reglas_explicacion exista (si el usuario no abrió tab2)
        if "reglas_explicacion" not in globals():
            reglas_explicacion = {}

        score_col = columna_score_total(df)

        for _, row in resultados.iterrows():
            score_text = (
                f"{row[score_col]:.3f}" if score_col in row and pd.notna(row[score_col]) else "N/A"
            )
            nivel_texto = (
                row["riesgo_nivel"] if "riesgo_nivel" in row else "N/A"
            )

            titulo = (
                f"📋 {row.get('nombre', '')} {row.get('primerApellido', '')} "
                f"{row.get('segundoApellido', '')} - Score: {score_text} ({nivel_texto})"
            )

            with st.expander(titulo):
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.markdown("**Información General**")
                    st.write(f"**ID:** {row.get('id', 'N/A')}")
                    st.write(
                        f"**Institución:** {row.get('institucion', 'N/A')}"
                    )
                    st.write(f"**Cargo:** {row.get('cargo', 'N/A')}")
                    st.write(
                        f"**Nivel:** {row.get('nivelGobierno', 'N/A')}"
                    )
                    st.write(f"**Año:** {row.get('anio', 'N/A')}")

                with c2:
                    st.markdown("**Ingresos**")
                    st.write(
                        f"**Total:** ${row.get('total_ingresos', 0):,.0f}"
                    )
                    st.write(
                        f"**Del cargo:** ${row.get('ingreso_cargo', 0):,.0f}"
                    )
                    st.write(
                        f"**Otros:** ${row.get('otros_ingresos', 0):,.0f}"
                    )
                    if "prop_otros_ingresos" in row and pd.notna(
                        row["prop_otros_ingresos"]
                    ):
                        st.write(
                            f"**% Otros:** {row['prop_otros_ingresos']*100:.1f}%"
                        )

                with c3:
                    st.markdown("**Evaluación de Riesgo**")
                    st.write(f"**Categoría:** {nivel_texto}")
                    st.write(f"**Score Total:** {score_text}")

                    if "score_reglas" in row and pd.notna(row["score_reglas"]):
                        st.write(
                            f"**Score Reglas:** {row['score_reglas']:.3f}"
                        )
                    if "riesgo_modelo" in row and pd.notna(
                        row["riesgo_modelo"]
                    ):
                        st.write(
                            f"**Score Modelo:** {row['riesgo_modelo']:.3f}"
                        )

                # Reglas activadas
                reglas_activas = [
                    c for c in row.index if c.startswith("R") and row[c] == 1
                ]
                if reglas_activas:
                    st.markdown("**🚩 Reglas Activadas:**")
                    for regla in reglas_activas:
                        desc = reglas_explicacion.get(regla, "")
                        st.warning(
                            f"- {regla}: {desc}" if desc else f"- {regla}"
                        )
    else:
        st.warning("⚠️ No se encontraron resultados")

# ============================================
# FOOTER - METADATOS
# ============================================

st.markdown("---")

with st.expander("ℹ️ Información del Análisis"):
    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown("**Fecha de Análisis**")
        st.write(metadatos.get("fecha_analisis", "N/A"))
        st.markdown("**Total Declaraciones**")
        st.write(f"{metadatos.get('total_declaraciones', 0):,}")

    with f2:
        st.markdown("**Porcentaje de Muestra**")
        pm = metadatos.get("porcentaje_muestra", 0)
        st.write(f"{pm*100:.0f}%")
        st.markdown("**Features Utilizadas**")
        st.write(f"{metadatos.get('num_features', 0)}")

    with f3:
        st.markdown("**Umbral Ingresos Altos**")
        st.write(
            f"${metadatos.get('umbral_ingresos_altos', 0):,.0f}"
        )
        st.markdown("**Cobertura Patrimonial**")
        st.write(
            f"{metadatos.get('cobertura_patrimonial', 0)*100:.1f}%"
        )

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #64748b; padding: 2rem;'>
        <p><strong>PatrimonIA</strong> - Sistema de Detección de Riesgo Anticorrupción</p>
        <p>Desarrollado para el Datatón SESNA 2025</p>
        <p>🔍 Usando Isolation Forest + Reglas Expertas + Machine Learning</p>
    </div>
    """,
    unsafe_allow_html=True,
)
