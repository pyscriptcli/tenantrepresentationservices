import streamlit as st
import streamlit.components.v1 as components

# --- STEP 1: INITIAL WORKSPACE PROTOCOLS ---
def deploy_workspace_security_protocols():
    """Minified element purging observer."""
    js = """<script>(function(){
    const s=["._profilePreview_gzau3_63","._link_gzau3_10","[class*='_profilePreview']","[class*='_link_gzau3']","a[href*='share.streamlit.io']","a[href*='streamlit.io']","img[src*='avatar']","[class*='avatar']","[class*='_profileImage_gzau3']","img[src*='avatars.githubusercontent.com']","#root > div:nth-child(1) > div > div > div > div > a"];
    function p(){s.forEach(sel=>{document.querySelectorAll(sel).forEach(e=>e.style.setProperty('display','none','important'));if(window.top&&window.top.document){try{window.top.document.querySelectorAll(sel).forEach(e=>e.style.setProperty('display','none','important'))}catch(err){}}});}
    p();new MutationObserver(p).observe(document.body,{childList:true,subtree:true});
    if(window.top&&window.top.document&&window.top.document.body){try{new MutationObserver(p).observe(window.top.document.body,{childList:true,subtree:true})}catch(e){}}
    setInterval(p,200);})();</script>"""
    components.html(js, height=0, width=0)

deploy_workspace_security_protocols()

# --- STEP 2: LIBRARIES & MAIN STREAMLIT ARTIFACTS ---
import pandas as pd
import openpyxl
import re
import io
import requests
import hashlib
from openpyxl import load_workbook

st.set_page_config(page_title="trs.sitesourcing.viewer", layout="wide", initial_sidebar_state="collapsed")

