import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

from data_loader import load_pets, FIELD_DESCRIPTIONS

def show():
    st.title(" Análisis Exploratorio")
    df = load_pets()

    submenu = st.selectbox("Selecciona una sección:", [
        " Descripción del Dataset",
        " Descripción de Campos",
        " Navegador del Dataset",
        " Buscador por Código (Bonus)",
        " Graficador Exploratorio",
        " Hipótesis"
    ])

    # ── 1. Descripción del Dataset ──────────────────────────────────────────
    if submenu == " Descripción del Dataset":
        st.subheader(" Descripción General del Dataset: pet_adoption_data")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Registros", df.shape[0])
        col2.metric("Variables", df.shape[1])
        col3.metric("Numéricas", df.select_dtypes(include='number').shape[1])
        col4.metric("Categóricas / Binarias", df.select_dtypes(include='object').shape[1])

        st.markdown("### Vista previa del dataset")
        st.dataframe(df.head(10), use_container_width=True)

        st.markdown("### Tipos de datos y completitud")
        dtype_df = pd.DataFrame({
            "Campo": df.columns,
            "Tipo de dato": df.dtypes.values.astype(str),
            "Valores nulos": df.isnull().sum().values,
            "% Completo": (((df.shape[0] - df.isnull().sum()) / df.shape[0]) * 100).round(1).values
        })
        st.dataframe(dtype_df, use_container_width=True)

        st.markdown("### Estadísticas descriptivas (variables numéricas)")
        st.dataframe(df.describe().round(2), use_container_width=True)

        st.markdown("### Distribución de la variable objetivo")
        vc = df['AdoptionLikelihood'].value_counts().reset_index()
        vc.columns = ['AdoptionLikelihood', 'Count']
        vc['Etiqueta'] = vc['AdoptionLikelihood'].map({1: 'Adoptado', 0: 'No Adoptado'})
        fig = px.pie(vc, names='Etiqueta', values='Count',
                     color_discrete_sequence=['#2e7d32','#ef5350'],
                     title="Distribución: Adoptado vs No Adoptado")
        st.plotly_chart(fig, use_container_width=True)

    # ── 2. Descripción de Campos ─────────────────────────────────────────────
    elif submenu == " Descripción de Campos":
        st.subheader(" Descripción de Campos")
        campo = st.selectbox("Selecciona un campo:", df.columns.tolist())

        st.markdown(f"#### Campo: `{campo}`")
        desc = FIELD_DESCRIPTIONS.get(campo, "Sin descripción disponible.")
        st.info(f"**Descripción:** {desc}")

        if df[campo].dtype in ['int64', 'float64'] and campo not in ['Vaccinated','HealthCondition','PreviousOwner','AdoptionLikelihood']:
            st.markdown("**Tipo:** Cuantitativo (Numérico)")
            stats = df[campo].describe().round(3)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Media", f"{stats['mean']:.2f}")
            col2.metric("Mediana", f"{df[campo].median():.2f}")
            col3.metric("Mínimo", f"{stats['min']:.2f}")
            col4.metric("Máximo", f"{stats['max']:.2f}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Desv. Estándar", f"{stats['std']:.2f}")
            col2.metric("Q1 (25%)", f"{stats['25%']:.2f}")
            col3.metric("Q3 (75%)", f"{stats['75%']:.2f}")
            col4.metric("Valores únicos", df[campo].nunique())
        else:
            st.markdown("**Tipo:** Categórico / Binario")
            valores = df[campo].value_counts().reset_index()
            valores.columns = ["Valor", "Frecuencia"]
            valores["% del total"] = (valores["Frecuencia"] / len(df) * 100).round(2)
            if campo in ['Vaccinated','HealthCondition','PreviousOwner','AdoptionLikelihood']:
                label_map = {0: 'No (0)', 1: 'Sí (1)'}
                valores["Valor"] = valores["Valor"].map(label_map)
            st.markdown(f"**Categorías únicas:** {df[campo].nunique()}")
            st.dataframe(valores, use_container_width=True)

    # ── 3. Navegador del Dataset ─────────────────────────────────────────────
    elif submenu == " Navegador del Dataset":
        st.subheader(" Navegador Completo del Dataset")
        col1, col2, col3 = st.columns(3)
        with col1:
            pet_filter = st.multiselect("Filtrar por Tipo:", df['PetType'].unique())
        with col2:
            size_filter = st.multiselect("Filtrar por Tamaño:", df['Size'].unique())
        with col3:
            adopted_filter = st.selectbox("Estado adopción:", ["Todos", "Adoptados (1)", "No Adoptados (0)"])

        filtered = df.copy()
        if pet_filter:
            filtered = filtered[filtered['PetType'].isin(pet_filter)]
        if size_filter:
            filtered = filtered[filtered['Size'].isin(size_filter)]
        if adopted_filter == "Adoptados (1)":
            filtered = filtered[filtered['AdoptionLikelihood'] == 1]
        elif adopted_filter == "No Adoptados (0)":
            filtered = filtered[filtered['AdoptionLikelihood'] == 0]

        st.markdown(f"Mostrando **{len(filtered)}** de {len(df)} registros")
        st.dataframe(filtered, use_container_width=True, height=450)

    # ── 4. Buscador (Bonus) ──────────────────────────────────────────────────
    elif submenu == " Buscador por Código (Bonus)":
        st.subheader(" Buscador de Registros por PetID")
        codigo = st.text_input("Ingresa el Pet ID (ej. PET0001):", "").strip().upper()
        if codigo:
            resultado = df[df['PetID'] == codigo]
            if not resultado.empty:
                st.success(f" Registro encontrado: **{codigo}**")
                row = resultado.iloc[0]
                col1, col2, col3 = st.columns(3)
                fields = list(df.columns)
                for i, col_name in enumerate(fields):
                    val = row[col_name]
                    if col_name in ['Vaccinated','HealthCondition','PreviousOwner','AdoptionLikelihood']:
                        val = " Sí" if val == 1 else " No"
                    [col1, col2, col3][i % 3].metric(col_name, val)
            else:
                st.error(f" No se encontró ningún registro con el código **{codigo}**.")
                st.info("Formato válido: PET0001 hasta PET0500")
        else:
            st.info("Ingresa un PetID para buscar (ej. PET0042).")

    # ── 5. Graficador Exploratorio ───────────────────────────────────────────
    elif submenu == " Graficador Exploratorio":
        st.subheader("Graficador Exploratorio")
        campo = st.selectbox("Selecciona un campo para graficar:",
                             [c for c in df.columns if c != 'PetID'])

        binary_cols = ['Vaccinated', 'HealthCondition', 'PreviousOwner', 'AdoptionLikelihood']

        if campo in binary_cols:
            st.markdown("**Campo binario detectado  Gráfico de barras**")
            vc = df[campo].value_counts().reset_index()
            vc.columns = [campo, 'Frecuencia']
            vc[campo] = vc[campo].map({0: 'No (0)', 1: 'Sí (1)'})
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(vc, x=campo, y='Frecuencia', color=campo,
                             color_discrete_sequence=['#ef5350','#2e7d32'],
                             title=f"Distribución de {campo}")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.pie(vc, names=campo, values='Frecuencia',
                              color_discrete_sequence=['#ef5350','#2e7d32'],
                              title=f"Proporción de {campo}")
                st.plotly_chart(fig2, use_container_width=True)

        elif df[campo].dtype in ['int64', 'float64']:
            st.markdown("**Campo numérico detectado  Histograma + Boxplot**")
            col1, col2 = st.columns(2)
            with col1:
                fig = px.histogram(df, x=campo, nbins=30, color_discrete_sequence=['#2e7d32'],
                                   title=f"Distribución de {campo}")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.box(df, y=campo, color_discrete_sequence=['#1b5e20'],
                              title=f"Boxplot de {campo}")
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.markdown("**Campo categórico detectado  Barras + Pie**")
            conteo = df[campo].value_counts().reset_index()
            conteo.columns = [campo, 'Frecuencia']
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(conteo, x=campo, y='Frecuencia', color='Frecuencia',
                             color_continuous_scale='Greens', title=f"Frecuencia de {campo}")
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.pie(conteo, names=campo, values='Frecuencia', title=f"Proporción de {campo}")
                st.plotly_chart(fig2, use_container_width=True)

    # ── 6. Hipótesis ─────────────────────────────────────────────────────────
    elif submenu == " Hipótesis":
        st.subheader(" Análisis de Hipótesis")
        hipotesis = st.selectbox("Selecciona una hipótesis:", [
            "H1: Las mascotas vacunadas tienen mayor probabilidad de ser adoptadas",
            "H2: A menor tiempo en el refugio, mayor probabilidad de adopción",
            "H3: Las mascotas más jóvenes (AgeMonths < 12) se adoptan más fácilmente"
        ])

        if hipotesis.startswith("H1"):
            st.markdown("### H1: Vacunación  Mayor probabilidad de adopción")
            st.markdown("**Análisis estadístico comparativo:**")
            
            vacc = df.groupby('Vaccinated')['AdoptionLikelihood'].agg(['mean','sum','count']).reset_index()
            vacc.columns = ['Vaccinated','Tasa Adopción','Adoptados','Total']
            vacc['Vaccinated'] = vacc['Vaccinated'].map({0:'No Vacunado', 1:'Vacunado'})
            vacc['Tasa Adopción %'] = (vacc['Tasa Adopción'] * 100).round(2)
            
            col1, col2, col3 = st.columns(3)
            tasa_vacc = vacc[vacc['Vaccinated']=='Vacunado']['Tasa Adopción %'].values[0]
            tasa_no = vacc[vacc['Vaccinated']=='No Vacunado']['Tasa Adopción %'].values[0]
            col1.metric("Tasa adopción VACUNADOS", f"{tasa_vacc}%")
            col2.metric("Tasa adopción NO VACUNADOS", f"{tasa_no}%")
            col3.metric("Diferencia", f"{tasa_vacc - tasa_no:.2f}%")
            
            st.dataframe(vacc, use_container_width=True)
            
            fig = px.bar(vacc, x='Vaccinated', y='Tasa Adopción %', color='Vaccinated',
                         color_discrete_sequence=['#ef5350','#2e7d32'],
                         title="Tasa de adopción: Vacunados vs No Vacunados",
                         text='Tasa Adopción %')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            
            # By pet type
            cross = df.groupby(['PetType','Vaccinated'])['AdoptionLikelihood'].mean().reset_index()
            cross['Vaccinated'] = cross['Vaccinated'].map({0:'No Vacunado', 1:'Vacunado'})
            cross['AdoptionLikelihood'] = (cross['AdoptionLikelihood'] * 100).round(2)
            fig2 = px.bar(cross, x='PetType', y='AdoptionLikelihood', color='Vaccinated',
                          barmode='group', color_discrete_sequence=['#ef5350','#2e7d32'],
                          title="Tasa de adopción por tipo de animal y vacunación",
                          labels={'AdoptionLikelihood':'Tasa Adopción (%)'})
            st.plotly_chart(fig2, use_container_width=True)
            
            if tasa_vacc > tasa_no:
                st.success(f" **HIPÓTESIS VALIDADA.** Los animales vacunados tienen una tasa de adopción del **{tasa_vacc}%** frente al **{tasa_no}%** de los no vacunados, una diferencia de {tasa_vacc-tasa_no:.2f} puntos porcentuales. La vacunación es un factor positivo para la adopción, probablemente porque los adoptantes perciben al animal como más sano y seguro.")
            else:
                st.warning(" **HIPÓTESIS NO VALIDADA.** Los datos no muestran una ventaja clara para los animales vacunados.")

        elif hipotesis.startswith("H2"):
            st.markdown("### H2: Menor tiempo en el refugio  Mayor probabilidad de adopción")
            
            corr = df['TimeInShelterDays'].corr(df['AdoptionLikelihood'])
            col1, col2, col3 = st.columns(3)
            col1.metric("Correlación (Time vs Adoption)", f"{corr:.4f}")
            col2.metric("Promedio días (Adoptados)", f"{df[df['AdoptionLikelihood']==1]['TimeInShelterDays'].mean():.1f}")
            col3.metric("Promedio días (No adoptados)", f"{df[df['AdoptionLikelihood']==0]['TimeInShelterDays'].mean():.1f}")
            
            # Box plot comparing shelter days by adoption status
            df_plot = df.copy()
            df_plot['Estado'] = df_plot['AdoptionLikelihood'].map({1:'Adoptado', 0:'No Adoptado'})
            fig = px.box(df_plot, x='Estado', y='TimeInShelterDays', color='Estado',
                         color_discrete_sequence=['#2e7d32','#ef5350'],
                         title="Días en el refugio según estado de adopción",
                         labels={'TimeInShelterDays':'Días en el Refugio'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Quartile analysis
            df['shelter_quartile'] = pd.qcut(df['TimeInShelterDays'], q=4,
                                              labels=['Q1 (0-25%)','Q2 (25-50%)','Q3 (50-75%)','Q4 (75-100%)'])
            grupo = df.groupby('shelter_quartile')['AdoptionLikelihood'].mean().reset_index()
            grupo['AdoptionLikelihood'] = (grupo['AdoptionLikelihood'] * 100).round(2)
            fig2 = px.bar(grupo, x='shelter_quartile', y='AdoptionLikelihood',
                          color_discrete_sequence=['#388e3c'],
                          title="Tasa de adopción por cuartil de días en refugio",
                          labels={'shelter_quartile':'Cuartil de Tiempo','AdoptionLikelihood':'Tasa Adopción (%)'},
                          text='AdoptionLikelihood')
            fig2.update_traces(texttemplate='%{text}%', textposition='outside')
            st.plotly_chart(fig2, use_container_width=True)
            
            if corr < -0.05:
                st.success(f" **HIPÓTESIS VALIDADA.** La correlación negativa ({corr:.4f}) confirma que a más días en el refugio, menor es la probabilidad de adopción. Esto puede deberse al efecto de 'refugio fatigue' o a que los animales más difíciles de adoptar permanecen más tiempo.")
            else:
                st.info(f"ℹ La correlación encontrada es {corr:.4f}. La relación existe pero es débil en este dataset.")

        elif hipotesis.startswith("H3"):
            st.markdown("### H3: Mascotas jóvenes (< 12 meses) se adoptan más")
            
            df['AgeGroup'] = pd.cut(df['AgeMonths'],
                                    bins=[0, 12, 36, 72, 120],
                                    labels=['Cachorro (<1 año)','Joven (1-3 años)','Adulto (3-6 años)','Senior (6+ años)'])
            grupo = df.groupby('AgeGroup')['AdoptionLikelihood'].agg(['mean','count']).reset_index()
            grupo.columns = ['Grupo Edad','Tasa Adopción','N']
            grupo['Tasa Adopción %'] = (grupo['Tasa Adopción'] * 100).round(2)
            
            col1, col2 = st.columns(2)
            col1.metric("Tasa cachorros (<1 año)", f"{grupo[grupo['Grupo Edad']=='Cachorro (<1 año)']['Tasa Adopción %'].values[0]:.1f}%")
            col2.metric("Tasa senior (6+ años)", f"{grupo[grupo['Grupo Edad']=='Senior (6+ años)']['Tasa Adopción %'].values[0]:.1f}%")
            
            st.dataframe(grupo, use_container_width=True)
            
            fig = px.bar(grupo, x='Grupo Edad', y='Tasa Adopción %', color='Tasa Adopción %',
                         color_continuous_scale='Greens',
                         title="Tasa de adopción por grupo de edad",
                         text='Tasa Adopción %')
            fig.update_traces(texttemplate='%{text}%', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            
            fig2 = px.scatter(df, x='AgeMonths', y='AdoptionLikelihood',
                              color='PetType', trendline='lowess',
                              title="Edad (meses) vs Probabilidad de Adopción",
                              labels={'AgeMonths':'Edad (meses)', 'AdoptionLikelihood':'Adoptado (1=Sí)'})
            st.plotly_chart(fig2, use_container_width=True)
            
            tasa_joven = grupo[grupo['Grupo Edad']=='Cachorro (<1 año)']['Tasa Adopción %'].values[0]
            tasa_senior = grupo[grupo['Grupo Edad']=='Senior (6+ años)']['Tasa Adopción %'].values[0]
            if tasa_joven > tasa_senior:
                st.success(f" **HIPÓTESIS VALIDADA.** Los cachorros/crías tienen una tasa de adopción del **{tasa_joven}%** frente al **{tasa_senior}%** de los animales senior. Los adoptantes prefieren animales jóvenes, posiblemente por la mayor esperanza de vida compartida y el vínculo emocional más fuerte.")
            else:
                st.warning(" Los datos no confirman claramente esta hipótesis en el dataset actual.")