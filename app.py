"""
TakeOne - Semantic Footage Search Engine
Main Streamlit Application

Professional Modern UI with Material Design
"""
import streamlit as st
import tempfile
import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# Suppress progress bars from libraries (works with all versions)
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env vars
load_dotenv()

# Page config must be first
st.set_page_config(
    page_title="TakeOne - AI Video Search",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS & THEME ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Cinema-Inspired Color Palette */
    :root {
        /* Primary Colors */
        --bg-primary: #0D1117;        /* Deep Slate - Professional dark-room aesthetic */
        --bg-secondary: #161B22;      /* Charcoal - Cards and UI elements */
        --bg-hover: #21262D;          /* Slightly lighter for hover states */
        
        /* Accent Colors */
        --accent-cyan: #00E5FF;       /* Electric Cyan - AI Glow, high-energy */
        --accent-rust: #E64A19;       /* Cinema Rust - Action, Rec/Play buttons */
        --accent-cyan-dim: #00B8D4;   /* Dimmed cyan for subtle effects */
        --accent-rust-dim: #D84315;   /* Dimmed rust for hover states */
        
        /* Text Colors */
        --text-primary: #F0F6FC;      /* High-Key White - Clear readability */
        --text-secondary: #8B949E;    /* Muted gray for secondary text */
        --text-tertiary: #6E7681;     /* Even more muted for hints */
        
        /* Semantic Colors */
        --success: #00E5FF;           /* Use cyan for success (AI theme) */
        --warning: #E64A19;           /* Use rust for warnings/actions */
        --error: #F85149;             /* Bright red for errors */
        
        /* Borders & Dividers */
        --border: #30363D;            /* Subtle borders */
        --border-bright: #484F58;     /* Brighter borders for focus */
    }

    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: var(--bg-primary);
        color: var(--text-primary);
    }

    /* Remove default padding */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* --- SIDEBAR --- */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        padding: 0.5rem 0;
    }
    
    /* Sidebar navigation buttons */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: transparent;
        color: var(--text-secondary);
        border: 1px solid transparent;
        text-align: left;
        padding: 0.875rem 1.25rem;
        font-size: 0.95rem;
        font-weight: 500;
        border-radius: 0.75rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        margin: 0.25rem 0;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: var(--bg-hover);
        color: var(--text-primary);
        border-color: var(--accent-cyan);
        transform: translateX(2px);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.15);
    }
    
    section[data-testid="stSidebar"] .stButton > button:active {
        transform: translateX(0);
    }

    /* --- HERO SECTION --- */
    .hero-container {
        text-align: center;
        padding: 2rem 0 3rem 0;
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-rust) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
        line-height: 1.1;
        text-shadow: 0 0 40px rgba(0, 229, 255, 0.3);
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        font-weight: 400;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }

    /* --- CARDS --- */
    .card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.2), 0 20px 25px -5px rgba(0, 0, 0, 0.4);
        border-color: var(--accent-cyan);
    }

    /* --- BUTTONS --- */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-cyan-dim) 100%);
        color: var(--bg-primary);
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.5);
        background: var(--accent-cyan);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary button */
    .stButton > button[kind="secondary"] {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        color: var(--text-primary);
        box-shadow: none;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--bg-hover);
        border-color: var(--border-bright);
    }

    /* --- BADGES --- */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.375rem 0.875rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s;
    }
    
    .badge-score {
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-cyan-dim) 100%);
        color: var(--bg-primary);
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
    }
    
    .badge-mood {
        background: rgba(0, 229, 255, 0.15);
        color: var(--accent-cyan);
        border: 1px solid rgba(0, 229, 255, 0.3);
    }
    
    .badge-type {
        background: rgba(230, 74, 25, 0.15);
        color: var(--accent-rust);
        border: 1px solid rgba(230, 74, 25, 0.3);
    }
    
    .badge:hover {
        transform: scale(1.05);
    }

    /* --- TAGS --- */
    .tag {
        display: inline-block;
        font-size: 0.75rem;
        color: var(--text-secondary);
        background: var(--bg-primary);
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        margin: 0.25rem;
        border: 1px solid var(--border);
        transition: all 0.2s;
    }
    
    .tag:hover {
        background: var(--bg-hover);
        color: var(--accent-cyan);
        border-color: var(--accent-cyan);
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.2);
    }

    /* --- INPUT FIELDS --- */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
        padding: 0.875rem 1.25rem;
        font-size: 1rem;
        transition: all 0.2s;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-cyan);
        box-shadow: 0 0 0 3px rgba(0, 229, 255, 0.1);
        background: var(--bg-primary);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-secondary);
    }

    /* --- SELECT BOXES --- */
    .stSelectbox > div > div {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
    }

    /* --- PROGRESS BARS --- */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-cyan) 0%, var(--accent-rust) 100%);
        border-radius: 9999px;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
    }

    /* --- EXPANDER --- */
    .streamlit-expanderHeader {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-hover);
        border-color: var(--accent-cyan);
    }

    /* --- METRICS --- */
    .stMetric {
        background: var(--bg-secondary);
        padding: 1rem;
        border-radius: 0.75rem;
        border: 1px solid var(--border);
    }
    
    .stMetric label {
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--accent-cyan);
        font-size: 1.875rem;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(0, 229, 255, 0.3);
    }

    /* --- VIDEO PLAYER --- */
    .stVideo {
        border-radius: 0.75rem;
        overflow: hidden;
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.2);
        border: 1px solid var(--border);
    }

    /* --- ALERTS --- */
    .stAlert {
        border-radius: 0.75rem;
        border: none;
        padding: 1rem 1.25rem;
    }
    
    /* Success */
    [data-testid="stAlert"][data-baseweb="notification"] > div:first-child {
        background: rgba(0, 229, 255, 0.1);
        border-left: 4px solid var(--success);
    }
    
    /* Info */
    .stInfo {
        background: rgba(0, 229, 255, 0.1);
        border-left: 4px solid var(--accent-cyan);
    }
    
    /* Warning */
    .stWarning {
        background: rgba(230, 74, 25, 0.1);
        border-left: 4px solid var(--warning);
    }
    
    /* Error */
    .stError {
        background: rgba(248, 81, 73, 0.1);
        border-left: 4px solid var(--error);
    }

    /* --- ICONS --- */
    .icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 0.75rem;
        margin-right: 0.75rem;
        font-size: 1.25rem;
    }
    
    .icon-primary {
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-cyan-dim) 100%);
        color: var(--bg-primary);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.3);
    }
    
    .icon-success {
        background: rgba(0, 229, 255, 0.15);
        color: var(--success);
    }
    
    .icon-warning {
        background: rgba(230, 74, 25, 0.15);
        color: var(--warning);
    }

    /* --- ANIMATIONS --- */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    .pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    /* --- SCROLLBAR --- */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }

    /* --- LOADING SPINNER --- */
    .stSpinner > div {
        border-color: var(--primary) transparent transparent transparent;
    }

    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--bg-card);
        padding: 0.5rem;
        border-radius: 0.75rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: var(--text-secondary);
        transition: all 0.2s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-hover);
        color: var(--text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
    }

    /* --- FILE UPLOADER --- */
    .stFileUploader {
        background: var(--bg-card);
        border: 2px dashed var(--border);
        border-radius: 0.75rem;
        padding: 2rem;
        transition: all 0.2s;
    }
    
    .stFileUploader:hover {
        border-color: var(--primary);
        background: var(--bg-hover);
    }

    /* --- DIVIDER --- */
    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


