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

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="trs.sitesourcing.viewer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SIMPLIFIED CSS WITH MINIMAL OVERRIDES ---
st.markdown("""
<style>
    /* Hide scrollbars but keep scrolling */
    ::-webkit-scrollbar { width: 0px !important; height: 0px !important; }
    * { scrollbar-width: none !important; -ms-overflow-style: none !important; }
    
    /* Remove ALL Streamlit padding and margins */
    .main > div {
        padding: 0px !important;
        margin: 0px !important;
        max-width: 100% !important;
    }
    
    .block-container {
        padding: 0px !important;
        margin: 0px !important;
        max-width: 100% !important;
    }
    
    /* Hide header */
    header { display: none !important; }
    
    /* Custom container styles - YOU CAN EDIT THESE */
    .custom-main-container {
        padding: 8px 12px !important;
        margin: 0px !important;
        background: #ffffff;
        min-height: 100vh;
    }
    
    .custom-tab-content {
        padding: 4px 0px !important;
        margin: 0px !important;
    }
    
    .custom-control-bar {
        display: flex;
        gap: 12px;
        padding: 6px 12px;
        background: #f0f4f9;
        border-radius: 8px;
        margin-bottom: 8px;
        align-items: center;
    }
    
    .custom-tabs {
        display: flex;
        gap: 0px;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 8px;
    }
    
    .custom-tab {
        padding: 8px 20px;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        font-weight: 500;
        color: #5f6368;
        transition: all 0.2s;
    }
    
    .custom-tab:hover {
        color: #1a73e8;
        background: #f8f9fa;
    }
    
    .custom-tab.active {
        color: #1a73e8;
        border-bottom-color: #1a73e8;
    }
    
    .custom-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        padding: 8px 0;
    }
    
    .custom-grid-item {
        border: 1px solid #dadce0;
        border-radius: 8px;
        overflow: hidden;
        background: #f8f9fa;
        aspect-ratio: 4/3;
        display: flex;
        flex-direction: column;
        transition: transform 0.2s;
    }
    
    .custom-grid-item:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .custom-grid-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        flex: 1;
    }
    
    .custom-grid-item .label {
        padding: 4px 8px;
        font-size: 0.7rem;
        font-weight: 600;
        color: #5f6368;
        background: white;
        text-align: center;
        border-top: 1px solid #dadce0;
        flex-shrink: 0;
    }
    
    .custom-grid-item a {
        text-decoration: none;
        color: inherit;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    /* Media queries */
    @media (max-width: 768px) {
        .custom-grid { grid-template-columns: repeat(2, 1fr); }
        .custom-control-bar { flex-wrap: wrap; }
    }
    @media (max-width: 480px) {
        .custom-grid { grid-template-columns: 1fr; }
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
TARGET_HASH = "6e7dfba0b39da481db37c3263c61cac6"
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest() == TARGET_HASH

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h3 style='text-align:center;margin-top:50px;'>Access Required</h3>", unsafe_allow_html=True)
        pwd = st.text_input("Enter password:", type="password", label_visibility="collapsed")
        if st.button("Login", use_container_width=True) or pwd:
            if check_password(pwd):
                st.session_state.authenticated = True
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Invalid password.")
    st.stop()

# --- CONFIGURATION ---
SOURCE_URL = "https://docs.google.com/spreadsheets/d/14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE/export?format=xlsx"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/1uS3xmnPi0o4c_EayQtURYDSMMPRDRGSb/export?format=xlsx"

# --- HELPER FUNCTIONS (same as before) ---
@st.cache_data(ttl=3600)
def download_file(url):
    try:
        response = requests.get(url, timeout=30)
        return io.BytesIO(response.content) if response.status_code == 200 else None
    except:
        return None

def clean_and_extract_url(cell_value):
    if cell_value is None:
        return ""
    val_str = str(cell_value).strip()
    formula_match = re.search(r'IMAGE\s*\(\s*["\'](https?://[^"\']+)["\']', val_str, re.IGNORECASE)
    if formula_match:
        return formula_match.group(1)
    url_match = re.search(r'(https?://[^\s"\']+)', val_str)
    if url_match:
        return url_match.group(1)
    return val_str

def get_cell_val_safe(row_cells, index):
    if index < len(row_cells):
        cell = row_cells[index]
        if cell.hyperlink and cell.hyperlink.target:
            return clean_and_extract_url(cell.hyperlink.target)
        return clean_and_extract_url(cell.value)
    return ""

def extract_google_drive_id(clean_url):
    if not clean_url:
        return None
    match = re.search(r'(?:id=|/d/|/uc\?.*?id=)([a-zA-Z0-9_-]{25,})', clean_url)
    return match.group(1) if match else None

def get_placeholders(sheet):
    placeholders = set()
    for row in sheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                matches = re.findall(r"\{\{(.*?)\}\}", cell.value)
                for match in matches:
                    name = match.split(":")[0].strip() if ":" in match else match.strip()
                    placeholders.add(name)
    return sorted(list(placeholders))

def sanitize_tab_name(name, existing_names):
    clean_name = re.sub(r'[\\/*?\[\]:]', '', str(name))[:31]
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
    original_sheets = wb.sheetnames
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
                            if isinstance(raw_data_val, float) and raw_data_val.is_integer(): 
                                val_str = str(int(raw_data_val))
                            elif hasattr(raw_data_val, 'strftime'): 
                                val_str = r_row.get(ph.upper(), "").strftime('%B %d, %Y')
                            else: 
                                val_str = str(raw_data_val)
                            new_val = re.sub(target_regex, val_str, new_val)
                    new_val = re.sub(r"\{\{.*?\}\}", "", new_val)
                    cell.value = new_val.strip() if new_val else ""
        for row in new_sheet.iter_rows():
            max_len = max([len(str(cell.value or '')) for cell in row])
            if max_len > 45: 
                new_sheet.row_dimensions[row[0].row].height = None
    if "TEMPLATE_TO_DELETE" in wb.sheetnames:
        wb.remove(wb["TEMPLATE_TO_DELETE"])
    for name in original_sheets:
        if name in wb.sheetnames and name != "TEMPLATE_TO_DELETE":
            wb.remove(wb[name])
    wb_buffer = io.BytesIO()
    wb.save(wb_buffer)
    wb_buffer.seek(0)
    return wb_buffer.getvalue()

# --- HTML FRAMEWORK (simplified) ---
HTML_FRAMEWORK = """
<!DOCTYPE html>
<html>
<head>
<style>
    /* Hide scrollbars */
    ::-webkit-scrollbar { width: 0px !important; height: 0px !important; }
    * { scrollbar-width: none !important; -ms-overflow-style: none !important; }
    
    html, body { margin:0; padding:0; background:#fff; font-family:Arial,sans-serif; }
    .container { padding:8px; }
    .waffle { border-collapse:collapse; width:100%; }
    .waffle td { padding:2px 3px !important; vertical-align:middle; border:none; }
    .s0 {background:#800000;text-align:center;font-weight:bold;color:#fff;font-size:8pt;}
    .s1 {background:#fff;text-align:left;font-weight:bold;color:#000;font-size:8pt;}
    .s2 {background:#fff;text-align:left;color:#000;font-size:8pt;}
    .s4 {background:#f8f9fa;text-align:left;color:#000;font-size:8pt;padding:2px 3px;}
    .s8 {background:#fff;text-align:left;color:#ff0000;font-size:8pt;}
    .remarks-label {white-space:nowrap;vertical-align:top;padding-top:8px;}
    .waffle td {padding:2px 3px;}
    .waffle tr {height:auto;}
</style>
</head>
<body>
<div class="container">
<table class="waffle">
    <colgroup><col style="width:223px;"><col style="width:100px;"><col style="width:86px;"><col style="width:100px;"><col style="width:94px;"><col style="width:100px;"><col style="width:81px;"><col style="width:15px;"><col style="width:148px;"><col style="width:176px;"><col style="width:100px;"><col style="width:100px;"><col style="width:100px;"><col style="width:125px;"><col style="width:29px;"></colgroup>
    <tbody>
        <tr><td class="s0" colspan="15">SITE INFORMATION REPORT</td></tr>
        <tr><td class="s1" colspan="7">General Information</td><td class="s1"></td><td class="s1" colspan="7">Location</td></tr>
        <tr><td class="s2">Trade Area Name</td><td class="s2"></td><td class="s4" colspan="5">_TRADE_AREA_</td><td class="s2"></td><td class="s2" colspan="2">Site Name</td><td class="s4" colspan="5">_SITE_NAME_</td></tr>
        <tr><td class="s2">Site Name:</td><td class="s2"></td><td class="s4" colspan="5">_SITE_NAME_</td><td class="s2"></td><td class="s2" colspan="2">Unit #, Bldg/St # and St Name</td><td class="s4" colspan="5">_UNIT_BLDG_ST_NAME_</td></tr>
        <tr><td class="s2">Site Number:</td><td class="s2"></td><td class="s4" colspan="5">_SITE_NO_</td><td class="s2"></td><td class="s2" colspan="2">Barangay/District Name</td><td class="s4" colspan="5">_BARANGAY_DISTRICT_NAME_</td></tr>
        <tr><td class="s2">Date Started</td><td class="s2"></td><td class="s4" colspan="5">_TIMESTAMP_</td><td class="s2"></td><td class="s2" colspan="2">City/Municipality</td><td class="s4" colspan="5">_CITY_MUNICIPALITY_</td></tr>
        <tr><td class="s2" colspan="2">Date Report Submitted</td><td class="s4" colspan="5">_DATE_OF_REPORT_</td><td class="s2"></td><td class="s2" colspan="2">Region</td><td class="s4" colspan="5">_REGION_</td></tr>
        <tr><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2" colspan="2">Postal Code</td><td class="s4" colspan="5">_POSTAL_CODE_</td></tr>
        <tr><td class="s1" colspan="7">Terms</td><td class="s2"></td><td class="s1" colspan="7">Rates</td></tr>
        <tr><td class="s2">Site Availability Date</td><td class="s2"></td><td class="s4" colspan="5">_SITE_AVAILABILITY_DATE_</td><td class="s2"></td><td class="s8" colspan="2">Monthly Rental Rate (Php)</td><td class="s4" colspan="5">_MONTHLY_RENTAL_RATE_</td></tr>
        <tr><td class="s2">COL Start Date</td><td class="s2"></td><td class="s4" colspan="5">_COL_START_DATE_</td><td class="s2"></td><td class="s8" colspan="2">Percentage Rent</td><td class="s4" colspan="5"></td></tr>
        <tr><td class="s2">COL End Date</td><td class="s2"></td><td class="s4" colspan="5">_COL_END_DATE_</td><td class="s2"></td><td class="s8" colspan="2">Minimum Guaranteed Rent</td><td class="s4" colspan="5"></td></tr>
        <tr><td class="s2">Lease Terms</td><td class="s2"></td><td class="s4" colspan="5">_LEASE_TERMS_</td><td class="s2"></td><td class="s8" colspan="2">Annual Escalation Rate (%)</td><td class="s4" colspan="5">_ESCALATION_</td></tr>
        <tr><td class="s1" colspan="7">Technical Info</td><td class="s2"></td><td class="s8" colspan="2">Advance Rental (Php)</td><td class="s4" colspan="5">_ADVANCE_RENTAL_</td></tr>
        <tr><td class="s2" colspan="2">Lot /Floor Area (in sqm)</td><td class="s4" colspan="5">_LOT_FLOOR_AREA_SQM_</td><td class="s2"></td><td class="s8" colspan="2">Security Deposit Amount (Php)</td><td class="s4" colspan="5">_SECURITY_DEPOSIT_</td></tr>
        <tr><td class="s2">Frontage (in m)</td><td class="s2"></td><td class="s4" colspan="5">_FRONTAGE_</td><td class="s2"></td><td class="s8" colspan="2">CUSA Dues</td><td class="s4" colspan="5">_CUSA_</td></tr>
        <tr><td class="s2" colspan="2">Type of Structure(if Bldg Lessee)</td><td class="s4" colspan="5"></td><td class="s2"></td><td class="s1" colspan="7">Provisions</td></tr>
        <tr><td class="s2">Soil Profile</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s2"></td><td class="s2" colspan="2">Lease Type</td><td class="s4" colspan="5">_LEASE_TYPE_</td></tr>
        <tr><td class="s1" colspan="7">Lessor and Tenant Details</td><td class="s2"></td><td class="s1" colspan="7">If with Sub-Lessor/Sub-Lessee</td></tr>
        <tr><td class="s2">Name of Lessor</td><td class="s2"></td><td class="s4" colspan="5">_LESSOR_</td><td class="s2"></td><td class="s2" colspan="2">Name of Sub-Lessor</td><td class="s4" colspan="5"></td></tr>
        <tr><td class="s2" colspan="2">Name of Authorized Representative</td><td class="s4" colspan="5">_CONTACT_PERSON_SOURCE_</td><td class="s2"></td><td class="s2" colspan="2">Name of Authorized Representative</td><td class="s4" colspan="5"></td></tr>
        <tr><td class="s2">Contact No.</td><td class="s2"></td><td class="s4" colspan="5">_CONTACT_NUMBER_</td><td class="s2"></td><td class="s2" colspan="2">Contact No.</td><td class="s4" colspan="5"></td></tr>
        <tr><td class="s2">E-mail Address</td><td class="s2"></td><td class="s4" colspan="5">_EMAIL_ADDRESS_</td><td class="s2"></td><td class="s2" colspan="2">E-mail Address</td><td class="s4" colspan="5"></td></tr>
        <tr><td class="s13" colspan="15">Regulatory</td></tr>
        <tr><td class="s14">Setback Requirement</td><td class="s15" colspan="4"></td><td class="s16" colspan="2">Perm Traffic Re-Routing</td><td class="s17"></td><td class="s15" colspan="2"></td><td class="s18" colspan="5">Future Development</td></tr>
        <tr><td class="s14">Road Widening</td><td class="s15" colspan="4"></td><td class="s16" colspan="2">Perm Road Closure</td><td class="s17"></td><td class="s15" colspan="2"></td><td class="s18" colspan="5">Zoning Clearance</td></tr>
        <tr><td class="s19">Pedestrian Overpass</td><td class="s20" colspan="4"></td><td class="s19" colspan="2">Infrastructure Programs</td><td class="s20"></td><td class="s20" colspan="2"></td><td class="s21" colspan="5">Gas Station</td></tr>
        <tr><td class="s22">Site Acquirability:</td><td class="s2" colspan="13"></td><td class="s2"></td></tr>
        <tr><td class="s2">Confidence Level</td><td class="s4" colspan="2"></td><td class="s2" colspan="11"></td><td class="s2"></td></tr>
        <tr><td class="s2">Site Availability</td><td class="s23" colspan="2"><div style="width:184px;">_SITE_AVAILABILITY_CLASS_</div></td><td class="s24"></td><td class="s25"></td><td class="s2" colspan="10"></td><td class="s2"></td></tr>
        <tr><td class="s2 remarks-label">Other Remarks:</td><td class="s5" colspan="7" style="white-space:normal;word-wrap:break-word;padding:8px 6px;">_REMARKS_</td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s7"></td></tr>
    </tbody>
</table>
</div>
</body>
</html>
"""

# --- LOAD DATA ---
@st.cache_data(ttl=3600)
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
                if cleaned_val != "":
                    has_val = True
        if has_val:
            parsed_data_list.append(row_dict)
            
    df = pd.DataFrame(parsed_data_list)
    df = df.loc[:, ~df.columns.str.contains('^$')]
    
    def create_site_display(row):
        site_no = row.get('SITE NO', '')
        site_name = row.get('SITE NAME', '')
        if pd.notna(site_no) and site_no != '':
            try:
                return f"{int(float(str(site_no)))} - {site_name}"
            except:
                return f"{site_no} - {site_name}"
        return str(site_name)

    df["SITE_DISPLAY"] = df.apply(create_site_display, axis=1)
    
    media_data_list = []
    media_ws = None
    for sheet_name in src_wb.sheetnames:
        if "PHOTO" in sheet_name.upper() or "DOC" in sheet_name.upper() or "MEDIA" in sheet_name.upper():
            media_ws = src_wb[sheet_name]
            break
    if not media_ws:
        media_ws = src_ws
        
    for r in media_ws.iter_rows(values_only=False):
        t_area = str(get_cell_val_safe(r, 13)).strip()
        s_name = str(get_cell_val_safe(r, 15)).strip()
        if t_area and s_name and t_area.upper() != "TRADE AREA":
            media_data_list.append({
                'TRADE AREA': t_area,
                'SITE NAME': s_name,
                '__DIRECT_TCT': get_cell_val_safe(r, 2),
                '__DIRECT_LOT_PLAN': get_cell_val_safe(r, 3),
                '__DIRECT_BLDG_PLAN': get_cell_val_safe(r, 4),
                '__DIRECT_TAX_MAP': get_cell_val_safe(r, 5),
                '__DIRECT_PHOTO_1': get_cell_val_safe(r, 7),
                '__DIRECT_PHOTO_2': get_cell_val_safe(r, 8),
                '__DIRECT_PHOTO_3': get_cell_val_safe(r, 9),
                '__DIRECT_PHOTO_4': get_cell_val_safe(r, 10),
                '__DIRECT_PHOTO_5': get_cell_val_safe(r, 11),
            })
    
    temp_wb = load_workbook(template_data)
    placeholders = get_placeholders(temp_wb.active)
    template_data.seek(0)
    
    return df, placeholders, template_data.getvalue(), media_data_list

with st.spinner("Loading Data Assets..."):
    df, placeholders, template_bytes_raw, media_data_list = load_data()

if df is None or template_bytes_raw is None:
    st.error("Failed to load data assets.")
    st.stop()

# --- MAIN UI WITH SIMPLE CONTROLS ---
# Use a simple container with minimal padding
main_container = st.container()

with main_container:
    # Trade Area selector
    trade_areas = ["Select Trade Area..."] + sorted(df["TRADE AREA"].dropna().unique().tolist())
    col1, col2, col3 = st.columns([1.5, 1.5, 1.0])
    
    with col1:
        selected_ta = st.selectbox("Trade Area", options=trade_areas, index=0, label_visibility="collapsed")
    
    with col2:
        if selected_ta and selected_ta != "Select Trade Area...":
            raw_sites = df[df["TRADE AREA"] == selected_ta]["SITE_DISPLAY"].dropna().unique().tolist()
            sorted_sites = sorted(raw_sites, key=parse_site_number)
            sites_in_ta = ["Select Site..."] + sorted_sites
        else:
            sites_in_ta = ["Select Site..."]
        selected_site_display = st.selectbox("Site Name", options=sites_in_ta, index=0, label_visibility="collapsed")
    
    with col3:
        if selected_ta and selected_ta != "Select Trade Area...":
            st.download_button(
                label="Export",
                data=generate_trade_area_report(selected_ta, df, template_bytes_raw, placeholders),
                file_name=f"{selected_ta}_Full_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    # Show content only when selections are made
    if selected_ta != "Select Trade Area..." and selected_site_display != "Select Site...":
        site_data = df[df["SITE_DISPLAY"] == selected_site_display]
        if not site_data.empty:
            site_row_data = site_data.iloc[0]
            
            target_ta = str(site_row_data.get('TRADE AREA', '')).strip()
            target_sn = str(site_row_data.get('SITE NAME', '')).strip()
            
            media_row_data = {}
            for m in media_data_list:
                if m['TRADE AREA'] == target_ta and m['SITE NAME'] == target_sn:
                    media_row_data = m
                    break
            if not media_row_data:
                media_row_data = site_row_data
            
            # Tabs
            tab1, tab2, tab3 = st.tabs(["INFORMATION", "PHOTOS", "DOCS"])
            
            # TAB 1: INFORMATION
            with tab1:
                def process_val(key_string):
                    val = site_row_data.get(key_string.upper(), "")
                    if pd.isna(val) or val is None: return ""
                    return str(val).strip()

                rendered_view = HTML_FRAMEWORK
                rendered_view = rendered_view.replace("_TRADE_AREA_", process_val("TRADE AREA"))
                rendered_view = rendered_view.replace("_SITE_NAME_", process_val("SITE NAME"))
                rendered_view = rendered_view.replace("_SITE_NO_", process_val("SITE NO"))
                rendered_view = rendered_view.replace("_TIMESTAMP_", process_val("TIMESTAMP"))
                rendered_view = rendered_view.replace("_DATE_OF_REPORT_", process_val("DATE OF REPORT"))
                rendered_view = rendered_view.replace("_UNIT_BLDG_ST_NAME_", process_val("UNIT #, BLDG/ST # AND ST NAME"))
                rendered_view = rendered_view.replace("_BARANGAY_DISTRICT_NAME_", process_val("BARANGAY/DISTRICT NAME"))
                rendered_view = rendered_view.replace("_CITY_MUNICIPALITY_", process_val("CITY/MUNICIPALITY"))
                rendered_view = rendered_view.replace("_REGION_", process_val("REGION"))
                rendered_view = rendered_view.replace("_POSTAL_CODE_", process_val("POSTAL CODE"))
                rendered_view = rendered_view.replace("_SITE_AVAILABILITY_DATE_", process_val("SITE AVAILABILITY DATE"))
                rendered_view = rendered_view.replace("_MONTHLY_RENTAL_RATE_", process_val("MONTHLY RENTAL RATE"))
                rendered_view = rendered_view.replace("_COL_START_DATE_", process_val("COL START DATE"))
                rendered_view = rendered_view.replace("_COL_END_DATE_", process_val("COL END DATE"))
                rendered_view = rendered_view.replace("_LEASE_TERMS_", process_val("LEASE TERMS"))
                rendered_view = rendered_view.replace("_ESCALATION_", process_val("ESCALATION"))
                rendered_view = rendered_view.replace("_ADVANCE_RENTAL_", process_val("ADVANCE RENTAL"))
                rendered_view = rendered_view.replace("_SECURITY_DEPOSIT_", process_val("SECURITY DEPOSIT"))
                rendered_view = rendered_view.replace("_CUSA_", process_val("CUSA"))
                rendered_view = rendered_view.replace("_LOT_FLOOR_AREA_SQM_", process_val("LOT/FLOOR AREA SQM"))
                rendered_view = rendered_view.replace("_FRONTAGE_", process_val("FRONTAGE"))
                rendered_view = rendered_view.replace("_LEASE_TYPE_", process_val("LEASE TYPE"))
                rendered_view = rendered_view.replace("_LESSOR_", process_val("LESSOR"))
                rendered_view = rendered_view.replace("_CONTACT_PERSON_SOURCE_", process_val("CONTACT PERSON/SOURCE"))
                rendered_view = rendered_view.replace("_CONTACT_NUMBER_", process_val("CONTACT NUMBER"))
                rendered_view = rendered_view.replace("_EMAIL_ADDRESS_", process_val("EMAIL ADDRESS"))
                rendered_view = rendered_view.replace("_SITE_AVAILABILITY_CLASS_", process_val("SITE AVAILABILITY CLASS"))
                rendered_view = rendered_view.replace("_REMARKS_", process_val("REMARKS"))
                rendered_view = re.sub(r"_[A-Z0-9_]+_", "", rendered_view)
                
                components.html(rendered_view, height=600, scrolling=True)
            
            # TAB 2: PHOTOS
            with tab2:
                direct_photo_mapping = {
                    "PROPERTY PHOTOS 1": "__DIRECT_PHOTO_1",
                    "PROPERTY PHOTOS 2": "__DIRECT_PHOTO_2",
                    "PROPERTY PHOTOS 3": "__DIRECT_PHOTO_3",
                    "PROPERTY PHOTOS 4": "__DIRECT_PHOTO_4",
                    "PROPERTY PHOTOS 5": "__DIRECT_PHOTO_5"
                }
                
                valid_photos = []
                for label, key in direct_photo_mapping.items():
                    raw_url = media_row_data.get(key, "")
                    if raw_url:
                        file_id = extract_google_drive_id(raw_url)
                        if file_id:
                            thumb_url = f"https://drive.google.com/thumbnail?sz=w800&id={file_id}"
                            full_url = f"https://drive.google.com/uc?export=view&id={file_id}"
                        else:
                            thumb_url = raw_url
                            full_url = raw_url
                        valid_photos.append((label, thumb_url, full_url))
                
                if valid_photos:
                    grid_html = """
                    <style>
                        ::-webkit-scrollbar { width:0px; height:0px; }
                        * { scrollbar-width:none; -ms-overflow-style:none; }
                        .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; padding:8px 0; }
                        .item { border:1px solid #dadce0; border-radius:8px; overflow:hidden; background:#f8f9fa; aspect-ratio:4/3; display:flex; flex-direction:column; transition:transform 0.2s; }
                        .item:hover { transform:scale(1.02); box-shadow:0 4px 12px rgba(0,0,0,0.15); }
                        .item img { width:100%; height:100%; object-fit:cover; flex:1; }
                        .item .label { padding:4px 8px; font-size:0.7rem; font-weight:600; color:#5f6368; background:#fff; text-align:center; border-top:1px solid #dadce0; flex-shrink:0; }
                        .item a { text-decoration:none; color:inherit; display:flex; flex-direction:column; height:100%; }
                        @media (max-width:768px) { .grid { grid-template-columns:repeat(2,1fr); } }
                        @media (max-width:480px) { .grid { grid-template-columns:1fr; } }
                    </style>
                    <div class="grid">
                    """
                    for label, thumb_url, full_url in valid_photos:
                        grid_html += f'''
                            <div class="item">
                                <a href="{full_url}" target="_blank">
                                    <img src="{thumb_url}" alt="{label}" loading="lazy">
                                    <div class="label">{label}</div>
                                </a>
                            </div>
                        '''
                    grid_html += "</div>"
                    components.html(grid_html, height=500, scrolling=True)
                else:
                    st.info("No photo links configured.")
            
            # TAB 3: DOCS
            with tab3:
                direct_doc_mapping = {
                    "TCT": "__DIRECT_TCT",
                    "LOT PLAN": "__DIRECT_LOT_PLAN",
                    "BLDG PLAN": "__DIRECT_BLDG_PLAN",
                    "TAX MAP": "__DIRECT_TAX_MAP"
                }
                
                valid_docs = []
                for label, key in direct_doc_mapping.items():
                    raw_url = media_row_data.get(key, "")
                    if raw_url:
                        file_id = extract_google_drive_id(raw_url)
                        if file_id:
                            thumb_url = f"https://drive.google.com/thumbnail?sz=w800&id={file_id}"
                            full_url = f"https://drive.google.com/uc?export=view&id={file_id}"
                        else:
                            thumb_url = raw_url
                            full_url = raw_url
                        valid_docs.append((label, thumb_url, full_url))
                
                if valid_docs:
                    grid_html = """
                    <style>
                        ::-webkit-scrollbar { width:0px; height:0px; }
                        * { scrollbar-width:none; -ms-overflow-style:none; }
                        .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; padding:8px 0; }
                        .item { border:1px solid #dadce0; border-radius:8px; overflow:hidden; background:#f8f9fa; aspect-ratio:4/3; display:flex; flex-direction:column; transition:transform 0.2s; }
                        .item:hover { transform:scale(1.02); box-shadow:0 4px 12px rgba(0,0,0,0.15); }
                        .item img { width:100%; height:100%; object-fit:cover; flex:1; }
                        .item .label { padding:4px 8px; font-size:0.7rem; font-weight:600; color:#5f6368; background:#fff; text-align:center; border-top:1px solid #dadce0; flex-shrink:0; }
                        .item a { text-decoration:none; color:inherit; display:flex; flex-direction:column; height:100%; }
                        @media (max-width:768px) { .grid { grid-template-columns:repeat(2,1fr); } }
                        @media (max-width:480px) { .grid { grid-template-columns:1fr; } }
                    </style>
                    <div class="grid">
                    """
                    for label, thumb_url, full_url in valid_docs:
                        grid_html += f'''
                            <div class="item">
                                <a href="{full_url}" target="_blank">
                                    <img src="{thumb_url}" alt="{label}" loading="lazy">
                                    <div class="label">{label}</div>
                                </a>
                            </div>
                        '''
                    grid_html += "</div>"
                    components.html(grid_html, height=500, scrolling=True)
                else:
                    st.info("No document links configured.")
