import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="The Confidence Gap - Publication", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase: Client = init_connection()

def save_registration(name, contact, email):
    supabase.table("attendees").insert({"name": name, "contact": contact if contact else "N/A", "email": email}).execute()

if 'page' not in st.session_state:
    st.session_state.page = 'viewer'
if 'registered' not in st.session_state:
    st.session_state.registered = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ''

PDF_PREVIEW_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&raw=1"
DIRECT_DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@500;600;700;800&display=swap');
    header, #MainMenu, footer { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }

    .top-bar {
        position: fixed; top: 0; left: 0; right: 0; height: 70px;
        background-color: #0c1a30; display: flex; align-items: center;
        justify-content: space-between; padding: 0 40px;
        z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .top-bar-title {
        font-family: 'Cormorant Garamond', serif; font-size: 1.8rem;
        font-weight: 700; color: #ffffff; letter-spacing: 1px;
    }
    .top-bar-title span { color: #c9a35e; }
    .top-bar-actions { display: flex; gap: 15px; align-items: center; }

    .nav-btn {
        background-color: transparent !important; color: #ffffff !important;
        padding: 8px 18px !important; border: 1px solid #ffffff !important;
        border-radius: 0px !important; font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important; font-size: 0.85rem !important;
        letter-spacing: 1px !important; cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    .nav-btn:hover { background-color: #ffffff !important; color: #0c1a30 !important; }

    .top-download-btn {
        background-color: #c9a35e !important; color: #0c1a30 !important;
        padding: 10px 25px !important; border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important; font-weight: 700 !important;
        font-size: 0.9rem !important; letter-spacing: 1px !important;
        border: 2px solid #c9a35e !important; cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    .top-download-btn:hover { background-color: transparent !important; color: #c9a35e !important; }

    .pdf-fullscreen-container {
        position: fixed; top: 70px; left: 0; right: 0; bottom: 0;
        width: 100vw; height: calc(100vh - 70px); overflow: hidden;
    }
    .pdf-fullscreen-container iframe { width: 100%; height: 100%; border: none; }

    .toolbar-cover {
        position: fixed; top: 70px; left: 0; right: 0; height: 45px;
        background-color: #0c1a30; z-index: 999; pointer-events: all;
    }

    .brave-warning {
        position: fixed; top: 70px; left: 50%; transform: translateX(-50%);
        background-color: #c9a35e; color: #0c1a30;
        padding: 12px 30px; border-radius: 0; z-index: 1001;
        font-family: 'Montserrat', sans-serif; font-weight: 700;
        font-size: 0.85rem; letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-align: center; max-width: 600px;
    }
    .brave-warning a {
        color: #0c1a30; text-decoration: underline; margin-left: 10px;
    }

    .register-page {
        min-height: 100vh; padding-top: 100px; padding-bottom: 60px;
        display: flex; flex-direction: column; align-items: center;
        background-color: #ffffff;
    }
    .register-card {
        background-color: white; border: 3px solid #c9a35e;
        padding: 40px; max-width: 550px; width: 90%;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05); margin-top: 20px;
    }
    .register-title {
        font-family: 'Cormorant Garamond', serif; color: #0c1a30;
        font-size: 2.2rem; font-weight: 700; text-align: center; margin-bottom: 10px;
    }
    .register-subtitle {
        font-family: 'Montserrat', sans-serif; color: #333;
        text-align: center; margin-bottom: 30px; font-size: 0.95rem;
    }
    .success-box {
        background-color: white; border: 3px solid #c9a35e;
        padding: 40px; text-align: center; max-width: 550px; width: 90%;
    }
    .download-link {
        display: inline-block; background-color: #003366; color: white;
        padding: 14px 30px; text-decoration: none; font-family: 'Montserrat', sans-serif;
        font-weight: 700; letter-spacing: 1px; margin-top: 15px;
    }
    .download-link:hover { background-color: #c9a35e; color: #0c1a30; }

    [data-testid="stForm"] {
        background-color: white !important; border: none !important;
        padding: 0 !important; box-shadow: none !important; margin: 0 !important;
    }
    [data-testid="stTextInput"] > div > div {
        background-color: transparent !important;
        border: 2px solid #003366 !important; border-radius: 0px !important;
    }
    [data-testid="stTextInput"] > div > div:focus-within { border-color: #c9a35e !important; }
    [data-testid="stTextInput"] input {
        color: #0c1a30 !important; font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
    }
    .stTextInput label p {
        font-family: 'Montserrat', sans-serif !important; color: #003366 !important;
        font-weight: 800 !important; font-size: 0.85rem !important; letter-spacing: 1px !important;
    }
    [data-testid="stFormSubmitButton"] > button {
        background-color: #003366 !important; color: white !important;
        border-radius: 0px !important; font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important; letter-spacing: 1px !important;
        border: none !important; width: 100% !important; padding: 14px !important;
        margin-top: 10px !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #c9a35e !important; color: #0c1a30 !important;
    }

    @media screen and (max-width: 768px) {
        .top-bar { padding: 0 20px !important; height: 60px !important; }
        .top-bar-title { font-size: 1.3rem !important; }
        .pdf-fullscreen-container { top: 60px !important; height: calc(100vh - 60px) !important; }
        .toolbar-cover { top: 60px !important; }
    }
    </style>

    <script>
    // Detect Brave browser
    function detectBrave() {
        if (navigator.brave) {
            navigator.brave.isBrave().then(function(isBrave) {
                if (isBrave) {
                    document.getElementById('brave-warning').style.display = 'block';
                }
            }).catch(function() {
                // Fallback detection
                if (navigator.plugins.length === 0 || 
                    (navigator.plugins.length > 0 && 
                     navigator.plugins['Brave Internal Notes'])) {
                    document.getElementById('brave-warning').style.display = 'block';
                }
            });
        }
    }
    window.onload = detectBrave;
    </script>
""", unsafe_allow_html=True)

# --- TOP BAR ---
top_bar_html = """
<div class="top-bar">
    <div class="top-bar-title">THE CONFIDENCE <span>GAP</span></div>
    <div class="top-bar-actions">
"""
if st.session_state.page == 'viewer':
    top_bar_html += """
        <button class="top-download-btn" onclick="document.getElementById('goto-register').click()">
            DOWNLOAD PUBLICATION
        </button>
    """
else:
    top_bar_html += """
        <button class="nav-btn" onclick="document.getElementById('back-to-viewer').click()">
            ← BACK TO VIEWER
        </button>
    """
top_bar_html += "</div></div>"
st.markdown(top_bar_html, unsafe_allow_html=True)

# --- BRAVE WARNING ---
st.markdown("""
<div id="brave-warning" class="brave-warning" style="display: none;">
    ⚠️ Using Brave? Click the lion icon in the address bar and turn OFF "Shields" for this site to view the PDF.
    <a href="https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&raw=1" target="_blank">Or view in new tab →</a>
</div>
""", unsafe_allow_html=True)

# --- ROUTING ---
if st.session_state.page == 'viewer':
    st.markdown('<div id="goto-register" style="display:none;"></div>', unsafe_allow_html=True)
    if st.button("GOTO_REGISTER", key="goto_register_btn"):
        st.session_state.page = 'register'
        st.rerun()

    pdf_html = f'''
    <div class="pdf-fullscreen-container">
        <iframe src="{PDF_PREVIEW_URL}" frameborder="0"></iframe>
    </div>
    <div class="toolbar-cover"></div>
    '''
    st.markdown(pdf_html, unsafe_allow_html=True)

elif st.session_state.page == 'register':
    st.markdown('<div id="back-to-viewer" style="display:none;"></div>', unsafe_allow_html=True)
    if st.button("BACK_TO_VIEWER", key="back_to_viewer_btn"):
        st.session_state.page = 'viewer'
        st.rerun()

    if not st.session_state.registered:
        register_html = """
        <div class="register-page">
            <div class="register-card">
                <div class="register-title">Register to Download</div>
                <div class="register-subtitle">
                    Complete the form below to unlock the full publication download.
                </div>
        """
        st.markdown(register_html, unsafe_allow_html=True)

        with st.form("registration_form"):
            name = st.text_input("FULL NAME *")
            contact = st.text_input("CONTACT NUMBER (OPTIONAL)")
            email = st.text_input("EMAIL *")
            submitted = st.form_submit_button("SUBMIT & UNLOCK DOWNLOAD")

            if submitted:
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

        st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        success_html = f"""
        <div class="register-page">
            <div class="success-box">
                <h3 style="font-family: 'Montserrat', sans-serif; color: #0c1a30; margin-bottom: 10px; font-size: 1.5rem;">
                    ✓ Registration Complete!
                </h3>
                <p style="font-family: 'Montserrat', sans-serif; color: #333; margin-bottom: 20px;">
                    Thank you, <b>{st.session_state.user_name}</b>. Your download is ready.
                </p>
                <a href="{DIRECT_DOWNLOAD_URL}" class="download-link" download>
                    DOWNLOAD PDF NOW
                </a>
                <br>
                <button onclick="document.getElementById('back-to-viewer').click()"
                        style="background-color: transparent; color: #0c1a30; border: 2px solid #0c1a30;
                               padding: 10px 25px; margin-top: 20px; cursor: pointer;
                               font-family: 'Montserrat', sans-serif; font-weight: 600;">
                    ← BACK TO VIEWER
                </button>
            </div>
        </div>
        """
        st.markdown(success_html, unsafe_allow_html=True)
