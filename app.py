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
    """Saves registration data directly to the Supabase cloud database."""
    data = {
        "name": name,
        "contact": contact,
        "email": email
    }
    supabase.table("attendees").insert(data).execute()[cite: 2]

# --- SESSION STATE ---
# Flow stages: "viewer" -> "register" -> "download"
if 'page_step' not in st.session_state:
    st.session_state.page_step = 'viewer'

# Public Supabase Storage URL (Optimized 8.35 MB PDF)
SUPABASE_PDF_URL = "https://cyczyaswxkpdcremqnkn.supabase.co/storage/v1/object/public/Midyear/Confidence_Gap_2026_Optimized.pdf"
DOWNLOAD_LINK = "https://cyczyaswxkpdcremqnkn.supabase.co/storage/v1/object/public/Midyear/Confidence_Gap_2026_Optimized.pdf"

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

    /* Edge-to-edge container */
    .main .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }

    /* HEADER TYPOGRAPHY */
    .header-container {
        margin-top: 10px;
        margin-bottom: 25px;
        text-align: center;
        padding: 0 20px;
    }
    
    .title-main { 
        font-family: 'Cormorant Garamond', serif !important; 
        font-size: 3.6rem !important; 
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
        font-size: 1.05rem !important; 
        color: #0c1a30 !important; 
        font-weight: 700 !important; 
        letter-spacing: 2px !important; 
        margin-top: 10px !important;
        margin-bottom: 20px !important;
    }

    .horizontal-divider {
        width: 100%;
        max-width: 800px;
        height: 2px;
        background-color: #c9a35e;
        margin: 15px auto;
    }
    
    .sub-header-1 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 0.85rem !important; 
        color: #0c1a30 !important; 
        font-weight: 800 !important; 
        letter-spacing: 2.5px !important; 
        margin-bottom: 6px !important;
    }

    .sub-header-2 { 
        font-family: 'Montserrat', sans-serif !important; 
        font-size: 0.8rem !important; 
        color: #0c1a30 !important; 
        font-weight: 600 !important; 
        letter-spacing: 4px !important; 
    }

    /* TOPBAR CTA BUTTON */
    .topbar-btn-container div[data-testid="stButton"] > button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1px !important;
        border: none !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
    }

    .topbar-btn-container div[data-testid="stButton"] > button:hover {
        background-color: #c9a35e !important;
        color: white !important;
    }

    /* FORM & CARD CONTAINER */
    [data-testid="stForm"], .success-box {
        background-color: white !important;
        border: 3px solid #c9a35e !important; 
        border-radius: 0px !important;
        padding: 35px 40px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05) !important;
        margin: 20px auto !important;
        max-width: 650px;
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

    /* FORM SUBMIT BUTTON */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border: none !important;
        width: 100% !important;
        padding: 12px !important;
        margin-top: 10px !important;
    }
    
    [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #c9a35e !important;
        color: white !important;
    }
    
    /* DOWNLOAD BUTTON */
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
        cursor: pointer;
    }
    
    a.custom-download-btn:hover {
        background-color: #c9a35e;
    }

    /* BACK / RESET BUTTON */
    .secondary-btn div[data-testid="stButton"] > button {
        background-color: transparent !important;
        color: #0c1a30 !important;
        border: 2px solid #003366 !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        width: 100% !important;
        padding: 10px !important;
        margin-top: 10px !important;
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
        font-size: 0.9rem !important; 
    }

    @media screen and (max-width: 768px) {
        .title-main { 
            font-size: 2rem !important; 
            letter-spacing: 0px !important;
        }
        
        .tagline { 
            font-size: 0.85rem !important; 
            letter-spacing: 1px !important; 
        }
        
        [data-testid="stForm"], .success-box {
            padding: 20px 20px !important;
            border: 2px solid #c9a35e !important; 
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- VIEW 1: FULLSCREEN VIEWER WITH TOPBAR ---
if st.session_state.page_step == 'viewer':
    # Top Action Bar
    top_col1, top_col2 = st.columns([3.5, 1.2])
    with top_col1:
        st.markdown("""
            <div style="padding: 14px 0 0 25px;">
                <span style="font-family: 'Cormorant Garamond', serif; font-size: 1.9rem; font-weight: 700; color: #0c1a30; letter-spacing: 1px;">
                    THE CONFIDENCE <span style="color: #c9a35e;">GAP</span>
                </span>
            </div>
        """, unsafe_allow_html=True)
    with top_col2:
        st.markdown('<div class="topbar-btn-container" style="padding: 12px 25px 0 0;">', unsafe_allow_html=True)
        if st.button("DOWNLOAD PUBLICATION", use_container_width=True):
            st.session_state.page_step = 'register'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # PDF.js Fullpage Canvas Viewer (Native, no browser PDF toolbars)
    pdf_viewer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
      <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ width: 100%; height: 100%; overflow-x: hidden; background-color: #f4f4f4; }}
        #viewer-container {{ width: 100%; display: flex; flex-direction: column; align-items: center; padding: 15px 0 60px 0; }}
        canvas {{ margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); max-width: 95%; height: auto !important; }}
        #bottom-bar {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 36px;
            background-color: #0c1a30;
            color: #c9a35e;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Montserrat', sans-serif;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
            z-index: 100;
        }}
      </style>
    </head>
    <body>
      <div id="viewer-container"></div>
      <div id="bottom-bar">🔒 REGISTER TO DOWNLOAD FULL PUBLICATION</div>

      <script>
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

        const loadingTask = pdfjsLib.getDocument("{SUPABASE_PDF_URL}");
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
    # Header Section
    st.markdown("""
    <div class="header-container" style="padding-top: 2rem;">
        <h1 class="title-main">THE CONFIDENCE <span class="title-gap-gold">GAP</span></h1>
        <div class="tagline">CLOSING THE DISTANCE BETWEEN FEAR AND FACT.</div>
        <div class="horizontal-divider"></div>
        <div class="sub-header-1">PHILIPPINE REAL ESTATE MARKET OVERVIEW</div>
        <div class="sub-header-2">INDUSTRIAL &nbsp;•&nbsp; OFFICE &nbsp;•&nbsp; RETAIL</div>
    </div>
    """, unsafe_allow_html=True)[cite: 2]

    with st.form("registration_form"):
        name = st.text_input("FULL NAME")[cite: 2]
        contact = st.text_input("CONTACT NUMBER")[cite: 2]
        email = st.text_input("EMAIL")[cite: 2]
        
        submitted = st.form_submit_button("REGISTER TO DOWNLOAD")
        
        if submitted:
            if name and contact and email:[cite: 2]
                try:
                    save_registration(name, contact, email)[cite: 2]
                    st.session_state.user_name = name[cite: 2]
                    st.session_state.page_step = 'download'
                    st.rerun() 
                except Exception as e:
                    st.error(f"Failed to register. Please try again. Error: {e}")[cite: 2]
            else:
                st.error("Please fill in all fields before submitting.")[cite: 2]

    # Return Button
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("← Return to Publication Preview", use_container_width=True):
            st.session_state.page_step = 'viewer'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)[cite: 2]

# --- VIEW 3: SUCCESS & DOWNLOAD CONFIRMATION ---
elif st.session_state.page_step == 'download':
    # Header Section
    st.markdown("""
    <div class="header-container" style="padding-top: 2rem;">
        <h1 class="title-main">THE CONFIDENCE <span class="title-gap-gold">GAP</span></h1>
        <div class="tagline">CLOSING THE DISTANCE BETWEEN FEAR AND FACT.</div>
        <div class="horizontal-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    success_html = (
        '<div class="success-box">'
        '<h3 style="font-family: \'Montserrat\', sans-serif; color: #0c1a30; margin-bottom: 10px; font-weight: 700;">Registration Successful!</h3>'
        f'<p style="font-family: \'Montserrat\', sans-serif; color: #333;">Thank you, <b>{st.session_state.get("user_name", "")}</b>. Click below to download the publication.</p>'
        f'<a href="{DOWNLOAD_LINK}" download="Confidence_Gap_2026.pdf" class="custom-download-btn">DOWNLOAD PUBLICATION</a>'
        '</div>'
    )
    st.markdown(success_html, unsafe_allow_html=True)[cite: 2]
    
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("Back to Viewer", use_container_width=True):
            st.session_state.page_step = 'viewer'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)[cite: 2]
