import streamlit as st
import requests
import re
import pandas as pd
import plotly.express as px

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False

try:
    from textblob import TextBlob
    TEXTBLOB_OK = True
except ImportError:
    TEXTBLOB_OK = False


# ── Helpers ───────────────────────────────────────────────────────────────────

def analizar_sentimiento(texto):
    blob = TextBlob(texto)
    pol = blob.sentiment.polarity
    sub = blob.sentiment.subjectivity
    if pol > 0.1:
        sent = "Positivo"
    elif pol < -0.1:
        sent = "Negativo"
    else:
        sent = "Neutral"
    return round(pol, 4), round(sub, 4), sent


def emoji_sentimiento(sent):
    return {"Positivo": "😊", "Negativo": "😠", "Neutral": "😐"}.get(sent, "❓")


def color_sentimiento(sent):
    return {
        "Positivo": ("#e8f5e9", "#388e3c", "#a5d6a7"),
        "Negativo": ("#ffebee", "#c62828", "#ef9a9a"),
        "Neutral":  ("#ede7f6", "#5c5096", "#d1c4e9"),
    }.get(sent, ("#f5f5f5", "#333", "#ddd"))


def extraer_textos(url, tipo):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        return None, f"No se pudo acceder. Codigo: {r.status_code}"
    soup = BeautifulSoup(r.text, "html.parser")
    if tipo == "Parrafos":
        tags = soup.find_all("p")
    elif tipo == "Titulos":
        tags = soup.find_all(["h1","h2","h3"])
    else:
        tags = soup.find_all(["p","h1","h2","h3"])
    textos = [t.get_text(strip=True) for t in tags if len(t.get_text(strip=True)) > 30]
    return textos, None


# ── Vista ─────────────────────────────────────────────────────────────────────