# --- SESSION STATE ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Home"
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
if "search_engine" not in st.session_state:
    st.session_state.search_engine = None
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "stats" not in st.session_state:
    st.session_state.stats = {"total_scenes": 0, "unique_videos": 0}
if "processing" not in st.session_state:
    st.session_state.processing = False
if "show_library_manager" not in st.session_state:
    st.session_state.show_library_manager = False

# Legacy support
if "indexed_clips" not in st.session_state: st.session_state.indexed_clips = 0
if "embedder" not in st.session_state: st.session_state.embedder = None
if "vector_search" not in st.session_state: st.session_state.vector_search = None


# --- HELPER FUNCTIONS ---
def check_api_key():
    return bool(os.environ.get("GEMINI_API_KEY"))

def format_time(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"

@st.cache_resource(show_spinner=False)
def load_pipeline(gemini_model: str = "gemini-2.5-flash"):
    from ingestion.pipeline import TakeOnePipeline
    import torch
    
    # Check GPU availability
    use_gpu = torch.cuda.is_available()
    if use_gpu:
        logger.info("GPU detected - enabling GPU acceleration")
    else:
        logger.info("No GPU detected - using CPU")
    
    return TakeOnePipeline(
        output_dir="./output",
        chroma_dir="./chroma_db",
        gemini_model=gemini_model
    )

@st.cache_resource(show_spinner=False)
def load_legacy_models():
    """Load legacy CLIP models (optional)."""
    try:
        from ingestion.embedder import CLIPEmbedder
        from search.vector_search import VectorSearch
        return CLIPEmbedder(), VectorSearch(persist_dir="./chroma_db")
    except ImportError as e:
        st.error(f"Legacy CLIP models not available: {e}")
        st.info("Please use Gemini mode instead, or install required packages.")
        return None, None


# --- VIEW COMPONENTS ---

def render_sidebar():
    with st.sidebar:
        # Logo and title with TakeOne clapperboard icon
        st.markdown("""
        <div style="display: flex; align-items: center; padding: 1rem 0 1.5rem 0; gap: 0.75rem;">
            <svg width="48" height="48" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" style="flex-shrink: 0;">
                <defs>
                    <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#00E5FF;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#E64A19;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <path d="M60.131 21.423H35.659l24.279-2.656l1.878-.206l-.224-1.876l-1.53-12.849l-.183-1.524l-1.527-.12l-2.22-.173L55.888 2l-.24.044l-51.923 9.565L2 11.927l.207 1.744l.404 3.397v16.381l.477.029v16.524l1.473.32l52.982 11.516l.746.162l.646-.408l2.191-1.383l.874-.55V21.423h-1.869M55.985 3.884l2.22.174l1.37 11.494l-1.739-2.536l-6.791-8.222l4.94-.91M42.58 6.354l9.299 11.413l-8.489.929l-8.431-10.938l7.621-1.404M28.059 9.029l7.692 10.503l-6.908.756l-7.046-10.105l6.262-1.154m-11.981 2.206l6.482 9.74l-5.731.626l-5.988-9.401l5.237-.965m-5.461 15.844l-2.77-3.601l.096-.184h4.72l-2.046 3.785m1.064 3.165c0 .55-.393.973-.874.946c-.479-.027-.863-.488-.863-1.029s.385-.965.863-.945c.481.018.874.479.874 1.028M4.516 17.246l-.453-3.797l1.961-.361l5.554 9.089l-1.146.125l-2.766.303l-.588-1l-2.562-4.359M6.474 22.8c0 .525-.359.952-.799.957c-.437.002-.787-.414-.787-.931c0-.519.351-.945.787-.957c.439-.011.799.406.799.931m-.799 6.213c.439.018.799.457.799.982c0 .525-.359.929-.799.903c-.437-.024-.787-.463-.787-.98c0-.518.35-.922.787-.905m54.456 15.454l-1.867.482l-43.419-5.381v4.129l43.419 6.875l1.867-.797v1.365l-1.867.814l-53.307-8.87v-.948l8.956 1.414v-4.098l-8.956-1.11v-.948l53.307 6.174l1.867-.468v1.367m0-8.235l-1.867.311l-53.307-3.89v-.923l9.713.62l-1.161-1.51l4.27-7.546h5.096l-5.473 9.183l5.727.369l6.006-9.552h6.882l-6.614 9.957l6.905.445l7.319-10.402h8.458L43.94 34.189l8.485.547l5.937-7.888l1.769-3.007v12.391" fill="url(#logoGradient)"/>
            </svg>
            <div style="flex: 1;">
                <div style="font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #00E5FF 0%, #E64A19 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2; filter: drop-shadow(0 0 10px rgba(0, 229, 255, 0.3));">TakeOne</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.125rem;">AI Video Search</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation buttons with custom icons
        st.markdown('<div style="font-size: 0.7rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">Navigation</div>', unsafe_allow_html=True)
        
        home_active = st.session_state.active_tab == "Home"
        library_active = st.session_state.active_tab == "Library"
        
        # Home button with smiley icon
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("""
            <div style="display: flex; align-items: center; justify-content: center; height: 38px;">
                <svg width="16" height="16" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                    <path d="M35 27.869A7.994 7.994 0 0 1 28 32h14a7.994 7.994 0 0 1-7-4.131" fill="currentColor"></path>
                    <circle cx="28" cy="24" r="3" fill="currentColor"></circle>
                    <circle cx="42" cy="24" r="3" fill="currentColor"></circle>
                    <path d="M32 2C15.432 2 2 15.432 2 32s13.432 30 30 30s30-13.432 30-30S48.568 2 32 2m14 30c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H23c-1.1 0-2-.9-2-2v-.5L16 48V32l5 2.5V34c0-1.1.9-2 2-2h5a8 8 0 0 1 0-16a7.994 7.994 0 0 1 7 4.131A7.994 7.994 0 0 1 42 16a8 8 0 0 1 0 16h4" fill="currentColor"></path>
                </svg>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("Home", key="nav_home", use_container_width=True, type="primary" if home_active else "secondary"):
                st.session_state.active_tab = "Home"
                st.rerun()
        
        # Library button with book icon
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("""
            <div style="display: flex; align-items: center; justify-content: center; height: 38px;">
                <svg width="16" height="16" viewBox="-0.5 0 21 21" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20.9999958,3.25 L20.9999958,19.5018874 C14.9999958,19.1144138 11.9999958,19.6137847 11.9999958,21 C11.9999958,21 11.9999958,9.95538748 11.9999958,5.61908 C11.9999958,3.25632105 14.9999958,2.46662772 20.9999958,3.25 Z M2.99999577,3.25 L2.99999577,19.5018874 L3.74965625,19.4572404 L3.74965625,19.4572404 L4.4667228,19.4222285 L4.4667228,19.4222285 L5.15119541,19.3968519 L5.15119541,19.3968519 L5.80307409,19.3811106 C5.90900437,19.37929 6.01357658,19.3778708 6.1167907,19.3768531 L6.71977848,19.3755647 L6.71977848,19.3755647 L7.29017232,19.3839114 L7.29017232,19.3839114 L7.82797223,19.4018935 L7.82797223,19.4018935 L8.33317821,19.4295108 C8.49614788,19.4403224 8.65368522,19.4527399 8.80579025,19.4667633 L9.24580836,19.5136511 C11.0113131,19.7290903 11.9280175,20.1954475 11.9959215,20.9127226 L11.9999958,20.9661174 L11.9999958,20.9661174 L11.9999958,5.61908 L11.9999958,5.61908 C11.9999958,3.69029719 10.0008288,2.809788 6.00249473,2.97755244 L5.38775087,3.01057916 C5.28279461,3.01739396 5.17658886,3.02486392 5.06913363,3.03298906 L4.40940852,3.08960194 C4.18450223,3.11109358 3.95459802,3.13520591 3.7196959,3.16193892 L2.99999577,3.25 L2.99999577,3.25 Z" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("Library", key="nav_library", use_container_width=True, type="primary" if library_active else "secondary"):
                st.session_state.active_tab = "Library"
                st.rerun()
        
        st.markdown("---")
        
        # Stats section with icon
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <svg width="16" height="16" viewBox="0 0 1800 1800" xmlns="http://www.w3.org/2000/svg" style="flex-shrink: 0;">
                <path fill="currentColor" d="M223.333,1785.167H82.119c-44.068,0-79.922-36.348-79.922-81.023V761.958c0-44.678,35.854-81.024,79.922-81.024h141.214c44.068,0,79.921,36.346,79.921,81.024v942.185C303.254,1748.819,267.401,1785.167,223.333,1785.167z M708.974,1785.167H567.755c-44.066,0-79.917-38.839-79.917-86.578V651.512c0-47.74,35.852-86.579,79.917-86.579h141.218c44.066,0,79.917,38.839,79.917,86.579v1047.077C788.891,1746.328,753.04,1785.167,708.974,1785.167z M1194.621,1785.167h-141.21c-44.072,0-79.926-31.604-79.926-70.452V972.037c0-38.848,35.854-70.453,79.926-70.453h141.21c44.072,0,79.926,31.605,79.926,70.453v742.678C1274.547,1753.563,1238.693,1785.167,1194.621,1785.167z M1680.271,1785.167h-141.219c-44.067,0-79.917-38.839-79.917-86.578V651.512c0-47.74,35.85-86.579,79.917-86.579h141.219c44.072,0,79.926,38.839,79.926,86.579v1047.077C1760.196,1746.328,1724.343,1785.167,1680.271,1785.167z"/>
            </svg>
            <div style="font-size: 0.7rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em;">Statistics</div>
        </div>
        """, unsafe_allow_html=True)
        
        if check_api_key() and st.session_state.pipeline:
            stats = st.session_state.stats
            
            # Scenes metric with icon
            st.markdown(f"""
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 0.75rem; margin-bottom: 0.75rem; border: 1px solid var(--border);">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <svg width="14" height="14" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" style="flex-shrink: 0;">
                        <path stroke="currentColor" stroke-width="2" fill="none" d="M3.945,3 L16.3335682,3 C16.5841978,3 16.8245622,3.09956232 17.0017841,3.2767842 L20.7232158,7.4482158 C20.9004377,7.62543768 21,7.86580202 21,8.1164316 L21,20.055 C21,20.5769091 20.5769091,21 20.055,21 L3.945,21 C3.42309091,21 3,20.5769091 3,20.055 L3,3.945 C3,3.42309091 3.42309091,3 3.945,3 Z M12,16.5 C13.3807119,16.5 14.5,15.3807119 14.5,14 C14.5,12.6192881 13.3807119,11.5 12,11.5 C10.6192881,11.5 9.5,12.6192881 9.5,14 C9.5,15.3807119 10.6192881,16.5 12,16.5 Z"/>
                    </svg>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">Indexed Content</div>
                </div>
                <div style="font-size: 1.75rem; font-weight: 700; color: var(--accent-cyan); text-shadow: 0 0 15px rgba(0, 229, 255, 0.3);">{stats.get("total_scenes", 0):,}</div>
                <div style="font-size: 0.7rem; color: var(--text-tertiary); margin-top: 0.25rem;">Total Scenes</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Videos metric
            st.markdown(f"""
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 0.75rem; border: 1px solid var(--border);">
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Videos Indexed</div>
                <div style="font-size: 1.75rem; font-weight: 700; color: var(--text-primary);">{stats.get("unique_videos", 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        elif st.session_state.embedder:
            st.metric("Clips Indexed", st.session_state.indexed_clips)
        else:
            st.markdown("""
            <div style="background: rgba(230, 74, 25, 0.1); padding: 1rem; border-radius: 0.75rem; border-left: 4px solid var(--warning); text-align: center;">
                <div style="font-size: 0.875rem; color: var(--warning); font-weight: 600;">System Offline</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">Initialize engine to start</div>
            </div>
            """, unsafe_allow_html=True)


def render_home():
    # Hero Section - Clean and professional with TakeOne branding
    st.markdown("""
    <div class="hero-container fade-in">
        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 2rem;">
            <svg width="80" height="80" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 1rem; filter: drop-shadow(0 0 8px rgba(0, 229, 255, 0.3));">
                <defs>
                    <linearGradient id="hero-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:#00E5FF;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#E64A19;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <path fill="url(#hero-gradient)" d="M60.131 21.423H35.659l24.279-2.656l1.878-.206l-.224-1.876l-1.53-12.849l-.183-1.524l-1.527-.12l-2.22-.173L55.888 2l-.24.044l-51.923 9.565L2 11.927l.207 1.744l.404 3.397v16.381l.477.029v16.524l1.473.32l52.982 11.516l.746.162l.646-.408l2.191-1.383l.874-.55V21.423h-1.869M55.985 3.884l2.22.174l1.37 11.494l-1.739-2.536l-6.791-8.222l4.94-.91M42.58 6.354l9.299 11.413l-8.489.929l-8.431-10.938l7.621-1.404M28.059 9.029l7.692 10.503l-6.908.756l-7.046-10.105l6.262-1.154m-11.981 2.206l6.482 9.74l-5.731.626l-5.988-9.401l5.237-.965m-5.461 15.844l-2.77-3.601l.096-.184h4.72l-2.046 3.785m1.064 3.165c0 .55-.393.973-.874.946c-.479-.027-.863-.488-.863-1.029s.385-.965.863-.945c.481.018.874.479.874 1.028M4.516 17.246l-.453-3.797l1.961-.361l5.554 9.089l-1.146.125l-2.766.303l-.588-1l-2.562-4.359M6.474 22.8c0 .525-.359.952-.799.957c-.437.002-.787-.414-.787-.931c0-.519.351-.945.787-.957c.439-.011.799.406.799.931m-.799 6.213c.439.018.799.457.799.982c0 .525-.359.929-.799.903c-.437-.024-.787-.463-.787-.98c0-.518.35-.922.787-.905m54.456 15.454l-1.867.482l-43.419-5.381v4.129l43.419 6.875l1.867-.797v1.365l-1.867.814l-53.307-8.87v-.948l8.956 1.414v-4.098l-8.956-1.11v-.948l53.307 6.174l1.867-.468v1.367m0-8.235l-1.867.311l-53.307-3.89v-.923l9.713.62l-1.161-1.51l4.27-7.546h5.096l-5.473 9.183l5.727.369l6.006-9.552h6.882l-6.614 9.957l6.905.445l7.319-10.402h8.458L43.94 34.189l8.485.547l5.937-7.888l1.769-3.007v12.391"/>
            </svg>
            <svg width="100%" height="80" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 0.5rem;">
                <defs>
                    <linearGradient id="text-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:#00E5FF;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#E64A19;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="48" font-weight="800" letter-spacing="4.8" fill="url(#text-gradient)" stroke="url(#text-gradient)" stroke-width="0.5">TakeOne</text>
            </svg>
        </div>
        <div style="font-size: 3rem; font-weight: 700; color: #F0F6FC; margin-bottom: 1rem; text-shadow: 0 0 20px rgba(0, 229, 255, 0.3);">Find the perfect shot.</div>
        <div class="hero-subtitle">AI-powered semantic search for your video footage</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Engine Status and Controls
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if check_api_key() and st.session_state.pipeline:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 0.75rem; border-left: 4px solid var(--success); display: flex; align-items: center;">
                <div style="width: 8px; height: 8px; background: var(--success); border-radius: 50%; margin-right: 0.75rem;"></div>
                <div>
                    <div style="font-weight: 600; color: var(--success);">Engine Online</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Ready to process and search</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.1); padding: 1rem; border-radius: 0.75rem; border-left: 4px solid var(--warning); display: flex; align-items: center;">
                <div style="width: 8px; height: 8px; background: var(--warning); border-radius: 50%; margin-right: 0.75rem;"></div>
                <div>
                    <div style="font-weight: 600; color: var(--warning);">Engine Offline</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Initialize to start using</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button("Initialize / Reload Engine", use_container_width=True, type="primary"):
            # Create a placeholder for status messages
            status_placeholder = st.empty()
            
            try:
                status_placeholder.info("Loading AI models...")
                pipeline = load_pipeline()
                
                status_placeholder.info("Initializing search engine...")
                st.session_state.pipeline = pipeline
                st.session_state.search_engine = pipeline.search_engine
                
                status_placeholder.info("Loading database statistics...")
                st.session_state.stats = pipeline.search_engine.get_stats()
                
                status_placeholder.success("Engine initialized successfully!")
                time.sleep(1)
                status_placeholder.empty()
                st.rerun()
            except Exception as e:
                status_placeholder.error(f"Failed to initialize: {e}")
                import traceback
                logger.error(traceback.format_exc())
    
    with col3:
        if st.session_state.search_results:
            if st.button("Clear Results", use_container_width=True, type="secondary"):
                st.session_state.search_results = []
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Process Section
    with st.expander("Quick Process Video", expanded=False):
        st.markdown("**Process a video directly from URL**")
        quick_url = st.text_input(
            "Video URL",
            placeholder="https://youtube.com/watch?v=... or paste any video link",
            key="quick_url",
            label_visibility="collapsed"
        )
        if st.button("Process Now", type="secondary", disabled=not quick_url):
            if check_api_key() and st.session_state.pipeline:
                process_from_url(quick_url, None, True)
            else:
                st.warning("Please initialize the engine first")
    
    # Search Bar Area
    st.markdown("### Search Your Footage")
    
    # Multilingual Support Badge
    st.markdown("""
    <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: linear-gradient(135deg, rgba(0, 229, 255, 0.15) 0%, rgba(230, 74, 25, 0.15) 100%); border-radius: 2rem; margin-bottom: 1rem; border: 1px solid rgba(0, 229, 255, 0.3);">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v1.99h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z" fill="currentColor" style="color: #00E5FF;"/>
        </svg>
        <span style="font-weight: 600; font-size: 0.875rem; color: #00E5FF;">Multilingual Support</span>
        <span style="font-size: 0.75rem; color: var(--text-secondary); padding-left: 0.5rem; border-left: 1px solid rgba(0, 229, 255, 0.3);">Type in any language - AI translates automatically</span>
    </div>
    """, unsafe_allow_html=True)
    
    col_search, col_opts = st.columns([3, 1])
    
    # Search Mode Selection
    st.markdown("### Search Mode")
    search_mode = st.radio(
        "Choose search type",
        ["Quick Search", "Script Sequence Search"],
        horizontal=True,
        help="Quick Search: Single query | Script Search: Multi-action sequence for video editing"
    )
    
    if search_mode == "Script Sequence Search":
        st.markdown("""
        <div style="background: rgba(0, 229, 255, 0.1); padding: 1rem; border-radius: 0.75rem; border-left: 4px solid var(--accent-cyan); margin-bottom: 1rem;">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">🎬 Script-to-Sequence Search</div>
            <div style="font-size: 0.875rem; color: var(--text-secondary);">
                Paste your script with multiple actions <strong>in any language</strong>. The system will:
                <br>• Translate/transliterate to English automatically
                <br>• Break it down into sequential actions with AI
                <br>• Enhance each query for better matches
                <br>• Return matching footage <strong>in order</strong> - perfect for video editing workflow!
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        script_text = st.text_area(
            "Paste your script here (any language supported)",
            placeholder="""Example (English):
A person walks down a busy city street, looking worried.
They stop and check their phone with a concerned expression.
Cut to a close-up of the phone screen showing a message.
The person starts running through the crowd.
They arrive at a building and rush inside.

उदाहरण (हिंदी):
एक व्यक्ति व्यस्त शहर की सड़क पर चिंतित दिख रहा है।
वे रुकते हैं और चिंतित चेहरे के साथ अपना फोन देखते हैं।""",
            height=200,
            help="Enter your script with multiple actions/scenes in ANY language. AI will translate and parse automatically."
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            results_per_action = st.slider("Results per action", 1, 5, 3, help="Number of footage options for each action")
        with col2:
            script_search_clicked = st.button("Search Script", type="primary", use_container_width=True)
        
        if script_search_clicked and script_text:
            perform_script_search(script_text, results_per_action)
        
        # Render Script Results
        if st.session_state.get("script_search_results"):
            render_script_results()
    
    else:  # Quick Search mode
        col_search, col_opts = st.columns([4, 1])
        
        with col_search:
            query = st.text_input(
                "Search query (any language)", 
                placeholder="e.g. 'person walking past a car' | 'व्यक्ति कार के पास चल रहा है' | 'వ్యక్తి కారు దగ్గర నడుస్తున్నాడు'", 
                label_visibility="collapsed",
                help="Type your search in ANY language - AI will translate and enhance automatically"
            )
        
        with col_opts:
            search_clicked = st.button("Search", type="primary", use_container_width=True)
        
        # Filters
        with st.expander("Advanced Filters", expanded=False):
            f_col1, f_col2, f_col3 = st.columns(3)
            mood_filter = f_col1.selectbox("Mood", ["Any", "Tense", "Joyful", "Melancholic", "Dramatic"])
            type_filter = f_col2.selectbox("Scene Type", ["Any", "Dialogue", "Action", "Establishing"])
            results_count = f_col3.slider("Results", 5, 50, 12)

        # Perform Search
        if search_clicked and query:
            perform_search(query, mood_filter, type_filter, results_count)
            
        # Render Results Grid
        if st.session_state.search_results:
            st.markdown("---")
            st.markdown(f"### Search Results ({len(st.session_state.search_results)} found)")
            render_results_grid()
        else:
            # Default / Empty State
            st.markdown("---")
            st.markdown("### Try these examples:")
            render_examples()


def perform_script_search(script_text, results_per_action):
    """Perform script-to-sequence search."""
    if not st.session_state.search_engine:
        st.warning("Please initialize the engine first")
        return
    
    from search.script_search import ScriptSequenceSearch
    
    with st.spinner("🎬 Parsing script into sequential actions..."):
        script_search = ScriptSequenceSearch(st.session_state.search_engine)
        results = script_search.search_script_sequence(
            script_text,
            results_per_action=results_per_action,
            use_query_expansion=True
        )
        
        st.session_state.script_search_results = results
        
        if results["status"] == "success":
            st.success(f"✅ Found {results['total_actions']} actions with {results['total_matches']} total matches!")
        else:
            st.error(f"❌ {results.get('error', 'Search failed')}")


def render_script_results():
    """Render script search results in sequential order."""
    results = st.session_state.get("script_search_results")
    
    if not results or results["status"] != "success":
        return
    
    st.markdown("---")
    st.markdown(f"### 🎬 Script Sequence Results")
    st.markdown(f"**{results['total_actions']} Actions** • **{results['total_matches']} Total Matches**")
    
    # Export options
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**Edit Sequence Ready** - Results are in script order")
    with col2:
        if st.button("📋 Copy Edit List", use_container_width=True):
            from search.script_search import ScriptSequenceSearch
            script_search = ScriptSequenceSearch(st.session_state.search_engine)
            edit_list = script_search.export_edit_sequence(results, format="text")
            st.code(edit_list, language="text")
    with col3:
        if st.button("💾 Download CSV", use_container_width=True):
            from search.script_search import ScriptSequenceSearch
            script_search = ScriptSequenceSearch(st.session_state.search_engine)
            csv_data = script_search.export_edit_sequence(results, format="csv")
            st.download_button(
                "Download",
                csv_data,
                file_name="edit_sequence.csv",
                mime="text/csv"
            )
    
    st.markdown("---")
    
    # Display each action in sequence
    for action_result in results["results"]:
        seq = action_result["sequence"]
        action = action_result["action"]
        matches = action_result["matches"]
        
        # Action header with sequence number
        st.markdown(f"""
        <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 0.75rem; border-left: 4px solid var(--accent-cyan); margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background: var(--accent-cyan); color: var(--bg-primary); width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.25rem;">
                    {seq}
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.25rem;">{action['action']}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">{action.get('description', '')}</div>
                </div>
                <div style="background: rgba(0, 229, 255, 0.15); padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: 600; color: var(--accent-cyan);">
                    {len(matches)} options
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display matches for this action
        if matches:
            cols = st.columns(min(len(matches), 3))
            for i, match in enumerate(matches):
                with cols[i % 3]:
                    render_match_card(match, i + 1, seq)
        else:
            st.warning(f"No matches found for action {seq}")
        
        st.markdown("<br>", unsafe_allow_html=True)


def render_match_card(match, option_num, sequence_num):
    """Render a single match card for script results using the same format as normal search."""
    # Extract data - use correct keys from search results
    score = match.get("score", 0)
    video_path = match.get("clip_path", "")
    thumb = match.get("thumbnail_path", "")
    mood = match.get("mood", "")
    scene_type = match.get("scene_type", "")
    description = match.get("description", "")
    start_time = match.get("start_time", 0)
    end_time = match.get("end_time", 0)
    time_str = f"{format_time(start_time)} - {format_time(end_time)}"
    tags = match.get("tags", [])
    
    # Create expandable card with modern styling (same as normal search)
    with st.expander(
        f"Option {option_num} • {int(score*100)}% Match • {scene_type.title() if scene_type else 'Scene'}", 
        expanded=(option_num==1)
    ):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Video player - prioritize video clip over thumbnail
            if video_path:
                # Convert to absolute path if relative
                if not os.path.isabs(video_path):
                    video_path = os.path.abspath(video_path)
                
                if os.path.exists(video_path):
                    # Try to read and display the video
                    try:
                        with open(video_path, 'rb') as video_file:
                            video_bytes = video_file.read()
                        st.video(video_bytes)
                    except Exception as e:
                        st.error(f"Error loading video: {e}")
                else:
                    st.warning(f"Video file not found")
            elif thumb:
                if not os.path.isabs(thumb):
                    thumb = os.path.abspath(thumb)
                if os.path.exists(thumb):
                    st.image(thumb, use_container_width=True)
                else:
                    st.warning(f"Thumbnail not found")
            else:
                st.warning("No media path provided")
            
            # Metadata badges
            st.markdown(f"""
            <div style="margin-top: 0.75rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
                <span class="badge badge-score">{int(score*100)}% Match</span>
                {f'<span class="badge badge-mood">{mood}</span>' if mood else ''}
                {f'<span class="badge badge-type">{scene_type}</span>' if scene_type else ''}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="margin-top: 0.75rem; padding: 0.75rem; background: var(--bg-card); border-radius: 0.5rem; border: 1px solid var(--border);">
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">TIMESTAMP</div>
                <div style="font-weight: 600;">{time_str}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Description
            st.markdown("**Description**")
            st.markdown(f"""
            <div style="padding: 1rem; background: var(--bg-card); border-radius: 0.5rem; border: 1px solid var(--border); margin-bottom: 1rem;">
                {description if description else "No description available"}
            </div>
            """, unsafe_allow_html=True)
            
            # Tags
            if tags and len(tags) > 0:
                st.markdown("**Tags**")
                tag_html = " ".join([f'<span class="tag">{tag}</span>' for tag in tags[:15]])
                st.markdown(f'<div style="margin-bottom: 1rem;">{tag_html}</div>', unsafe_allow_html=True)
            
            # File path details
            with st.expander("📁 File Details", expanded=False):
                st.code(video_path, language="text")
    
    if description:
        with st.expander("Description", expanded=False):
            st.markdown(f"<div style='font-size: 0.875rem;'>{description}</div>", unsafe_allow_html=True)


def render_examples():
    examples = [
        ("Person looking worried", "Person looking worried"),
        ("Romantic sunset on beach", "Romantic sunset on the beach"),
        ("High speed car chase", "High speed car chase"),
        ("Quiet moment of reflection", "Quiet moment of reflection")
    ]
    cols = st.columns(4)
    for i, (label, query) in enumerate(examples):
        if cols[i].button(label, use_container_width=True, type="secondary"):
            perform_search(query, "Any", "Any", 10)
            st.rerun()

def perform_search(query, mood, scene_type, limit):
    # Logic to route to active engine (Gemini or CLIP)
    filters = {}
    if mood != "Any": filters["mood"] = mood.lower()
    if scene_type != "Any": filters["scene_type"] = scene_type.lower()
    
    if st.session_state.search_engine: # Gemini Mode
        with st.spinner("AI is generating comprehensive search queries to find all matching scenes..."):
            # Use AI-powered comprehensive query expansion (enabled by default)
            results = st.session_state.search_engine.search(
                query, 
                top_k=limit, 
                filters=filters,
                use_query_expansion=True  # AI generates comprehensive queries
            )
            st.session_state.search_results = results
            
            # Show info about AI query expansion
            if results:
                st.info(f"AI analyzed your query and searched the database comprehensively. Found {len(results)} matching scenes.")
    
    elif st.session_state.embedder: # CLIP Mode
        with st.spinner("Matching embeddings..."):
            emb = st.session_state.embedder.embed_text(query)
            results = st.session_state.vector_search.search(emb, top_k=limit)
            st.session_state.search_results = results
    else:
        st.warning("Please initialize the engine first (click 'Initialize / Reload Engine' button)")


def render_results_grid():
    results = st.session_state.search_results
    
    if not results:
        st.info("No results found. Try a different search query.")
        return
    
    # Display results in modern cards
    for i, res in enumerate(results):
        # Extract data - use correct keys from search results
        score = res.get("score", 0)
        video_path = res.get("clip_path", "")
        thumb = res.get("thumbnail_path", "")
        mood = res.get("mood", "")
        scene_type = res.get("scene_type", "")
        description = res.get("description", "")
        start_time = res.get("start_time", 0)
        end_time = res.get("end_time", 0)
        time_str = f"{format_time(start_time)} - {format_time(end_time)}"
        tags = res.get("tags", [])
        
        # Create expandable card with modern styling
        with st.expander(
            f"Result #{i+1} • {int(score*100)}% Match • {scene_type.title() if scene_type else 'Scene'}", 
            expanded=(i==0)
        ):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Video player - prioritize video clip over thumbnail
                # Debug: Show what paths we're trying to use
                st.caption(f"🔍 Debug: Clip path: {video_path}")
                
                if video_path:
                    # Convert to absolute path if relative
                    if not os.path.isabs(video_path):
                        video_path = os.path.abspath(video_path)
                    
                    st.caption(f"🔍 Absolute path: {video_path}")
                    st.caption(f"🔍 File exists: {os.path.exists(video_path)}")
                    
                    if os.path.exists(video_path):
                        # Try to read and display the video
                        try:
                            with open(video_path, 'rb') as video_file:
                                video_bytes = video_file.read()
                            st.video(video_bytes)
                        except Exception as e:
                            st.error(f"Error loading video: {e}")
                            st.caption(f"Path: {video_path}")
                    else:
                        st.warning(f"Video file not found at: {video_path}")
                elif thumb:
                    if not os.path.isabs(thumb):
                        thumb = os.path.abspath(thumb)
                    if os.path.exists(thumb):
                        st.image(thumb, use_container_width=True)
                    else:
                        st.warning(f"Thumbnail not found at: {thumb}")
                else:
                    st.warning("No media path provided")
                
                # Metadata badges
                st.markdown(f"""
                <div style="margin-top: 0.75rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
                    <span class="badge badge-score">{int(score*100)}% Match</span>
                    {f'<span class="badge badge-mood">{mood}</span>' if mood else ''}
                    {f'<span class="badge badge-type">{scene_type}</span>' if scene_type else ''}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="margin-top: 0.75rem; padding: 0.75rem; background: var(--bg-card); border-radius: 0.5rem; border: 1px solid var(--border);">
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">TIMESTAMP</div>
                    <div style="font-weight: 600;">{time_str}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Description
                st.markdown("**Description**")
                st.markdown(f"""
                <div style="padding: 1rem; background: var(--bg-card); border-radius: 0.5rem; border: 1px solid var(--border); margin-bottom: 1rem;">
                    {description if description else "No description available"}
                </div>
                """, unsafe_allow_html=True)
                
                # Tags
                if tags and len(tags) > 0:
                    st.markdown("**Tags**")
                    tag_html = " ".join([f'<span class="tag">{tag}</span>' for tag in tags[:15]])
                    st.markdown(f'<div style="margin-bottom: 1rem;">{tag_html}</div>', unsafe_allow_html=True)
                
                # Show more details - NO RERUN, use expander
                with st.expander("Show Full Analysis", expanded=False):
                    st.markdown("### Complete Analysis")
                    
                    # Try to get full analysis from ChromaDB
                    try:
                        scene_id = res.get("id", "")
                        
                        if scene_id and st.session_state.search_engine:
                            full_scene = st.session_state.search_engine.get_scene(scene_id)
                            if full_scene and full_scene.get("document"):
                                st.markdown("**Full Searchable Text**")
                                st.text(full_scene["document"])
                            
                            # Show all metadata
                            if full_scene and full_scene.get("metadata"):
                                metadata = full_scene["metadata"]
                                
                                st.markdown("**Metadata**")
                                col_a, col_b, col_c = st.columns(3)
                                
                                with col_a:
                                    if metadata.get("scene_type"):
                                        st.metric("Scene Type", metadata["scene_type"])
                                    if metadata.get("mood"):
                                        st.metric("Mood", metadata["mood"])
                                
                                with col_b:
                                    if metadata.get("duration"):
                                        st.metric("Duration", f"{metadata['duration']:.1f}s")
                                    if metadata.get("video_id"):
                                        st.metric("Video ID", metadata["video_id"])
                                
                                with col_c:
                                    if metadata.get("clip_index") is not None:
                                        st.metric("Clip Index", metadata["clip_index"])
                                
                                # Show all tags
                                all_tags = metadata.get("tags", "")
                                if all_tags:
                                    st.markdown("**All Tags**")
                                    if isinstance(all_tags, str):
                                        tags_list = all_tags.split(',')
                                        st.write(", ".join(tags_list))
                                    else:
                                        st.write(", ".join(all_tags))
                    except Exception as e:
                        st.error(f"Could not load full analysis: {e}")
                        # Fallback: show what we have
                        st.json(res)


def render_library():
    st.markdown("## Library")
    st.markdown("Upload videos or provide URLs to build your searchable footage library")
    
    # Upload Zone
    st.markdown("### Add New Footage")
    
    # Tab for Upload vs URL
    tab1, tab2 = st.tabs(["Upload Files", "From URL"])
    
    with tab1:
        uploaded_files = st.file_uploader(
            "Drag & Drop videos or click to browse", 
            accept_multiple_files=True, 
            type=['mp4','mov','avi','mkv','webm'],
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.markdown(f"""
            <div style="background: rgba(6, 182, 212, 0.1); padding: 1rem; border-radius: 0.75rem; border-left: 4px solid var(--accent); margin-bottom: 1rem;">
                <div style="font-weight: 600; color: var(--accent);">{len(uploaded_files)} file(s) selected</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">Ready to process</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Disable button if already processing
            button_disabled = st.session_state.processing
            button_label = "Processing..." if button_disabled else f"Process {len(uploaded_files)} Video(s)"
            
            if st.button(button_label, type="primary", key="process_files", disabled=button_disabled, use_container_width=True):
                st.session_state.processing = True
                process_queue(uploaded_files)
    
    with tab2:
        st.markdown("**Supported platforms**: YouTube, Google Drive, Vimeo, direct links, and more")
        
        url_input = st.text_input(
            "Video URL",
            placeholder="https://www.youtube.com/watch?v=... or https://drive.google.com/...",
            help="Paste a video URL from YouTube, Google Drive, or any supported platform"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            custom_name = st.text_input(
                "Custom name (optional)",
                placeholder="Leave empty to use video title",
                help="Optional custom identifier for this video"
            )
        with col2:
            cleanup = st.checkbox("Auto-cleanup", value=True, help="Delete downloaded file after processing")
        
        # Disable button if already processing
        button_disabled = st.session_state.processing or not url_input
        button_label = "Processing..." if st.session_state.processing else "Process from URL"
        
        if st.button(button_label, type="primary", disabled=button_disabled, key="process_url", use_container_width=True):
            st.session_state.processing = True
            process_from_url(url_input, custom_name if custom_name else None, cleanup)

    st.markdown("---")
    
    # Existing Content
    st.markdown("### Indexed Content")
    
    if st.session_state.stats.get("total_scenes", 0) > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 0.75rem; border: 1px solid var(--border); text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: 0.5rem;">{st.session_state.stats['total_scenes']:,}</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">Total Scenes</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 0.75rem; border: 1px solid var(--border); text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: var(--secondary); margin-bottom: 0.5rem;">{st.session_state.stats.get('unique_videos', 0)}</div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">Videos Indexed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("View All Videos", type="secondary", use_container_width=True):
                st.session_state.show_all_videos = not st.session_state.get('show_all_videos', False)
                st.rerun()
        
        with col4:
            if st.button("Library Manager", type="secondary", use_container_width=True):
                st.session_state.show_library_manager = not st.session_state.get('show_library_manager', False)
                st.rerun()
        
        # Library Manager Section
        if st.session_state.get('show_library_manager', False):
            st.markdown("---")
            st.markdown("### Library Manager")
            
            tab1, tab2 = st.tabs(["Create New Library", "Restore Archive"])
            
            with tab1:
                st.markdown("**Create a fresh library**")
                st.info("Current library will be archived with timestamp. You can restore it later.")
                
                if st.button("Archive Current & Create New", type="primary", use_container_width=True):
                    if st.session_state.search_engine:
                        with st.spinner("Archiving current library..."):
                            archive_path = st.session_state.search_engine.archive_and_create_new()
                            st.session_state.stats = {"total_scenes": 0, "unique_videos": 0}
                            st.session_state.search_results = []
                            st.success(f"✅ Library archived successfully!")
                            st.info(f"Archive location: {archive_path}")
                            time.sleep(2)
                            st.rerun()
                    else:
                        st.warning("Please initialize engine first")
            
            with tab2:
                st.markdown("**Restore from archive**")
                
                if st.session_state.search_engine:
                    archives = st.session_state.search_engine.list_archives()
                    
                    if archives:
                        st.markdown(f"Found {len(archives)} archived libraries:")
                        
                        for archive in archives:
                            with st.expander(f"📦 {archive['timestamp_str']} ({archive['scene_count']} scenes)", expanded=False):
                                col_a, col_b = st.columns([2, 1])
                                
                                with col_a:
                                    st.markdown(f"**Archive:** `{archive['name']}`")
                                    st.markdown(f"**Scenes:** {archive['scene_count']:,}")
                                    st.markdown(f"**Created:** {archive['timestamp_str']}")
                                
                                with col_b:
                                    if st.button("Restore", key=f"restore_{archive['name']}", type="primary", use_container_width=True):
                                        with st.spinner("Restoring archive..."):
                                            success = st.session_state.search_engine.restore_from_archive(archive['path'])
                                            if success:
                                                st.session_state.stats = st.session_state.search_engine.get_stats()
                                                st.success("✅ Archive restored successfully!")
                                                time.sleep(2)
                                                st.rerun()
                                            else:
                                                st.error("Failed to restore archive")
                    else:
                        st.info("No archived libraries found")
                else:
                    st.warning("Please initialize engine first")
        
        # Show all videos list
        if st.session_state.get('show_all_videos', False):
            st.markdown("---")
            st.markdown("### All Indexed Videos")
            
            try:
                # Get all scenes from ChromaDB
                if st.session_state.search_engine:
                    all_data = st.session_state.search_engine.collection.get(
                        include=["metadatas", "documents"]
                    )
                    
                    if all_data and all_data.get("ids"):
                        # Group by video_id
                        videos = {}
                        for i, scene_id in enumerate(all_data["ids"]):
                            metadata = all_data["metadatas"][i] if all_data.get("metadatas") else {}
                            document = all_data["documents"][i] if all_data.get("documents") else ""
                            
                            video_id = metadata.get("video_id", "unknown")
                            if video_id not in videos:
                                videos[video_id] = []
                            
                            videos[video_id].append({
                                'id': scene_id,
                                'clip_path': metadata.get('clip_path', ''),
                                'thumbnail_path': metadata.get('thumbnail_path', ''),
                                'description': metadata.get('description', '')[:150],  # Truncate
                                'full_description': metadata.get('description', ''),
                                'document': document,
                                'start_time': metadata.get('start_time', 0),
                                'end_time': metadata.get('end_time', 0),
                                'scene_type': metadata.get('scene_type', ''),
                                'mood': metadata.get('mood', ''),
                                'tags': metadata.get('tags', '').split(',') if metadata.get('tags') else []
                            })
                        
                        # Display each video's clips
                        for video_id, clips in videos.items():
                            with st.expander(f"Video: {video_id} ({len(clips)} scenes)", expanded=False):
                                # Delete video button
                                if st.button(f"Delete Entire Video", key=f"delete_video_{video_id}", type="secondary"):
                                    st.session_state.search_engine.delete_video(video_id)
                                    st.session_state.stats = st.session_state.search_engine.get_stats()
                                    st.success(f"Deleted {video_id}")
                                    time.sleep(1)
                                    st.rerun()
                                
                                st.markdown("---")
                                
                                # Display clips in grid (3 columns)
                                for idx in range(0, len(clips), 3):
                                    cols = st.columns(3)
                                    for col_idx, col in enumerate(cols):
                                        if idx + col_idx < len(clips):
                                            clip = clips[idx + col_idx]
                                            
                                            with col:
                                                # Show video clip (preferred) or thumbnail as fallback
                                                if clip['clip_path'] and os.path.exists(clip['clip_path']):
                                                    st.video(clip['clip_path'])
                                                elif clip['thumbnail_path'] and os.path.exists(clip['thumbnail_path']):
                                                    st.image(clip['thumbnail_path'], use_container_width=True)
                                                else:
                                                    st.markdown("""
                                                    <div style="background: var(--bg-card); padding: 2rem; text-align: center; border-radius: 0.5rem;">
                                                        <div style="opacity: 0.3;">No preview</div>
                                                    </div>
                                                    """, unsafe_allow_html=True)
                                                
                                                # Time and type
                                                time_str = f"{format_time(clip['start_time'])} - {format_time(clip['end_time'])}"
                                                st.caption(f"{time_str}")
                                                
                                                if clip['scene_type']:
                                                    st.markdown(f"""
                                                    <span class="badge badge-type">{clip['scene_type']}</span>
                                                    """, unsafe_allow_html=True)
                                                
                                                # Truncated description
                                                st.markdown(f"""
                                                <div style="font-size: 0.875rem; margin-top: 0.5rem; color: var(--text-secondary);">
                                                    {clip['description']}...
                                                </div>
                                                """, unsafe_allow_html=True)
                                                
                                                # Full details (expandable) - NO RERUN, just expander
                                                with st.expander("View Details", expanded=False):
                                                    st.markdown("**Full Description:**")
                                                    st.markdown(clip['full_description'])
                                                    
                                                    if clip['tags']:
                                                        st.markdown("**Tags:**")
                                                        tag_html = " ".join([f'<span class="tag">{tag.strip()}</span>' for tag in clip['tags'][:10]])
                                                        st.markdown(tag_html, unsafe_allow_html=True)
                                                    
                                                    if clip['document']:
                                                        st.markdown("**Full Analysis:**")
                                                        st.text(clip['document'])
                    else:
                        st.info("No videos found in database")
            except Exception as e:
                st.error(f"Error loading videos: {e}")
                import traceback
                st.code(traceback.format_exc())
    else:
        st.markdown("""
        <div style="background: var(--bg-card); padding: 2rem; border-radius: 0.75rem; border: 2px dashed var(--border); text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.2;">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block;">
                    <path d="M19 3H5C3.89543 3 3 3.89543 3 5V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V5C21 3.89543 20.1046 3 19 3Z" stroke="currentColor" stroke-width="2"/>
                    <path d="M10 9L15 12L10 15V9Z" fill="currentColor"/>
                </svg>
            </div>
            <div style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem;">Library is empty</div>
            <div style="color: var(--text-secondary);">Upload videos or provide URLs to get started</div>
        </div>
        """, unsafe_allow_html=True)

def process_queue(files):
    # Determine pipeline to use
    use_gemini = check_api_key() and st.session_state.pipeline
    
    if not use_gemini:
        st.error("Please initialize Gemini pipeline in Settings first.")
        st.session_state.processing = False
        return
    
    # Create progress containers
    progress_container = st.container()
    
    with progress_container:
        overall_progress = st.progress(0.0, text="Initializing...")
        stage_progress = st.progress(0.0, text="")
        status_text = st.empty()
    
    import torch
    use_gpu = torch.cuda.is_available()
    
    if use_gpu:
        status_text.info("GPU acceleration enabled")
    else:
        status_text.warning("Running on CPU (slower)")
    
    try:
        success_count = 0
        for file_idx, file in enumerate(files):
            # Update overall progress
            overall_pct = file_idx / len(files)
            overall_progress.progress(overall_pct, text=f"Processing file {file_idx+1}/{len(files)}: {file.name}")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name
            
            try:
                # Progress callback for stages
                def stage_callback(stage_name, current, total):
                    if total > 0:
                        stage_pct = current / total
                        stage_progress.progress(stage_pct, text=f"{stage_name}: {current}/{total} ({int(stage_pct*100)}%)")
                        status_text.info(f"{file.name} - {stage_name}: {current}/{total}")
                
                # Use Gemini Pipeline with GPU support
                res = st.session_state.pipeline.process_video(
                    tmp_path,
                    use_yolo=True,
                    yolo_scene_detection=True,
                    progress_callback=stage_callback
                )
                
                if res['status'] == 'complete':
                    st.toast(f"Indexed {file.name}", icon="✅")
                    success_count += 1
                    # Update stats
                    st.session_state.stats = st.session_state.pipeline.search_engine.get_stats()
                else:
                    st.error(f"Failed {file.name}: {res.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"Failed {file.name}: {e}")
                import traceback
                logger.error(traceback.format_exc())
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            
            # Update overall progress
            overall_progress.progress((file_idx + 1) / len(files), text=f"Completed {file_idx+1}/{len(files)} files")
        
        # Show completion message
        if success_count > 0:
            status_text.success(f"Successfully processed {success_count}/{len(files)} videos")
        else:
            status_text.warning("No videos were successfully processed")
        
        time.sleep(2)
        
    finally:
        # Always reset processing state
        st.session_state.processing = False
        progress_container.empty()
        st.rerun()


def process_from_url(url: str, custom_name: str = None, cleanup: bool = True):
    """Process video from URL."""
    use_gemini = check_api_key() and st.session_state.pipeline
    
    if not use_gemini:
        st.error("Gemini pipeline required for URL processing. Please initialize in Settings.")
        st.session_state.processing = False
        return
    
    # Create progress containers
    progress_container = st.container()
    
    with progress_container:
        overall_status = st.empty()
        stage_progress = st.progress(0.0, text="")
        stage_status = st.empty()
    
    import torch
    use_gpu = torch.cuda.is_available()
    
    if use_gpu:
        overall_status.info("GPU acceleration enabled")
    else:
        overall_status.warning("Running on CPU (slower)")
    
    try:
        overall_status.info(f"Downloading video from URL...")
        stage_progress.progress(0.05, text="Downloading...")
        
        # Progress callback for stages
        def stage_callback(stage_name, current, total):
            if total > 0:
                stage_pct = current / total
                stage_progress.progress(stage_pct, text=f"{stage_name}: {current}/{total} ({int(stage_pct*100)}%)")
                stage_status.info(f"{stage_name}: {current}/{total}")
        
        # Process with pipeline (handles download automatically)
        with st.spinner("Processing video..."):
            res = st.session_state.pipeline.process_video(
                video_path=url,
                video_id=custom_name,
                cleanup_download=cleanup,
                use_yolo=True,
                yolo_scene_detection=True,
                progress_callback=stage_callback
            )
        
        stage_progress.progress(1.0, text="Complete!")
        
        if res['status'] == 'complete':
            video_title = res.get('video_id', 'video')
            scenes_count = res['stages']['scene_detection']['optimized_scenes']
            
            # Clear progress indicators first
            progress_container.empty()
            
            st.success(f"Successfully processed: {video_title}")
            st.info(f"Detected {scenes_count} scenes")
            
            # Show processing details
            with st.expander("Processing Details"):
                st.json({
                    'video_id': res['video_id'],
                    'downloaded_from': res.get('original_url', url),
                    'scenes_detected': scenes_count,
                    'yolo_analysis': res['stages'].get('yolo_analysis', {}),
                    'gemini_analyzed': res['stages'].get('analysis', {}).get('gemini_analyzed', 0),
                    'indexed_scenes': res['stages'].get('indexing', {}).get('indexed', 0)
                })
            
            # Update stats
            st.session_state.stats = st.session_state.pipeline.search_engine.get_stats()
            
            st.toast(f"Indexed {video_title}", icon="✅")
            
            # Reset processing flag BEFORE rerun
            st.session_state.processing = False
            
            # Small delay then rerun
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"Processing failed: {res.get('error', 'Unknown error')}")
            st.session_state.processing = False
            
    except Exception as e:
        st.error(f"Failed to process URL: {str(e)}")
        import traceback
        with st.expander("Error Details"):
            st.code(traceback.format_exc())
        st.session_state.processing = False
    finally:
        # Ensure cleanup
        progress_container.empty()



# --- MAIN ROUTER ---

render_sidebar()

if st.session_state.active_tab == "Home":
    render_home()
elif st.session_state.active_tab == "Library":
    render_library()
