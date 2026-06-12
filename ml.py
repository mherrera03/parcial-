import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, confusion_matrix, classification_report,
                             mean_squared_error, r2_score, mean_absolute_error)
from sklearn.preprocessing import LabelEncoder
import sys, os

from data_loader import load_pets

def show():
    st.title(" Aprendizaje Automático")
    df = load_pets()

    st.markdown("Configura el experimento de Machine Learning para predecir adopción de mascotas.")

    col1, col2 = st.columns(2)
    with col1:
        algoritmo = st.selectbox(" Algoritmo:", [
            "Regresión Logística",
            "Árbol de Decisión (Clasificación)",
            "Random Forest (Clasificación)",
            "Regresión Lineal (numérica)",
            "Árbol de Decisión (Regresión)"
        ])
    with col2:
        task_type = "clasificacion" if algoritmo in [
            "Regresión Logística","Árbol de Decisión (Clasificación)","Random Forest (Clasificación)"
        ] else "regresion"

        if task_type == "clasificacion":
            var_dependiente = st.selectbox(" Variable a predecir (dependiente):", [
                "AdoptionLikelihood",
                "Vaccinated"
            ])
        else:
            var_dependiente = st.selectbox(" Variable a predecir (dependiente):", [
                "AdoptionFee",
                "TimeInShelterDays",
                "WeightKg",
                "AgeMonths"
            ])

    var_independiente = st.selectbox(" Variable independiente (predictora):", [
        "AgeMonths",
        "WeightKg",
        "TimeInShelterDays",
        "AdoptionFee"
    ])

    test_size = st.slider(" Porcentaje de datos de PRUEBA:", 10, 50, 20, 5)
    train_size = 100 - test_size
    st.caption(f"Entrenamiento: **{train_size}%** | Prueba: **{test_size}%**")

    if "Árbol" in algoritmo:
        max_depth = st.slider("Profundidad máxima del árbol:", 2, 15, 5)
    if "Random Forest" in algoritmo:
        n_estimators = st.slider("Número de árboles:", 10, 200, 100, 10)

    if st.button("▶️ Entrenar Modelo", type="primary"):
        data = df[[var_independiente, var_dependiente]].dropna()
        X = data[[var_independiente]].values
        y = data[var_dependiente].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size/100, random_state=42
        )

        # Select and train model
        if algoritmo == "Regresión Logística":
            model = LogisticRegression(random_state=42, max_iter=1000)
        elif algoritmo == "Árbol de Decisión (Clasificación)":
            model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
        elif algoritmo == "Random Forest (Clasificación)":
            model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
        elif algoritmo == "Regresión Lineal (numérica)":
            model = LinearRegression()
        else:
            model = DecisionTreeRegressor(max_depth=max_depth, random_state=42)

        model.fit(X_train, y_train)
        y_pred_test = model.predict(X_test)
        y_pred_train = model.predict(X_train)

        st.markdown("---")
        st.subheader(" Parámetros del Modelo Entrenado")

        if task_type == "clasificacion":
            acc_test = accuracy_score(y_test, y_pred_test)
            acc_train = accuracy_score(y_train, y_pred_train)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Accuracy (Prueba)", f"{acc_test:.4f}", delta=f"{acc_test-acc_train:+.4f} vs Train")
            col2.metric("Accuracy (Entrenamiento)", f"{acc_train:.4f}")
            col3.metric("Datos Entrenamiento", len(X_train))
            col4.metric("Datos Prueba", len(X_test))

            if algoritmo == "Regresión Logística":
                col1, col2 = st.columns(2)
                col1.metric("Coeficiente", f"{model.coef_[0][0]:.6f}")
                col2.metric("Intercepto", f"{model.intercept_[0]:.4f}")

            st.markdown("### Reporte de Clasificación")
            report = classification_report(y_test, y_pred_test, output_dict=True)
            report_df = pd.DataFrame(report).transpose().round(3)
            st.dataframe(report_df, use_container_width=True)

            # Confusion matrix
            st.markdown("### Matriz de Confusión")
            cm = confusion_matrix(y_test, y_pred_test)
            fig_cm = px.imshow(cm, text_auto=True, color_continuous_scale='Greens',
                               title="Matriz de Confusión (Datos de Prueba)",
                               labels=dict(x="Predicho", y="Real"),
                               x=['No Adoptado (0)', 'Adoptado (1)'],
                               y=['No Adoptado (0)', 'Adoptado (1)'])
            st.plotly_chart(fig_cm, use_container_width=True)

        else:
            r2 = r2_score(y_test, y_pred_test)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            mae = mean_absolute_error(y_test, y_pred_test)
            r2_train = r2_score(y_train, y_pred_train)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("R² (Prueba)", f"{r2:.4f}", delta=f"{r2-r2_train:+.4f}")
            col2.metric("R² (Entrenamiento)", f"{r2_train:.4f}")
            col3.metric("RMSE", f"{rmse:.4f}")
            col4.metric("MAE", f"{mae:.4f}")

        # ── Main Visualization ────────────────────────────────────────────────
        st.markdown("---")
        st.subheader(" Gráfica: Entrenamiento vs Predicciones de Prueba")

        idx_train = np.argsort(X_train[:, 0])
        idx_test = np.argsort(X_test[:, 0])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=X_train[idx_train, 0], y=y_train[idx_train],
            mode='markers', name='Entrenamiento (real)',
            marker=dict(color='#1b5e20', size=5, opacity=0.5)
        ))
        fig.add_trace(go.Scatter(
            x=X_test[idx_test, 0], y=y_test[idx_test],
            mode='markers', name='Prueba (real)',
            marker=dict(color='#f97316', size=8, symbol='diamond', opacity=0.8)
        ))
        fig.add_trace(go.Scatter(
            x=X_test[idx_test, 0], y=y_pred_test[idx_test],
            mode='lines+markers', name='Predicciones (prueba)',
            line=dict(color='#ef4444', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        x_line = np.linspace(X.min(), X.max(), 200).reshape(-1, 1)
        y_line = model.predict(x_line)
        fig.add_trace(go.Scatter(
            x=x_line[:, 0], y=y_line, mode='lines', name='Línea del modelo',
            line=dict(color='#2e7d32', width=2)
        ))
        fig.update_layout(
            title=f"{algoritmo}: {var_independiente} → {var_dependiente}",
            xaxis_title=var_independiente, yaxis_title=var_dependiente,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)