import re
import streamlit as st

# -------------------------
# Page Config (MUST be the first Streamlit command in the script)
# -------------------------
st.set_page_config(
    page_title="Hybrid Cricket Search Engine",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

from modules.pipeline import CricketRAGPipeline

# -------------------------
# Initialize pipeline
# -------------------------
@st.cache_resource
def load_pipeline():
    return CricketRAGPipeline()

pipeline = load_pipeline()

# -------------------------
# Custom CSS (dark professional theme, adapts to light/dark)
# -------------------------
st.markdown("""
<style>

/* =========================================================
   KEYFRAMES
   ========================================================= */
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes underlineGrow {
    from { width: 0%; }
    to   { width: 140px; }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 0 rgba(79,172,254,0.0); }
    50%      { box-shadow: 0 0 16px rgba(79,172,254,0.55); }
}
@keyframes badgeShine {
    0%   { transform: translateX(-120%) rotate(20deg); }
    100% { transform: translateX(220%) rotate(20deg); }
}
@keyframes spinnerBounce {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-6px); }
}

/* =========================================================
   Global
   ========================================================= */
.stApp {
    background: linear-gradient(180deg, #0e1117 0%, #12151c 100%);
}

/* =========================================================
   Title
   ========================================================= */
.big-title{
    text-align:center;
    font-size:46px;
    font-weight:800;
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 50%, #4facfe 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px;
    letter-spacing: 0.5px;
    animation: fadeInDown 0.6s ease-out, gradientShift 6s ease-in-out infinite;
}
.subtitle{
    text-align:center;
    color:#9aa4b2;
    font-size:17px;
    font-weight:500;
    margin-top: 4px;
    margin-bottom: 6px;
    animation: fadeInDown 0.8s ease-out;
}
.title-underline{
    display:block;
    margin: 8px auto 14px auto;
    height: 3px;
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    border-radius: 4px;
    animation: underlineGrow 1s ease-out forwards;
}

/* =========================================================
   Search bar
   ========================================================= */
div[data-testid="stTextInput"] input {
    border-radius: 10px !important;
    border: 1px solid rgba(79,172,254,0.35) !important;
    padding: 12px 14px !important;
    font-size: 16px !important;
    transition: box-shadow 0.25s ease, border-color 0.25s ease;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(79,172,254,0.9) !important;
    box-shadow: 0 0 0 3px rgba(79,172,254,0.18) !important;
}

div.stButton > button {
    background: linear-gradient(90deg, #1565C0 0%, #1E88E5 100%);
    color: white;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 10px 28px;
    font-size: 16px;
    width: 100%;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 14px rgba(21,101,192,0.35);
}
div.stButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 22px rgba(30,136,229,0.55);
    color: white;
}
div.stButton > button:active {
    transform: translateY(0) scale(0.98);
}

/* =========================================================
   Column headers
   ========================================================= */
.col-header {
    text-align:center;
    font-size: 20px;
    font-weight: 700;
    padding: 10px 0;
    border-radius: 10px;
    margin-bottom: 14px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    animation: fadeInDown 0.5s ease-out;
}

/* =========================================================
   Result Cards
   ========================================================= */
.result-card{
    position: relative;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 14px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.09);
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    opacity: 0;
    animation: fadeInUp 0.5s ease-out forwards;
}
.result-card:hover{
    border-color: rgba(79,172,254,0.45);
    box-shadow: 0 10px 26px rgba(79,172,254,0.22);
    transform: translateY(-4px) scale(1.01);
}
.top-pick{
    border-color: rgba(255,193,7,0.55) !important;
    animation: fadeInUp 0.5s ease-out forwards, pulseGlow 2.4s ease-in-out infinite;
}
.top-pick-badge{
    position: absolute;
    top: -10px;
    right: 14px;
    overflow: hidden;
    background: linear-gradient(90deg, #f7b733, #fc4a1a);
    color: #1a1a1a;
    font-size: 11px;
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 20px;
    box-shadow: 0 3px 10px rgba(247,183,51,0.4);
}
.top-pick-badge::after{
    content: "";
    position: absolute;
    top: 0; left: 0;
    width: 40%;
    height: 100%;
    background: rgba(255,255,255,0.55);
    animation: badgeShine 2.6s ease-in-out infinite;
}
.player-name{
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 8px;
    color: #4facfe;
}
.field-row{
    font-size: 14px;
    margin-bottom: 4px;
    color: inherit;
    opacity: 0.92;
}
.field-label{
    font-weight: 600;
    opacity: 0.75;
}

/* =========================================================
   AI Answer box
   ========================================================= */
.answer-box{
    border-radius: 16px;
    padding: 22px 26px;
    background: linear-gradient(135deg, rgba(21,101,192,0.15) 0%, rgba(0,242,254,0.08) 100%);
    border: 1px solid rgba(79,172,254,0.35);
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    font-size: 16px;
    line-height: 1.6;
    opacity: 0;
    animation: fadeInUp 0.6s ease-out forwards;
}

/* =========================================================
   Sidebar
   ========================================================= */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(255,255,255,0.08);
}
.sidebar-title{
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 6px;
    color: #4facfe;
}
.example-chip{
    display:block;
    padding: 8px 12px;
    margin-bottom: 6px;
    border-radius: 8px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    font-size: 14px;
    cursor: pointer;
    transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
    opacity: 0;
    animation: fadeInUp 0.4s ease-out forwards;
}
.example-chip:hover{
    background: rgba(79,172,254,0.10);
    border-color: rgba(79,172,254,0.4);
    transform: translateX(4px);
}
.tech-chip{
    padding: 6px 0;
    font-size: 14px;
    opacity: 0;
    animation: fadeIn 0.5s ease-out forwards;
}

.no-results{
    text-align:center;
    padding: 20px;
    opacity: 0.6;
    font-size: 14px;
    animation: fadeIn 0.4s ease-out;
}

/* =========================================================
   Spinner text (built-in Streamlit spinner icon already animates;
   this nudges the caption text for a subtle "searching" feel)
   ========================================================= */
div[data-testid="stSpinner"] p {
    animation: spinnerBounce 1s ease-in-out infinite;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Title
# -------------------------
st.markdown('<p class="big-title">🏏 Hybrid Cricket Search Engine</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">BM25 + FAISS + Reciprocal Rank Fusion + Groq</p>', unsafe_allow_html=True)
st.markdown('<span class="title-underline"></span>', unsafe_allow_html=True)

st.write("")

# -------------------------
# Search bar
# -------------------------
search_col1, search_col2 = st.columns([5, 1])

with search_col1:
    query = st.text_input(
        "Search",
        placeholder="Ask about any cricketer...",
        label_visibility="collapsed"
    )

with search_col2:
    search = st.button("🔍 Search")

st.divider()


# -------------------------
# Helper: parse a document string into clean fields
# -------------------------
def parse_document(doc_text: str) -> dict:
    """
    Parses a document string of the form 'Key: Value' per line
    into a dictionary, mapping common field name variants
    to a standard set of keys.
    """
    fields = {}
    for line in doc_text.split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip().lower()] = value.strip()

    def find(*keys, default="Not available"):
        for k in keys:
            if k in fields and fields[k]:
                return fields[k]
        return default

    return {
        "name": find("name", "player", "player name", default="Unknown Player"),
        "country": find("country", "nation", "nationality"),
        "role": find("role", "position", "player role"),
        "style": find("batting/bowling style", "batting style", "bowling style",
                       "style", "batting bowling style"),
        "era": find("era", "years active", "period", "career span"),
    }


def render_card(doc_text: str, delay: float = 0.0, is_top_pick: bool = False):
    info = parse_document(doc_text)
    card_class = "result-card top-pick" if is_top_pick else "result-card"
    badge_html = '<div class="top-pick-badge">🏆 Top Pick</div>' if is_top_pick else ""

    # IMPORTANT: build this as ONE line with no embedded newlines/indentation.
    # Streamlit's markdown renderer treats any line starting with 4+ spaces
    # as an "indented code block" and shows it as literal text instead of
    # parsing it as HTML -- even with unsafe_allow_html=True. Multi-line
    # f-strings with indented parts (like the previous version of this
    # function) hit that exact bug intermittently.
    html = (
        f'<div class="{card_class}" style="animation-delay:{delay:.2f}s">'
        f'{badge_html}'
        f'<div class="player-name">🏏 {info["name"]}</div>'
        f'<div class="field-row"><span class="field-label">🌍 Country:</span> {info["country"]}</div>'
        f'<div class="field-row"><span class="field-label">🎯 Role:</span> {info["role"]}</div>'
        f'<div class="field-row"><span class="field-label">🏏 Style:</span> {info["style"]}</div>'
        f'<div class="field-row"><span class="field-label">📅 Era:</span> {info["era"]}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_column(title_html: str, indices, documents, max_items=None, highlight_first=False):
    st.markdown(f'<div class="col-header">{title_html}</div>', unsafe_allow_html=True)
    items = indices if max_items is None else indices[:max_items]
    if not items:
        st.markdown('<div class="no-results">No results found</div>', unsafe_allow_html=True)
        return
    for position, idx in enumerate(items):
        render_card(
            documents[idx],
            delay=position * 0.08,
            is_top_pick=(highlight_first and position == 0)
        )


# -------------------------
# Search Logic
# -------------------------
if search and query:

    with st.spinner("🔎 Searching across semantic, BM25 and hybrid indexes..."):
        semantic, bm25, hybrid, documents = pipeline.search(query)
        answer = pipeline.answer(query)

    st.divider()

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        render_column("🔵 Semantic Search", semantic, documents)

    with col2:
        render_column("🟢 BM25 Search", bm25, documents)

    with col3:
        render_column("🟣 Hybrid Search", hybrid, documents, max_items=5, highlight_first=True)

    st.divider()

    st.markdown("### 🤖 AI Answer")
    st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

elif search and not query:
    st.warning("⚠️ Please enter a query before searching.")


# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">📌 Example Queries</div>', unsafe_allow_html=True)

    examples = [
        "Waqar Younis",
        "Greatest Australian batsman",
        "Left arm fast bowlers",
        "Indian wicket keeper",
        "Pakistan fast bowlers",
        "Best leg spinner",
    ]

    for i, ex in enumerate(examples):
        st.markdown(
            f'<div class="example-chip" style="animation-delay:{i * 0.06:.2f}s">• {ex}</div>',
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown('<div class="sidebar-title">⚙️ Technology Stack</div>', unsafe_allow_html=True)

    tech = [
        "Streamlit",
        "FAISS",
        "BM25",
        "Reciprocal Rank Fusion (RRF)",
        "Sentence Transformers",
        "Groq Llama 3.3",
    ]

    for i, t in enumerate(tech):
        st.markdown(
            f'<div class="tech-chip" style="animation-delay:{i * 0.06:.2f}s">✔ {t}</div>',
            unsafe_allow_html=True
        )