import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from data_loader import load_books


def is_wattpad(publisher):
    return "Wattpad" in str(publisher)


def badge_html(publisher):
    if is_wattpad(publisher):
        return '<span style="background:#ff6314;color:white;font-size:0.68rem;padding:2px 8px;border-radius:20px;font-weight:700;letter-spacing:0.5px;">WATTPAD</span>'
    return ""


@st.cache_data(show_spinner=False)
def build_similarity(df: pd.DataFrame):
    genres = df["genre"].unique().tolist()
    df_feat = df.copy()
    for g in genres:
        df_feat[f"genre_{g}"] = (df["genre"] == g).astype(int)
    df_feat["es_wattpad"] = df["publisher"].str.contains("Wattpad", na=False).astype(int)
    scaler = MinMaxScaler()
    num_cols = ["avg_rating", "pages", "publish_year", "ratings_count"]
    df_feat[num_cols] = scaler.fit_transform(df[num_cols])
    feature_cols = [c for c in df_feat.columns if c.startswith("genre_")] + num_cols + ["es_wattpad"]
    return cosine_similarity(df_feat[feature_cols].values)


def get_cover(book):
    url = book.get("cover_url", "") if isinstance(book, dict) else ""
    if pd.notna(url) and str(url).startswith("http"):
        return str(url)
    return "https://placehold.co/200x300/9575cd/ffffff?text=Sin+Portada"


PLACEHOLDER = "https://placehold.co/200x300/9575cd/ffffff?text=Sin+Portada"


def preload_images(books_list):
    """
    Inyecta un bloque JS que precarga todas las URLs de portadas
    antes de que se rendericen las tarjetas. Esto evita el problema
    de que Streamlit no muestra la imagen hasta interactuar.
    """
    urls = [get_cover(b) for b in books_list]
    urls_js = ",".join(f'"{u}"' for u in urls)
    st.markdown(f"""
    <script>
    (function(){{
        var urls=[{urls_js}];
        urls.forEach(function(u){{
            var img=new Image();
            img.src=u;
        }});
    }})();
    </script>
    """, unsafe_allow_html=True)


def _card_html(book):
    cover  = get_cover(book)
    title  = str(book.get("title", "")).replace('"', "&quot;")
    author = str(book.get("author", ""))
    genre  = str(book.get("genre", ""))
    rating = book.get("avg_rating", "")
    wattpad_badge = (
        '<span style="position:absolute;top:8px;right:8px;background:#ff6314;'
        'color:#fff;font-size:.58rem;padding:2px 7px;border-radius:20px;'
        'font-weight:700;letter-spacing:.5px;">WATTPAD</span>'
        if is_wattpad(book.get("publisher", "")) else ""
    )
    return f"""
    <div style="border:1px solid #d1c4e9;border-radius:12px;overflow:hidden;
                background:#fff;display:flex;flex-direction:column;
                box-shadow:0 2px 8px rgba(0,0,0,.07);">
        <div style="position:relative;width:100%;height:220px;
                    overflow:hidden;background:#ede7f6;flex-shrink:0;">
            <img src="{cover}"
                 onerror="this.onerror=null;this.src='{PLACEHOLDER}'"
                 style="position:absolute;top:0;left:0;
                        width:100%;height:100%;object-fit:cover;
                        display:block;"
                 alt="{title}"/>
            {wattpad_badge}
        </div>
        <div style="padding:10px 12px;flex:1;display:flex;
                    flex-direction:column;gap:3px;">
            <div style="font-weight:700;color:#4a4080;font-size:13px;
                        line-height:1.3;overflow:hidden;
                        display:-webkit-box;-webkit-line-clamp:2;
                        -webkit-box-orient:vertical;min-height:34px;">
                {title}
            </div>
            <div style="font-size:11px;color:#666;white-space:nowrap;
                        overflow:hidden;text-overflow:ellipsis;">{author}</div>
            <div style="font-size:11px;color:#666;white-space:nowrap;
                        overflow:hidden;text-overflow:ellipsis;">{genre}</div>
            <div style="font-size:12px;color:#555;margin-top:2px;">⭐ {rating}</div>
        </div>
    </div>"""


def _row_html(chunk, cols):
    cards = "".join(_card_html(book) for book in chunk)
    return (
        f'<div style="display:grid;gap:14px;'
        f'grid-template-columns:repeat({cols},1fr);">'
        f'{cards}</div>'
    )


