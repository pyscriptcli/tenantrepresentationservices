import streamlit as st
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="The Confidence Gap - Publication", layout="centered", initial_sidebar_state="collapsed")

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
if 'registered' not in st.session_state:
    st.session_state.registered = False

# --- CSS INJECTION ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Montserrat:wght@500;600;700;800&display=swap');

    /* Hide default Streamlit elements */
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Solid White Background */
    .stApp {
        background-color: #ffffff;
    }

    /* Container alignment */
    .main .block-container {
        padding-top: 2rem; 
        max-width: 800px;
    }

    /* HEADER TYPOGRAPHY */
    .header-container {
        margin-top: 10px;
        margin-bottom: 35px;
    }
    
    .title-main { 
        font-family: 'Playfair Display', serif; 
        font-size: 4.8rem; 
        font-weight: 700;
        color: #0c1a30; 
        margin: 0; 
        line-height: 1.05;
        letter-spacing: 1px;
    }
    
    .title-gap-gold {
        color: #c9a35e; /* Signature Gold */
    }

    .tagline { 
        font-family: 'Montserrat', sans-serif; 
        font-size: 1.15rem; 
        color: #0c1a30; 
        font-weight: 700; 
        letter-spacing: 2px; 
        margin-top: 12px;
        margin-bottom: 25px;
    }

    .horizontal-divider {
        width: 100%;
        height: 2px;
        background-color: #c9a35e;
        margin: 20px 0 15px 0;
    }
    
    .sub-header-1 { 
        font-family: 'Montserrat', sans-serif; 
        font-size: 0.9rem; 
        color: #0c1a30; 
        font-weight: 800; 
        letter-spacing: 2.5px; 
        margin-bottom: 6px;
    }

    .sub-header-2 { 
        font-family: 'Montserrat', sans-serif; 
        font-size: 0.85rem; 
        color: #0c1a30; 
        font-weight: 600; 
        letter-spacing: 4px; 
    }

    /* FORM CONTAINER (Black Border Outer Box) */
    [data-testid="stForm"] {
        background-color: white !important;
        border: 8px solid black !important;
        border-radius: 0px !important;
        padding: 35px 40px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
        margin-top: 30px;
    }

    /* FIX FOR INPUT TEXT BOX UI */
    div[data-baseweb="input"] {
        border: 2px solid #003366 !important;
        border-radius: 0px !important;
        background-color: transparent !important;
        box-shadow: none !important;
        padding: 4px 8px !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #c9a35e !important;
    }

    div[data-baseweb="input"] input {
        background-color: transparent !important;
        color: #0c1a30 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    .stTextInput label p {
        font-family: 'Montserrat', sans-serif;
        color: #003366 !important;
        font-weight: 800 !important;
        font-size: 0.95rem;
        letter-spacing: 1px;
    }

    /* SUBMIT BUTTON */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 0px !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700 !important;
        letter-spacing: 1px;
        border: none;
        width: 100%;
        padding: 12px;
        margin-top: 10px;
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
    }
    a.custom-download-btn:hover {
        background-color: #c9a35e;
    }
    
    .success-box {
        background-color: white;
        border: 8px solid black;
        border-radius: 0px !important;
        padding: 35px 40px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        margin-top: 30px;
    }

    .footer-text { 
        margin-top: 60px; 
        margin-bottom: 20px; 
        text-align: center; 
        font-family: 'Montserrat', sans-serif; 
        color: #0c1a30; 
        font-weight: 700; 
        letter-spacing: 3px; 
        font-size: 0.9rem; 
    }
    </style>
""", unsafe_allow_html=True)

# --- MAIN APP LOGIC ---

# Header Section
st.markdown("""
    <div class="header-container">
        <h1 class="title-main">THE CONFIDENCE <span class="title-gap-gold">GAP</span></h1>
        <div class="tagline">CLOSING THE DISTANCE BETWEEN FEAR AND FACT.</div>
        <div class="horizontal-divider"></div>
        <div class="sub-header-1">PHILIPPINE REAL ESTATE MARKET OVERVIEW</div>
        <div class="sub-header-2">INDUSTRIAL &nbsp;•&nbsp; OFFICE &nbsp;•&nbsp; RETAIL</div>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.registered:
    # 1. REGISTRATION FORM 
    with st.form("registration_form"):
        name = st.text_input("NAME")
        contact = st.text_input("CONTACT NUMBER")
        email = st.text_input("EMAIL")
        
        submitted = st.form_submit_button("REGISTER")
        
        if submitted:
            if name and contact and email:
                try:
                    save_registration(name, contact, email)
                    st.session_state.registered = True
                    st.session_state.user_name = name
                    st.rerun() 
                except Exception as e:
                    st.error(f"Failed to register. Please try again. Error: {e}")
            else:
                st.error("Please fill in all fields before submitting.")

else:
    # 2. SUCCESS PAGE & DOWNLOAD REVEAL
    download_link = "https://jpyholdings-my.sharepoint.com/:b:/g/personal/sondi_tuazon_primephilippines_com/IQCjmzWqCLZCRo0Khn9zkCWpAfP7pow-_TTcQdB9LDWuIB0?e=rXQ6mY&download=1"
    
    st.markdown(f"""
        <div class="success-box">
            <h3 style="font-family: 'Montserrat', sans-serif; color: #0c1a30; margin-bottom: 10px;">Registration Successful!</h3>
            <p style="font-family: 'Montserrat', sans-serif; color: #333;">Thank you, <b>{st.session_state.user_name}</b>. Click below to begin your download.</p>
            <a href="{download_link}" class="custom-download-btn" target="_blank">DOWNLOAD PUBLICATION</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Reset Button 
    if st.button("Register Another User", use_container_width=True):
        st.session_state.registered = False
        st.rerun()

# Inject Footer
st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)
