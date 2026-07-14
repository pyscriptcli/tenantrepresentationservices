import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from openpyxl.utils import get_column_letter, range_boundaries
import re
import io
import requests
from copy import copy
import os
import hashlib
from openpyxl import load_workbook
import streamlit.components.v1 as components
import base64

#--- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="trs.sitesourcing.viewer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#--- GLOBAL STYLESHEET ENFORCER ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');

* { font-family: 'Google Sans', 'Roboto', 'Segoe UI', sans-serif !important; }

/* Hide default streamlit layout elements to allow true full screen experience */
header[data-testid="stHeader"], 
[data-testid="stHeader"], 
.stApp > header,
div[data-testid="stDecoration"] {
    display: none !important;
    height: 0px !important;
    opacity: 0 !important;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .block-container {
    padding: 0px !important;
    margin: 0px !important;
    width: 100% !important;
    height: 100vh !important;
    overflow: hidden !important;
    background-color: #ffffff !important;
}

/* Remove internal padding from streamlit columns and rows */
div[data-testid="stVerticalBlock"] > div {
    padding: 0px !important;
    margin: 0px !important;
}

/* Hide UI Deployment watermarks cleanly */
#MainMenu, .stAppDeployButton, div[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
}
</style>
""", unsafe_allow_html=True)

#--- RUNTIME WORKSPACE SECURITY OBSERVERS ---
def deploy_workspace_security_protocols():
    injected_js = """
    <script>
    (function() {
        const restrictedUrls = ["https://share.streamlit.io/user/pyscriptcli", "https://streamlit.io/cloud"];
        function checkAndBlockUrl(url) {
            if (!url) return false;
            const shouldBlock = restrictedUrls.some(blockedUrl => url.toLowerCase().trim().includes(blockedUrl.toLowerCase().trim()));
            if (shouldBlock) {
                window.stop();
                if (window.top) { window.top.location.href = window.location.origin; }
                else { window.location.href = window.location.origin; }
                return true;
            }
            return false;
        }
        document.addEventListener('click', function(e) {
            const target = e.target.closest('a');
            if (target && target.href) {
                if (checkAndBlockUrl(target.href)) {
                    e.preventDefault(); e.stopPropagation();
                }
            }
        }, true);
        setInterval(function() {
            try {
                checkAndBlockUrl(window.location.href);
                if (window.top && window.top !== window) { checkAndBlockUrl(window.top.location.href); }
            } catch(e) {}
        }, 1000);
    })();
    </script>
    """
    components.html(injected_js, height=0, width=0)

deploy_workspace_security_protocols()

#--- PROGRAMMATIC LIGHT MODE LOCK ---
_config_dir = ".streamlit"
_config_file = os.path.join(_config_dir, "config.toml")
if not os.path.exists(_config_file):
    os.makedirs(_config_dir, exist_ok=True)
    with open(_config_file, "w", encoding="utf-8") as f:
        f.write('[theme]\nbase="light"\n')

#--- LOGIN VERIFICATION LOGIC ---
TARGET_HASH = "6e7dfba0b39da481db37c3263c61cac6"
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest() == TARGET_HASH

# --- CONFIGURATION ---
SOURCE_URL = "https://docs.google.com/spreadsheets/d/14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE/export?format=xlsx"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/1uS3xmnPi0o4c_EayQtURYDSMMPRDRGSb/export?format=xlsx"
MAP_LAYER_URL = "https://www.google.com/maps/d/embed?mid=1vX69yZ_4UWh54b73w2Q9pU0n0M5t58s&ehbc=2E312F" # Configured via map workspace target

# --- DATA STORAGE CONTROLLERS ---
if 'selected_trade_area' not in st.session_state:
    st.session_state.selected_trade_area = None
if 'selected_site_display' not in st.session_state:
    st.session_state.selected_site_display = None
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False
if 'modal_tab' not in st.session_state:
    st.session_state.modal_tab = "REPORT"

#--- HELPER FUNCTIONS ---
@st.cache_data(ttl=3600)
def download_file(url):
    try:
        response = requests.get(url, timeout=30)
        return io.BytesIO(response.content) if response.status_code == 200 else None
    except:
        return None

def clean_and_extract_url(cell_value):
    if cell_value is None: return ""
    val_str = str(cell_value).strip()
    formula_match = re.search(r'IMAGE\s*\(\s*["\'](https://[^"\']+)["\']', val_str, re.IGNORECASE)
    if formula_match: return formula_match.group(1)
    url_match = re.search(r'(https://[^\s"\']+)', val_str)
    if url_match: return url_match.group(1)
    return val_str

def get_cell_val_safe(row_cells, index):
    if index < len(row_cells):
        cell = row_cells[index]
        if cell.hyperlink and cell.hyperlink.target:
            return clean_and_extract_url(cell.hyperlink.target)
        return clean_and_extract_url(cell.value)
    return ""

def extract_google_drive_id(clean_url):
    if not clean_url: return None
    match = re.search(r'(?:id=|/d/|/uc?.*?id=)([a-zA-Z0-9_-]{25,})', clean_url)
    return match.group(1) if match else None

def get_placeholders(sheet):
    placeholders = set()
    for row in sheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                matches = re.findall(r"{{(.*?)}}", cell.value)
                for match in matches:
                    name = match.split(":")[0].strip() if ":" in match else match.strip()
                    placeholders.add(name)
    return sorted(list(placeholders))

def sanitize_tab_name(name, existing_names):
    clean_name = re.sub(r'[/*?\[\]:]', '', str(name))[:31]
    if not clean_name: clean_name = "Sheet"
    if clean_name not in existing_names:
        existing_names.add(clean_name)
        return clean_name
    counter = 1
    while True:
        new_name = f"{clean_name[:27]} ({counter})"
        if new_name not in existing_names:
            existing_names.add(new_name)
            return new_name
        counter += 1

def parse_site_number(site_display_str):
    match = re.match(r"^(\d+)", site_display_str)
    return int(match.group(1)) if match else float('inf')

@st.cache_data(ttl=600, show_spinner=False)
def generate_trade_area_report(trade_area, df, template_bytes_raw, placeholders):
    ta_data = df[df["TRADE AREA"] == trade_area]
    wb = load_workbook(io.BytesIO(template_bytes_raw))
    base_sheet = wb.active
    base_sheet.title = "TEMPLATE_TO_DELETE"
    existing_tabs = set()
    for _, r_row in ta_data.iterrows():
        s_name = r_row.get("SITE NAME", "Unknown")
        safe_tab_name = sanitize_tab_name(s_name, existing_tabs)
        new_sheet = wb.copy_worksheet(base_sheet)
        new_sheet.title = safe_tab_name
        for row_cells in new_sheet.iter_rows():
            for cell in row_cells:
                if isinstance(cell.value, str) and "{{" in cell.value:
                    new_val = cell.value
                    for ph in placeholders:
                        target_regex = r"\{\{\s*" + re.escape(ph) + r"(\s*:.*?)?\}\}"
                        if re.search(target_regex, new_val):
                            raw_data_val = r_row.get(ph.upper(), "")
                            if pd.isna(raw_data_val) or raw_data_val is None: raw_data_val = ""
                            if isinstance(raw_data_val, float) and raw_data_val.is_integer(): val_str = str(int(raw_data_val))
                            elif hasattr(raw_data_val, 'strftime'): val_str = r_row.get(ph.upper(), "").strftime('%B %d, %Y')
                            else: val_str = str(raw_data_val)
                            new_val = re.sub(target_regex, val_str, new_val)
                    new_val = re.sub(r"\{\{.*?\}\}", "", new_val)
                    cell.value = new_val.strip() if new_val else ""
    if "TEMPLATE_TO_DELETE" in wb.sheetnames:
        wb.remove(wb["TEMPLATE_TO_DELETE"])
    wb_buffer = io.BytesIO()
    wb.save(wb_buffer)
    wb_buffer.seek(0)
    return wb_buffer.getvalue()

#--- HTML MATRICES ---
HTML_FRAMEWORK = """
<!DOCTYPE html>
<html>
<head>
<style type="text/css">
html, body { margin: 0; padding: 0; background-color: #ffffff; font-family: Arial, sans-serif; height: auto; overflow: visible; }
.ritz.grid-container { height: auto; overflow: visible !important; padding: 5px; box-sizing: border-box; }
.ritz .waffle { border-collapse: collapse; width: 100%; table-layout: fixed; }
.ritz .waffle td { padding: 4px 5px !important; vertical-align: middle; border: 1px solid #e0e0e0 !important; font-size: 8.5pt; color: #333; }
.ritz .waffle .s0 { background-color:#800000; text-align:center; font-weight:bold; color:#ffffff; font-size:10pt; }
.ritz .waffle .s1 { background-color:#f5f5f5; font-weight:bold; color:#111; }
.ritz .waffle .s2 { background-color:#ffffff; font-weight:normal; }
.ritz .waffle .s4 { background-color:#fff; font-weight:500; color:#000; }
.ritz .waffle .s8 { background-color:#fff; color:#b00; font-weight:500; }
.ritz .waffle .s13 { background-color:#e0e0e0; font-weight:bold; color:#b00; }
</style>
</head>
<body>
<div class="ritz grid-container" dir="ltr">
<table class="waffle" cellspacing="0" cellpadding="0">
<colgroup>
<col style="width:140px;"> <col style="width:140px;"> <col style="width:140px;"> <col style="width:140px;"> <col style="width:140px;">
</colgroup>
<tbody>
<tr> <td class="s0" colspan="5">SITE INFORMATION REPORT</td> </tr>
<tr> <td class="s1" colspan="2">General Information</td> <td class="s2"></td> <td class="s1" colspan="2">Location</td> </tr>
<tr> <td class="s4">Trade Area Name</td> <td colspan="2">_TRADE_AREA_</td> <td class="s4">Site Name</td> <td>_SITE_NAME_</td> </tr>
<tr> <td class="s4">Site Name:</td> <td colspan="2">_SITE_NAME_</td> <td class="s4">Unit #/Bldg/St</td> <td>_UNIT_BLDG_ST_NAME_</td> </tr>
<tr> <td class="s4">Site Number:</td> <td colspan="2">_SITE_NO_</td> <td class="s4">Barangay/District</td> <td>_BARANGAY_DISTRICT_NAME_</td> </tr>
<tr> <td class="s4">Date Started</td> <td colspan="2">_TIMESTAMP_</td> <td class="s4">City/Municipality</td> <td>_CITY_MUNICIPALITY_</td> </tr>
<tr> <td class="s4">Date Submitted</td> <td colspan="2">_DATE_OF_REPORT_</td> <td class="s4">Region</td> <td>_REGION_</td> </tr>
<tr> <td class="s1" colspan="2">Terms</td> <td class="s2"></td> <td class="s1" colspan="2">Rates</td> </tr>
<tr> <td class="s4">Availability Date</td> <td colspan="2">_SITE_AVAILABILITY_DATE_</td> <td class="s8">Monthly Rental (Php)</td> <td>_MONTHLY_RENTAL_RATE_</td> </tr>
<tr> <td class="s4">Lease Terms</td> <td colspan="2">_LEASE_TERMS_</td> <td class="s8">Annual Escalation (%)</td> <td>_ESCALATION_</td> </tr>
<tr> <td class="s1" colspan="2">Technical Info</td> <td class="s2"></td> <td class="s8">Security Deposit</td> <td>_SECURITY_DEPOSIT_</td> </tr>
<tr> <td class="s4">Lot/Floor Area (sqm)</td> <td colspan="2">_LOT_FLOOR_AREA_SQM_</td> <td class="s8">CUSA Dues</td> <td>_CUSA_</td> </tr>
<tr> <td class="s4">Frontage (m)</td> <td colspan="2">_FRONTAGE_</td> <td class="s4">Lease Type</td> <td>_LEASE_TYPE_</td> </tr>
<tr> <td class="s1" colspan="2">Lessor Details</td> <td class="s2"></td> <td class="s1" colspan="2">Authorized Rep</td> </tr>
<tr> <td class="s4">Name of Lessor</td> <td colspan="2">_LESSOR_</td> <td class="s4">Rep Name</td> <td>_CONTACT_PERSON_SOURCE_</td> </tr>
<tr> <td class="s4">Contact Number</td> <td colspan="2">_CONTACT_NUMBER_</td> <td class="s4">Email Address</td> <td>_EMAIL_ADDRESS_</td> </tr>
<tr> <td class="s13" colspan="5">Regulatory & Remarks</td> </tr>
<tr> <td class="s4">Confidence Level</td> <td colspan="4">_SITE_AVAILABILITY_CLASS_</td> </tr>
<tr> <td class="s4">Other Remarks:</td> <td colspan="4">_REMARKS_</td> </tr>
</tbody>
</table>
</div>
</body>
</html>
"""

#--- LOAD DATA ASSETS ---
@st.cache_data(ttl=3600, show_spinner=True)
def load_data():
    source_bytes = download_file(SOURCE_URL)
    template_data = download_file(TEMPLATE_URL)
    if source_bytes is None or template_data is None:
        return None, None, None, []
    src_wb = load_workbook(io.BytesIO(source_bytes.getvalue()), data_only=False)
    src_ws = src_wb.active
    raw_rows = list(src_ws.iter_rows(values_only=False))
    header_row = [str(cell.value).strip().upper() if cell.value else "" for cell in raw_rows[0]]
    parsed_data_list = []
    for r in raw_rows[1:]:
        row_dict = {}
        has_val = False
        for idx, cell in enumerate(r):
            if idx < len(header_row) and header_row[idx]:
                cleaned_val = clean_and_extract_url(cell.value)
                row_dict[header_row[idx]] = cleaned_val
                if cleaned_val != "": has_val = True
        if has_val: parsed_data_list.append(row_dict)
    df = pd.DataFrame(parsed_data_list)
    df = df.loc[:, ~df.columns.str.contains('^$')]
    
    def create_site_display(row):
        site_no = row.get('SITE NO', '')
        site_name = row.get('SITE NAME', '')
        if pd.notna(site_no) and site_no != '':
            try: return f"{int(float(str(site_no)))} - {site_name}"
            except: return f"{site_no} - {site_name}"
        return str(site_name)
    df["SITE_DISPLAY"] = df.apply(create_site_display, axis=1)
    
    media_data_list = []
    media_ws = None
    for sheet_name in src_wb.sheetnames:
        if "PHOTO" in sheet_name.upper() or "DOC" in sheet_name.upper() or "MEDIA" in sheet_name.upper():
            media_ws = src_wb[sheet_name]
            break
    if not media_ws: media_ws = src_ws
    for r in media_ws.iter_rows(values_only=False):
        t_area = str(get_cell_val_safe(r, 13)).strip()
        s_name = str(get_cell_val_safe(r, 15)).strip()
        if t_area and s_name and t_area.upper() != "TRADE AREA":
            media_data_list.append({
                'TRADE AREA': t_area, 'SITE NAME': s_name,
                '__DIRECT_TCT': get_cell_val_safe(r, 2), '__DIRECT_LOT_PLAN': get_cell_val_safe(r, 3),
                '__DIRECT_BLDG_PLAN': get_cell_val_safe(r, 4), '__DIRECT_TAX_MAP': get_cell_val_safe(r, 5),
                '__DIRECT_PHOTO_1': get_cell_val_safe(r, 7), '__DIRECT_PHOTO_2': get_cell_val_safe(r, 8),
                '__DIRECT_PHOTO_3': get_cell_val_safe(r, 9), '__DIRECT_PHOTO_4': get_cell_val_safe(r, 10),
                '__DIRECT_PHOTO_5': get_cell_val_safe(r, 11),
            })
    temp_wb = load_workbook(template_data)
    placeholders = get_placeholders(temp_wb.active)
    template_bytes_raw = template_data.getvalue()
    return df, placeholders, template_bytes_raw, media_data_list

# --- MAIN RUNTIME ENGINE ---
if not st.session_state.authenticated:
    r1_col1, r1_col2, r1_col3 = st.columns([1, 1.2, 1])
    with r1_col2:
        st.markdown("<h3 style='text-align: center; margin-top:50px;'>TRS Site Information Report</h3>", unsafe_allow_html=True)
        password_input = st.text_input("", placeholder="Enter password", type="password")
        if st.button("Login", use_container_width=True) or (password_input and len(password_input) > 0):
            if check_password(password_input):
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Invalid token string provided.")
    st.stop()

df, placeholders, template_bytes_raw, media_data_list = load_data()
if df is None:
    st.error("Failed to load workbook assets.")
    st.stop()

# Set initial default state parameters if unassigned
trade_areas = sorted(df["TRADE AREA"].dropna().unique().tolist())
if st.session_state.selected_trade_area is None and len(trade_areas) > 0:
    st.session_state.selected_trade_area = trade_areas[0]

# --- RENDER MAP BACKGROUND ENGINE ---
map_iframe_html = f"""
<iframe src="{MAP_LAYER_URL}" width="100%" height="100%" style="border:none; position:absolute; top:0; left:0; z-index:1;"></iframe>
"""
components.html(map_iframe_html, height=1000, scrolling=False)

# --- INJECT ABSOLUTE SEARCH BAR REPLACEMENT CONTAINER ---
st.markdown("""
<style>
/* Absolute positioning context container to place Streamlit columns over map spatial frame */
div.floating-control-bar {
    position: absolute;
    top: 16px;
    left: 75px;
    width: 580px;
    z-index: 99999;
    background: #ffffff;
    padding: 6px 12px;
    border-radius: 24px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    display: flex;
    gap: 10px;
    align-items: center;
}
div.floating-control-bar div[data-testid="element-container"] {
    margin: 0px !important;
    padding: 0px !important;
}
</style>
""", unsafe_allow_html=True)

# Build custom floating structural wrapper using styled markdown element containment blocks
with st.container():
    st.markdown('<div class="floating-control-bar">', unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 0.8])
    
    with f_col1:
        current_ta_idx = trade_areas.index(st.session_state.selected_trade_area) if st.session_state.selected_trade_area in trade_areas else 0
        chosen_ta = st.selectbox("TA_Selector", options=trade_areas, index=current_ta_idx, label_visibility="collapsed")
        if chosen_ta != st.session_state.selected_trade_area:
            st.session_state.selected_trade_area = chosen_ta
            st.session_state.selected_site_display = None
            st.session_state.show_modal = False
            st.rerun()
            
    with f_col2:
        raw_sites = df[df["TRADE AREA"] == st.session_state.selected_trade_area]["SITE_DISPLAY"].dropna().unique().tolist()
        sites_in_ta = sorted(raw_sites, key=parse_site_number)
        
        if st.session_state.selected_site_display is None and len(sites_in_ta) > 0:
            st.session_state.selected_site_display = sites_in_ta[0]
            
        current_site_idx = sites_in_ta.index(st.session_state.selected_site_display) if st.session_state.selected_site_display in sites_in_ta else 0
        chosen_site = st.selectbox("Site_Selector", options=sites_in_ta, index=current_site_idx, label_visibility="collapsed")
        if chosen_site != st.session_state.selected_site_display:
            st.session_state.selected_site_display = chosen_site
            st.session_state.show_modal = True # Pop open report container on choice event
            st.rerun()
            
    with f_col3:
        if st.session_state.selected_site_display:
            # Quick toggle button UI element mapping over map framework
            if st.button("📄 View", use_container_width=True):
                st.session_state.show_modal = not st.session_state.show_modal
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# --- SITE REPORT POP-OUT MODAL CARD OVERLAY ---
if st.session_state.show_modal and st.session_state.selected_site_display:
    site_data = df[df["SITE_DISPLAY"] == st.session_state.selected_site_display]
    if not site_data.empty:
        site_row_data = site_data.iloc[0]
        
        # Cross reference configuration links
        target_ta = str(site_row_data["TRADE AREA"])
        target_sn = str(site_row_data["SITE NAME"])
        media_row_data = next((m for m in media_data_list if m['TRADE AREA'] == target_ta and m['SITE NAME'] == target_sn), site_row_data.to_dict())

        # Inject CSS layout configurations to build pop-out HUD Card UI
        st.markdown("""
        <style>
        div.site-modal-card {
            position: absolute;
            top: 90px;
            left: 75px;
            width: 720px;
            height: calc(100vh - 140px);
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
            z-index: 99999;
            display: flex;
            flex-direction: column;
            border: 1px solid #dadce0;
            overflow: hidden;
        }
        div.modal-header-tabs {
            background: #f1f3f4;
            padding: 8px 16px;
            display: flex;
            border-bottom: 1px solid #dadce0;
            align-items: center;
            justify-content: space-between;
        }
        div.tab-btn-group { display: flex; gap: 8px; }
        div.modal-body-content {
            flex: 1;
            padding: 12px;
            overflow-y: auto !important;
        }
        /* Style Streamlit native elements inside the overlay card container */
        .modal-header-tabs b { font-size: 0.85rem; color: #3c4043; letter-spacing: 0.5px; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="site-modal-card">', unsafe_allow_html=True)
        
        # Card Header Navigation Matrix Interface Component Layer
        m_head_col1, m_head_col2 = st.columns([4, 1])
        with m_head_col1:
            st.markdown(f"<div style='padding:8px 0 0 12px;'><b>SITE INFORMATION REPORT | PHOTOS | DOCS</b> Matrix ({target_sn})</div>", unsafe_allow_html=True)
        with m_head_col2:
            if st.button("✖ Close", key="close_modal_hud", use_container_width=True):
                st.session_state.show_modal = False
                st.rerun()

        # In-Card Navigation Control Tab Elements
        t_col1, t_col2, t_col3, t_col4 = st.columns([1, 1, 1, 1.2])
        with t_col1:
            if st.button("📊 Report", variant="primary" if st.session_state.modal_tab == "REPORT" else "secondary", use_container_width=True):
                st.session_state.modal_tab = "REPORT"; st.rerun()
        with t_col2:
            if st.button("📷 Photos", variant="primary" if st.session_state.modal_tab == "PHOTOS" else "secondary", use_container_width=True):
                st.session_state.modal_tab = "PHOTOS"; st.rerun()
        with t_col3:
            if st.button("📂 Docs", variant="primary" if st.session_state.modal_tab == "DOCS" else "secondary", use_container_width=True):
                st.session_state.modal_tab = "DOCS"; st.rerun()
        with t_col4:
            st.download_button(
                label="📥 Export TA",
                data=generate_trade_area_report(st.session_state.selected_trade_area, df, template_bytes_raw, placeholders),
                file_name=f"{st.session_state.selected_trade_area}_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="modal_download_btn"
            )

        st.markdown('<div class="modal-body-content">', unsafe_allow_html=True)
        
        # --- SUB-TAB ROUTING VIEWER ROUTINES ---
        if st.session_state.modal_tab == "REPORT":
            def process_val(key_string):
                val = site_row_data.get(key_string.upper(), "")
                return "" if pd.isna(val) or val is None else str(val).strip()
            
            view_html = HTML_FRAMEWORK
            replacements = {
                "_TRADE_AREA_": "TRADE AREA", "_SITE_NAME_": "SITE NAME", "_SITE_NO_": "SITE NO",
                "_TIMESTAMP_": "TIMESTAMP", "_DATE_OF_REPORT_": "DATE OF REPORT",
                "_UNIT_BLDG_ST_NAME_": "UNIT #, BLDG/ST # AND ST NAME", "_BARANGAY_DISTRICT_NAME_": "BARANGAY/DISTRICT NAME",
                "_CITY_MUNICIPALITY_": "CITY/MUNICIPALITY", "_REGION_": "REGION", "_POSTAL_CODE_": "POSTAL CODE",
                "_SITE_AVAILABILITY_DATE_": "SITE AVAILABILITY DATE", "_MONTHLY_RENTAL_RATE_": "MONTHLY RENTAL RATE",
                "_LEASE_TERMS_": "LEASE TERMS", "_ESCALATION_": "ESCALATION", "_SECURITY_DEPOSIT_": "SECURITY DEPOSIT",
                "_CUSA_": "CUSA", "_LOT_FLOOR_AREA_SQM_": "LOT/FLOOR AREA SQM", "_FRONTAGE_": "FRONTAGE",
                "_LEASE_TYPE_": "LEASE TYPE", "_LESSOR_": "LESSOR", "_CONTACT_PERSON_SOURCE_": "CONTACT PERSON/SOURCE",
                "_CONTACT_NUMBER_": "CONTACT NUMBER", "_EMAIL_ADDRESS_": "EMAIL ADDRESS",
                "_SITE_AVAILABILITY_CLASS_": "SITE AVAILABILITY CLASS", "_REMARKS_": "REMARKS"
            }
            for mark, column in replacements.items():
                view_html = view_html.replace(mark, process_val(column))
            view_html = re.sub(r"_[A-Z0-9_]+_", "", view_html)
            components.html(view_html, height=650, scrolling=True)

        elif st.session_state.modal_tab == "PHOTOS":
            photo_keys = ["__DIRECT_PHOTO_1", "__DIRECT_PHOTO_2", "__DIRECT_PHOTO_3", "__DIRECT_PHOTO_4", "__DIRECT_PHOTO_5"]
            valid_photos = []
            for idx, key in enumerate(photo_keys, 1):
                url = media_row_data.get(key, "")
                if url:
                    f_id = extract_google_drive_id(url)
                    thumb = f"https://drive.google.com/thumbnail?sz=w600&id={f_id}" if f_id else url
                    full = f"https://drive.google.com/uc?export=view&id={f_id}" if f_id else url
                    valid_photos.append((f"Photo {idx}", thumb, full))
            
            if valid_photos:
                p_cols = st.columns(2)
                for i, (lbl, thumb, full) in enumerate(valid_photos):
                    with p_cols[i % 2]:
                        st.markdown(f"""
                        <div style="border:1px solid #dadce0; border-radius:8px; overflow:hidden; margin-bottom:10px; background:#f8f9fa;">
                            <a href="{full}" target="_blank"><img src="{thumb}" style="width:100%; aspect-ratio:4/3; object-fit:cover; display:block;"></a>
                            <div style="padding:4px; font-size:0.75rem; text-align:center; background:#fff; font-weight:500;">{lbl}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else: st.info("No photos loaded for this record link.")

        elif st.session_state.modal_tab == "DOCS":
            doc_mappings = {"TCT": "__DIRECT_TCT", "LOT PLAN": "__DIRECT_LOT_PLAN", "BLDG PLAN": "__DIRECT_BLDG_PLAN", "TAX MAP": "__DIRECT_TAX_MAP"}
            valid_docs = []
            for label, key in doc_mappings.items():
                url = media_row_data.get(key, "")
                if url:
                    f_id = extract_google_drive_id(url)
                    thumb = f"https://drive.google.com/thumbnail?sz=w600&id={f_id}" if f_id else url
                    full = f"https://drive.google.com/uc?export=view&id={f_id}" if f_id else url
                    valid_docs.append((label, thumb, full))
            
            if valid_docs:
                d_cols = st.columns(2)
                for i, (label, thumb, full) in enumerate(valid_docs):
                    with d_cols[i % 2]:
                        st.markdown(f"""
                        <div style="border:1px solid #dadce0; border-radius:8px; overflow:hidden; margin-bottom:10px; background:#f8f9fa;">
                            <a href="{full}" target="_blank"><img src="{thumb}" style="width:100%; aspect-ratio:4/3; object-fit:cover; display:block;"></a>
                            <div style="padding:4px; font-size:0.75rem; text-align:center; background:#fff; font-weight:500;">{label}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else: st.info("No documents configured for this record selection.")

        st.markdown('</div>', unsafe_allow_html=True) # close body content container wrapper
        st.markdown('</div>', unsafe_allow_html=True) # close whole modal card layout block
