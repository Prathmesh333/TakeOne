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
    
    /* Global Theme Variables */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #8b5cf6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --bg-hover: #334155;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --border: #334155;
    }

    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
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
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
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
        border-color: var(--primary);
        transform: translateX(2px);
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
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
        line-height: 1.1;
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
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: var(--primary);
    }

    /* --- BUTTONS --- */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary button */
    .stButton > button[kind="secondary"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        color: var(--text-primary);
        box-shadow: none;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--bg-hover);
        border-color: var(--primary);
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
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
    }
    
    .badge-mood {
        background: rgba(6, 182, 212, 0.15);
        color: #06b6d4;
        border: 1px solid rgba(6, 182, 212, 0.3);
    }
    
    .badge-type {
        background: rgba(139, 92, 246, 0.15);
        color: #a78bfa;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }
    
    .badge:hover {
        transform: scale(1.05);
    }

    /* --- TAGS --- */
    .tag {
        display: inline-block;
        font-size: 0.75rem;
        color: var(--text-secondary);
        background: var(--bg-dark);
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        margin: 0.25rem;
        border: 1px solid var(--border);
        transition: all 0.2s;
    }
    
    .tag:hover {
        background: var(--bg-hover);
        color: var(--text-primary);
        border-color: var(--primary);
    }

    /* --- INPUT FIELDS --- */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
        padding: 0.875rem 1.25rem;
        font-size: 1rem;
        transition: all 0.2s;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-secondary);
    }

    /* --- SELECT BOXES --- */
    .stSelectbox > div > div {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
    }

    /* --- PROGRESS BARS --- */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
        border-radius: 9999px;
    }

    /* --- EXPANDER --- */
    .streamlit-expanderHeader {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-hover);
        border-color: var(--primary);
    }

    /* --- METRICS --- */
    .stMetric {
        background: var(--bg-card);
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
        color: var(--text-primary);
        font-size: 1.875rem;
        font-weight: 700;
    }

    /* --- VIDEO PLAYER --- */
    .stVideo {
        border-radius: 0.75rem;
        overflow: hidden;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }

    /* --- ALERTS --- */
    .stAlert {
        border-radius: 0.75rem;
        border: none;
        padding: 1rem 1.25rem;
    }
    
    /* Success */
    [data-testid="stAlert"][data-baseweb="notification"] > div:first-child {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid var(--success);
    }
    
    /* Info */
    .stInfo {
        background: rgba(6, 182, 212, 0.1);
        border-left: 4px solid var(--accent);
    }
    
    /* Warning */
    .stWarning {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid var(--warning);
    }
    
    /* Error */
    .stError {
        background: rgba(239, 68, 68, 0.1);
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
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
    }
    
    .icon-success {
        background: rgba(16, 185, 129, 0.15);
        color: var(--success);
    }
    
    .icon-warning {
        background: rgba(245, 158, 11, 0.15);
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
        # Logo and title in single container
        st.markdown("""
        <div style="display: flex; align-items: center; padding: 1.5rem 0 2rem 0; gap: 1rem;">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 3H5C3.89543 3 3 3.89543 3 5V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V5C21 3.89543 20.1046 3 19 3Z" stroke="url(#gradient)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 9L15 12L10 15V9Z" fill="url(#gradient)"/>
                <defs>
                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
                    </linearGradient>
                </defs>
            </svg>
            <div>
                <div style="font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2;">TakeOne</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.125rem;">AI Video Search</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation buttons - clean and professional with SVG icons
        st.markdown('<div style="font-size: 0.7rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">Navigation</div>', unsafe_allow_html=True)
        
        # Custom CSS for navigation buttons with icons
        home_active = st.session_state.active_tab == "Home"
        library_active = st.session_state.active_tab == "Library"
        
        st.markdown("""
        <style>
        /* Hide default button styling for nav buttons */
        div[data-testid="stSidebar"] button[kind="secondary"] p {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 500;
            font-size: 0.95rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Home button
        home_icon = """
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 0.5rem;">
            <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9 22V12H15V22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        """
        
        col1, col2 = st.columns([1, 6])
        with col1:
            st.markdown(home_icon, unsafe_allow_html=True)
        with col2:
            if st.button("Home", key="nav_home", use_container_width=True, type="primary" if home_active else "secondary"):
                st.session_state.active_tab = "Home"
                st.rerun()
        
        # Library button
        library_icon = """
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 0.5rem;">
            <path d="M4 19.5C4 18.837 4.26339 18.2011 4.73223 17.7322C5.20107 17.2634 5.83696 17 6.5 17H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M6.5 2H20V22H6.5C5.83696 22 5.20107 21.7366 4.73223 21.2678C4.26339 20.7989 4 20.163 4 19.5V4.5C4 3.83696 4.26339 3.20107 4.73223 2.73223C5.20107 2.26339 5.83696 2 6.5 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        """
        
        col1, col2 = st.columns([1, 6])
        with col1:
            st.markdown(library_icon, unsafe_allow_html=True)
        with col2:
            if st.button("Library", key="nav_library", use_container_width=True, type="primary" if library_active else "secondary"):
                st.session_state.active_tab = "Library"
                st.rerun()
        
        st.markdown("---")
        
        # Stats section
        st.markdown('<div style="font-size: 0.7rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.05em;">Statistics</div>', unsafe_allow_html=True)
        
        if check_api_key() and st.session_state.pipeline:
            stats = st.session_state.stats
            
            # Scenes metric
            st.markdown(f"""
            <div style="background: var(--bg-card); padding: 1rem; border-radius: 0.75rem; margin-bottom: 0.75rem; border: 1px solid var(--border);">
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Total Scenes</div>
                <div style="font-size: 1.75rem; font-weight: 700; color: var(--text-primary);">{stats.get("total_scenes", 0):,}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Videos metric
            st.markdown(f"""
            <div style="background: var(--bg-card); padding: 1rem; border-radius: 0.75rem; border: 1px solid var(--border);">
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Videos Indexed</div>
                <div style="font-size: 1.75rem; font-weight: 700; color: var(--text-primary);">{stats.get("unique_videos", 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        elif st.session_state.embedder:
            st.metric("Clips Indexed", st.session_state.indexed_clips)
        else:
            st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.1); padding: 1rem; border-radius: 0.75rem; border-left: 4px solid var(--warning); text-align: center;">
                <div style="font-size: 0.875rem; color: var(--warning); font-weight: 600;">System Offline</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">Initialize engine to start</div>
            </div>
            """, unsafe_allow_html=True)


def render_home():
    # Hero Section - Clean and professional
    st.markdown("""
    <div class="hero-container fade-in">
        <div class="hero-title">Find the perfect shot.</div>
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
    
    col_search, col_opts = st.columns([3, 1])
    
    with col_search:
        query = st.text_input(
            "Search query", 
            placeholder="e.g. 'person walking past a car' or 'sunset on the beach'", 
            label_visibility="collapsed"
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
