import streamlit as st

def show():
    # ── Hero / Banner ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style='background: linear-gradient(135deg, #7c6fbf 0%, #5c5096 100%);
                padding: 2.5rem; border-radius: 16px; color: white;
                text-align: center; margin-bottom: 2rem;
                box-shadow: 0 4px 20px rgba(124,111,191,0.3);'>
        <p style='font-family: DM Serif Display, serif; font-size: 2.2rem; margin:0;'>
            Portafolio de Ciencia de Datos
        </p>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.88; font-size: 1rem;'>
            Pet Adoption Analysis · UGB Ciclo I-2026
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Perfil profesional ────────────────────────────────────────────────────
    st.markdown("## 👩‍💻 Sobre mí")

    col_foto, col_bio = st.columns([1, 2], gap="large")

    with col_foto:
        # INSTRUCCIÓN: Reemplaza la URL de abajo con el link directo a tu foto.
        # Puedes subirla a GitHub, Imgur, o incluirla como archivo local con st.image("mi_foto.jpg").
        FOTO_URL = "https://placehold.co/300x300/7c6fbf/ffffff?text=Tu+Foto"
        st.markdown(f"""
        <div style='text-align:center;'>
            <img src="{FOTO_URL}"
                 style='width:200px; height:200px; border-radius:50%;
                        border: 4px solid #9575cd;
                        box-shadow: 0 4px 16px rgba(124,111,191,0.35);
                        object-fit:cover;'
                 onerror="this.src='https://placehold.co/300x300/7c6fbf/ffffff?text=Foto'" />
        </div>
        """, unsafe_allow_html=True)

    with col_bio:
        st.markdown("""
        <div style='background:#ede7f6; border-radius:14px; padding:1.5rem;
                    border-left: 4px solid #9575cd;'>
            <p style='font-family: DM Serif Display, serif; font-size:1.6rem;
                      color:#4a4080; margin:0 0 0.3rem 0;'>
                Mariana Herrera Márquez
            </p>
            <p style='color:#7c6fbf; font-size:0.9rem; margin:0 0 1rem 0; font-weight:500;'>
                Estudiante de Ingeniería en Sistemas y Redes Informáticas · UGB
            </p>
            <p style='color:#444; font-size:0.95rem; line-height:1.75; margin:0;'>
                Cursando el 5° año de Ingeniería en Sistemas y Redes Informáticas en la
                Universidad Gerardo Barrios. Apasionada por el desarrollo frontend y la
                creación de interfaces digitales que combinan funcionalidad con buen diseño.
                Actualmente explorando el mundo de la Ciencia de Datos, aplicando técnicas
                de análisis exploratorio, aprendizaje automático y visualización de datos
                para extraer insights significativos de datasets reales.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Video de Data Storytelling ────────────────────────────────────────────
    st.markdown("## 🎬 Demo: Data Storytelling")
    st.markdown("Presentación del análisis exploratorio y machine learning aplicado al dataset de adopción de mascotas.")

    # INSTRUCCIÓN: Reemplaza VIDEO_URL con tu link de YouTube.
    # Formato correcto: https://www.youtube.com/embed/TU_ID_DE_VIDEO
    # Ejemplo: si tu link es https://youtu.be/abc123, pon https://www.youtube.com/embed/abc123
    VIDEO_URL = ""  # ← Pega aquí tu link embed de YouTube

    if VIDEO_URL:
        st.markdown(f"""
        <div style='border-radius:14px; overflow:hidden;
                    box-shadow: 0 4px 20px rgba(124,111,191,0.25); margin-bottom:1rem;'>
            <iframe width="100%" height="450"
                src="{VIDEO_URL}"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
                style="display:block;">
            </iframe>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#ede7f6; border-radius:12px; padding:2rem;
                    text-align:center; border:2px dashed #9575cd; margin-bottom:1rem;'>
            <p style='color:#7c6fbf; font-size:1rem; margin:0;'>
                🎬 Video de Data Storytelling — Próximamente<br>
                <small style='color:#999;'>Reemplaza VIDEO_URL en inicio.py con tu link de YouTube embed</small>
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Tarjetas de navegación ────────────────────────────────────────────────
    st.markdown("## 🗂️ Contenido del Portafolio")

    card_style = """
    <div style='background:{bg}; border-radius:14px; padding:1.5rem;
                text-align:center; border:1px solid {border};
                box-shadow: 0 2px 8px rgba(124,111,191,0.12);'>
        <p style='font-size:1.5rem; margin:0 0 0.3rem 0;'>{icono}</p>
        <p style='font-family: DM Serif Display, serif; font-size:1.05rem;
                  color:{title}; margin:0.3rem 0;'>{titulo}</p>
        <p style='color:#6b6b9b; font-size:0.85rem; margin:0;'>{desc}</p>
    </div>
    """

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(card_style.format(
            bg="#ede7f6", border="#d1c4e9", title="#4a4080", icono="📊",
            titulo="Análisis Exploratorio",
            desc="Estadísticas, gráficos e hipótesis sobre el dataset de adopción."
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(card_style.format(
            bg="#e8eaf6", border="#c5cae9", title="#3f3a7a", icono="🤖",
            titulo="Aprendizaje Automático",
            desc="Modelos predictivos para estimar la probabilidad de adopción."
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(card_style.format(
            bg="#e3f2fd", border="#b3d9f7", title="#3a6080", icono="📚",
            titulo="Recomendación de Libros",
            desc="Sistema inteligente de recomendación literaria personalizada."
        ), unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(card_style.format(
            bg="#f3e5f5", border="#e1bee7", title="#6a1f80", icono="📁",
            titulo="Carga de Archivos",
            desc="Carga un CSV o Excel y visualiza sus datos con gráficos automáticos."
        ), unsafe_allow_html=True)
    with col5:
        st.markdown(card_style.format(
            bg="#fce4ec", border="#f8bbd0", title="#7b1f3a", icono="💬",
            titulo="Análisis de Sentimientos",
            desc="Extrae opiniones de la web y analiza su sentimiento con TextBlob."
        ), unsafe_allow_html=True)
    with col6:
        st.markdown(card_style.format(
            bg="#e8f5e9", border="#c8e6c9", title="#2e7d32", icono="🧠",
            titulo="Interfaz IA",
            desc="Chat inteligente para consultar datos y conceptos de Machine Learning."
        ), unsafe_allow_html=True)

    st.markdown("---")

    # ── Sobre el dataset ──────────────────────────────────────────────────────
    st.markdown("## 🐾 Sobre el Dataset")
    st.markdown("""
    Esta aplicación fue desarrollada como parte de la **Tarea Laboratorio I y II — Cómputo 3**
    del curso **Técnica Electiva I - Ciencia de Datos** de la **Universidad Gerardo Barrios**, Ciclo I-2026.

    **Dataset principal:** `pet_adoption_data` — Información sobre mascotas en refugios y su probabilidad de adopción.

    | Variable | Tipo | Descripción |
    |---|---|---|
    | PetID | Categórica | Identificador único |
    | PetType | Categórica | Tipo de animal (Dog, Cat, Rabbit, Bird) |
    | Breed | Categórica | Raza del animal |
    | AgeMonths | Numérica | Edad en meses |
    | Color | Categórica | Color del animal |
    | Size | Categórica | Tamaño (Small, Medium, Large) |
    | WeightKg | Numérica | Peso en kg |
    | Vaccinated | Binaria | ¿Está vacunado? (0/1) |
    | HealthCondition | Binaria | ¿Tiene condición médica? (0/1) |
    | TimeInShelterDays | Numérica | Días en el refugio |
    | AdoptionFee | Numérica | Tarifa de adopción ($) |
    | PreviousOwner | Binaria | ¿Tuvo dueño anterior? (0/1) |
    | AdoptionLikelihood | Binaria | **Variable objetivo**: adoptado (1) o no (0) |
    """)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Mascotas", "500")
    col2.metric("Variables", "13")
    col3.metric("Tipos de Mascotas", "4")
    col4.metric("Variable Objetivo", "AdoptionLikelihood")

    st.info("💡 Usa el menú lateral para navegar entre todas las secciones del portafolio.")