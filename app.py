import streamlit as st
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="The Confidence Gap - Publication", layout="wide", initial_sidebar_state="collapsed")

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

# --- URL CONFIGURATION ---
# Online viewer preview (raw=1) and Direct download (dl=1)
PDF_PREVIEW_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&raw=1"
DIRECT_DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"

# --- CSS INJECTION ---
st.markdown("""
    <style>
    /* Imported Cormorant Garamond and Montserrat */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@500;600;700;800&display=swap');

    /* Hide default Streamlit elements */
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Solid White Background */
    .stApp, .main {
        background-color: #ffffff !important;
    }

    /* Container alignment for full-screen layout */
    .main .block-container {
        padding-top: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* TOP BAR STYLING */
    .top-bar-title {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #0c1a30 !important;
        margin: 0 !important;
        line-height: 1.1 !important;
        letter-spacing: 1px !important;
    }
    .top-bar-gold {
        color: #c9a35e !important;
    }
    .top-bar-subtitle {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.75rem !important;
        color: #0c1a30 !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
    }

    .horizontal-divider {
        width: 100%;
        height: 2px;
        background-color: #c9a35e;
        margin: 10px 0 15px 0;
    }

    /* FULL SCREEN PDF EMBED CONTAINER */
    .pdf-container {
        border: 2px solid #003366;
        width: 100%;
        height: 78vh;
        background-color: #f8f9fa;
    }

    /* FORM CONTAINER */
    [data-testid="stForm"] {
        background-color: white !important;
        border: 3px solid #c9a35e !important; 
        border-radius: 0px !important;
        padding: 30px 35px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05) !important;
        margin-top: 20px !important;
    }

    /* INPUT TEXT BOX UI */
    [data-testid="stTextInput"] > div > div {
        background-color: transparent !important;
        border: 2px solid #003366 !important;
        border-radius: 0px !important;
        box-shadow: none !important;
    }

    [data-testid="stTextInput"] > div > div:focus-within {
        border-color: #c9a35e !important;
    }

    [data-testid="stTextInput"] input {
        background-color: transparent !important;
        color: #0c1a30 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
    }
    
    .stTextInput label p {
        font-family: 'Montserrat', sans-serif !important;
        color: #003366 !important;
        font-weight: 800 !important;
        font-size: 0.9rem !important;
        letter-spacing: 1px !important;
    }

    /* SUBMIT & ACTION BUTTONS */
    [data-testid="stFormSubmitButton"] > button, .stButton > button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border: none !important;
        width: 100% !important;
        padding: 12px !important;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFormSubmitButton"] > button:hover, .stButton > button:hover {
        background-color: #c9a35e !important;
        color: white !important;
    }
    
    /* CUSTOM DOWNLOAD BUTTON */
    a.custom-download-btn {
        display: block;
        width: 100%;
        text-align: center;
        background-color: #003366;
        color: white !important;
        padding: 14px 20px;
        border-radius: 0px !important;
        text-decoration: none;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 1px;
        margin-top: 15px;
        margin-bottom: 10px;
        transition: background-color 0.3s ease;
    }
    a.custom-download-btn:hover {
        background-color: #c9a35e;
    }
    
    .success-box {
        background-color: white !important;
        border: 3px solid #c9a35e !important; 
        border-radius: 0px !important;
        padding: 30px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05) !important;
        text-align: center !important;
        margin-top: 20px !important;
    }

    .footer-text { 
        margin-top: 20px; 
        margin-bottom: 10px; 
        text-align: center; 
        font-family: 'Montserrat', sans-serif !important; 
        color: #0c1a30 !important; 
        font-weight: 700 !important; 
        letter-spacing: 3px !important; 
        font-size: 0.75rem !important; 
    }

    @media screen and (max-width: 768px) {
        .top-bar-title { 
            font-size: 1.2rem !important; 
        }
        .pdf-container {
            height: 60vh;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- TOP BAR LANDING HEADER ---
col_brand, col_action = st.columns([3, 1], vertical_alignment="center")

with col_brand:
    st.markdown("""
    <div>
        <h1 class="top-bar-title">THE CONFIDENCE <span class="top-bar-gold">GAP</span></h1>
        <div class="top-bar-subtitle">PHILIPPINE REAL ESTATE MARKET OVERVIEW &nbsp;•&nbsp; INDUSTRIAL &nbsp;•&nbsp; OFFICE &nbsp;•&nbsp; RETAIL</div>
    </div>
    """, unsafe_allow_html=True)

with col_action:
    if not st.session_state.registered:
        if st.button("📥 DOWNLOAD PUBLICATION", use_container_width=True):
            st.session_state.show_register_modal = True
            st.rerun()
    else:
        if st.button("📥 GET PDF FILE", use_container_width=True):
            st.session_state.show_register_modal = True
            st.rerun()

st.markdown('<div class="horizontal-divider"></div>', unsafe_allow_html=True)

# --- FULL-SCREEN PDF VIEWER ---
st.markdown(f'''
    <iframe src="{PDF_PREVIEW_URL}" class="pdf-container" frameborder="0"></iframe>
''', unsafe_allow_html=True)

# --- REGISTRATION MODAL / SECTION (Triggered from Top Bar) ---
if st.session_state.show_register_modal:
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.registered:
        st.markdown("### Complete Quick Registration to Unlock Download")
        
        with st.form("registration_form"):
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
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Failed to register. Please try again. Error: {e}")
                else:
                    st.error("Please provide both your Full Name and Email.")
    else:
        success_html = (
            '<div class="success-box">'
            '<h3 style="font-family: \'Montserrat\', sans-serif; color: #0c1a30; margin-bottom: 10px;">Registration Complete!</h3>'
            f'<p style="font-family: \'Montserrat\', sans-serif; color: #333;">Thank you, <b>{st.session_state.user_name}</b>. Your verified download link is ready below.</p>'
            f'<a href="{DIRECT_DOWNLOAD_URL}" class="custom-download-btn">DOWNLOAD PDF NOW</a>'
            '</div>'
        )
        st.markdown(success_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Close / Reset"):
            st.session_state.show_register_modal = False
            st.rerun()

# --- FOOTER ---
st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)
