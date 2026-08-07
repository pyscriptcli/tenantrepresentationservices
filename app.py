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

# --- CSS INJECTION (MATCHING REFERENCE IMAGE & SHARP SQUARED FIELDS) ---
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

    /* HEADER TYPOGRAPHY (Matched to Reference Image) */
    .header-container {
        margin-top: 10px;
        margin-bottom: 40px;
    }
    
    .title-the { 
        font-family: 'Playfair Display', serif; 
        font-size: 3.8rem; 
        color: #0c1a30; 
        margin: 0; 
        line-height: 0.95;
        letter-spacing: 2px;
    }
    
    .title-confidence { 
        font-family: 'Playfair Display', serif; 
        font-size: 7.2rem; 
        font-weight: 700;
        color: #0c1a30; 
        margin: 0; 
        line-height: 0.95;
        letter-spacing: 1px;
    }
    
    .gap-row { 
        display: flex; 
        align-items: center; 
        margin-top: 5px; 
    }
    
    .title-gap { 
        font-family: 'Playfair Display', serif; 
        font-size: 8rem; 
        font-weight: 700;
        color: #c9a35e; /* Gold tone from reference image */
        margin: 0; 
        line-height: 0.85; 
    }
    
    .vertical-divider {
        width: 1.5px;
        height: 75px;
        background-color: #c9a35e;
        margin: 0 25px;
    }

    .tagline { 
        font-family: 'Montserrat', sans-serif; 
        font-size: 1.05rem; 
        color: #0c1a30; 
        font-weight: 600; 
        letter-spacing: 2px; 
        line-height: 1.45;
    }

    .horizontal-divider {
        width: 60%;
        height: 1.5px;
        background-color: #c9a35e;
        margin: 25px 0 15px 0;
    }
    
    .sub-header-1 { 
        font-family: 'Montserrat', sans-serif; 
        font-size: 0.85rem; 
        color: #0c1a30; 
        font-weight: 800; 
        letter-spacing: 2.5px; 
        margin-bottom: 5px;
    }

    .sub-header-2 { 
        font-family: 'Montserrat', sans-serif; 
        font-size: 0.85rem; 
        color: #0c1a30; 
        font-weight: 600; 
        letter-spacing: 4px; 
    }

    /* FORM & INPUT FIELD STYLING (Square with Sharp Edges) */
    [data-testid="stForm"] {
        background-color: white !important;
        border: 8px solid black !important;
        border-radius: 0px !important; /* Sharp box */
        padding: 35px 40px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
        margin-top: 30px;
    }

    /* Text Input Boxes - Sharp/Square Edges */
    .stTextInput > div > div > input {
        border-radius: 0px !important; /* Forces square sharp edges */
        background-color: #aebce0; 
        color: #000;
        font-weight: 600;
        border: 1px solid #8e9ec7 !important;
        padding: 10px 15px;
    }
    
    .stTextInput label p {
        font-family: 'Montserrat', sans-serif;
        color: #003366 !important;
        font-weight: 800 !important;
        font-size: 0.95rem;
        letter-spacing: 1px;
    }

    /* Submit Button - Sharp/Square Edges */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 0px !important; /* Forces sharp edges */
        font-family: 'Montserrat', sans-serif;
        font-weight: 700 !important;
        letter-spacing: 1px;
        border: none;
        width: 100%;
        padding: 12px;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #c9a35e !important;
        color: white !important;
    }
    
    /* Download Button - Sharp/Square Edges */
    a.custom-download-btn {
        display: block;
        width: 100%;
        text-align: center;
        background-color: #003366;
        color: white !important;
        padding: 14px 20px;
        border-radius: 0px !important; /* Sharp edges */
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
        border-radius: 0px !important; /* Sharp edges */
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

# Inject Typography Layout Matching Reference Image
st.markdown("""
    <div class="header-container">
        <p class="title-the">THE</p>
        <p class="title-confidence">CONFIDENCE</p>
        <div class="gap-row">
            <p class="title-gap">GAP</p>
            <div class="vertical-divider"></div>
            <div class="tagline">
                CLOSING THE DISTANCE<br>BETWEEN FEAR AND FACT.
            </div>
        </div>
        <div class="horizontal-divider"></div>
        <div class="sub-header-1">PHILIPPINE REAL ESTATE MARKET OVERVIEW</div>
        <div class="sub-header-2">INDUSTRIAL &nbsp;•&nbsp; OFFICE &nbsp;•&nbsp; RETAIL</div>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.registered:
    # 1. REGISTRATION FORM (Square with Sharp Edges)
    with st.form("registration_form"):
        name = st.text_input("NAME")
        contact = st.text_input("CONTACT NUMBER")
        email = st.text_input("EMAIL")
        
        # Spacer
        st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("REGISTER")
        
        if submitted:
            if name and contact and email:
                try:
                    # Save to Supabase
                    save_registration(name, contact, email)
                    st.session_state.registered = True
                    st.session_state.user_name = name
                    st.rerun() 
                except Exception as e:
                    st.error(f"Failed to register. Please try again. Error: {e}")
            else:
                st.error("Please fill in all fields before submitting.")

else:
    # 2. SUCCESS PAGE & DIRECT DOWNLOAD REVEAL
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
