import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client

# --- PAGE CONFIGURATION (Full screen layout) ---
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
        "contact": contact,
        "email": email
    }
    supabase.table("attendees").insert(data).execute()

# --- SESSION STATE ---
if 'page_step' not in st.session_state:
    st.session_state.page_step = 'viewer'

PDF_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&raw=1"
DOWNLOAD_LINK = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"

# --- GLOBAL STYLES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@500;600;700;800&display=swap');

    /* Remove Streamlit default elements and padding */
    header, #MainMenu, footer { visibility: hidden !important; display: none !important; }
    
    .stApp {
        background-color: #0c1a30 !important;
    }
    
    .main .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }

    /* TOPBAR STYLING */
    .topbar-wrapper {
        background-color: #0c1a30;
        padding: 14px 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #1d2d44;
        width: 100%;
        box-sizing: border-box;
    }
    
    .brand-title {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        letter-spacing: 2px !important;
        margin: 0;
    }
    
    .brand-gap {
        color: #c9a35e !important;
    }

    /* Streamlit Button as Topbar Action */
    .viewer-btn-container div[data-testid="stButton"] > button {
        background-color: #c9a35e !important;
        color: #0c1a30 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 10px 22px !important;
        transition: all 0.2s ease !important;
    }

    .viewer-btn-container div[data-testid="stButton"] > button:hover {
        background-color: #dfb76c !important;
        color: #0c1a30 !important;
    }

    /* FORM & SUCCESS CARD STYLES */
    .centered-page-wrapper {
        background-color: #ffffff;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 40px 20px;
    }

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

# --- VIEW 1: FULLSCREEN VIEWER ---
if st.session_state.page_step == 'viewer':
    # Top Bar Header
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

    # Clean Fullscreen PDF.js Viewer (No toolbar/download icon displayed)
    pdfjs_viewer = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
      <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ width: 100%; height: 100%; overflow-x: hidden; background-color: #323639; }}
        #viewer-container {{ width: 100%; display: flex; flex-direction: column; align-items: center; padding: 15px 0 60px 0; }}
        canvas {{ margin-bottom: 18px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); max-width: 95%; height: auto !important; }}
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
      <div id="viewer-container"></div>
      <div id="bottom-bar">🔒 REGISTER TO DOWNLOAD FULL PUBLICATION</div>

      <script>
        const url = "{PDF_URL}";
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

        const loadingTask = pdfjsLib.getDocument(url);
        loadingTask.promise.then(function(pdf) {{
          const container = document.getElementById('viewer-container');
          
          for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {{
            pdf.getPage(pageNum).then(function(page) {{
              const viewport = page.getViewport({{ scale: 1.5 }});
              const canvas = document.createElement('canvas');
              const context = canvas.getContext('2d');
              canvas.height = viewport.height;
              canvas.width = viewport.width;

              container.appendChild(canvas);

              const renderContext = {{
                canvasContext: context,
                viewport: viewport
              }};
              page.render(renderContext);
            }});
          }}
        }}).catch(function(error) {{
            const container = document.getElementById('viewer-container');
            container.innerHTML = '<iframe src="{PDF_URL}#toolbar=0&navpanes=0" width="100%" height="900px" style="border:none;"></iframe>';
        }});
      </script>
    </body>
    </html>
    """
    components.html(pdfjs_viewer, height=920, scrolling=True)

# --- VIEW 2: REGISTRATION STEP ---
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

# --- VIEW 3: DOWNLOAD READY STEP ---
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