def render_cards_with_buttons(books_list, cols=3, key_prefix="g"):
    clicked = None

    # Precarga todas las imágenes antes de renderizar
    preload_images(books_list)

    rows = (len(books_list) + cols - 1) // cols
    for row in range(rows):
        start = row * cols
        chunk = books_list[start: start + cols]

        st.markdown(_row_html(chunk, cols), unsafe_allow_html=True)

        btn_cols = st.columns(cols)
        for j in range(len(chunk)):
            with btn_cols[j]:
                if st.button("Ver mas", key=f"{key_prefix}_{start+j}", use_container_width=True):
                    clicked = start + j

        st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

    return clicked


def mostrar_detalle(book, df):
    cover    = get_cover(book)
    synopsis = str(book.get("synopsis", "")).strip()
    has_syn  = synopsis and synopsis not in ["", "nan", "Sinopsis no disponible."]

    if st.button("Volver al catalogo", key=f"close_{abs(hash(book['title']))}"):
        st.session_state.pop("modal_book", None)
        st.rerun()

    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(cover, use_container_width=True)

    with col2:
        wattpad = badge_html(book.get("publisher", ""))
        st.markdown(f"### {book['title']} {wattpad}", unsafe_allow_html=True)
        st.markdown(f"Autor: {book['author']}")
        st.markdown(f"Genero: {book['genre']}")
        st.markdown(f"Editorial: {book['publisher']}")
        st.markdown(f"Ano: {int(book['publish_year'])}")
        st.markdown(f"Paginas: {int(book['pages'])}")
        st.markdown(f"Calificacion: {book['avg_rating']}/5")
        st.markdown(f"Votos: {int(book['ratings_count']):,}")

        st.markdown("**Sinopsis**")
        if has_syn:
            st.markdown(
                f'<div style="background:#f8f5ff;border-left:4px solid #9575cd;'
                f'border-radius:8px;padding:1rem;font-size:14px;line-height:1.7;'
                f'color:#333;margin-top:4px;">{synopsis}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("No hay sinopsis disponible.")

    st.markdown("---")
    st.subheader("Tambien te podria gustar")

    sim_books = df[
        (df["genre"] == book["genre"]) &
        (df["title"] != book["title"])
    ].sort_values("avg_rating", ascending=False).head(3)

    if not sim_books.empty:
        sim_list = [r.to_dict() for _, r in sim_books.iterrows()]
        clicked  = render_cards_with_buttons(sim_list, cols=3, key_prefix="sim")
        if clicked is not None:
            st.session_state["modal_book"] = sim_list[clicked]
            st.rerun()

st.cache_data.clear()
def show():
    st.markdown("""
    <div style='background:linear-gradient(135deg,#4a3f8f,#7c6fbf,#9575cd);
                padding:2rem;border-radius:16px;color:white;margin-bottom:1.5rem;
                box-shadow:0 4px 24px rgba(74,63,143,.35);'>
        <h2 style='margin:0;font-size:1.8rem;'>Sistema de Recomendacion de Libros</h2>
        <p style='margin:.5rem 0 0;opacity:.88;font-size:.95rem;'>
            Clasicos en espanol, literatura latinoamericana y tus favoritos de Wattpad.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df = load_books()
    if "synopsis" not in df.columns:
        df["synopsis"] = "Sinopsis no disponible."

    sim_matrix = build_similarity(df)
    genres = sorted(df["genre"].unique().tolist())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total libros", len(df))
    col2.metric("Generos", df["genre"].nunique())
    col3.metric("Wattpad", len(df[df["publisher"].str.contains("Wattpad", na=False)]))
    col4.metric("Autores", df["author"].nunique())

    if "modal_book" in st.session_state:
        st.markdown("---")
        mostrar_detalle(st.session_state["modal_book"], df)
        return

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["Por Libro", "Por Preferencias", "Catalogo"])

    with tab1:
        st.subheader("Recomendaciones basadas en un libro que te gusto")
        filtro_g  = st.multiselect("Filtrar lista por genero:", genres, key="t1g")
        lista     = df[df["genre"].isin(filtro_g)]["title"].tolist() if filtro_g else df["title"].tolist()
        libro_sel = st.selectbox("Selecciona un libro:", lista)
        n_rec     = st.slider("Cantidad de recomendaciones:", 3, 12, 6, key="n1")

        if st.button("Buscar recomendaciones", type="primary", key="btn1"):
            st.session_state["rec_tab1"] = (libro_sel, n_rec)

        if "rec_tab1" in st.session_state:
            libro_s, n_s = st.session_state["rec_tab1"]
            idx_base = df[df["title"] == libro_s].index[0]
            scores   = sorted(enumerate(sim_matrix[idx_base]), key=lambda x: x[1], reverse=True)
            scores   = [s for s in scores if s[0] != idx_base][:n_s]

            base = df.iloc[idx_base]
            st.markdown(f"""
            <div style='background:#ede7f6;border-radius:10px;padding:.9rem;
                        border-left:4px solid #9575cd;margin-bottom:1.2rem;'>
                Basado en: <b>{base["title"]}</b> {badge_html(base["publisher"])}<br>
                <small style='color:#666;'>{base["author"]} · {base["genre"]} · ⭐ {base["avg_rating"]}</small>
            </div>""", unsafe_allow_html=True)

            books_list = [df.iloc[bidx].to_dict() for bidx, _ in scores]
            clicked = render_cards_with_buttons(books_list, cols=3, key_prefix="t1")
            if clicked is not None:
                st.session_state["modal_book"] = books_list[clicked]
                st.rerun()

    with tab2:
        st.subheader("Recomendaciones segun tus gustos")
        c1, c2 = st.columns(2)
        with c1:
            generos_pref = st.multiselect("Generos favoritos:", genres, default=[], key="pref_gen")
            rating_min   = st.slider("Calificacion minima:", 1.0, 5.0, 4.0, 0.1)
            solo_wattpad = st.checkbox("Solo titulos de Wattpad")
        with c2:
            paginas_max = st.slider("Paginas maximas:", 50, 1200, 600, 50)
            anio_min    = st.slider("Publicado desde:", 1900, 2023, 2005)
            n_pref      = st.slider("Cantidad:", 3, 12, 6, key="n_pref")

        if st.button("Buscar libros para mi", type="primary", key="btn2"):
            filtered = df[
                (df["avg_rating"] >= rating_min) &
                (df["pages"] <= paginas_max) &
                (df["publish_year"] >= anio_min)
            ].copy()
            if generos_pref:
                filtered = filtered[filtered["genre"].isin(generos_pref)]
            if solo_wattpad:
                filtered = filtered[filtered["publisher"].str.contains("Wattpad", na=False)]
            filtered = filtered.sort_values("avg_rating", ascending=False).head(n_pref)
            st.session_state["filtered_tab2"] = filtered.to_dict("records")

        if "filtered_tab2" in st.session_state:
            books_list = st.session_state["filtered_tab2"]
            if not books_list:
                st.warning("No se encontraron libros. Prueba con filtros menos restrictivos.")
            else:
                st.success(f"Encontramos {len(books_list)} libros para ti:")
                clicked = render_cards_with_buttons(books_list, cols=3, key_prefix="t2")
                if clicked is not None:
                    st.session_state["modal_book"] = books_list[clicked]
                    st.rerun()

    with tab3:
        st.subheader("Catalogo Completo")
        c1, c2, c3 = st.columns(3)
        with c1:
            search = st.text_input("Buscar:", placeholder="titulo, autor...")
        with c2:
            genero_cat = st.multiselect("Genero:", genres, key="cat_gen")
        with c3:
            solo_watt_cat = st.checkbox("Solo Wattpad", key="cat_watt")

        cat = df.copy()
        if search:
            cat = cat[
                cat["title"].str.contains(search, case=False, na=False) |
                cat["author"].str.contains(search, case=False, na=False)
            ]
        if genero_cat:
            cat = cat[cat["genre"].isin(genero_cat)]
        if solo_watt_cat:
            cat = cat[cat["publisher"].str.contains("Wattpad", na=False)]

        st.markdown(f"Mostrando {len(cat)} libros")
        books_list = cat.to_dict("records")
        clicked = render_cards_with_buttons(books_list, cols=4, key_prefix="cat")
        if clicked is not None:
            st.session_state["modal_book"] = books_list[clicked]
            st.rerun()