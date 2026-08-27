import streamlit as st
import fitz  # PyMuPDF
import requests
import base64
import json
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

# --- CACHED RENDERING & SUPABASE PERSISTENCE ---
PUBLICATION_KEY = "confidence_gap_2026_midyear"
DROPBOX_RAW_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&raw=1"
DOWNLOAD_LINK = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"

@st.cache_data(show_spinner="Loading document preview...")
def get_or_create_rendered_pdf():
    # 1. Check if rendered version exists in Supabase
    try:
        res = supabase.table("publication_cache").select("pages_json").eq("publication_key", PUBLICATION_KEY).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]["pages_json"]
    except Exception:
        pass

    # 2. If not found, download & render PDF pages
    response = requests.get(DROPBOX_RAW_URL)
    pdf_bytes = response.content
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    images_base64 = []
    for page in doc:
        pix = page.get_pixmap(dpi=140)
        img_bytes = pix.tobytes("jpeg")
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        images_base64.append(f"data:image/jpeg;base64,{b64}")

    # 3. Save rendered pages to Supabase for all future visits
    try:
        supabase.table("publication_cache").upsert({
            "publication_key": PUBLICATION_KEY,
            "pages_json": images_base64
        }).execute()
    except Exception as e:
        st.warning(f"Could not write cache to database: {e}")

    return images_base64

# --- SESSION STATE ---
if 'page_step' not in st.session_state:
    st.session_state.page_step = 'viewer'

# --- CSS INJECTION ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@500;600;700;800&display=swap');

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

    /* VIEWER SCROLL CONTAINER */
    .pdf-stream-wrapper {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px 0 60px 0;
        background-color: #111e33;
    }

    .pdf-page-img {
        max-width: 85%;
        width: 1000px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }

    #bottom-bar {
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

# --- STEP 1: PDF VIEWER ---
if st.session_state.page_step == 'viewer':
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

    pages = get_or_create_rendered_pdf()
    img_tags = "".join([f'<img class="pdf-page-img" src="{src}" alt="Page" />' for src in pages])
    
    st.markdown(f"""
        <div class="pdf-stream-wrapper">
            {img_tags}
        </div>
        <div id="bottom-bar">🔒 REGISTER TO DOWNLOAD FULL PUBLICATION</div>
    """, unsafe_allow_html=True)

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
            <a href="{DOWNLOAD_LINK}" class="custom-download-btn">DOWNLOAD FULL PUBLICATION</a>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Back to Viewer", use_container_width=True):
        st.session_state.page_step = 'viewer'
        st.rerun()
