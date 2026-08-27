import streamlit as st
import streamlit.components.v1 as components
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
    data = {
        "name": name,
        "contact": contact,
        "email": email
    }
    supabase.table("attendees").insert(data).execute()

# --- SESSION STATE & URLS ---
if 'page_step' not in st.session_state:
    st.session_state.page_step = 'viewer'

# Dropbox preview URL with raw/embed parameter
DROPBOX_EMBED_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&st=yd9so3nt&raw=1"
DROPBOX_DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"

# --- GLOBAL STYLES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@500;600;700;800&display=swap');

    /* Remove Streamlit default elements */
    header, #MainMenu, footer { visibility: hidden !important; display: none !important; }
    
    .stApp {
        background-color: #0c1a30 !important;
    }
    
    .main .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }

    /* TOP BAR ACTION BUTTON */
    .viewer-btn-container div[data-testid="stButton"] > button {
        background-color: #c9a35e !important;
        color: #0c1a30 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
    }

    .viewer-btn-container div[data-testid="stButton"] > button:hover {
        background-color: #dfb76c !important;
        color: #0c1a30 !important;
    }

    /* FORM & SUCCESS CARDS */
    [data-testid="stForm"], .success-box {
        background-color: #ffffff !important;
        border: 2px solid #c9a35e !important;
        border-radius: 0px !important;
        padding: 40px !important;
        max-width: 580px;
        margin: 30px auto !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.06) !important;
    }

    [data-testid="stTextInput"] > div > div {
        background-color: transparent !important;
        border: 2px solid #003366 !important;
        border-radius: 0px !important;
    }

    [data-testid="stTextInput"] > div > div:focus-within {
        border-color: #c9a35e !important;
    }

    [data-testid="stTextInput"] input {
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

    [data-testid="stFormSubmitButton"] > button, a.custom-download-btn {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        border: none !important;
        width: 100% !important;
        padding: 14px !important;
        text-align: center;
        text-decoration: none;
        display: block;
        margin-top: 15px;
    }

    [data-testid="stFormSubmitButton"] > button:hover, a.custom-download-btn:hover {
        background-color: #c9a35e !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- STEP 1: DROPBOX VIEWER WITH MASKED TOOLBAR ---
if st.session_state.page_step == 'viewer':
    # Top Bar
    bar_left, bar_right = st.columns([3.5, 1.2])
    with bar_left:
        st.markdown("""
            <div style="padding: 16px 0 0 30px;">
                <span style="font-family: 'Cormorant Garamond', serif; font-size: 2rem; font-weight: 700; color: #ffffff; letter-spacing: 2px;">
                    THE CONFIDENCE <span style="color: #c9a35e;">GAP</span>
                </span>
            </div>
        """, unsafe_allow_html=True)
    with bar_right:
        st.markdown('<div class="viewer-btn-container" style="padding: 12px 30px 0 0;">', unsafe_allow_html=True)
        if st.button("DOWNLOAD PUBLICATION", use_container_width=True):
            st.session_state.page_step = 'register'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Dropbox iframe wrapped with a CSS mask that conceals Dropbox's top controls
    dropbox_viewer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ width: 100%; height: 100%; overflow: hidden; background-color: #0c1a30; }}
        
        .viewer-container {{
            position: relative;
            width: 100%;
            height: calc(100vh - 75px);
            overflow: hidden;
        }}
        
        /* Solid header overlay concealing Dropbox controls */
        .dropbox-mask {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 98px;
            background-color: #0c1a30;
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: center;
            border-bottom: 1px solid #1d2d44;
        }}
        
        .dropbox-mask span {{
            font-family: 'Montserrat', sans-serif;
            font-size: 11px;
            color: #c9a35e;
            font-weight: 700;
            letter-spacing: 2px;
        }}

        /* Negative top margin pulls Dropbox content upwards to tuck its ribbon underneath the mask */
        iframe {{
            width: 100%;
            height: calc(100% + 98px);
            border: none;
            margin-top: -98px;
        }}

        #bottom-bar {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 38px;
            background-color: #0c1a30;
            color: #c9a35e;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Montserrat', sans-serif;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
            border-top: 1px solid #1d2d44;
            z-index: 100;
        }}
      </style>
    </head>
    <body>
      <div class="viewer-container">
        <div class="dropbox-mask">
            <span>2026 ANNUAL PROPERTY OUTLOOK &bull; PREVIEW MODE</span>
        </div>
        <iframe src="{DROPBOX_EMBED_URL}" allowfullscreen="true"></iframe>
      </div>
      <div id="bottom-bar">🔒 REGISTER TO DOWNLOAD FULL PUBLICATION</div>
    </body>
    </html>
    """
    components.html(dropbox_viewer_html, height=920)

# --- STEP 2: REGISTRATION FORM ---
elif st.session_state.page_step == 'register':
    st.markdown("""
        <div style="background-color: #ffffff; padding: 40px 20px 10px 20px; text-align: center;">
            <h1 style="font-family: 'Cormorant Garamond', serif; font-size: 3rem; font-weight: 700; color: #0c1a30; margin: 0;">
                THE CONFIDENCE <span style="color: #c9a35e;">GAP</span>
            </h1>
            <p style="font-family: 'Montserrat', sans-serif; font-size: 0.85rem; font-weight: 700; color: #0c1a30; letter-spacing: 2px; margin-top: 8px;">
                CLOSING THE DISTANCE BETWEEN FEAR AND FACT.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("registration_form"):
        st.markdown("<p style='font-family: Montserrat; font-weight:800; color:#0c1a30; font-size:0.95rem; text-align:center; letter-spacing:1px; margin-bottom:20px;'>ENTER YOUR DETAILS TO UNLOCK DOWNLOAD</p>", unsafe_allow_html=True)
        name = st.text_input("FULL NAME")
        contact = st.text_input("CONTACT NUMBER")
        email = st.text_input("EMAIL")
        
        submitted = st.form_submit_button("SUBMIT & UNLOCK PDF")
        if submitted:
            if name and contact and email:
                try:
                    save_registration(name, contact, email)
                    st.session_state.user_name = name
                    st.session_state.page_step = 'download'
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to register. Error: {e}")
            else:
                st.error("Please fill in all fields.")

    if st.button("← Back to Preview", use_container_width=True):
        st.session_state.page_step = 'viewer'
        st.rerun()

# --- STEP 3: DOWNLOAD CONFIRMATION ---
elif st.session_state.page_step == 'download':
    st.markdown("""
        <div style="background-color: #ffffff; padding: 40px 20px 10px 20px; text-align: center;">
            <h1 style="font-family: 'Cormorant Garamond', serif; font-size: 3rem; font-weight: 700; color: #0c1a30; margin: 0;">
                THE CONFIDENCE <span style="color: #c9a35e;">GAP</span>
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="success-box" style="text-align: center;">
            <h3 style="font-family: 'Montserrat', sans-serif; color: #0c1a30; margin-bottom: 10px; font-weight: 700;">Registration Confirmed</h3>
            <p style="font-family: 'Montserrat', sans-serif; color: #555; font-size: 0.95rem;">Thank you, <b>{st.session_state.get('user_name', '')}</b>. Your file is ready for download.</p>
            <a href="{DROPBOX_DOWNLOAD_URL}" class="custom-download-btn">DOWNLOAD FULL PUBLICATION</a>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Back to Viewer", use_container_width=True):
        st.session_state.page_step = 'viewer'
        st.rerun()