def show():
    st.markdown("""
    <div style='background:linear-gradient(135deg,#7c6fbf,#b39ddb);
                padding:1.8rem;border-radius:14px;color:white;margin-bottom:1.5rem;
                box-shadow:0 4px 18px rgba(124,111,191,0.3);'>
        <h2 style='margin:0;font-family:DM Serif Display,serif;'>
            💬 Analisis de Sentimientos y Scraping
        </h2>
        <p style='margin:0.4rem 0 0 0;opacity:0.9;font-size:0.95rem;'>
            Extrae textos de cualquier pagina web y clasifica su sentimiento con TextBlob.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not BS4_OK:
        st.error("Falta instalar BeautifulSoup4: `pip install beautifulsoup4`")
        return
    if not TEXTBLOB_OK:
        st.error("Falta instalar TextBlob: `pip install textblob`")
        return

    # ── Analizador rapido individual ──────────────────────────────────────────
    with st.expander("✏️ Analiza un texto rapido aqui", expanded=False):
        txt = st.text_area("Escribe o pega un texto:",
                           value="I love this! It is fantastic and amazing.",
                           height=90, key="txt_rapido")
        if st.button("Analizar", key="btn_rapido"):
            pol, sub, sent = analizar_sentimiento(txt)
            emoji = emoji_sentimiento(sent)
            bg, fg, borde = color_sentimiento(sent)
            st.markdown(f"""
            <div style='background:{bg};border-left:5px solid {borde};
                        border-radius:10px;padding:1rem;margin-top:0.5rem;'>
                <span style='font-size:2rem;'>{emoji}</span>
                <span style='font-size:1.2rem;font-weight:600;color:{fg};margin-left:0.5rem;'>
                    {sent}
                </span><br>
                <small style='color:#666;'>Polaridad: <b>{pol}</b> &nbsp;|&nbsp; Subjetividad: <b>{sub}</b></small>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(" Extraccion desde pagina web")

    col1, col2 = st.columns([3,1])
    with col1:
        url = st.text_input("URL del sitio web:",
                            value="https://es.wikipedia.org/wiki/Inteligencia_artificial",
                            placeholder="https://...")
    with col2:
        tipo = st.selectbox("Tipo de texto:", ["Parrafos", "Titulos", "Parrafos y titulos"])

    cantidad = st.slider("Cantidad maxima de textos a analizar:", 3, 20, 10)

    if st.button("Extraer y analizar textos", type="primary", use_container_width=True):
        if not url.strip():
            st.warning("Ingresa una URL valida.")
            return

        try:
            with st.spinner("Extrayendo textos del sitio web..."):
                textos, error = extraer_textos(url, tipo)

            if error:
                st.error(error)
                return
            if not textos:
                st.warning("No se encontraron textos. Prueba con otra URL o tipo de texto.")
                return

            textos = textos[:cantidad]
            st.success(f"Se extrajeron **{len(textos)}** textos para analizar.")

            # Analizar
            filas = []
            for i, t in enumerate(textos, 1):
                pol, sub, sent = analizar_sentimiento(t)
                filas.append({"N": i, "Texto": t, "Polaridad": pol,
                               "Subjetividad": sub, "Sentimiento": sent})
            df = pd.DataFrame(filas)

            # Metricas
            conteo = df["Sentimiento"].value_counts()
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            col1.metric("😊 Positivos", conteo.get("Positivo", 0))
            col2.metric("😠 Negativos", conteo.get("Negativo", 0))
            col3.metric("😐 Neutros",   conteo.get("Neutral", 0))

            # Graficos
            colores = {"Positivo":"#9575cd","Negativo":"#e57373","Neutral":"#b0bec5"}
            col_a, col_b = st.columns(2)
            with col_a:
                fig1 = px.pie(df, names="Sentimiento", title="Distribucion de sentimientos",
                              color="Sentimiento", color_discrete_map=colores)
                fig1.update_traces(textinfo="percent+label")
                st.plotly_chart(fig1, use_container_width=True)
            with col_b:
                cnt = df["Sentimiento"].value_counts().reset_index()
                cnt.columns = ["Sentimiento","Cantidad"]
                fig2 = px.bar(cnt, x="Sentimiento", y="Cantidad",
                              color="Sentimiento", color_discrete_map=colores,
                              title="Cantidad por sentimiento", text="Cantidad")
                fig2.update_traces(textposition="outside")
                st.plotly_chart(fig2, use_container_width=True)

            # Scatter polaridad vs subjetividad
            fig3 = px.scatter(df, x="Polaridad", y="Subjetividad",
                              color="Sentimiento", color_discrete_map=colores,
                              size_max=12, title="Polaridad vs Subjetividad",
                              hover_data={"Texto": True, "N": True})
            st.plotly_chart(fig3, use_container_width=True)

            # Detalle de cada texto con tarjetas
            st.markdown("---")
            st.subheader("📋 Textos analizados")
            for row in filas:
                emoji = emoji_sentimiento(row["Sentimiento"])
                bg, fg, borde = color_sentimiento(row["Sentimiento"])
                st.markdown(f"""
                <div style='background:{bg};border-left:5px solid {borde};
                            border-radius:10px;padding:1rem;margin-bottom:0.8rem;'>
                    <div style='display:flex;align-items:center;gap:0.5rem;margin-bottom:0.4rem;'>
                        <span style='font-size:1.4rem;'>{emoji}</span>
                        <span style='font-weight:600;color:{fg};'>Texto {row["N"]} — {row["Sentimiento"]}</span>
                        <span style='font-size:0.8rem;color:#777;margin-left:auto;'>
                            Polaridad: {row["Polaridad"]} &nbsp;|&nbsp; Subjetividad: {row["Subjetividad"]}
                        </span>
                    </div>
                    <p style='margin:0;color:#333;font-size:0.92rem;line-height:1.5;'>{row["Texto"][:300]}{'...' if len(row["Texto"])>300 else ''}</p>
                </div>
                """, unsafe_allow_html=True)

            # Conclusion
            st.markdown("---")
            st.subheader("✅ Conclusion")
            dominante = df["Sentimiento"].value_counts().idxmax()
            pct = df["Sentimiento"].value_counts(normalize=True).max() * 100
            pol_prom = df["Polaridad"].mean()
            sub_prom = df["Subjetividad"].mean()
            emoji_d = emoji_sentimiento(dominante)
            bg_d, fg_d, borde_d = color_sentimiento(dominante)
            st.markdown(f"""
            <div style='background:{bg_d};border-left:5px solid {borde_d};
                        border-radius:10px;padding:1.2rem;'>
                <p style='margin:0;color:#333;font-size:0.96rem;line-height:1.7;'>
                    {emoji_d} Segun los <b>{len(textos)}</b> textos extraidos de la pagina web,
                    el sentimiento predominante es <b style='color:{fg_d};'>{dominante}</b>
                    con un <b>{pct:.1f}%</b> de los textos.<br>
                    Polaridad promedio: <b>{pol_prom:.4f}</b> &nbsp;|&nbsp;
                    Subjetividad promedio: <b>{sub_prom:.4f}</b><br><br>
                    Una polaridad cercana a <b>1</b> indica contenido positivo,
                    cercana a <b>-1</b> indica contenido negativo,
                    y cercana a <b>0</b> indica neutralidad.
                    Una subjetividad alta indica que el contenido es mas opiniativo que informativo.
                </p>
            </div>
            """, unsafe_allow_html=True)

        except requests.exceptions.MissingSchema:
            st.error("URL invalida. Debe iniciar con `http://` o `https://`.")
        except Exception as e:
            st.error(f"Ocurrio un error: {e}")
