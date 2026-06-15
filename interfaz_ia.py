import streamlit as st
import pandas as pd
import re
import os

try:
    from data_loader import load_pets
    DF_OK = True
except Exception:
    DF_OK = False


# ── Base de conocimiento ──────────────────────────────────────────────────────

def get_df():
    if DF_OK:
        try:
            return load_pets()
        except Exception:
            pass
    # fallback
    try:
        return pd.read_csv(os.path.join(os.path.dirname(__file__), "pet_adoption_data.csv"))
    except Exception:
        return None


def responder(pregunta: str, df) -> str:
    p = pregunta.lower()
    # normalizar acentos
    for a, b in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("¿",""),("?","")]:
        p = p.replace(a, b)

    # ── Preguntas sobre el dataset ────────────────────────────────────────────
    if df is not None:
        # cuantas columnas
        if any(x in p for x in ["cuantas columnas","numero de columnas","cuantos campos","cuantas variables"]):
            cols = df.columns.tolist()
            return f" El dataset tiene **{len(cols)} columnas**:\n\n" + \
                   "\n".join(f"- `{c}`" for c in cols)

        # cuantos registros / filas
        if any(x in p for x in ["cuantos registros","cuantas filas","cuantos datos","tamano"]):
            return f" El dataset tiene **{len(df)} registros** (filas) y **{df.shape[1]} columnas**."

        # media / promedio de un campo
        m = re.search(r"(media|promedio|mean)\s+(?:del?\s+campo\s+)?(\w+)", p)
        if m:
            campo = m.group(2)
            match = next((c for c in df.columns if c.lower() == campo.lower()), None)
            if match and pd.api.types.is_numeric_dtype(df[match]):
                return f" La media del campo **{match}** es **{df[match].mean():.4f}**."
            else:
                return f" No encontre el campo `{campo}` o no es numerico. Campos numericos disponibles: {', '.join(df.select_dtypes('number').columns.tolist())}"

        # maximo de un campo
        m2 = re.search(r"(maximo|mayor valor|max)\s+(?:del?\s+campo\s+)?(\w+)", p)
        if m2:
            campo = m2.group(2)
            match = next((c for c in df.columns if c.lower() == campo.lower()), None)
            if match and pd.api.types.is_numeric_dtype(df[match]):
                return f" El valor maximo del campo **{match}** es **{df[match].max():.4f}**."

        # minimo de un campo
        m3 = re.search(r"(minimo|menor valor|min)\s+(?:del?\s+campo\s+)?(\w+)", p)
        if m3:
            campo = m3.group(2)
            match = next((c for c in df.columns if c.lower() == campo.lower()), None)
            if match and pd.api.types.is_numeric_dtype(df[match]):
                return f"🔻 El valor minimo del campo **{match}** es **{df[match].min():.4f}**."

        # valores unicos de un campo categorico
        m4 = re.search(r"(valores|categorias|opciones)\s+(?:de[l]?\s+)?(?:campo\s+)?(\w+)", p)
        if m4:
            campo = m4.group(2)
            match = next((c for c in df.columns if c.lower() == campo.lower()), None)
            if match:
                unicos = df[match].unique().tolist()
                return f" Los valores unicos de **{match}** son:\n\n" + \
                       "\n".join(f"- `{v}`" for v in unicos[:20])

        # tasa de adopcion
        if any(x in p for x in ["tasa de adopcion","cuantos adoptados","porcentaje adoptado","adoptados"]):
            adoptados = df["AdoptionLikelihood"].sum()
            total = len(df)
            pct = adoptados / total * 100
            return f"🐾 De {total} mascotas, **{int(adoptados)}** fueron adoptadas ({pct:.1f}%).\n\n" \
                   f"**{total - int(adoptados)}** no fueron adoptadas ({100-pct:.1f}%)."

        # mascota mas comun
        if any(x in p for x in ["tipo de mascota","mas comun","que animales","cuantos perros","cuantos gatos"]):
            vc = df["PetType"].value_counts()
            lines = "\n".join(f"- **{k}**: {v} mascotas" for k, v in vc.items())
            return f"🐕 Distribucion por tipo de mascota:\n\n{lines}"

        # correlacion
        if "correlacion" in p:
            num_cols = df.select_dtypes("number").columns.tolist()
            corr = df[num_cols].corr()["AdoptionLikelihood"].drop("AdoptionLikelihood").sort_values(ascending=False)
            lines = "\n".join(f"- **{k}**: {v:.4f}" for k, v in corr.items())
            return f" Correlacion con **AdoptionLikelihood** (variable objetivo):\n\n{lines}\n\n" \
                   "Valores cercanos a 1 indican correlacion positiva fuerte."

        # estadisticas generales
        if any(x in p for x in ["estadisticas","describe","resumen","distribucion"]):
            desc = df.describe().round(2)
            return f" Estadisticas descriptivas del dataset:\n\n```\n{desc.to_string()}\n```"

    # ── Conceptos de ML ───────────────────────────────────────────────────────
    respuestas_ml = {
        "accuracy": "✅ **Accuracy** es la proporcion de predicciones correctas sobre el total.\n\n"
                    "`Accuracy = Predicciones correctas / Total`\n\n"
                    "Ejemplo: si el modelo evalua 100 mascotas y acierta en 82, el accuracy es **0.82 (82%)**.",
        "regresion logistica": " **Regresion Logistica** calcula la *probabilidad* de que una mascota sea adoptada.\n\n"
                               "Usa una funcion sigmoide que transforma cualquier valor al rango [0, 1].\n\n"
                               "Si la probabilidad supera 0.5, predice *adoptado*; si no, *no adoptado*.",
        "arbol de decision": " **Arbol de Decision** divide los datos con reglas como:\n\n"
                             "- Si AgeMonths < 12 → rama izquierda\n- Si Vaccinated = 1 → Adoptado\n\n"
                             "Es facil de interpretar. La profundidad maxima controla su complejidad.",
        "random forest": " **Random Forest** combina muchos arboles de decision.\n\n"
                         "Cada arbol vota y gana la mayoria. Esto reduce el sobreajuste y mejora la precision.",
        "sobreajuste": " **Sobreajuste (Overfitting)** ocurre cuando el modelo aprende de memoria los datos de entrenamiento.\n\n"
                       "Se detecta cuando el accuracy de entrenamiento es mucho mayor al de prueba.",
        "entrenamiento": " Dividir datos en **entrenamiento y prueba** es esencial para evaluar el modelo honestamente.\n\n"
                         "- **Entrenamiento (70-80%)**: el modelo aprende\n- **Prueba (20-30%)**: se evalua con datos que no vio",
        "confusion": " La **Matriz de Confusion** muestra los errores del modelo:\n\n"
                     "- **TP**: predijo adoptado y si fue adoptado ✅\n"
                     "- **TN**: predijo no adoptado y no lo fue ✅\n"
                     "- **FP**: predijo adoptado pero no lo fue ❌\n"
                     "- **FN**: predijo no adoptado pero si lo fue ❌",
        "textblob": " **TextBlob** es una libreria de Python para analisis de lenguaje natural.\n\n"
                    "Calcula **polaridad** (-1 negativo a 1 positivo) y **subjetividad** (0 objetivo a 1 subjetivo).",
        "similitud coseno": " **Similitud de Coseno** mide el angulo entre dos vectores.\n\n"
                            "Angulo 0° = similitud 1 (identicos). Angulo 90° = similitud 0 (sin relacion).\n\n"
                            "Se usa en el sistema de recomendacion de libros.",
        "scraping": " **Web Scraping** es extraer datos automaticamente de paginas web.\n\n"
                    "La app usa `requests` para descargar el HTML y `BeautifulSoup` para extraer el texto.",
    }

    for clave, respuesta in respuestas_ml.items():
        if clave in p:
            return respuesta

    # Dataset general
    if any(x in p for x in ["dataset","datos","que contiene","de que trata"]):
        return (" El dataset **pet_adoption_data** tiene **500 registros** y **13 columnas**.\n\n"
                "Contiene informacion sobre mascotas en refugios: tipo, raza, edad, peso, vacunacion, "
                "condicion de salud, dias en refugio, tarifa y si fue adoptada o no.\n\n"
                "La **variable objetivo** es `AdoptionLikelihood` (1=adoptado, 0=no adoptado).")

    return ("🤔 No encontre una respuesta para esa pregunta. Prueba con:\n\n"
            "- *Cuantas columnas tiene el dataset?*\n"
            "- *Cual es la media de AgeMonths?*\n"
            "- *Cuantos registros tiene el dataset?*\n"
            "- *Tasa de adopcion del dataset*\n"
            "- *Que es el accuracy?*\n"
            "- *Que es un arbol de decision?*\n"
            "- *Correlacion con AdoptionLikelihood*")


