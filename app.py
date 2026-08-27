import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client

# --- PAGE CONFIGURATION (Full screen edge-to-edge layout) ---
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
    supabase.table("attendees").insert(data).execute()[cite: 1]

# --- SESSION STATE & LINKS ---
if 'page_step' not in st.session_state:
    st.session_state.page_step = 'viewer'

# Embed URL for SharePoint/OneDrive document viewer
SHAREPOINT_EMBED_URL = "https://jpyholdings-my.sharepoint.com/personal/sondi_tuazon_primephilippines_com/_layouts/15/Doc.aspx?sourcedoc={personal/sondi_tuazon_primephilippines_com/Documents/CRD 2026  COMPILED ONE DRIVE/01_2026 ANNUAL PROPERTY OUTLOOK (1).pdf}&action=embedview&wdStartOn=1"
DOWNLOAD_LINK = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"[cite: 1]

# --- GLOBAL STYLES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@500;600;700;800&display=swap');

    /* Remove Streamlit chrome and margins */
    header, #MainMenu, footer { visibility: hidden !important; display: none !important; }
    
    .stApp {
        background-color: #0c1a30 !important;
    }
    
    .main .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }

    /* TOPBAR BUTTON */
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

    /* FORM STYLES */
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

# --- STEP 1: SHAREPOINT EMBEDDED VIEWER WITH COVERED TOOLBAR ---
if st.session_state.page_step == 'viewer':
    # Top Action Bar
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

    # SharePoint Iframe with a CSS top overlay that hides the OneDrive/SharePoint ribbon header
    sharepoint_viewer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ width: 100%; height: 100%; overflow: hidden; background-color: #0c1a30; }}
        
        .viewer-wrapper {{
            position: relative;
            width: 100%;
            height: calc(100vh - 75px);
            overflow: hidden;
        }}
        
        /* Masks the default SharePoint top toolbar */
        .toolbar-mask {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 52px;
            background-color: #0c1a30;
            z-index: 10;
            display: flex;
            align-items: center;
            padding-left: 20px;
            border-bottom: 1px solid #1d2d44;
        }}
        
        .toolbar-mask span {{
            font-family: 'Montserrat', sans-serif;
            font-size: 11px;
            color: #c9a35e;
            font-weight: 700;
            letter-spacing: 2px;
        }}

        /* Negative top margin pulls iframe upward to tuck SharePoint toolbar under mask */
        iframe {{
            width: 100%;
            height: calc(100% + 52px);
            border: none;
            margin-top: -52px;
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
      <div class="viewer-wrapper">
        <div class="toolbar-mask">
            <span>2026 PROPERTY OUTLOOK &bull; PREVIEW MODE</span>
        </div>
        <iframe src="{SHAREPOINT_EMBED_URL}" allowfullscreen="true"></iframe>
      </div>
      <div id="bottom-bar">🔒 REGISTER TO DOWNLOAD FULL PUBLICATION</div>
    </body>
    </html>
    """
    components.html(sharepoint_viewer_html, height=920)

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
    """, unsafe_allow_html=True)[cite: 1]
    
    with st.form("registration_form"):
        st.markdown("<p style='font-family: Montserrat; font-weight:800; color:#0c1a30; font-size:0.95rem; text-align:center; letter-spacing:1px; margin-bottom:20px;'>ENTER YOUR DETAILS TO UNLOCK DOWNLOAD</p>", unsafe_allow_html=True)
        name = st.text_input("FULL NAME")[cite: 1]
        contact = st.text_input("CONTACT NUMBER")[cite: 1]
        email = st.text_input("EMAIL")[cite: 1]
        
        submitted = st.form_submit_button("SUBMIT & UNLOCK PDF")
        if submitted:
            if name and contact and email:[cite: 1]
                try:
                    save_registration(name, contact, email)[cite: 1]
                    st.session_state.user_name = name[cite: 1]
                    st.session_state.page_step = 'download'
                    st.rerun()[cite: 1]
                except Exception as e:
                    st.error(f"Failed to register. Error: {e}")[cite: 1]
            else:
                st.error("Please fill in all fields.")

    if st.button("← Back to Preview", use_container_width=True):
        st.session_state.page_step = 'viewer'
        st.rerun()

# --- STEP 3: DOWNLOAD READY STEP ---
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
            <a href="{DOWNLOAD_LINK}" class="custom-download-btn">DOWNLOAD FULL PUBLICATION</a>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Back to Viewer", use_container_width=True):
        st.session_state.page_step = 'viewer'
        st.rerun()
