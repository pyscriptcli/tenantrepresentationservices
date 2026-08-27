import streamlit as st
from supabase import create_client, Client
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="The Confidence Gap", layout="wide", initial_sidebar_state="collapsed")

# --- SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

def save_registration(name, contact, email):
    data = {"name": name, "contact": contact or "N/A", "email": email}
    supabase.table("attendees").insert(data).execute()

# --- SESSION STATE ---
if 'registered' not in st.session_state:
    st.session_state.registered = False
if 'show_register_modal' not in st.session_state:
    st.session_state.show_register_modal = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- URLS ---
PDF_PREVIEW_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&raw=1"
DIRECT_DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/sabby4jlnqn8n9ba1fdoe/PRIME-PHILIPPINES-2026-MID-YEAR-PUBLICATION-1.pdf?rlkey=jrcmg67cxfsjro9sx83c5tmcx&dl=1"

# --- PDF.js viewer with download/print disabled ---
encoded_pdf = urllib.parse.quote(PDF_PREVIEW_URL, safe='')
VIEWER_URL = (
    f"https://cdn.jsdelivr.net/npm/pdfjs-dist@2.16.105/web/viewer.html"
    f"?file={encoded_pdf}"
    f"&disableDownload=true&disablePrint=true&disableOpenFile=true"
    f"#toolbar=0"
)

# --- GLOBAL CSS ---
st.markdown("""
    <style>
    /* Reset Streamlit padding */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    header, footer, #MainMenu {
        visibility: hidden !important;
    }
    .stApp, .main {
        background: #fff !important;
        margin: 0 !important;
    }

    /* Full‑screen iframe */
    .pdf-iframe {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        border: none;
        z-index: 0;
    }

    /* Top bar – fixed */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 10;
        background: rgba(255,255,255,0.95);
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        padding: 12px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        backdrop-filter: blur(4px);
        box-sizing: border-box;
    }
    .top-bar .brand {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2rem;
        font-weight: 700;
        color: #0c1a30;
        letter-spacing: 0.5px;
    }
    .top-bar .brand span {
        color: #c9a35e;
    }
    .top-bar .actions {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .top-bar .actions .btn {
        background: #003366;
        color: white;
        border: none;
        padding: 10px 24px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        cursor: pointer;
        text-decoration: none;
        transition: background 0.25s;
        border-radius: 0;
    }
    .top-bar .actions .btn:hover {
        background: #c9a35e;
    }
    .top-bar .actions .btn.gold {
        background: #c9a35e;
    }
    .top-bar .actions .btn.gold:hover {
        background: #003366;
    }
    .top-bar .actions .btn.outline {
        background: transparent;
        color: #003366;
        border: 2px solid #003366;
        padding: 8px 20px;
    }
    .top-bar .actions .btn.outline:hover {
        background: #003366;
        color: white;
    }

    /* Modal overlay */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 20;
        display: flex;
        justify-content: center;
        align-items: center;
        animation: fadeIn 0.25s;
    }
    .modal-box {
        background: white;
        padding: 40px 45px;
        max-width: 460px;
        width: 90%;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border-top: 6px solid #c9a35e;
        position: relative;
    }
    .modal-box .close {
        position: absolute;
        top: 12px;
        right: 18px;
        font-size: 28px;
        cursor: pointer;
        color: #888;
        background: transparent;
        border: none;
    }
    .modal-box .close:hover {
        color: #222;
    }
    .modal-box h2 {
        font-family: 'Cormorant Garamond', serif;
        font-weight: 700;
        color: #0c1a30;
        text-align: center;
        margin-top: 0;
        margin-bottom: 6px;
    }
    .modal-box p {
        font-family: 'Montserrat', sans-serif;
        color: #555;
        text-align: center;
        margin-bottom: 20px;
    }
    .modal-box .success {
        text-align: center;
        font-family: 'Montserrat', sans-serif;
        color: #0c1a30;
    }
    .modal-box .success .dl-link {
        display: inline-block;
        margin-top: 15px;
        background: #003366;
        color: white;
        padding: 12px 30px;
        text-decoration: none;
        font-weight: 700;
        font-family: 'Montserrat', sans-serif;
        transition: background 0.3s;
    }
    .modal-box .success .dl-link:hover {
        background: #c9a35e;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.96); }
        to { opacity: 1; transform: scale(1); }
    }

    @media (max-width: 640px) {
        .top-bar { padding: 8px 15px; }
        .top-bar .brand { font-size: 1.2rem; }
        .top-bar .actions .btn { padding: 6px 14px; font-size: 0.7rem; }
        .modal-box { padding: 30px 20px; }
    }
    </style>
""", unsafe_allow_html=True)

