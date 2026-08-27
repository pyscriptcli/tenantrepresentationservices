import streamlit as st
import streamlit.components.v1 as components
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
        "contact": contact,
        "email": email
    }
    supabase.table("attendees").insert(data).execute()

# --- SESSION STATE ---
if 'page_step' not in st.session_state:
    st.session_state.page_step = 'viewer'

# Fast stream preview from Supabase & Full-resolution original download from Dropbox
SUPABASE_PREVIEW_URL = "https://cyczyaswxkpdcremqnkn.supabase.co/storage/v1/object/public/Midyear/Confidence_Gap_2026_Optimized.pdf"
DROPBOX_ORIGINAL_DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"

# --- GLOBAL CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@500;600;700;800&display=swap');

    /* Remove default Streamlit whitespace, headers, footers */
    header, #MainMenu, footer { visibility: hidden !important; display: none !important; }
    
    .stApp {
        background-color: #0c1a30 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .main .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }

    /* TOPBAR CONTAINER & ACTION BUTTON */
    .topbar-wrapper {
        background-color: #0c1a30;
        padding: 12px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #1a2a44;
    }

    .topbar-btn-container div[data-testid="stButton"] > button {
        background-color: #c9a35e !important;
        color: #0c1a30 !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1px !important;
        border: none !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }

    .topbar-btn-container div[data-testid="stButton"] > button:hover {
        background-color: #dfb76c !important;
        color: #0c1a30 !important;
    }

    /* REGISTRATION & SUCCESS FORMS */
    .light-theme-bg {
        background-color: #ffffff;
        min-height: 100vh;
        padding: 40px 20px;
    }

    .header-container {
        text-align: center;
        margin-bottom: 30px;
    }

    .title-main { 
        font-family: 'Cormorant Garamond', serif !important; 
        font-size: 3.4rem !important; 
        font-weight: 700 !important; 
        color: #0c1a30 !important; 
        margin: 0 !important; 
        line-height: 1.05 !important;
        letter-spacing: 1px !important;
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
        margin-top: 10px !important;
        margin-bottom: 15px !important;
    }

    .horizontal-divider {
        width: 100%;
        max-width: 600px;
        height: 2px;
        background-color: #c9a35e;
        margin: 15px auto;
    }
    
    .sub-header-1 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 0.8rem !important; 
        color: #0c1a30 !important; 
        font-weight: 800 !important; 
        letter-spacing: 2px !important; 
        margin-bottom: 4px !important;
    }

    .sub-header-2 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 0.75rem !important; 
        color: #0c1a30 !important; 
        font-weight: 600 !important; 
        letter-spacing: 3px !important; 
    }

    [data-testid="stForm"], .success-box {
        background-color: #ffffff !important;
        border: 2.5px solid #c9a35e !important; 
        border-radius: 0px !important;
        padding: 35px 40px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.06) !important;
        margin: 0 auto !important;
        max-width: 580px;
    }

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

    [data-testid="stFormSubmitButton"] > button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border: none !important;
        width: 100% !important;
        padding: 13px !important;
        margin-top: 10px !important;
    }
    
    [data-testid="stFormSubmitButton"] > button:hover {
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
        font-size: 0.95rem;
        letter-spacing: 1px;
        margin-top: 20px;
        margin-bottom: 10px;
        transition: background-color 0.3s ease;
        cursor: pointer;
    }
    
    a.custom-download-btn:hover {
        background-color: #c9a35e;
    }

    .secondary-btn div[data-testid="stButton"] > button {
        background-color: transparent !important;
        color: #003366 !important;
        border: 1.5px solid #003366 !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        width: 100% !important;
        padding: 10px !important;
        margin-top: 15px;
    }

    .secondary-btn div[data-testid="stButton"] > button:hover {
        border-color: #c9a35e !important;
        color: #c9a35e !important;
    }

    .footer-text { 
        margin-top: 40px; 
        margin-bottom: 20px; 
        text-align: center; 
        font-family: 'Montserrat', sans-serif !important; 
        color: #0c1a30 !important; 
        font-weight: 700 !important; 
        letter-spacing: 3px !important; 
        font-size: 0.85rem !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- VIEW 1: FULLSCREEN VIEWER ---
if st.session_state.page_step == 'viewer':
    # Top Bar
    bar_col1, bar_col2 = st.columns([3.8, 1.2])
    with bar_col1:
        st.markdown("""
            <div style="padding: 14px 0 0 35px;">
                <span style="font-family: 'Cormorant Garamond', serif; font-size: 2rem; font-weight: 700; color: #ffffff; letter-spacing: 1.5px;">
                    THE CONFIDENCE <span style="color: #c9a35e;">GAP</span>
                </span>
            </div>
        """, unsafe_allow_html=True)
    with bar_col2:
        st.markdown('<div class="topbar-btn-container" style="padding: 12px 35px 0 0; text-align: right;">', unsafe_allow_html=True)
        if st.button("DOWNLOAD PUBLICATION", use_container_width=True):
            st.session_state.page_step = 'register'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Edge-to-edge PDF.js Viewport
    pdf_viewer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
      <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ width: 100%; height: 100%; overflow-x: hidden; background-color: #0c1a30; }}
        #viewer-container {{ width: 100%; display: flex; flex-direction: column; align-items: center; padding: 20px 0 60px 0; }}
        canvas {{ margin-bottom: 22px; box-shadow: 0 8px 30px rgba(0,0,0,0.6); max-width: 90%; height: auto !important; }}
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
            border-top: 1px solid #1a2a44;
            z-index: 100;
        }}
      </style>
    </head>
    <body>
      <div id="viewer-container"></div>
      <div id="bottom-bar">🔒 REGISTER TO DOWNLOAD FULL PUBLICATION</div>

      <script>
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

        const loadingTask = pdfjsLib.getDocument("{SUPABASE_PREVIEW_URL}");
        loadingTask.promise.then(async function(pdf) {{
          const container = document.getElementById('viewer-container');
          
          for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {{
            const page = await pdf.getPage(pageNum);
            const viewport = page.getViewport({{ scale: 1.5 }});
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            container.appendChild(canvas);

            await page.render({{
              canvasContext: context,
              viewport: viewport
            }}).promise;
          }}
        }});
      </script>
    </body>
    </html>
    """
    components.html(pdf_viewer_html, height=920, scrolling=True)

# --- VIEW 2: REGISTRATION FORM ---
elif st.session_state.page_step == 'register':
    st.markdown("""
    <div style="background-color: #ffffff; min-height: 100vh; padding: 40px 20px 20px 20px;">
        <div class="header-container">
            <h1 class="title-main">THE CONFIDENCE <span class="title-gap-gold">GAP</span></h1>
            <div class="tagline">CLOSING THE DISTANCE BETWEEN FEAR AND FACT.</div>
            <div class="horizontal-divider"></div>
            <div class="sub-header-1">PHILIPPINE REAL ESTATE MARKET OVERVIEW</div>
            <div class="sub-header-2">INDUSTRIAL &nbsp;•&nbsp; OFFICE &nbsp;•&nbsp; RETAIL</div>
        </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1.8, 1])
    with col_m:
        with st.form("registration_form"):
            st.markdown("<p style='font-family: Montserrat; font-weight:800; color:#0c1a30; font-size:0.95rem; text-align:center; letter-spacing:1px; margin-bottom:20px;'>ENTER YOUR DETAILS TO UNLOCK DOWNLOAD</p>", unsafe_allow_html=True)
            name = st.text_input("FULL NAME")
            contact = st.text_input("CONTACT NUMBER")
            email = st.text_input("EMAIL")
            
            submitted = st.form_submit_button("SUBMIT & UNLOCK FULL PDF")
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
                    st.error("Please fill in all fields.")

        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("← Back to Preview", use_container_width=True):
            st.session_state.page_step = 'viewer'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- VIEW 3: DOWNLOAD READY STEP ---
