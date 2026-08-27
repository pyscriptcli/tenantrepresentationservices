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
    data = {
        "name": name,
        "contact": contact,
        "email": email
    }
    supabase.table("attendees").insert(data).execute()

# --- SESSION STATE ---
if 'page_step' not in st.session_state:
    st.session_state.page_step = 'viewer'

# URLs
SUPABASE_PREVIEW_URL = "https://cyczyaswxkpdcremqnkn.supabase.co/storage/v1/object/public/Midyear/Confidence_Gap_2026_Optimized.pdf"
DROPBOX_ORIGINAL_DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"

# --- DYNAMIC CSS HANDLING (Scroll Lock & Tighter Margins) ---
if st.session_state.page_step == 'viewer':
    # Lock outer scroll, reduce margins, make iframe fill the screen
    layout_css = """
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        overflow: hidden !important;
        height: 100vh !important;
        background-color: #0c1a30 !important;
    }
    .main .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    /* Force iframe to take exact remaining screen height */
    iframe[title="streamlit_components.v1.components.html"] {
        height: calc(100vh - 45px) !important; 
        width: 100% !important;
    }
    /* Make button very compact */
    .topbar-btn-container div[data-testid="stButton"] > button {
        padding: 4px 15px !important;
        font-size: 0.75rem !important;
        min-height: 0 !important;
        margin-top: 8px !important;
    }
    /* Remove vertical gaps in top bar */
    [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    """
else:
    # Allow scrolling for registration/success forms
    layout_css = """
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        overflow: auto !important;
        background-color: #0c1a30 !important;
    }
    .main .block-container {
        padding: 3rem 1rem !important;
        max-width: 100% !important;
    }
    """

