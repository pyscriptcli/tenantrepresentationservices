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
# Online viewer preview - disabled toolbar and downloads via URL params
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

    /* Remove padding for full-screen */
    .main .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        max-width: 100% !important;
    }

    /* HEADER TYPOGRAPHY */
    .header-container {
        margin-top: 10px;
        margin-bottom: 15px;
        padding: 0 20px;
    }
    
    .title-main { 
        font-family: 'Cormorant Garamond', serif !important; 
        font-size: 3.2rem !important; 
        font-weight: 700 !important; 
        color: #0c1a30 !important; 
        margin: 0 !important; 
        line-height: 1.05 !important;
        letter-spacing: 1px !important;
        white-space: nowrap !important;
    }
    
    .title-gap-gold { 
        font-family: 'Cormorant Garamond', serif !important; 
        color: #c9a35e !important; 
    }

    .tagline { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 0.95rem !important; 
        color: #0c1a30 !important; 
        font-weight: 700 !important; 
        letter-spacing: 2px !important; 
        margin-top: 8px !important;
        margin-bottom: 15px !important;
    }

    .horizontal-divider {
        width: 100%;
        height: 2px;
        background-color: #c9a35e;
        margin: 10px 0;
    }
    
    .sub-header-1 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 0.8rem !important; 
        color: #0c1a30 !important; 
        font-weight: 800 !important; 
        letter-spacing: 2.5px !important; 
        margin-bottom: 4px !important;
    }

    .sub-header-2 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 0.75rem !important; 
        color: #0c1a30 !important; 
        font-weight: 600 !important; 
        letter-spacing: 4px !important; 
    }

    /* FULL-SCREEN PDF CONTAINER */
    .pdf-fullscreen-container {
        position: relative;
        width: 100vw;
        height: calc(100vh - 180px);
        margin: 0;
        padding: 0;
        overflow: hidden;
    }

    .pdf-iframe {
        width: 100%;
        height: 100%;
        border: none;
        pointer-events: auto;
    }

    /* OVERLAY TO BLOCK DOWNLOADS */
    .pdf-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: transparent;
        z-index: 10;
        pointer-events: auto;
    }

    /* FORM CONTAINER */
    [data-testid="stForm"] {
        background-color: white !important;
        border: 3px solid #c9a35e !important; 
        border-radius: 0px !important;
        padding: 30px 35px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05) !important;
        margin: 20px auto !important;
        max-width: 600px !important;
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
        padding: 14px !important;
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
        margin: 20px auto !important;
        max-width: 600px !important;
    }

    .footer-text { 
        margin-top: 30px; 
        margin-bottom: 20px; 
        text-align: center; 
        font-family: 'Montserrat', sans-serif !important; 
        color: #0c1a30 !important; 
        font-weight: 700 !important; 
        letter-spacing: 3px !important; 
        font-size: 0.85rem !important; 
    }

    /* Prevent text selection and right-click */
    .no-select {
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }

    @media screen and (max-width: 768px) {
        .title-main { 
            font-size: 1.8rem !important; 
            letter-spacing: 0px !important;
        }
        .pdf-fullscreen-container {
            height: calc(100vh - 250px);
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- JAVASCRIPT TO DISABLE RIGHT-CLICK AND DOWNLOADS ---
st.markdown("""
    <script>
    // Disable right-click on PDF iframe
    document.addEventListener('contextmenu', function(e) {
        if (e.target.tagName === 'IFRAME') {
            e.preventDefault();
            return false;
        }
    });
    
    // Disable keyboard shortcuts for download
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'p')) {
            e.preventDefault();
            return false;
        }
    });
    </script>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("""
<div class="header-container">
    <h1 class="title-main">THE CONFIDENCE <span class="title-gap-gold">GAP</span></h1>
    <div class="tagline">CLOSING THE DISTANCE BETWEEN FEAR AND FACT.</div>
    <div class="horizontal-divider"></div>
    <div class="sub-header-1">PHILIPPINE REAL ESTATE MARKET OVERVIEW</div>
    <div class="sub-header-2">INDUSTRIAL &nbsp;•&nbsp; OFFICE &nbsp;•&nbsp; RETAIL</div>
</div>
""", unsafe_allow_html=True)

# --- PDF VIEWER WITH DOWNLOAD PROTECTION ---
if not st.session_state.registered:
    # Show full-screen PDF with overlay protection
    st.markdown(f'''
        <div class="pdf-fullscreen-container no-select">
            <iframe 
                src="{PDF_PREVIEW_URL}" 
                class="pdf-iframe"
                frameborder="0"
                oncontextmenu="return false;"
            ></iframe>
            <div class="pdf-overlay" oncontextmenu="return false;"></div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Download button beneath viewer
    st.markdown("<div style='text-align: center; margin: 20px 0;'>", unsafe_allow_html=True)
    if st.button("📥 DOWNLOAD FULL PUBLICATION", use_container_width=True, key="download_btn"):
        st.session_state.show_register_modal = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Registration form
    if st.session_state.show_register_modal:
        st.markdown("<div style='max-width: 600px; margin: 0 auto;'>", unsafe_allow_html=True)
        st.markdown("### Complete Quick Registration to Download")
        
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
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- SUCCESS & DIRECT DOWNLOAD REVEAL ---
    success_html = (
        '<div class="success-box">'
        '<h3 style="font-family: \'Montserrat\', sans-serif; color: #0c1a30; margin-bottom: 10px;">Registration Complete!</h3>'
        f'<p style="font-family: \'Montserrat\', sans-serif; color: #333;">Thank you, <b>{st.session_state.user_name}</b>. Your download link is ready below.</p>'
        f'<a href="{DIRECT_DOWNLOAD_URL}" class="custom-download-btn" download>DOWNLOAD PDF NOW</a>'
        '</div>'
    )
    st.markdown(success_html, unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; margin: 20px 0;'>", unsafe_allow_html=True)
    if st.button("Register Another User", use_container_width=True):
        st.session_state.registered = False
        st.session_state.show_register_modal = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)