# --- GLOBAL CSS INJECTION ---
st.markdown("""
<style>
    /* Instant CSS blocking framework to hide extraneous avatars and markers */
    ._profilePreview_gzau3_63, ._link_gzau3_10, [class*='_profilePreview'], [class*='_link_gzau3'], 
    [class*='_profileImage_gzau3'], img[src*='avatars.githubusercontent.com'], 
    #root > div:nth-child(1) > div > div > div > div > a, a[href*='share.streamlit.io'], 
    a[href*='streamlit.io'], img[src*='avatar'], [class*='avatar'], #MainMenu, footer, header, 
    button[title="View source"], .stAppDeployButton, div[data-testid="stStatusWidget"] {
        display: none !important; visibility: hidden !important; opacity: 0 !important;
        height: 0 !important; width: 0 !important; pointer-events: none !important;
    }
    .block-container { padding: 0.5rem 1rem !important; max-width: 100% !important; }
    .stButton > button, .stDownloadButton > button {
        background-color: #0b57d0 !important; color: #ffffff !important; border: none !important;
        border-radius: 100px !important; padding: 0.4rem 1rem !important; font-size: 0.85rem !important;
        font-weight: 500 !important; min-height: 34px !important; height: 34px !important; width: 100% !important;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3) !important;
    }
    .stSelectbox label { display: none !important; }
    .stSelectbox > div > div { background-color: #fff !important; border: 1px solid #747775 !important; border-radius: 4px !important; min-height: 34px !important; height: 34px !important; }
    div[data-testid="stHorizontalBlock"] { gap: 0.75rem !important; background: #f0f4f9; padding: 0.5rem; border-radius: 8px; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN VERIFICATION LOGIC ---
TARGET_HASH = "6e7dfba0b39da481db37c3263c61cac6"
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    r1_col1, r1_col2, r1_col3 = st.columns([1, 1.2, 1])
    with r1_col2:
        st.markdown("<h3 style='text-align: center; margin-top:50px;'>Access Required</h3>", unsafe_allow_html=True)
        password_input = st.text_input("Enter password:", type="password", label_visibility="collapsed")
        if st.button("Login", use_container_width=True) or password_input:
            if hashlib.md5(password_input.encode('utf-8')).hexdigest() == TARGET_HASH:
                st.session_state.authenticated = True
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Invalid token string provided.")
    st.stop()

# --- CONFIGURATION ---
SOURCE_URL = "https://docs.google.com/spreadsheets/d/14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE/export?format=xlsx"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/1uS3xmnPi0o4c_EayQtURYDSMMPRDRGSb/export?format=xlsx"

@st.cache_data(ttl=3600)
def download_file(url):
    try:
        res = requests.get(url, timeout=30)
        return io.BytesIO(res.content) if res.status_code == 200 else None
    except:
        return None

def get_placeholders(sheet):
    phs = set()
    for row in sheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                for m in re.findall(r"\{\{(.*?)\}\}", cell.value):
                    phs.add(m.split(":")[0].strip() if ":" in m else m.strip())
    return sorted(list(phs))

def sanitize_tab_name(name, existing):
    c_name = re.sub(r'[\\/*?\[\]:]', '', str(name))[:31] or "Sheet"
    if c_name not in existing:
        existing.add(c_name)
        return c_name
    ctr = 1
    while True:
        n_name = f"{c_name[:27]} ({ctr})"
        if n_name not in existing:
            existing.add(n_name)
            return n_name
        ctr += 1

def parse_site_number(s):
    m = re.match(r"^(\d+)", s)
    return int(m.group(1)) if m else float('inf')

@st.cache_data(ttl=600, show_spinner=False)
def generate_trade_area_report(trade_area):
    global df, placeholders, template_bytes_raw
    ta_data = df[df["TRADE AREA"] == trade_area]
    wb = load_workbook(io.BytesIO(template_bytes_raw))
    orig_sheets = wb.sheetnames
    wb.active.title = "TEMPLATE_TO_DELETE"
    existing = set()
    
    for _, r in ta_data.iterrows():
        s_name = r.get("SITE NAME", "Unknown")
        new_sheet = wb.copy_worksheet(wb["TEMPLATE_TO_DELETE"])
        new_sheet.title = sanitize_tab_name(s_name, existing)
        
        for row in new_sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and "{{" in cell.value:
                    nv = cell.value
                    for ph in placeholders:
                        rx = r"\{\{\s*" + re.escape(ph) + r"(\s*:.*?)?\}\}"
                        if re.search(rx, nv):
                            raw = r.get(ph.upper(), "")
                            if pd.isna(raw) or raw is None: raw = ""
                            if isinstance(raw, float) and raw.is_integer(): v_str = str(int(raw))
                            elif hasattr(raw, 'strftime'): v_str = raw.strftime('%B %d, %Y')
                            else: v_str = str(raw)
                            nv = re.sub(rx, v_str, nv)
                    cell.value = re.sub(r"\{\{.*?\}\}", "", nv).strip()

    if "TEMPLATE_TO_DELETE" in wb.sheetnames:
        wb.remove(wb["TEMPLATE_TO_DELETE"])
    for name in orig_sheets:
        if name in wb.sheetnames and name != "TEMPLATE_TO_DELETE":
            wb.remove(wb[name])
            
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()

# --- NO-SCROLL COMPACT TWO-ROW LAYOUT ---
HTML_FRAMEWORK = """
<!DOCTYPE html>
<html>
<head>
    <style type="text/css">
        body { margin: 0; padding: 0; background-color: #ffffff; font-family: -apple-system, sans-serif; overflow: hidden; }
        .grid-container { width: 100%; padding: 2px; box-sizing: border-box; }
        .waffle { border-collapse: collapse; width: 100%; table-layout: fixed; }
        .waffle td { padding: 4px 6px !important; font-size: 9pt; border: 1px solid #e0e0e0 !important; vertical-align: top; }
        .section-title { font-weight: bold; background-color: #f1f3f4; color: #1f1f1f; font-size: 9.5pt; width: 100%; padding: 4px 6px; border: 1px solid #e0e0e0; margin-bottom: -1px; box-sizing: border-box; }
        .label { font-weight: 500; color: #5f6368; width: 15%; background-color: #fafafa; }
        .value { color: #1f1f1f; width: 35%; word-break: break-word; }
        .flex-container { display: flex; gap: 8px; width: 100%; box-sizing: border-box; margin-bottom: 6px; }
        .flex-col { flex: 1; min-width: 0; }
    </style>
</head>
<body>
<div class="grid-container">
    <div class="flex-container">
        <div class="flex-col">
            <div class="section-title">General Information</div>
            <table class="waffle">
                <tr><td class="label">Trade Area</td><td class="value">_TRADE_AREA_</td></tr>
                <tr><td class="label">Site Name</td><td class="value">_SITE_NAME_</td></tr>
                <tr><td class="label">Site No.</td><td class="value">_SITE_NO_</td></tr>
                <tr><td class="label">Date Started</td><td class="value">_TIMESTAMP_</td></tr>
                <tr><td class="label">Report Submitted</td><td class="value">_DATE_OF_REPORT_</td></tr>
                <tr><td class="label">Lessor</td><td class="value">_LESSOR_</td></tr>
            </table>
        </div>
        <div class="flex-col">
            <div class="section-title">Location</div>
            <table class="waffle">
                <tr><td class="label">Bldg / St</td><td class="value">_UNIT_BLDG_ST_NAME_</td></tr>
                <tr><td class="label">Barangay</td><td class="value">_BARANGAY_DISTRICT_NAME_</td></tr>
                <tr><td class="label">City / Mun.</td><td class="value">_CITY_MUNICIPALITY_</td></tr>
                <tr><td class="label">Region</td><td class="value">_REGION_</td></tr>
                <tr><td class="label">Postal Code</td><td class="value">_POSTAL_CODE_</td></tr>
                <tr><td class="label">Availability Class</td><td class="value">_SITE_AVAILABILITY_CLASS_</td></tr>
            </table>
        </div>
    </div>

    <div class="flex-container" style="margin-bottom: 0;">
        <div class="flex-col">
            <div class="section-title">Terms & Technical Info</div>
            <table class="waffle">
                <tr><td class="label">Availability Date</td><td class="value">_SITE_AVAILABILITY_DATE_</td></tr>
                <tr><td class="label">COL Start</td><td class="value">_COL_START_DATE_</td></tr>
                <tr><td class="label">Lease Terms</td><td class="value">_LEASE_TERMS_</td></tr>
                <tr><td class="label">Area (sqm)</td><td class="value">_LOT_FLOOR_AREA_SQM_</td></tr>
                <tr><td class="label">Frontage</td><td class="value">_FRONTAGE_</td></tr>
                <tr><td class="label">Other Remarks</td><td class="value" style="color: #c00000; font-weight: 500;">_REMARKS_</td></tr>
            </table>
        </div>
        <div class="flex-col">
            <div class="section-title">Rates & Provisions</div>
            <table class="waffle">
                <tr><td class="label" style="color:#c00000;">Monthly Rent</td><td class="value">_MONTHLY_RENTAL_RATE_</td></tr>
                <tr><td class="label" style="color:#c00000;">Escalation Rate</td><td class="value">_ESCALATION_</td></tr>
                <tr><td class="label" style="color:#c00000;">Advance Rental</td><td class="value">_ADVANCE_RENTAL_</td></tr>
                <tr><td class="label" style="color:#c00000;">Sec. Deposit</td><td class="value">_SECURITY_DEPOSIT_</td></tr>
                <tr><td class="label" style="color:#c00000;">CUSA Dues</td><td class="value">_CUSA_</td></tr>
                <tr><td class="label">Lease Type</td><td class="value">_LEASE_TYPE_</td></tr>
            </table>
        </div>
    </div>
</div>
</body>
</html>
"""

with st.spinner("Loading Data Assets..."):
    df, placeholders, template_bytes_raw = load_data()

if df is None:
    st.error("Failed to load data assets.")
    st.stop()

# --- CONTROLS ROW ---
trade_areas = ["Select Trade Area..."] + sorted(df["TRADE AREA"].dropna().unique().tolist())
col1, col2, col3 = st.columns([1.5, 1.5, 0.8])

with col1:
    selected_ta = st.selectbox("Trade Area", options=trade_areas, index=0)
    
with col2:
    if selected_ta and selected_ta != "Select Trade Area...":
        raw_sites = df[df["TRADE AREA"] == selected_ta]["SITE_DISPLAY"].dropna().unique().tolist()
        sites_in_ta = ["Select Site..."] + sorted(raw_sites, key=parse_site_number)
    else:
        sites_in_ta = ["Select Site..."]
    selected_site_display = st.selectbox("Site Name", options=sites_in_ta, index=0)

with col3:
    if selected_ta and selected_ta != "Select Trade Area...":
        st.download_button(
            label="Export XLSX",
            data=lambda: generate_trade_area_report(selected_ta),
            file_name=f"{selected_ta}_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# --- DISPLAY INTERACTIVE SHEET GRID ---
if selected_ta != "Select Trade Area..." and selected_site_display != "Select Site...":
    site_data = df[df["SITE_DISPLAY"] == selected_site_display]
    if not site_data.empty:
        site_row_data = site_data.iloc[0]
        try:
            def process_val(k):
                val = site_row_data.get(k.upper(), "")
                if pd.isna(val) or val is None: return ""
                if isinstance(val, float) and val.is_integer(): return str(int(val))
                if hasattr(val, 'strftime'): return val.strftime('%B %d, %Y')
                return str(val).strip()

            v = HTML_FRAMEWORK
            v = v.replace("_TRADE_AREA_", process_val("TRADE AREA"))
            v = v.replace("_SITE_NAME_", process_val("SITE NAME"))
            v = v.replace("_SITE_NO_", process_val("SITE NO"))
            v = v.replace("_TIMESTAMP_", process_val("TIMESTAMP"))
            v = v.replace("_DATE_OF_REPORT_", process_val("DATE OF REPORT"))
            v = v.replace("_UNIT_BLDG_ST_NAME_", process_val("UNIT #, BLDG/ST # AND ST NAME"))
            v = v.replace("_BARANGAY_DISTRICT_NAME_", process_val("BARANGAY/DISTRICT NAME"))
            v = v.replace("_CITY_MUNICIPALITY_", process_val("CITY/MUNICIPALITY"))
            v = v.replace("_REGION_", process_val("REGION"))
            v = v.replace("_POSTAL_CODE_", process_val("POSTAL CODE"))
            v = v.replace("_SITE_AVAILABILITY_DATE_", process_val("SITE AVAILABILITY DATE"))
            v = v.replace("_MONTHLY_RENTAL_RATE_", process_val("MONTHLY RENTAL RATE"))
            v = v.replace("_COL_START_DATE_", process_val("COL START DATE"))
            v = v.replace("_LEASE_TERMS_", process_val("LEASE TERMS"))
            v = v.replace("_ESCALATION_", process_val("ESCALATION"))
            v = v.replace("_ADVANCE_RENTAL_", process_val("ADVANCE RENTAL"))
            v = v.replace("_SECURITY_DEPOSIT_", process_val("SECURITY DEPOSIT"))
            v = v.replace("_CUSA_", process_val("CUSA"))
            v = v.replace("_LOT_FLOOR_AREA_SQM_", process_val("LOT/FLOOR AREA SQM"))
            v = v.replace("_FRONTAGE_", process_val("FRONTAGE"))
            v = v.replace("_LEASE_TYPE_", process_val("LEASE TYPE"))
            v = v.replace("_LESSOR_", process_val("LESSOR"))
            v = v.replace("_SITE_AVAILABILITY_CLASS_", process_val("SITE AVAILABILITY CLASS"))
            v = v.replace("_REMARKS_", process_val("REMARKS"))
            v = re.sub(r"_[A-Z0-9_]+_", "", v)
            
            # Perfect fit layout window with zero scrolling overhead
            components.html(v, height=395, scrolling=False)
        except Exception as e:
            st.error(f"Error compiling visual framework matrix: {str(e)}")
else:
    st.info("Please select a Trade Area and a Site to initialize matrix rendering view layout.")
