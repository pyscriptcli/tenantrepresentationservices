import base64
import os
import re
from pathlib import Path

import streamlit as st
from supabase import create_client


DOWNLOAD_URL = "https://www.dropbox.com/scl/fi/gq0e9fgy8ya24v3hbr6tu/The-Confidende-Gap.pdf?rlkey=x7zc276sd0dh2bo4znm2ckdmk&st=koyo4weg&dl=1"

st.set_page_config(page_title="The Confidence Gap | PRIME Philippines", layout="wide")


@st.cache_resource
def init_connection():
    url = os.getenv("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
    key = os.getenv("SUPABASE_KEY") or st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


@st.cache_data
def font_styles():
    directory = Path(__file__).with_name("confidencegap_fonts")
    faces = []
    for family, hosted_url in (
        ("Cormorant Garamond", "https://fonts.gstatic.com/s/cormorantgaramond/v21/co3bmX5slCNuHLi8bLeY9MK7whWMhyjYqXtK.woff2"),
        ("Montserrat", "https://fonts.gstatic.com/s/montserrat/v31/JTUSjIg1_i6t8kCHKm459Wlhyw.woff2"),
    ):
        filename = family.lower().replace(" ", "") + ".woff2"
        try:
            data = base64.b64encode((directory / filename).read_bytes()).decode("ascii")
            source = f"data:font/woff2;base64,{data}"
        except FileNotFoundError:
            source = hosted_url
        faces.append(f"@font-face {{font-family:'{family}';font-weight:400 700;"
                     f"font-display:swap;src:url('{source}') format('woff2')}}")
    return "<style>" + "".join(faces) + "</style>"


st.html(font_styles())
st.html("""
<style>
:root {
    --prime-blue:#003366; --prime-warm-white:#fff; --prime-gold:#c9a35e; --navy:#0c1a30;
    --prime-gray:#181D1E; --font-display:'Cormorant Garamond',Georgia,serif;
    --font-ui:Montserrat,Arial,Helvetica,sans-serif;
}
[data-testid="stHeader"] {display:none}
[data-testid="stAppViewContainer"] {background:var(--navy)}
[data-testid="stMainBlockContainer"] {
    width:calc(100% - 1rem);max-width:675px; padding:88px 0 18px; margin-inline:auto;
}
.st-key-publication {
    background:var(--prime-warm-white); color:var(--prime-blue); border:2px solid var(--prime-gold);
    padding:clamp(2rem,10vw,79px) clamp(1rem,7vw,51px) 56px;
    font-family:var(--font-ui);
}
.cover {text-align:center; text-transform:uppercase}
.cover h1 {
    font:700 clamp(1.8rem,.6rem + 6vw,3.6rem)/1.1 var(--font-display);
    color:var(--navy); letter-spacing:0; padding:0; margin:0;
}
.cover h1 span {display:block;color:var(--prime-gold);padding-inline-end:.68em}
.cover p,.panel-title,.panel-note,[data-testid="stTextInput"] label p,
[data-testid="stFormSubmitButton"] button p,.st-key-download_panel a p {font-family:var(--font-ui)}
.cover p {text-wrap:balance;line-height:1.5}
.cover .subtitle {
    font-size:clamp(.81rem,.62rem + .8vw,1.02rem);font-weight:700;letter-spacing:.13em;color:var(--navy);
    margin:clamp(1rem,4vw,1.85rem) 0 0;padding-bottom:1.25rem;border-bottom:2px solid var(--prime-gold);
}
.scope {font-weight:700;font-size:.91rem;letter-spacing:.13em;margin:1.1rem 0 .35rem}
.sector {font-size:.87rem;font-weight:500;letter-spacing:.35em;margin:0}
[data-testid="stForm"] {padding:0;border:0;background:transparent}
.panel-title {color:var(--prime-blue);text-align:center;text-transform:uppercase;text-wrap:balance;
    font-size:clamp(.95rem,.7rem + .8vw,1.07rem);font-weight:700;letter-spacing:.045em;line-height:1.45;
    padding:0;margin:clamp(1rem,5.5vw,3.4rem) 0 .4rem}
.panel-note {color:var(--prime-gray);text-align:center}
[data-testid="stTextInput"] label p {color:var(--prime-blue);font-weight:700;
    font-size:.98rem;letter-spacing:.05em;text-transform:uppercase}
[data-testid="stTextInputRootElement"] {
    background:var(--prime-warm-white);border:2px solid var(--prime-blue);border-radius:0;
    min-height:45px;
}
[data-testid="stTextInput"] input {min-height:41px;background:var(--prime-warm-white);
    color:var(--prime-gray);font:400 1rem/1.5 var(--font-ui)}
[data-testid="stTextInputRootElement"]:focus-within,button:focus-visible,a:focus-visible {
    outline:2px solid var(--prime-blue)!important;outline-offset:3px}
[data-testid="stFormSubmitButton"] button,.st-key-download_panel a {
    background:var(--prime-blue);color:var(--prime-warm-white);border:2px solid var(--prime-blue);
    border-radius:0;min-height:57px;padding:.75rem .9rem;margin-top:1.1rem;text-transform:uppercase;
}
[data-testid="stFormSubmitButton"] button {width:248px}
[data-testid="stFormSubmitButton"] button p {font:600 .92rem/1.45 "Source Sans",Arial,sans-serif;letter-spacing:.035em}
[data-testid="stFormSubmitButton"] button:hover,.st-key-download_panel a:hover {
    color:var(--prime-blue);background:var(--prime-warm-white);border-color:var(--prime-blue)}
@media(min-width:48rem) {
    [data-testid="stMainBlockContainer"] {position:relative;left:-6.5px}
    .panel-title {margin-top:2.86rem}
    [data-testid="stTextInput"] {margin-bottom:4.5px}
    [data-testid="stFormSubmitButton"] button {margin-top:14px}
}
@media(max-width:36rem) {
    [data-testid="stMainBlockContainer"] {padding:.5rem 0}
    .cover h1 span {padding-inline-end:0}
    .st-key-publication {padding-inline:clamp(.85rem,4vw,1.5rem)}
    .scope {font-size:.81rem}
    .stElementContainer:has([data-testid="stFormSubmitButton"]),
    [data-testid="stFormSubmitButton"],[data-testid="stFormSubmitButton"] button {width:100%}
}
@media (max-height: 62rem) {
    [data-testid="stMain"] {display:flex;flex-direction:column}
    [data-testid="stMainBlockContainer"] {flex:none;margin-block:auto}
    [data-testid="stMainBlockContainer"] {padding-block:clamp(6px, 2dvh, 18px)}
    .st-key-publication {padding-block:clamp(12px, 3dvh, 32px)}
    .cover h1 {font-size:clamp(1.8rem, min(7vw, 6dvh), 3.6rem)}
    .cover .subtitle {margin-top:1.4dvh;padding-bottom:1.3dvh}
    .scope {margin-block:.8dvh .25rem}
    .panel-title {margin-block:1.6dvh .25rem}
    [data-testid="stTextInput"] {margin-bottom:0}
    [data-testid="stFormSubmitButton"] button {margin-top:.5dvh;min-height:46px}
    .st-key-publication, [data-testid="stForm"] [data-testid="stVerticalBlock"] {gap:clamp(4px, 1.2dvh, 12px)}
}
@media (max-height: 43rem) {
    [data-testid="stMainBlockContainer"] {padding-block:4px}
    .st-key-publication {padding-block:8px;gap:4px}
    .cover .subtitle,.scope,.panel-title {margin-top:4px}
    .cover .subtitle {padding-bottom:4px}
    [data-testid="stForm"] [data-testid="stVerticalBlock"] {gap:4px}
}
</style>
""")

with st.container(key="publication"):
    st.html("""
    <section class="cover">
      <h1>The Confidence <span>Gap</span></h1>
      <p class="subtitle">Closing the distance between fear and fact.</p>
      <p class="scope">Philippine real estate market overview</p>
      <p class="sector">Retail Report</p>
    </section>
    """)
    if st.session_state.get("page_step") == "download":
        with st.container(key="download_panel"):
            st.html('<h2 class="panel-title">Your publication is ready</h2>'
                    '<p class="panel-note">Registration complete. Download the full midyear report below.</p>')
            st.link_button("Download publication (PDF)", DOWNLOAD_URL)
    else:
        with st.form("registration_form"):
            st.html('<h2 class="panel-title">Enter your details to unlock download</h2>')
            name = st.text_input("Full name", autocomplete="name").strip()
            contact = st.text_input("Contact number", autocomplete="tel").strip()
            email = st.text_input("Email", autocomplete="email").strip()
            submitted = st.form_submit_button("Submit & unlock full PDF")
            if submitted:
                if not all((name, contact, email)):
                    st.error("Enter your full name, contact number and email address.")
                elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                    st.error("Enter an email address such as name@example.com.")
                else:
                    try:
                        with st.spinner("Saving your registration…"):
                            init_connection().table("attendees").insert(
                                {"name": name, "contact": contact, "email": email}
                            ).execute()
                    except Exception:
                        st.error("Registration is unavailable. Your details are still here. Please try again later.")
                    else:
                        st.session_state.page_step = "download"
                        st.rerun()
