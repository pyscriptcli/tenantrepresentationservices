import streamlit as st
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="The Confidence Gap - Publication", layout="centered", initial_sidebar_state="collapsed")

# --- SUPABASE DATABASE SETUP ---
# Initialize the connection to Supabase using Streamlit Secrets
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
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Montserrat:wght@400;600;700&display=swap');

    /* Hide default Streamlit elements */
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Solid White Background */
    .stApp {
        background-color: #ffffff;
    }

    /* Typography Styles - SIZES INCREASED */
    .header-container {
        margin-top: 20px;
        margin-bottom: 50px;
    }
    
    .title-the { font-family: 'Playfair Display', serif; font-size: 5.5rem; color: #1a2a40; margin: 0; line-height: 1; }
    .title-confidence { font-family: 'Playfair Display', serif; font-size: 8.5rem; color: #1a2a40; margin: 0; line-height: 1; }
    
    .gap-container { display: flex; align-items: center; margin-top: 5px; gap: 20px; }
    .title-gap { font-family: 'Playfair Display', serif; font-size: 9.5rem; color: #cba365; margin: 0; line-height: 0.9; }
    .title-closing { font-family: 'Montserrat', sans-serif; font-size: 1.2rem; color: #1a2a40; font-weight: 600; letter-spacing: 2px; border-left: 4px solid #cba365; padding-left: 20px; line-height: 1.5; }
    
    .title-subtitle { font-family: 'Montserrat', sans-serif; font-size: 1.1rem; color: #1a2a40; font-weight: 700; letter-spacing: 2px; margin-top: 40px; line-height: 1.6; }

    .footer-text { margin-top: 60px; margin-bottom: 20px; text-align: center; font-family: 'Montserrat', sans-serif; color: #1a2a40; font-weight: 600; letter-spacing: 3px; font-size: 0.9rem; }

    /* Adjust Streamlit Block Container */
    .main .block-container {
        padding-top: 2rem; 
        max-width: 750px;
    }

    /* Style Streamlit Form to look exactly like the black bordered box */
    [data-testid="stForm"] {
        background-color: white !important;
        border: 8px solid black !important;
        border-radius: 15px !important;
        padding: 30px 40px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
    }

    /* Style Form Inputs */
    .stTextInput > div > div > input {
        border-radius: 20px;
        background-color: #aebce0; 
        color: #000;
        font-weight: 600;
    }
    .stTextInput label p {
        font-family: 'Montserrat', sans-serif;
        color: #003366 !important;
        font-weight: 700 !important;
        font-size: 0.9rem;
    }

    /* Form Button */
    [data-testid="stFormSubmitButton"] > button {
        background-color: #003366 !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none;
        width: 100%;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #cba365 !important;
        color: white !important;
    }
    
    /* Custom Download Button Styling */
    a.custom-download-btn {
        display: block;
        width: 100%;
        text-align: center;
        background-color: #003366;
        color: white !important;
        padding: 12px 20px;
        border-radius: 20px;
        text-decoration: none;
        font-family: 'Montserrat', sans-serif;
        font-weight: bold;
        font-size: 1rem;
        margin-top: 15px;
        margin-bottom: 15px;
        transition: background-color 0.3s ease;
    }
    a.custom-download-btn:hover {
        background-color: #cba365;
    }
    
    .success-box {
        background-color: white;
        border: 8px solid black;
        border-radius: 15px;
        padding: 30px 40px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- MAIN APP LOGIC ---

# Inject the Enlarged Typography Header
st.markdown("""
    <div class="header-container">
        <p class="title-the">THE</p>
        <p class="title-confidence">CONFIDENCE</p>
        <div class="gap-container">
            <p class="title-gap">GAP</p>
            <p class="title-closing">CLOSING THE DISTANCE<br>BETWEEN FEAR AND FACT.</p>
        </div>
        <p class="title-subtitle">PHILIPPINE REAL ESTATE MARKET OVERVIEW<br>INDUSTRIAL &nbsp;•&nbsp; OFFICE &nbsp;•&nbsp; RETAIL</p>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.registered:
    # 1. REGISTRATION FORM 
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
    # 2. SUCCESS PAGE & DOWNLOAD REVEAL
    download_link = "https://jpyholdings-my.sharepoint.com/:b:/g/personal/sondi_tuazon_primephilippines_com/IQCjmzWqCLZCRo0Khn9zkCWpAfP7pow-_TTcQdB9LDWuIB0?e=rXQ6mY&download=1"
    
    st.markdown(f"""
        <div class="success-box">
            <h3 style="font-family: 'Montserrat', sans-serif; color: #1a2a40;">Registration Successful!</h3>
            <p style="font-family: 'Montserrat', sans-serif; color: #333;">Thank you, <b>{st.session_state.user_name}</b>. You can now download the publication.</p>
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