# --- GLOBAL STYLES ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@500;600;700;800&display=swap');

    /* Hide Default Streamlit Elements */
    header, #MainMenu, footer {{ visibility: hidden !important; display: none !important; }}
    
    {layout_css}

    /* TOPBAR ACTION BUTTON */
    .topbar-btn-container div[data-testid="stButton"] > button {{
        background-color: #c9a35e !important;
        color: #0c1a30 !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }}

    .topbar-btn-container div[data-testid="stButton"] > button:hover {{
        background-color: #dfb76c !important;
    }}

    /* REGISTRATION & SUCCESS UNIFIED CARD */
    [data-testid="stForm"], .success-box {{
        background-color: #ffffff !important;
        border: 2px solid #c9a35e !important; 
        border-radius: 0px !important;
        padding: 50px 45px !important;
        box-shadow: 0px 15px 40px rgba(0,0,0,0.4) !important;
        margin: 0 auto !important;
        max-width: 650px;
    }}

    /* INPUT FIELDS */
    [data-testid="stTextInput"] > div > div {{
        background-color: transparent !important;
        border: 2px solid #003366 !important;
        border-radius: 0px !important;
        box-shadow: none !important;
    }}

    [data-testid="stTextInput"] > div > div:focus-within {{
        border-color: #c9a35e !important;
    }}

    [data-testid="stTextInput"] input {{
        background-color: transparent !important;
        color: #0c1a30 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
    }}
    
    .stTextInput label p {{
        font-family: 'Montserrat', sans-serif !important;
        color: #003366 !important;
        font-weight: 800 !important;
        font-size: 0.9rem !important;
        letter-spacing: 1px !important;
    }}

    /* PRIMARY CTA BUTTONS */
    [data-testid="stFormSubmitButton"] > button, a.custom-download-btn {{
        background-color: #003366 !important;
        color: white !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border: none !important;
        width: 100% !important;
        padding: 14px !important;
        margin-top: 15px !important;
        text-align: center;
        text-decoration: none;
        display: block;
        transition: background-color 0.2s ease;
    }}
    
    [data-testid="stFormSubmitButton"] > button:hover, a.custom-download-btn:hover {{
        background-color: #c9a35e !important;
        color: #ffffff !important;
    }}

    /* SECONDARY BACK BUTTON */
    .secondary-btn div[data-testid="stButton"] > button {{
        background-color: transparent !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        width: auto !important;
        min-width: 250px;
        padding: 10px !important;
        margin: 25px auto 0 auto !important;
        display: block;
    }}

    .secondary-btn div[data-testid="stButton"] > button:hover {{
        border-color: #c9a35e !important;
        color: #c9a35e !important;
    }}

    .footer-text {{ 
        margin-top: 50px; 
        margin-bottom: 20px; 
        text-align: center; 
        font-family: 'Montserrat', sans-serif !important; 
        color: #4a5c78 !important; 
        font-weight: 700 !important; 
        letter-spacing: 3px !important; 
        font-size: 0.8rem !important; 
    }}
    </style>
""", unsafe_allow_html=True)

# --- VIEW 1: FULLSCREEN VIEWER ---
if st.session_state.page_step == 'viewer':
    
    # Ultra-compact Top Bar Header
    bar_col1, bar_col2 = st.columns([5, 1])
    with bar_col1:
        st.markdown("""
            <div style="padding: 10px 0 0 20px;">
                <span style="font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; font-weight: 700; color: #ffffff; letter-spacing: 1.5px;">
                    THE CONFIDENCE <span style="color: #c9a35e;">GAP</span>
                </span>
            </div>
        """, unsafe_allow_html=True)
    with bar_col2:
        st.markdown('<div class="topbar-btn-container" style="text-align: right; padding-right: 20px;">', unsafe_allow_html=True)
        if st.button("DOWNLOAD PUBLICATION", use_container_width=True):
            st.session_state.page_step = 'register'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Edge-to-edge PDF.js Viewport (Handles its own scrolling internally)
    pdf_viewer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
      <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ 
            width: 100%; 
            height: 100%; 
            overflow-y: auto; 
            overflow-x: hidden; 
            background-color: #0c1a30; 
        }}
        #viewer-container {{ 
            width: 100%; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            padding: 10px 0 50px 0; 
        }}
        /* Render high-res internally, but restrict visual size to fit screen height */
        canvas {{ 
            max-width: 95vw; 
            max-height: 85vh; /* Fits one page per screen height perfectly */
            object-fit: contain; 
            margin-bottom: 20px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.5); 
        }}
        #bottom-bar {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 35px;
            background-color: #0c1a30;
            color: #c9a35e;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Montserrat', sans-serif;
            font-size: 10px;
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
            /* Scale at 2.5x for sharp text, CSS max-height scales it down to fit screen */
            const viewport = page.getViewport({{ scale: 2.5 }});
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            container.appendChild(canvas);
            await page.render({{ canvasContext: context, viewport: viewport }}).promise;
          }}
        }});
      </script>
    </body>
    </html>
    """
    # The height parameter here doesn't restrict it because our global CSS overrides the iframe to fill `100vh`
    components.html(pdf_viewer_html, height=800, scrolling=True)

# --- VIEW 2: REGISTRATION FORM ---
elif st.session_state.page_step == 'register':
    # Everything is rendered inside the form block so it belongs to a single white unified card.
    with st.form("registration_form"):
        st.markdown("""
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="font-family: 'Cormorant Garamond', serif; font-size: 3.2rem; font-weight: 700; color: #0c1a30; margin: 0; line-height: 1.1;">
                THE CONFIDENCE <span style="color: #c9a35e;">GAP</span>
            </h1>
            <p style="font-family: 'Montserrat', sans-serif; font-size: 0.9rem; font-weight: 700; color: #0c1a30; letter-spacing: 2px; margin-top: 10px;">
                CLOSING THE DISTANCE BETWEEN FEAR AND FACT.
            </p>
            <div style="width: 100%; height: 2px; background-color: #c9a35e; margin: 15px 0;"></div>
            <p style="font-family: 'Montserrat', sans-serif; font-size: 0.8rem; font-weight: 800; color: #0c1a30; letter-spacing: 2px; margin-bottom: 5px;">
                PHILIPPINE REAL ESTATE MARKET OVERVIEW
            </p>
            <p style="font-family: 'Montserrat', sans-serif; font-size: 0.75rem; font-weight: 600; color: #0c1a30; letter-spacing: 3px;">
                INDUSTRIAL &bull; OFFICE &bull; RETAIL
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-family: Montserrat; font-weight:800; color:#0c1a30; font-size:0.95rem; text-align:center; letter-spacing:1px; margin-top:30px; margin-bottom:15px;'>ENTER YOUR DETAILS TO UNLOCK DOWNLOAD</p>", unsafe_allow_html=True)
        
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

    # Return Button located outside the white box, blending with the navy bg
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("← Return to Publication Preview", use_container_width=True):
        st.session_state.page_step = 'viewer'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)

# --- VIEW 3: DOWNLOAD READY STEP ---
elif st.session_state.page_step == 'download':
    
    # Unified success box
    success_html = f"""
    <div class="success-box" style="text-align: center;">
        <h1 style="font-family: 'Cormorant Garamond', serif; font-size: 3.2rem; font-weight: 700; color: #0c1a30; margin: 0; line-height: 1.1;">
            THE CONFIDENCE <span style="color: #c9a35e;">GAP</span>
        </h1>
        <div style="width: 100%; height: 2px; background-color: #c9a35e; margin: 25px 0;"></div>
        <h3 style="font-family: 'Montserrat', sans-serif; color: #0c1a30; margin-bottom: 15px; font-weight: 800;">Registration Successful!</h3>
        <p style="font-family: 'Montserrat', sans-serif; color: #555; font-size: 0.95rem; margin-bottom: 30px;">
            Thank you, <b>{st.session_state.get("user_name", "")}</b>. Click below to download the full resolution publication.
        </p>
        <a href="{DROPBOX_ORIGINAL_DOWNLOAD_URL}" target="_blank" class="custom-download-btn">DOWNLOAD FULL PUBLICATION</a>
    </div>
    """
    st.markdown(success_html, unsafe_allow_html=True)
    
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("← Return to Viewer", use_container_width=True):
        st.session_state.page_step = 'viewer'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)
