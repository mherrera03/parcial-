import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io


def show():
    st.title("Carga de Archivos y Analisis de Datos")
    st.markdown("""
    Carga un archivo **CSV** o **Excel** desde tu computadora y la aplicacion generara
    automaticamente estadisticas descriptivas y graficos segun el tipo de datos detectado.
    """)

    archivo = st.file_uploader(
        "Selecciona un archivo CSV o Excel",
        type=["csv", "xlsx", "xls"],
        help="Formatos admitidos: .csv, .xlsx, .xls"
    )

    if archivo is None:
        st.markdown("""
        <div style='background:#ede7f6; border-radius:12px; padding:2rem;
                    text-align:center; border:1px solid #d1c4e9; margin-top:1rem;'>
            <p style='color:#7c6fbf; font-size:1rem; margin:0;'>
                Aun no se ha cargado ningun archivo.<br>
                Usa el selector de arriba para cargar un CSV o Excel.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Leer el archivo ───────────────────────────────────────────────────────
    try:
        if archivo.name.endswith(".csv"):
            # Intentar diferentes encodings
            try:
                df = pd.read_csv(archivo, encoding="utf-8")
            except UnicodeDecodeError:
                archivo.seek(0)
                df = pd.read_csv(archivo, encoding="latin-1")
        else:
            df = pd.read_excel(archivo)
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
        return

    st.success(f"Archivo cargado correctamente: **{archivo.name}** — {df.shape[0]} filas x {df.shape[1]} columnas")

    tab1, tab2, tab3 = st.tabs(["Resumen General", "Explorar Columna", "Graficos Automaticos"])

    # ── Tab 1: Resumen ────────────────────────────────────────────────────────
    with tab1:
        st.subheader("Vista previa de los datos")
        st.dataframe(df.head(20), use_container_width=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Filas", df.shape[0])
        col2.metric("Columnas", df.shape[1])
        numericas = df.select_dtypes(include="number").shape[1]
        col3.metric("Columnas numericas", numericas)
        col4.metric("Columnas categoricas", df.shape[1] - numericas)

        st.subheader("Tipos de datos y completitud")
        info_df = pd.DataFrame({
            "Columna": df.columns,
            "Tipo": df.dtypes.values.astype(str),
            "Valores nulos": df.isnull().sum().values,
            "% Completo": (((df.shape[0] - df.isnull().sum()) / df.shape[0]) * 100).round(1).values
        })
        st.dataframe(info_df, use_container_width=True)

        if numericas > 0:
            st.subheader("Estadisticas descriptivas (columnas numericas)")
            st.dataframe(df.describe().round(3), use_container_width=True)

    # ── Tab 2: Explorar columna ───────────────────────────────────────────────
    with tab2:
        st.subheader("Analisis de una columna especifica")
        col_sel = st.selectbox("Selecciona una columna:", df.columns.tolist())

        serie = df[col_sel]
        st.markdown(f"**Columna:** `{col_sel}` — Tipo detectado: `{serie.dtype}`")
        st.markdown(f"Valores nulos: **{serie.isnull().sum()}** de {len(serie)}")
        st.markdown(f"Valores unicos: **{serie.nunique()}**")

        if pd.api.types.is_numeric_dtype(serie):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Media", f"{serie.mean():.3f}")
            col2.metric("Mediana", f"{serie.median():.3f}")
            col3.metric("Minimo", f"{serie.min():.3f}")
            col4.metric("Maximo", f"{serie.max():.3f}")
            col1, col2 = st.columns(2)
            with col1:
                fig = px.histogram(df, x=col_sel, nbins=30,
                                   color_discrete_sequence=["#9575cd"],
                                   title=f"Distribucion de {col_sel}")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.box(df, y=col_sel, color_discrete_sequence=["#7c6fbf"],
                              title=f"Boxplot de {col_sel}")
                st.plotly_chart(fig2, use_container_width=True)
        else:
            vc = serie.value_counts().reset_index()
            vc.columns = [col_sel, "Frecuencia"]
            vc["Porcentaje"] = (vc["Frecuencia"] / len(serie) * 100).round(2)
            st.dataframe(vc, use_container_width=True)
            fig = px.bar(vc.head(20), x=col_sel, y="Frecuencia",
                         color="Frecuencia", color_continuous_scale="Purples",
                         title=f"Frecuencia de valores en {col_sel}")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    # ── Tab 3: Graficos automaticos ───────────────────────────────────────────
    with tab3:
        st.subheader("Graficos automaticos por tipo de columna")

        num_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(include="object").columns.tolist()

        if len(num_cols) >= 2:
            st.markdown("#### Mapa de correlacion (columnas numericas)")
            corr = df[num_cols].corr().round(2)
            fig_corr = px.imshow(
                corr, text_auto=True,
                color_continuous_scale="RdBu_r",
                title="Matriz de Correlacion",
                aspect="auto"
            )
            st.plotly_chart(fig_corr, use_container_width=True)

        if num_cols:
            st.markdown("#### Distribucion de columnas numericas")
            col_plot = st.selectbox("Columna numerica para histograma:", num_cols, key="num_auto")

            if cat_cols:
                color_col = st.selectbox("Colorear por (opcional):", ["Ninguno"] + cat_cols, key="color_auto")
            else:
                color_col = "Ninguno"

            color_arg = color_col if color_col != "Ninguno" else None
            fig_hist = px.histogram(
                df, x=col_plot, color=color_arg,
                nbins=30, title=f"Distribucion de {col_plot}",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        if len(num_cols) >= 2:
            st.markdown("#### Diagrama de dispersion")
            c1, c2 = st.columns(2)
            with c1:
                eje_x = st.selectbox("Eje X:", num_cols, key="scatter_x")
            with c2:
                eje_y = st.selectbox("Eje Y:", num_cols, index=min(1, len(num_cols)-1), key="scatter_y")
            color_scatter = None
            if cat_cols:
                color_scatter = st.selectbox("Colorear por:", ["Ninguno"] + cat_cols, key="scatter_c")
                color_scatter = None if color_scatter == "Ninguno" else color_scatter

            fig_sc = px.scatter(
                df, x=eje_x, y=eje_y, color=color_scatter,
                title=f"{eje_x} vs {eje_y}",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                trendline="ols" if color_scatter is None else None
            )
            st.plotly_chart(fig_sc, use_container_width=True)

        if cat_cols:
            st.markdown("#### Frecuencia de columnas categoricas")
            cat_plot = st.selectbox("Columna categorica:", cat_cols, key="cat_auto")
            vc2 = df[cat_plot].value_counts().reset_index()
            vc2.columns = [cat_plot, "Frecuencia"]
            c1, c2 = st.columns(2)
            with c1:
                fig_bar = px.bar(
                    vc2.head(15), x=cat_plot, y="Frecuencia",
                    color="Frecuencia", color_continuous_scale="Purples",
                    title=f"Frecuencia de {cat_plot}"
                )
                fig_bar.update_xaxes(tickangle=45)
                st.plotly_chart(fig_bar, use_container_width=True)
            with c2:
                fig_pie = px.pie(
                    vc2.head(10), names=cat_plot, values="Frecuencia",
                    title=f"Proporcion de {cat_plot}",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_pie, use_container_width=True)
