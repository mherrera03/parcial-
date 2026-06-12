# Portafolio de Ciencia de Datos — Mariana Herrera Márquez
## Técnica Electiva I - Ciencia de Datos | UGB Ciclo I-2026

### Estructura del proyecto
```
pet_adoption_app/
├── app.py                  # Archivo principal (navegación y estilos)
├── data_loader.py          # Carga de datos
├── requirements.txt        # Dependencias
├── pet_adoption_data.csv   # Dataset principal (500 registros)
├── books.csv               # Dataset para recomendación de libros
├── .streamlit/
│   └── config.toml         # Tema visual
│
├── inicio.py               # Portafolio profesional
├── exploratorio.py         # Análisis Exploratorio
├── ml.py                   # Aprendizaje Automático
├── recomendacion.py        # Sistema de Recomendación de Libros
├── interfaz_ia.py          # Interfaz IA (chat sin API)
├── carga_archivos.py       # Carga de CSV/Excel
└── sentimientos.py         # Análisis de Sentimientos + Scraping
```

### Instalación local
```bash
pip install -r requirements.txt
python -m textblob.download_corpora
streamlit run app.py
```

### Deploy en Streamlit Cloud
1. Sube todo el proyecto a un repositorio de GitHub (público o privado)
2. Ve a https://share.streamlit.io y conecta tu cuenta de GitHub
3. Selecciona el repositorio y pon `app.py` como archivo principal
4. En **Settings > Secrets** agrega (si usas API de Anthropic):
   ```
   ANTHROPIC_API_KEY = "tu-clave-aqui"
   ```
5. Click en **Deploy** — en 2-3 minutos estará en línea

### Módulos
| Módulo | Descripción | Tarea |
|--------|-------------|-------|
| inicio.py | Portafolio profesional con bio y video | Parcial |
| exploratorio.py | EDA completo con 3 hipótesis | Tarea 1 |
| ml.py | 5 algoritmos de ML | Tarea 1 |
| recomendacion.py | Recomendación de libros con similitud coseno | Tarea 1 |
| interfaz_ia.py | Chat IA local sobre el dataset | Tarea 1 (Bonus) |
| carga_archivos.py | Carga CSV/Excel con gráficos automáticos | Tarea 2 |
| sentimientos.py | Scraping + análisis de sentimientos TextBlob | Tarea 2 |
