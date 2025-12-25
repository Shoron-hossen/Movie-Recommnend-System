import pickle
import streamlit as st
import requests
import concurrent.futures

# -------------------------------
# 1. PAGE CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide",
    page_icon="🎬",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# 2. CONSTANTS & API
# -------------------------------
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

# -------------------------------
# 3. CUSTOM CSS (FINAL COLOR FIXES)
# -------------------------------
st.markdown("""
    <style>
    /* 1. Main Background - Dark */
    .stApp {
        background: linear-gradient(to bottom, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* 2. Global Text - Default to White */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: white;
    }

    /* 3. Movie Cards - Glass Effect */
    div[data-testid="column"] {
        background: rgba(0, 0, 0, 0.25);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        transition: transform 0.2s;
    }
    div[data-testid="column"]:hover {
        transform: translateY(-5px);
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255,255,255,0.3);
    }

    /* 4. Select Box Input Field (The box you click) */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* 5. SEARCH SUGGESTIONS DROP-DOWN (THE FIX) */
    /* Target the Popup Container */
    div[data-baseweb="popover"] {
        background-color: white !important;
    }

    /* NUCLEAR OPTION: Force EVERY element inside the popup to be BLACK */
    div[data-baseweb="popover"] * {
        color: black !important;
        font-weight: bold;
    }

    /* 6. BUTTONS: NEXT / PREVIOUS (Standard Buttons) */
    /* Force text to be BLACK on White Background */
    .stButton > button {
        background-color: white !important;
        color: black !important; 
        border: none !important;
        font-weight: bold !important;
    }

    /* 7. BUTTONS: PRIMARY ("Show Recommendation") */
    /* Override the rule above for Red buttons -> Keep text WHITE */
    .stButton > button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important; 
    }
    /* Ensure hover state stays white */
    .stButton > button[kind="primary"]:hover {
        color: white !important;
    }
    /* Ensure all text inside primary button is white */
    .stButton > button[kind="primary"] * {
        color: white !important;
    }

    /* 8. LINK BUTTONS (Info / Trailer / Find to Watch) */

    /* White Link Buttons (Info/Trailer) -> Black Text */
    div[data-testid="stLinkButton"] > a {
        background-color: white !important;
    }
    div[data-testid="stLinkButton"] > a p {
        color: black !important;
        font-weight: 700 !important;
    }

    /* Red Link Button (Find to Watch) -> White Text */
    div[data-testid="stLinkButton"] > a[kind="primary"] {
        background-color: #ff4b4b !important;
    }
    div[data-testid="stLinkButton"] > a[kind="primary"] p {
        color: white !important;
    }

    </style>
""", unsafe_allow_html=True)


# -------------------------------
# 4. LOAD DATA
# -------------------------------
@st.cache_data
def load_movies():
    return pickle.load(open('movie_list.pkl', 'rb'))


@st.cache_resource
def load_similarity():
    return pickle.load(open('similarity.pkl', 'rb'))


movies = load_movies()
similarity = load_similarity()


# -------------------------------
# 5. FAST DATA FETCHING
# -------------------------------
def get_details_single(movie_input):
    """Worker function to fetch details for ONE movie."""
    title = ""
    poster = PLACEHOLDER
    rating = 0
    tmdb_id = None
    imdb_id = None

    try:
        if isinstance(movie_input, dict):
            title = movie_input.get("title")
            tmdb_id = movie_input.get("id")
            poster_path = movie_input.get("poster_path")
            poster = POSTER_BASE + poster_path if poster_path else PLACEHOLDER
            rating = movie_input.get("vote_average", 0)
        else:
            title = movie_input
            search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
            r = requests.get(search_url, timeout=2).json()
            results = r.get("results", [])

            target = None
            for m in results:
                if m["title"].lower() == title.lower():
                    target = m
                    break
            if not target and results:
                target = results[0]

            if target:
                tmdb_id = target.get("id")
                poster_path = target.get("poster_path")
                poster = POSTER_BASE + poster_path if poster_path else PLACEHOLDER
                rating = target.get("vote_average", 0)

        if tmdb_id:
            ext_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids?api_key={TMDB_API_KEY}"
            ext_data = requests.get(ext_url, timeout=1).json()
            imdb_id = ext_data.get("imdb_id")

    except Exception:
        pass

    return {
        "title": title,
        "poster": poster,
        "rating": rating,
        "tmdb_id": tmdb_id,
        "imdb_id": imdb_id
    }


@st.cache_data(show_spinner=False)
def fetch_batch_details(movie_list):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(get_details_single, movie_list))
    return results


