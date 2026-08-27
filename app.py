import streamlit as st
import streamlit.components.v1 as components
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
        "contact": contact,
        "email": email
    }
    supabase.table("attendees").insert(data).execute()

# --- SESSION STATE ---
# Flow stages: "viewer" -> "register" -> "download"
if 'page_step' not in st.session_state:
    st.session_state.page_step = 'viewer'

# PDF URL (raw=1 / embedded view)
PDF_EMBED_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&raw=1#toolbar=0&navpanes=0"
DOWNLOAD_LINK = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"

# --- CSS INJECTION ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@500;600;700;800&display=swap');

    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    .stApp, .main {
        background-color: #ffffff !important;
    }

    .main .block-container {
        padding-top: 2rem; 
        max-width: 850px;
    }

    /* HEADER TYPOGRAPHY */
    .header-container {
        margin-top: 10px;
        margin-bottom: 25px;
    }
    
    .title-main { 
        font-family: 'Cormorant Garamond', serif !important; 
        font-size: 4.2rem !important; 
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
        font-size: 1.15rem !important; 
        color: #0c1a30 !important; 
        font-weight: 700 !important; 
        letter-spacing: 2px !important; 
        margin-top: 12px !important;
        margin-bottom: 25px !important;
    }

    .horizontal-divider {
        width: 100%;
        height: 2px;
        background-color: #c9a35e;
        margin: 20px 0 15px 0;
    }
    
    .sub-header-1 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 0.9rem !important; 
        color: #0c1a30 !important; 
        font-weight: 800 !important; 
        letter-spacing: 2.5px !important; 
        margin-bottom: 6px !important;
    }

    .sub-header-2 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 0.85rem !important; 
        color: #0c1a30 !important; 
        font-weight: 600 !important; 
        letter-spacing: 4px !important; 
    }

    /* FORM CONTAINER */
    [data-testid="stForm"] {
        background-color: white !important;
        border: 3px solid #c9a35e !important; 
        border-radius: 0px !important;
        padding: 35px 40px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05) !important;
        margin-top: 20px !important;
    }

    /* INPUT FIELDS */
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
        font-size: 0.95rem !important;
        letter-spacing: 1px !important;
    }

    /* BUTTONS */
    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border: none !important;
        width: 100% !important;
        padding: 14px !important;
        margin-top: 10px !important;
        transition: background-color 0.3s ease;
    }

    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #c9a35e !important;
        color: white !important;
    }
    
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
        margin-top: 20px;
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
        padding: 35px 40px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05) !important;
        text-align: center !important;
        margin-top: 30px !important;
    }

    .footer-text { 
        margin-top: 40px; 
        margin-bottom: 20px; 
        text-align: center; 
        font-family: 'Montserrat', sans-serif !important; 
        color: #0c1a30 !important; 
        font-weight: 700 !important; 
        letter-spacing: 3px !important; 
        font-size: 0.9rem !important; 
    }

    @media screen and (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }
        
        .title-main { 
            font-size: 1.8rem !important; 
            white-space: nowrap !important; 
            letter-spacing: 0px !important;
        }
        
        .tagline { 
            font-size: 0.85rem !important; 
            letter-spacing: 1px !important; 
            margin-bottom: 15px !important;
        }
        
        .sub-header-1 { font-size: 0.7rem !important; letter-spacing: 1px !important; }
        .sub-header-2 { font-size: 0.65rem !important; letter-spacing: 2px !important; }
        
        [data-testid="stForm"], .success-box {
            padding: 20px 20px !important;
            border: 2px solid #c9a35e !important; 
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

# --- STEP 1: PDF VIEWER WITH OVERLAY TOPBAR ---
if st.session_state.page_step == 'viewer':
    # Top overlay bar holding the forward CTA button
    top_col1, top_col2 = st.columns([1.8, 1.2])
    with top_col1:
        st.markdown("<p style='font-family: Montserrat; font-weight:700; color:#0c1a30; margin-top:10px;'>PREVIEW PUBLICATION</p>", unsafe_allow_html=True)
    with top_col2:
        if st.button("DOWNLOAD PUBLICATION", use_container_width=True):
            st.session_state.page_step = 'register'
            st.rerun()

    # Embedded viewer container (covers browser PDF chrome)
    viewer_html = f"""
    <div style="position: relative; width: 100%; height: 750px; border: 3px solid #c9a35e; overflow: hidden; background: #525659;">
        <!-- Top cover strip to obscure embedded browser toolbar buttons -->
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 48px; background-color: #0c1a30; z-index: 99; display: flex; align-items: center; justify-content: space-between; padding: 0 15px;">
            <span style="color: #c9a35e; font-family: 'Montserrat', sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 1px;">CONFIDENCE GAP — PREVIEW ONLY</span>
            <span style="color: #ffffff; font-family: 'Montserrat', sans-serif; font-size: 12px;">Full Access Upon Registration</span>
        </div>
        <!-- Viewer Frame -->
        <iframe src="{PDF_EMBED_URL}" width="100%" height="100%" style="border: none; margin-top: 0px;"></iframe>
    </div>
    """
    components.html(viewer_html, height=760)

# --- STEP 2: REGISTRATION FORM ---
elif st.session_state.page_step == 'register':
    with st.form("registration_form"):
        st.markdown("<p style='font-family: Montserrat; font-weight:800; color:#0c1a30; font-size:1.1rem; text-align:center;'>COMPLETE REGISTRATION TO ACCESS DOWNLOAD</p>", unsafe_allow_html=True)
        name = st.text_input("FULL NAME")
        contact = st.text_input("CONTACT NUMBER")
        email = st.text_input("EMAIL")
        
        submitted = st.form_submit_button("UNLOCK & DOWNLOAD")
        
        if submitted:
            if name and contact and email:
                try:
                    save_registration(name, contact, email)
                    st.session_state.user_name = name
                    st.session_state.page_step = 'download'
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to register. Please try again. Error: {e}")
            else:
                st.error("Please fill in all fields before submitting.")

# --- STEP 3: SUCCESS & DOWNLOAD CONFIRMATION ---
elif st.session_state.page_step == 'download':
    success_html = (
        '<div class="success-box">'
        '<h3 style="font-family: \'Montserrat\', sans-serif; color: #0c1a30; margin-bottom: 10px;">Registration Successful!</h3>'
        f'<p style="font-family: \'Montserrat\', sans-serif; color: #333;">Thank you, <b>{st.session_state.get("user_name", "")}</b>. Click below to download the full publication file.</p>'
        f'<a href="{DOWNLOAD_LINK}" class="custom-download-btn">GET PDF COPY</a>'
        '</div>'
    )
    st.markdown(success_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Return to Viewer", use_container_width=True):
        st.session_state.page_step = 'viewer'
        st.rerun()

# --- FOOTER ---
st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)