elif st.session_state.page_step == 'download':
    st.markdown("""
    <div style="background-color: #ffffff; min-height: 100vh; padding: 40px 20px 20px 20px;">
        <div class="header-container">
            <h1 class="title-main">THE CONFIDENCE <span class="title-gap-gold">GAP</span></h1>
            <div class="tagline">CLOSING THE DISTANCE BETWEEN FEAR AND FACT.</div>
            <div class="horizontal-divider"></div>
        </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1.8, 1])
    with col_m:
        success_html = (
            '<div class="success-box" style="text-align: center;">'
            '<h3 style="font-family: \'Montserrat\', sans-serif; color: #0c1a30; margin-bottom: 10px; font-weight: 700;">Registration Confirmed</h3>'
            f'<p style="font-family: \'Montserrat\', sans-serif; color: #555; font-size: 0.95rem;">Thank you, <b>{st.session_state.get("user_name", "")}</b>. Click below to download the full resolution publication.</p>'
            f'<a href="{DROPBOX_ORIGINAL_DOWNLOAD_URL}" class="custom-download-btn">DOWNLOAD FULL PUBLICATION</a>'
            '</div>'
        )
        st.markdown(success_html, unsafe_allow_html=True)
        
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("← Return to Viewer", use_container_width=True):
            st.session_state.page_step = 'viewer'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