# -------------------------------
# 6. HELPER: LINKS GENERATOR
# -------------------------------
def get_links(title, tmdb_id, imdb_id):
    """Generates the Watch/Trailer/Info links"""
    detail_link = f"https://www.themoviedb.org/movie/{tmdb_id}" if tmdb_id else "#"

    if imdb_id:
        trailer_link = f"https://www.imdb.com/title/{imdb_id}/"
    else:
        trailer_link = f"https://www.imdb.com/find?q={title}"

    watch_query = title.replace(" ", "+")
    watch_link = f"https://www.google.com/search?q=watch+{watch_query}+online+free"

    return detail_link, trailer_link, watch_link


# -------------------------------
# 7. RECOMMEND ENGINE
# -------------------------------
def recommend(movie_name):
    try:
        idx = movies[movies['title'] == movie_name].index[0]
        distances = sorted(
            enumerate(similarity[idx]),
            key=lambda x: x[1],
            reverse=True
        )[1:6]

        titles = [movies.iloc[i[0]].title for i in distances]
        return titles
    except IndexError:
        return []


# -------------------------------
# 8. RENDER UI CARDS
# -------------------------------
def render_cards_efficiently(data_input):
    processed_data = fetch_batch_details(data_input)

    cols = st.columns(5)
    for i, item in enumerate(processed_data):
        with cols[i % 5]:
            title = item['title']
            poster = item['poster']
            rating = item['rating']
            tmdb_id = item['tmdb_id']
            imdb_id = item['imdb_id']

            link_detail, link_trailer, link_watch = get_links(title, tmdb_id, imdb_id)

            st.image(poster, use_container_width=True)
            st.markdown(f"**{title}**")
            st.caption(f"⭐ {rating:.1f}/10")

            c1, c2 = st.columns(2)
            with c1:
                # Secondary (Info) -> Black Text
                st.link_button("📄 Info", link_detail, use_container_width=True)
            with c2:
                # Secondary (Trailer) -> Black Text
                st.link_button("🎬 Trailer", link_trailer, use_container_width=True)

            # Primary (Find to Watch) -> White Text
            st.link_button("▶️ Find to Watch", link_watch, use_container_width=True, type="primary")


# -------------------------------
# 9. MAIN APP
# -------------------------------
st.title("🎬 Movie Recommendation System")

tab1, tab2, tab3 = st.tabs(["🔍 Recommendations", "🎭 Browse Genres", "🏆 Top 250"])

# --- TAB 1: RECOMMENDATIONS ---
with tab1:
    st.subheader("Get Recommendations")

    if movies is not None:
        selected_movie = st.selectbox(
            "Select a movie",
            movies['title'].values
        )

        if st.button("Show Recommendation", type="primary"):
            titles = recommend(selected_movie)
            if not titles:
                st.error("Movie not found in database.")
            else:
                st.write(f"### Movies similar to **{selected_movie}**:")
                render_cards_efficiently(titles)
    else:
        st.error("Movie data not found.")

# --- TAB 2: GENRES ---
with tab2:
    st.subheader("Browse by Genre")


    @st.cache_data
    def get_genres():
        return requests.get(f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}").json().get(
            "genres", [])


    genres = get_genres()
    if genres:
        g_names = [g['name'] for g in genres]
        sel_genre = st.selectbox("Choose Genre", g_names)

        if sel_genre:
            gid = next(g['id'] for g in genres if g['name'] == sel_genre)
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={gid}&sort_by=popularity.desc&vote_count.gte=300"
            data = requests.get(url).json().get("results", [])[:10]
            render_cards_efficiently(data)

# --- TAB 3: TOP 250 ---
with tab3:
    st.subheader("Top Rated Movies")
    if 'top_page' not in st.session_state: st.session_state.top_page = 1

    # Buttons for Pagination (Now Black Text)
    c1, c2, c3 = st.columns([1, 8, 1])
    with c1:
        if st.button("Prev"):
            if st.session_state.top_page > 1: st.session_state.top_page -= 1; st.rerun()
    with c3:
        if st.button("Next"): st.session_state.top_page += 1; st.rerun()
    with c2:
        st.markdown(f"<center>Page {st.session_state.top_page}</center>", unsafe_allow_html=True)

    url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={TMDB_API_KEY}&page={st.session_state.top_page}"
    data = requests.get(url).json().get("results", [])
    render_cards_efficiently(data)

# -------------------------------
# 10. FOOTER SPACER
# -------------------------------
st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)