# --- FULL‑SCREEN PDF IFRAME ---
st.markdown(f'<iframe src="{VIEWER_URL}" class="pdf-iframe" allowfullscreen></iframe>', unsafe_allow_html=True)

# --- TOP BAR (conditional) ---
top_bar_placeholder = st.empty()

def render_top_bar():
    if st.session_state.registered:
        # Registered: show welcome, direct download, and reset button
        top_bar_placeholder.markdown(f"""
            <div class="top-bar">
                <div class="brand">THE CONFIDENCE <span>GAP</span></div>
                <div class="actions">
                    <span style="font-family: 'Montserrat', sans-serif; font-weight: 600; color: #0c1a30;">
                        👋 {st.session_state.user_name}
                    </span>
                    <a href="{DIRECT_DOWNLOAD_URL}" class="btn gold" download>⬇ DOWNLOAD PDF</a>
                    <button class="btn outline" id="resetBtn">Register Another</button>
                </div>
            </div>
        """, unsafe_allow_html=True)
        # Reset button logic (JS + hidden Streamlit button)
        if st.button("Reset", key="reset_btn", help=""):
            st.session_state.registered = False
            st.session_state.user_name = ""
            st.session_state.show_register_modal = False
            st.rerun()
        st.markdown("""
            <style>div[data-testid="stButton"]:has(button[key="reset_btn"]) { display: none !important; }</style>
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                const resetBtn = document.getElementById('resetBtn');
                if (resetBtn) {
                    resetBtn.addEventListener('click', function() {
                        const hidden = document.querySelector('button[key="reset_btn"]');
                        if (hidden) hidden.click();
                    });
                }
            });
            </script>
        """, unsafe_allow_html=True)
    else:
        # Not registered: show brand and download button
        top_bar_placeholder.markdown("""
            <div class="top-bar">
                <div class="brand">THE CONFIDENCE <span>GAP</span></div>
                <div class="actions">
                    <button class="btn" id="openModalBtn">📥 DOWNLOAD PUBLICATION</button>
                </div>
            </div>
        """, unsafe_allow_html=True)
        # Open modal via hidden button
        if st.button("Open Modal", key="open_modal_btn", help=""):
            st.session_state.show_register_modal = True
            st.rerun()
        st.markdown("""
            <style>div[data-testid="stButton"]:has(button[key="open_modal_btn"]) { display: none !important; }</style>
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                const openBtn = document.getElementById('openModalBtn');
                if (openBtn) {
                    openBtn.addEventListener('click', function() {
                        const hidden = document.querySelector('button[key="open_modal_btn"]');
                        if (hidden) hidden.click();
                    });
                }
            });
            </script>
        """, unsafe_allow_html=True)

render_top_bar()

# --- REGISTRATION MODAL ---
if st.session_state.show_register_modal and not st.session_state.registered:
    # We'll render the modal using a container with fixed positioning via CSS
    with st.container():
        st.markdown("""
            <div class="modal-overlay" id="modalOverlay">
                <div class="modal-box">
                    <button class="close" id="closeModalBtn">✕</button>
                    <h2>Quick Registration</h2>
                    <p>Fill in your details to get the full publication.</p>
        """, unsafe_allow_html=True)

        # Streamlit form inside modal
        with st.form("reg_form", clear_on_submit=False):
            name = st.text_input("FULL NAME *", key="reg_name")
            contact = st.text_input("CONTACT NUMBER (optional)", key="reg_contact")
            email = st.text_input("EMAIL *", key="reg_email")
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
                        st.error(f"Registration failed: {e}")
                else:
                    st.error("Please enter both Full Name and Email.")

        # Close modal via hidden button
        if st.button("Close Modal", key="close_modal_btn", help=""):
            st.session_state.show_register_modal = False
            st.rerun()
        st.markdown("""
            <style>div[data-testid="stButton"]:has(button[key="close_modal_btn"]) { display: none !important; }</style>
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                const closeBtn = document.getElementById('closeModalBtn');
                if (closeBtn) {
                    closeBtn.addEventListener('click', function() {
                        const hidden = document.querySelector('button[key="close_modal_btn"]');
                        if (hidden) hidden.click();
                    });
                }
            });
            </script>
        """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

# If registered, we don't show the modal.
