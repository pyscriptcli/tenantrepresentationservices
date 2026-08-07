import streamlit as st
import qrcode
import sqlite3
import base64
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="The Confidence Gap - Registration", layout="centered", initial_sidebar_state="collapsed")

# --- DATABASE SETUP ---
def init_db():
    """Initializes the SQLite database."""
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT NOT NULL,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_registration(name, contact, email):
    """Saves registration data to SQLite."""
    conn = sqlite3.connect('registrations.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO attendees (name, contact, email) 
        VALUES (?, ?, ?)
    ''', (name, contact, email))
    conn.commit()
    conn.close()

# Initialize database
init_db()

# --- SESSION STATE ---
if 'registered' not in st.session_state:
    st.session_state.registered = False

# --- HELPER FUNCTIONS ---
def generate_qr(data):
    """Generates a QR code and returns the base64 string for HTML injection."""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

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

    /* Typography Styles */
    .header-container {
        margin-top: 20px;
        margin-bottom: 50px;
    }
    
    .title-the { font-family: 'Playfair Display', serif; font-size: 4rem; color: #1a2a40; margin: 0; line-height: 1; }
    .title-confidence { font-family: 'Playfair Display', serif; font-size: 7rem; color: #1a2a40; margin: 0; line-height: 1; }
    
    .gap-container { display: flex; align-items: center; margin-top: 5px; gap: 20px; }
    .title-gap { font-family: 'Playfair Display', serif; font-size: 8rem; color: #cba365; margin: 0; line-height: 0.9; }
    .title-closing { font-family: 'Montserrat', sans-serif; font-size: 1.1rem; color: #1a2a40; font-weight: 600; letter-spacing: 2px; border-left: 3px solid #cba365; padding-left: 15px; line-height: 1.5; }
    
    .title-subtitle { font-family: 'Montserrat', sans-serif; font-size: 1rem; color: #1a2a40; font-weight: 700; letter-spacing: 2px; margin-top: 35px; line-height: 1.6; }

    .footer-text { margin-top: 60px; margin-bottom: 20px; text-align: center; font-family: 'Montserrat', sans-serif; color: #1a2a40; font-weight: 600; letter-spacing: 3px; font-size: 0.9rem; }

    /* Adjust Streamlit Block Container */
    .main .block-container {
        padding-top: 2rem; 
        max-width: 700px;
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
    
    /* Custom QR Code Box Styling */
    .qr-box {
        background-color: white;
        border: 8px solid black;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
        text-align: center;
    }
    .qr-box img {
        width: 100%;
        max-width: 350px;
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
    # 1. REGISTRATION FORM (Styled as the center box)
    with st.form("registration_form"):
        name = st.text_input("NAME")
        contact = st.text_input("CONTACT NUMBER")
        email = st.text_input("EMAIL")
        
        # Spacer
        st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("REGISTER")
        
        if submitted:
            if name and contact and email:
                save_registration(name, contact, email)
                st.session_state.registered = True
                st.session_state.user_name = name
                st.rerun() 
            else:
                st.error("Please fill in all fields before submitting.")

else:
    # 2. SUCCESS PAGE & QR CODE REVEAL
    qr_data = f"ACCESS_GRANTED | Name: {st.session_state.user_name} | Event: The Confidence Gap"
    qr_b64 = generate_qr(qr_data)
    
    # Render the QR code strictly matching the reference image's thick black border layout
    st.markdown(f"""
        <div class="qr-box">
            <img src="data:image/png;base64,{qr_b64}" alt="Your QR Code">
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Download and Reset Buttons 
    col1, col2 = st.columns(2)
    
    # Convert base64 back to bytes for the download button
    qr_bytes = base64.b64decode(qr_b64)
    
    with col1:
        st.download_button(
            label="Download QR Code",
            data=qr_bytes,
            file_name="event_access_qr.png",
            mime="image/png",
            use_container_width=True
        )
    with col2:
        if st.button("New Registration", use_container_width=True):
            st.session_state.registered = False
            st.rerun()

# Inject Footer
st.markdown('<div class="footer-text">EVIDENCE CREATES CONFIDENCE.</div>', unsafe_allow_html=True)
