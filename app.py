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
    supabase.table("attendees").insert(data).execute()[cite: 1]

# --- SESSION STATE ---
if 'page_step' not in st.session_state:
    st.session_state.page_step = 'viewer'

# --- SUPABASE CDN LINKS ---
PDF_PUBLIC_URL = "https://cyczyaswxkpdcremqnkn.supabase.co/storage/v1/object/public/Midyear/Confidence_Gap_2026_Optimized.pdf"
DOWNLOAD_LINK = "https://cyczyaswxkpdcremqnkn.supabase.co/storage/v1/object/public/Midyear/Confidence_Gap_2026_Optimized.pdf"

# --- GLOBAL STYLES ---
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

    /* TOPBAR ACTION BUTTON */
    .viewer-btn-container div[data-testid="stButton"] > button {
        background-color: #c9a35e !important;
        color: #0c1a30 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1.5px !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 12px 28px !important;
        transition: all 0.2s ease !important;
    }

    .viewer-btn-container div[data-testid="stButton"] > button:hover {
        background-color: #dfb76c !important;
        color: #0c1a30 !important;
    }

    /* CARD CONTAINERS FOR REGISTRATION & SUCCESS */
    [data-testid="stForm"], .success-card {
        background-color: #ffffff !important;
        border: 2px solid #c9a35e !important;
        border-radius: 0px !important;
        padding: 40px 35px !important;
        box-shadow: 0px 12px 35px rgba(0,0,0,0.3) !important;
        text-align: left;
    }

    [data-testid="stTextInput"] > div > div {
        background-color: #ffffff !important;
        border: 1.5px solid #003366 !important;
        border-radius: 0px !important;
    }

    [data-testid="stTextInput"] > div > div:focus-within {
        border-color: #c9a35e !important;
    }

    [data-testid="stTextInput"] input {
        color: #0c1a30 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    .stTextInput label p {
        font-family: 'Montserrat', sans-serif !important;
        color: #003366 !important;
        font-weight: 800 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1px !important;
    }

    /* PRIMARY CTA BUTTONS */
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
        margin-top: 20px;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }

    [data-testid="stFormSubmitButton"] > button:hover, a.custom-download-btn:hover {
        background-color: #c9a35e !important;
        color: #0c1a30 !important;
    }

    /* SECONDARY BACK BUTTON */
    .back-btn-container div[data-testid="stButton"] > button {
        background-color: transparent !important;
        color: #c9a35e !important;
        border: 1px solid #c9a35e !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        letter-spacing: 1px !important;
        padding: 10px !important;
        width: 100% !important;
        margin-top: 15px;
    }

    .back-btn-container div[data-testid="stButton"] > button:hover {
        background-color: rgba(201, 163, 94, 0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- STEP 1: FAST FULLSCREEN VIEWER ---
if st.session_state.page_step == 'viewer':
    bar_left, bar_right = st.columns([3.5, 1.2])
    with bar_left:
        st.markdown("""
            <div style="padding: 18px 0 0 30px;">
                <span style="font-family: 'Cormorant Garamond', serif; font-size: 2.2rem; font-weight: 700; color: #ffffff; letter-spacing: 2px;">
                    THE CONFIDENCE <span style="color: #c9a35e;">GAP</span>
                </span>
            </div>
        """, unsafe_allow_html=True)
    with bar_right:
        st.markdown('<div class="viewer-btn-container" style="padding: 14px 30px 0 0;">', unsafe_allow_html=True)
        if st.button("DOWNLOAD PUBLICATION", use_container_width=True):
            st.session_state.page_step = 'register'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Supabase direct CDN streaming using PDF.js canvas pipeline
    viewer_component = f"""
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
        canvas {{ margin-bottom: 24px; box-shadow: 0 8px 30px rgba(0,0,0,0.6); max-width: 90%; height: auto !important; }}
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
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

        const loadingTask = pdfjsLib.getDocument("{PDF_PUBLIC_URL}");
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
    components.html(viewer_component, height=920, scrolling=True)

# --- STEP 2: REGISTRATION FORM ---
elif st.session_state.page_step == 'register':
    st.markdown("""
        <div style="text-align: center; padding-top: 45px; padding-bottom: 10px;">
            <h1 style="font-family: 'Cormorant Garamond', serif; font-size: 3.2rem; font-weight: 700; color: #ffffff; margin: 0; letter-spacing: 2px;">
                THE CONFIDENCE <span style="color: #c9a35e;">GAP</span>
            </h1>
            <p style="font-family: 'Montserrat', sans-serif; font-size: 0.85rem; font-weight: 700; color: #c9a35e; letter-spacing: 2.5px; margin-top: 10px;">
                CLOSING THE DISTANCE BETWEEN FEAR AND FACT.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        with st.form("registration_form"):
            st.markdown("<p style='font-family: Montserrat; font-weight: 800; color: #0c1a30; font-size: 0.95rem; text-align: center; letter-spacing: 1px; margin-bottom: 25px;'>ENTER YOUR DETAILS TO UNLOCK DOWNLOAD</p>", unsafe_allow_html=True)
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

        st.markdown('<div class="back-btn-container">', unsafe_allow_html=True)
        if st.button("← Back to Publication Preview", use_container_width=True):
            st.session_state.page_step = 'viewer'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- STEP 3: DOWNLOAD READY STEP ---
elif st.session_state.page_step == 'download':
    st.markdown("""
        <div style="text-align: center; padding-top: 45px; padding-bottom: 10px;">
            <h1 style="font-family: 'Cormorant Garamond', serif; font-size: 3.2rem; font-weight: 700; color: #ffffff; margin: 0; letter-spacing: 2px;">
                THE CONFIDENCE <span style="color: #c9a35e;">GAP</span>
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown(f"""
            <div class="success-card" style="text-align: center;">
                <h2 style="font-family: 'Montserrat', sans-serif; color: #0c1a30; font-size: 1.4rem; font-weight: 800; margin-bottom: 15px; letter-spacing: 0.5px;">Registration Confirmed</h2>
                <p style="font-family: 'Montserrat', sans-serif; color: #555; font-size: 0.95rem; margin-bottom: 25px;">
                    Thank you, <b>{st.session_state.get('user_name', '')}</b>. Your file is ready for download.
                </p>
                <a href="{DOWNLOAD_LINK}" download="Confidence_Gap_2026.pdf" class="custom-download-btn">DOWNLOAD FULL PUBLICATION</a>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="back-btn-container">', unsafe_allow_html=True)
        if st.button("← Return to Viewer", use_container_width=True):
            st.session_state.page_step = 'viewer'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
