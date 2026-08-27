import streamlit as st
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="The Confidence Gap - Publication", layout="centered", initial_sidebar_state="collapsed")

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
# Online viewer preview (dl=0) and Direct download (dl=1)
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

    /* Container alignment */
    .main .block-container {
        padding-top: 1.5rem; 
        max-width: 850px;
    }

    /* HEADER TYPOGRAPHY */
    .header-container {
        margin-top: 10px;
        margin-bottom: 25px;
    }
    
    .title-main { 
        font-family: 'Cormorant Garamond', serif !important; 
        font-size: 3.8rem !important; 
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
        font-size: 1.05rem !important; 
        color: #0c1a30 !important; 
        font-weight: 700 !important; 
        letter-spacing: 2px !important; 
        margin-top: 10px !important;
        margin-bottom: 20px !important;
    }

    .horizontal-divider {
        width: 100%;
        height: 2px;
        background-color: #c9a35e;
        margin: 15px 0;
    }
    
    .sub-header-1 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 0.85rem !important; 
        color: #0c1a30 !important; 
        font-weight: 800 !important; 
        letter-spacing: 2.5px !important; 
        margin-bottom: 4px !important;
    }

    .sub-header-2 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 0.8rem !important; 
        color: #0c1a30 !important; 
        font-weight: 600 !important; 
        letter-spacing: 4px !important; 
    }

    /* PDF EMBED CONTAINER */
    .pdf-container {
        border: 2px solid #003366;
        margin-top: 20px;
        margin-bottom: 20px;
        width: 100%;
        height: 600px;
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
        margin-top: 20px !important;
    }

    .footer-text { 
        margin-top: 50px; 
        margin-bottom: 20px; 
        text-align: center; 
        font-family: 'Montserrat', sans-serif !important; 
        color: #0c1a30 !important; 
        font-weight: 700 !important; 
        letter-spacing: 3px !important; 
        font-size: 0.85rem !important; 
    }

    @media screen and (max-width: 768px) {
        .title-main { 
            font-size: 1.8rem !important; 
            letter-spacing: 0px !important;
        }
        .pdf-container {
            height: 400px;
        }
    }
    </style>
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

# --- PDF VIEWER (Always visible online first) ---
st.markdown(f'''
    <iframe src="{PDF_PREVIEW_URL}" class="pdf-container" frameborder="0"></iframe>
''', unsafe_allow_html=True)

# --- REGISTRATION / DOWNLOAD WORKFLOW ---
if not st.session_state.registered:
    
    if not st.session_state.show_register_modal:
        # Trigger button beneath the viewer
        if st.button("📥 DOWNLOAD FULL PUBLICATION"):
            st.session_state.show_register_modal = True
            st.rerun()
            
    if st.session_state.show_register_modal:
        st.markdown("### Complete Quick Registration to Download")
        
        with st.form("registration_form"):
            name = st.text_input("FULL NAME *")
            contact = st.text_input("CONTACT NUMBER (OPTIONAL)")
            email = st.text_input("EMAIL *")
            
            submitted = st.form_submit_button("SUBMIT & UNLOCK DOWNLOAD")
            
            if submitted:
                # Name and Email are required; contact is optional
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
    # --- SUCCESS & DIRECT DOWNLOAD REVEAL ---
    success_html = (
        '<div class="success-box">'
        '<h3 style="font-family: \'Montserrat\', sans-serif; color: #0c1a30; margin-bottom: 10px;">Registration Complete!</h3>'
        f'<p style="font-family: \'Montserrat\', sans-serif; color: #333;">Thank you, <b>{st.session_state.user_name}</b>. Your download link is ready below.</p>'
        f'<a href="{DIRECT_DOWNLOAD_URL}" class="custom-download-btn">DOWNLOAD PDF NOW</a>'
        '</div>'
    )
    st.markdown(success_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Register Another User"):
        st.session_state.registered = False
        st.session_state.show_register_modal = False
        st.rerun()

# --- FOOTER ---
st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)
