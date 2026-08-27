import streamlit as st
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The Confidence Gap - Publication", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- SUPABASE DATABASE SETUP ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

def save_registration(name, contact, email):
    """Saves registration data directly to the Supabase cloud database."""
    data = {
        "name": name,
        "contact": contact if contact else "N/A",
        "email": email
    }
    supabase.table("attendees").insert(data).execute()

# --- SESSION STATE ---
if 'registered' not in st.session_state:
    st.session_state.registered = False
if 'show_register_modal' not in st.session_state:
    st.session_state.show_register_modal = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- URL CONFIGURATION ---
PDF_PREVIEW_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&raw=1"
DIRECT_DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"

# --- CSS INJECTION & FULL SCREEN STYLING ---
st.markdown("""
    <style>
    /* Imported Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@500;600;700;800&display=swap');

    /* Hide default Streamlit elements */
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Full Screen Layout Adjustments */
    .stApp, .main {
        background-color: #ffffff !important;
    }

    .main .block-container {
        padding-top: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 100% !important;
    }

    /* TOP BAR STYLING */
    .top-bar-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #ffffff;
        border-bottom: 2px solid #c9a35e;
        padding: 8px 10px;
        margin-bottom: 10px;
    }

    .brand-title {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #0c1a30 !important;
        margin: 0 !important;
        line-height: 1.1 !important;
        letter-spacing: 0.5px !important;
    }

    .brand-gold {
        color: #c9a35e !important;
    }

    .brand-subtitle {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.7rem !important;
        color: #003366 !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        display: block;
    }

    /* FULL SCREEN PDF WRAPPER & TOOLBAR BLOCKER */
    .pdf-wrapper {
        position: relative;
        width: 100%;
        height: calc(100vh - 110px);
        border: 2px solid #003366;
        background-color: #f8f9fa;
    }

    .pdf-container {
        width: 100%;
        height: 100%;
        border: none;
    }

    /* Covers up the default toolbar/download buttons on the PDF viewer iframe */
    .iframe-cover-top-right {
        position: absolute;
        top: 0;
        right: 0;
        width: 200px;
        height: 50px;
        background-color: #f1f3f5;
        z-index: 10;
        pointer-events: auto;
    }

    /* CUSTOM DOWNLOAD BUTTON IN TOP BAR */
    a.custom-download-btn {
        display: inline-block;
        background-color: #003366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 0px !important;
        text-decoration: none;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 1px;
        transition: background-color 0.3s ease;
        text-align: center;
    }
    a.custom-download-btn:hover {
        background-color: #c9a35e;
    }

    /* FORM AND INPUT STYLING */
    [data-testid="stTextInput"] > div > div {
        background-color: transparent !important;
        border: 2px solid #003366 !important;
        border-radius: 0px !important;
    }
    [data-testid="stTextInput"] input {
        color: #0c1a30 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
    }
    
    @media screen and (max-width: 768px) {
        .brand-title {
            font-size: 1.3rem !important;
        }
        .pdf-wrapper {
            height: calc(100vh - 130px);
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- REGISTRATION MODAL DIALOG ---
@st.dialog("Complete Quick Registration to Download")
def registration_dialog():
    st.markdown("<p style='font-family: Montserrat; font-size: 0.9rem; color: #0c1a30;'>Please enter your details below to unlock and download the full publication.</p>", unsafe_allow_html=True)
    
    with st.form("modal_registration_form"):
        name = st.text_input("FULL NAME *")
        contact = st.text_input("CONTACT NUMBER (OPTIONAL)")
        email = st.text_input("EMAIL *")
        
        submitted = st.form_submit_button("SUBMIT & UNLOCK DOWNLOAD")
        
        if submitted:
            if name.strip() and email.strip():
                try:
                    save_registration(name, contact, email)
                    st.session_state.registered = True
                    st.session_state.user_name = name
                    st.session_state.show_register_modal = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to register. Error: {e}")
            else:
                st.error("Please provide both your Full Name and Email.")

# Trigger modal dialog if state is active
if st.session_state.show_register_modal and not st.session_state.registered:
    registration_dialog()

# --- TOP NAVIGATION BAR ---
col_logo, col_btn = st.columns([3, 1])

with col_logo:
    st.markdown("""
        <div class="top-bar-container" style="border:none; padding:0; margin:0;">
            <div>
                <h1 class="brand-title">THE CONFIDENCE <span class="brand-gold">GAP</span></h1>
                <span class="brand-subtitle">PHILIPPINE REAL ESTATE MARKET OVERVIEW &nbsp;•&nbsp; INDUSTRIAL &nbsp;•&nbsp; OFFICE &nbsp;•&nbsp; RETAIL</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_btn:
    if not st.session_state.registered:
        if st.button("📥 DOWNLOAD PUBLICATION", use_container_width=True, type="primary"):
            st.session_state.show_register_modal = True
            st.rerun()
    else:
        st.markdown(f'''
            <div style="text-align: right;">
                <a href="{DIRECT_DOWNLOAD_URL}" class="custom-download-btn">📥 DOWNLOAD PDF NOW</a>
            </div>
        ''', unsafe_allow_html=True)

# Success banner feedback if recently registered
if st.session_state.registered and st.session_state.user_name:
    st.success(f"Welcome, {st.session_state.user_name}! Registration successful. Your download link in the top bar is active.")

# --- FULL-SCREEN PDF VIEWER LANDING PAGE ---
st.markdown(f'''
    <div class="pdf-wrapper">
        <!-- Covers up the top toolbar/download buttons of the iframe viewer -->
        <div class="iframe-cover-top-right"></div>
        <iframe src="{PDF_PREVIEW_URL}" class="pdf-container" frameborder="0"></iframe>
    </div>
''', unsafe_allow_html=True)
