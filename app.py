import streamlit as st
import sys
import os

st.set_page_config(
    page_title="Pet Adoption",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ede7f6 0%, #e8eaf6 50%, #e3f2fd 100%);
        border-right: 1px solid #d1c4e9;
    }
    [data-testid="stSidebar"] * {
        color: #4a4080 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #5c5096 !important;
        font-weight: 500;
    }

    /* Main background */
    .main .block-container {
        background-color: #faf8ff;
        padding-top: 2rem;
    }
    .stApp {
        background-color: #f5f2ff;
    }

    /* Metrics */
    div[data-testid="metric-container"] {
        background-color: #ede7f6;
        border-radius: 12px;
        padding: 12px;
        border: 1px solid #d1c4e9;
    }
    div[data-testid="metric-container"] label {
        color: #7c6fbf !important;
        font-size: 0.8rem !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #4a4080 !important;
        font-weight: 600;
    }

    /* Buttons */
    .stButton > button {
        background-color: #7c6fbf;
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #5c5096;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(124,111,191,0.3);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background-color: #ede7f6;
        border-radius: 8px 8px 0 0;
        color: #5c5096;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #7c6fbf !important;
        color: white !important;
    }

    /* Headers */
    h1, h2, h3 {
        color: #4a4080;
        font-family: 'DM Serif Display', serif;
    }
    h1 { font-size: 2rem; }

    /* Dataframe */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Selectbox, slider */
    .stSelectbox > div > div,
    .stMultiselect > div > div {
        border-color: #d1c4e9;
        border-radius: 8px;
    }

    /* Info / success / warning boxes */
    .stAlert {
        border-radius: 10px;
    }

    /* Divider */
    hr {
        border-color: #d1c4e9;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: #ede7f6;
        border-radius: 12px;
        border: 1px solid #d1c4e9;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <p style='font-family: DM Serif Display, serif; font-size: 1.4rem; color: #4a4080; margin:0;'>
            Pet Adoption
        </p>
        
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navegacion", options=[
        "Inicio",
        "Analisis Exploratorio",
        "Aprendizaje Automatico",
        "Sistema de Recomendacion",
        "Interfaz IA",
        "Carga de Archivos",
        "Analisis de Sentimientos"
    ], label_visibility="collapsed")
    st.markdown("---")
    

try:
    if page == "Inicio":
        import inicio; inicio.show()
    elif page == "Analisis Exploratorio":
        import exploratorio; exploratorio.show()
    elif page == "Aprendizaje Automatico":
        import ml; ml.show()
    elif page == "Sistema de Recomendacion":
        import recomendacion; recomendacion.show()
    elif page == "Interfaz IA":
        import interfaz_ia; interfaz_ia.show()
    elif page == "Carga de Archivos":
        import carga_archivos; carga_archivos.show()
    elif page == "Analisis de Sentimientos":
        import sentimientos; sentimientos.show()
except Exception as e:
    st.error(f"Error: {e}")
    import traceback
    st.code(traceback.format_exc())