# ── Vista ─────────────────────────────────────────────────────────────────────

SUGERENCIAS = [
    "Cuantas columnas tiene el dataset?",
    "Cual es la media de AgeMonths?",
    "Tasa de adopcion del dataset",
    "Que tipos de mascotas hay y cuantos?",
    "Que es el accuracy en clasificacion?",
    "Cual es el maximo de AdoptionFee?",
    "Que es un Random Forest?",
    "Correlacion con AdoptionLikelihood",
    "Cuantos registros tiene el dataset?",
    "Que es la matriz de confusion?",
]

def show():
    st.markdown("""
    <div style='background:linear-gradient(135deg,#7c6fbf,#9575cd);
                padding:1.8rem;border-radius:14px;color:white;margin-bottom:1.5rem;
                box-shadow:0 4px 18px rgba(124,111,191,0.3);'>
        <h2 style='margin:0;font-family:DM Serif Display,serif;'>
             Interfaz IA — Asistente de Ciencia de Datos
        </h2>
        <p style='margin:0.4rem 0 0 0;opacity:0.9;font-size:0.95rem;'>
            Haz preguntas sobre el dataset o conceptos de Machine Learning. Sin necesidad de API.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = get_df()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sugerencias interactivas como chips
    if not st.session_state.messages:
        st.markdown("** Preguntas que puedes hacer:**")
        cols = st.columns(2)
        for i, sugg in enumerate(SUGERENCIAS):
            with cols[i % 2]:
                if st.button(sugg, key=f"s_{i}", use_container_width=True):
                    st.session_state.messages.append({"role":"user","content":sugg})
                    resp = responder(sugg, df)
                    st.session_state.messages.append({"role":"assistant","content":resp})
                    st.rerun()
        st.markdown("---")

    # Historial de mensajes con estilo
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style='display:flex;justify-content:flex-end;margin-bottom:0.6rem;'>
                <div style='background:#7c6fbf;color:white;padding:0.8rem 1.1rem;
                            border-radius:16px 16px 4px 16px;max-width:75%;
                            font-size:0.94rem;box-shadow:0 2px 8px rgba(124,111,191,0.3);'>
                    {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='display:flex;justify-content:flex-start;margin-bottom:0.6rem;'>
                <div style='background:#ede7f6;color:#333;padding:0.8rem 1.1rem;
                            border-radius:16px 16px 16px 4px;max-width:80%;
                            font-size:0.94rem;border:1px solid #d1c4e9;'>
                    {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Input
    prompt = st.chat_input("Escribe tu pregunta sobre el dataset o Ciencia de Datos...")
    if prompt:
        st.session_state.messages.append({"role":"user","content":prompt})
        resp = responder(prompt, df)
        st.session_state.messages.append({"role":"assistant","content":resp})
        st.rerun()

    # Limpiar
    if st.session_state.messages:
        st.markdown("---")
        if st.button(" Limpiar conversacion", use_container_width=False):
            st.session_state.messages = []
            st.rerun()

    # Ayuda
    with st.expander(" Preguntas de ejemplo"):
        st.markdown("""
        **Sobre el dataset:**
        - Cuantas columnas tiene el dataset?
        - Cuantos registros tiene el dataset?
        - Cual es la media de AgeMonths?
        - Cual es el maximo de AdoptionFee?
        - Cuales son los valores del campo PetType?
        - Tasa de adopcion del dataset
        - Correlacion con AdoptionLikelihood
        - Estadisticas del dataset

        **Sobre Machine Learning:**
        - Que es el accuracy?
        - Que es la regresion logistica?
        - Que es un arbol de decision?
        - Que es Random Forest?
        - Que es el sobreajuste?
        - Que es la matriz de confusion?

        **Sobre la aplicacion:**
        - Como funciona el scraping?
        - Que es TextBlob?
        - Como funciona la similitud de coseno?
        """)
