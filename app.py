import streamlit as st
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
        "contact": contact if contact else "N/A",
        "email": email
    }
    supabase.table("attendees").insert(data).execute()

# --- SESSION STATE ---
if 'registered' not in st.session_state:
    st.session_state.registered = False
if 'show_register_modal' not in st.session_state:
    st.session_state.show_register_modal = False

# --- URL CONFIGURATION ---
PDF_PREVIEW_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&raw=1"
DIRECT_DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"

# --- CSS INJECTION ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@500;600;700;800&display=swap');

    /* Hide default Streamlit elements */
    header { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    
    /* TOP NAVIGATION BAR */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 70px;
        background-color: #0c1a30;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 40px;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .top-bar-title {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        letter-spacing: 1px !important;
    }
    
    .top-bar-title span {
        color: #c9a35e !important;
    }
    
    /* FULL SCREEN PDF CONTAINER */
    .pdf-fullscreen-container {
        position: fixed;
        top: 70px;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100vw;
        height: calc(100vh - 70px);
        border: none;
        margin: 0;
        padding: 0;
        overflow: hidden;
    }
    
    .pdf-fullscreen-container iframe {
        width: 100%;
        height: 100%;
        border: none;
    }
    
    /* TOP TOOLBAR BLOCKER - Covers PDF viewer toolbar */
    .toolbar-top-blocker {
        position: fixed;
        top: 70px;
        left: 0;
        right: 0;
        height: 45px;
        background: linear-gradient(to bottom, rgba(12, 26, 48, 0.95), rgba(12, 26, 48, 0.7));
        z-index: 999;
        pointer-events: all;
        backdrop-filter: blur(5px);
    }
    
    /* BOTTOM TOOLBAR BLOCKER */
    .toolbar-bottom-blocker {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 50px;
        background-color: #0c1a30;
        z-index: 999;
        pointer-events: all;
    }
    
    .toolbar-blocker-text {
        color: #c9a35e;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-align: center;
        padding-top: 15px;
    }

    /* DOWNLOAD BUTTON IN TOP BAR */
    .top-download-btn {
        background-color: #c9a35e !important;
        color: #0c1a30 !important;
        padding: 10px 25px !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        letter-spacing: 1px !important;
        border: 2px solid #c9a35e !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    
    .top-download-btn:hover {
        background-color: transparent !important;
        color: #c9a35e !important;
    }

    /* REGISTRATION MODAL OVERLAY */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(12, 26, 48, 0.9);
        z-index: 2000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .modal-content {
        background-color: white !important;
        border: 3px solid #c9a35e !important;
        border-radius: 0px !important;
        padding: 40px !important;
        max-width: 500px;
        width: 90%;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.3) !important;
    }

    /* FORM STYLING */
    [data-testid="stForm"] {
        background-color: white !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
        margin: 0 !important;
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
        font-size: 0.85rem !important;
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
        padding: 14px !important;
        margin-top: 10px !important;
    }
    
    [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #c9a35e !important;
        color: #0c1a30 !important;
    }

    /* SUCCESS MESSAGE */
    .success-message {
        background-color: white !important;
        border: 3px solid #c9a35e !important;
        padding: 30px !important;
        text-align: center !important;
        margin: 20px auto !important;
        max-width: 500px;
    }

    @media screen and (max-width: 768px) {
        .top-bar {
            padding: 0 20px !important;
            height: 60px !important;
        }
        .top-bar-title {
            font-size: 1.3rem !important;
        }
        .pdf-fullscreen-container {
            top: 60px !important;
            height: calc(100vh - 60px) !important;
        }
        .toolbar-top-blocker {
            top: 60px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- TOP NAVIGATION BAR ---
top_bar_html = f"""
<div class="top-bar">
    <div class="top-bar-title">THE CONFIDENCE <span>GAP</span></div>
    <button class="top-download-btn" onclick="document.getElementById('download-trigger').click()">
        📥 DOWNLOAD PUBLICATION
    </button>
</div>
"""
st.markdown(top_bar_html, unsafe_allow_html=True)

# Hidden button to trigger registration modal
if not st.session_state.registered:
    st.markdown('<div id="download-trigger" style="display:none;"></div>', unsafe_allow_html=True)
    
    if st.session_state.show_register_modal:
        # Registration Modal Overlay
        modal_html = """
        <div class="modal-overlay">
            <div class="modal-content">
                <h2 style="font-family: 'Cormorant Garamond', serif; color: #0c1a30; font-size: 2rem; margin-bottom: 10px; text-align: center;">
                    Complete Registration
                </h2>
                <p style="font-family: 'Montserrat', sans-serif; color: #333; text-align: center; margin-bottom: 25px; font-size: 0.9rem;">
                    Enter your details to download the full publication
                </p>
        """
        st.markdown(modal_html, unsafe_allow_html=True)
        
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
                        st.session_state.show_register_modal = False
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Failed to register. Please try again. Error: {e}")
                else:
                    st.error("Please provide both your Full Name and Email.")
        
        # Close modal button
        if st.button("CANCEL", key="close_modal"):
            st.session_state.show_register_modal = False
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Check if hidden trigger was activated (via JavaScript click)
    if not st.session_state.show_register_modal:
        if st.button("📥 DOWNLOAD PUBLICATION", key="hidden_download_trigger", type="primary"):
            st.session_state.show_register_modal = True
            st.rerun()

else:
    # Registered user - show success and direct download
    success_html = f"""
    <div style="position: fixed; top: 120px; left: 50%; transform: translateX(-50%); z-index: 1500;">
        <div class="success-message">
            <h3 style="font-family: 'Montserrat', sans-serif; color: #0c1a30; margin-bottom: 10px; font-size: 1.5rem;">
                ✓ Registration Complete!
            </h3>
            <p style="font-family: 'Montserrat', sans-serif; color: #333; margin-bottom: 20px;">
                Thank you, <b>{st.session_state.user_name}</b>. Your download is ready.
            </p>
            <a href="{DIRECT_DOWNLOAD_URL}" 
               style="display: inline-block; background-color: #003366; color: white; padding: 12px 30px; 
                      text-decoration: none; font-family: 'Montserrat', sans-serif; font-weight: 700; 
                      letter-spacing: 1px; border-radius: 0px;"
               download>
               DOWNLOAD PDF NOW
            </a>
            <br>
            <button onclick="location.reload()" 
                    style="background-color: transparent; color: #0c1a30; border: 2px solid #0c1a30; 
                           padding: 8px 20px; margin-top: 15px; cursor: pointer; font-family: 'Montserrat', sans-serif;">
                Close
            </button>
        </div>
    </div>
    """
    st.markdown(success_html, unsafe_allow_html=True)

# --- FULL SCREEN PDF VIEWER WITH TOOLBAR BLOCKERS ---
pdf_html = f'''
<div class="pdf-fullscreen-container">
    <iframe src="{PDF_PREVIEW_URL}" frameborder="0"></iframe>
</div>
<div class="toolbar-top-blocker"></div>
<div class="toolbar-bottom-blocker">
    <div class="toolbar-blocker-text">
        🔒 REGISTER TO DOWNLOAD FULL PUBLICATION
    </div>
</div>
'''
st.markdown(pdf_html, unsafe_allow_html=True)
