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
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="trs.sitesourcing.viewer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MINIMAL CSS - ONLY TO HIDE STREAMLIT ELEMENTS ---
st.markdown("""
<style>
    /* Hide scrollbars */
    ::-webkit-scrollbar { width: 0px !important; height: 0px !important; }
    * { scrollbar-width: none !important; -ms-overflow-style: none !important; }
    
    /* Remove ALL Streamlit padding and margins */
    .main > div, .block-container, [data-testid="stAppViewContainer"], 
    [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
        padding: 0px !important;
        margin: 0px !important;
        max-width: 100% !important;
        min-height: 0px !important;
        height: auto !important;
    }
    
    /* Hide header */
    header, [data-testid="stHeader"], .stApp > header {
        display: none !important;
        height: 0px !important;
    }
    
    /* Hide deployment watermarks */
    ._profilePreview_gzau3_63, ._link_gzau3_10, [class*='_profilePreview'],
    [class*='_link_gzau3'], a[href*='share.streamlit.io'], a[href*='streamlit.io'],
    img[src*='avatar'], [class*='avatar'], #MainMenu, button[title="View source"],
    .stAppDeployButton, div[data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
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

# --- HELPER FUNCTIONS ---
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

# --- MAIN APP - FULL HTML/IFRAME APPROACH ---
def process_val(site_row_data, key_string):
    val = site_row_data.get(key_string.upper(), "")
    if pd.isna(val) or val is None: return ""
    return str(val).strip()

def build_info_html(site_row_data):
    html = f"""
    <div style="padding:8px 12px;background:#f8f9fa;border-radius:4px;font-size:8pt;">
        <table style="width:100%;border-collapse:collapse;">
            <tr><td colspan="15" style="background:#800000;color:#fff;font-weight:bold;text-align:center;padding:4px;">SITE INFORMATION REPORT</td></tr>
            <tr><td colspan="7" style="font-weight:bold;border-bottom:1px solid #bfbfbf;padding:2px;">General Information</td><td></td><td colspan="7" style="font-weight:bold;border-bottom:1px solid #bfbfbf;padding:2px;">Location</td></tr>
            <tr><td style="padding:2px;">Trade Area Name</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'TRADE AREA')}</td><td></td><td colspan="2" style="padding:2px;">Site Name</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'SITE NAME')}</td></tr>
            <tr><td style="padding:2px;">Site Name:</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'SITE NAME')}</td><td></td><td colspan="2" style="padding:2px;">Unit #, Bldg/St # and St Name</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'UNIT #, BLDG/ST # AND ST NAME')}</td></tr>
            <tr><td style="padding:2px;">Site Number:</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'SITE NO')}</td><td></td><td colspan="2" style="padding:2px;">Barangay/District Name</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'BARANGAY/DISTRICT NAME')}</td></tr>
            <tr><td style="padding:2px;">Date Started</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'TIMESTAMP')}</td><td></td><td colspan="2" style="padding:2px;">City/Municipality</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'CITY/MUNICIPALITY')}</td></tr>
            <tr><td colspan="2" style="padding:2px;">Date Report Submitted</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'DATE OF REPORT')}</td><td></td><td colspan="2" style="padding:2px;">Region</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'REGION')}</td></tr>
            <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td colspan="2" style="padding:2px;">Postal Code</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'POSTAL CODE')}</td></tr>
            <tr><td colspan="7" style="font-weight:bold;border-bottom:1px solid #bfbfbf;padding:2px;">Terms</td><td></td><td colspan="7" style="font-weight:bold;border-bottom:1px solid #bfbfbf;padding:2px;">Rates</td></tr>
            <tr><td style="padding:2px;">Site Availability Date</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'SITE AVAILABILITY DATE')}</td><td></td><td colspan="2" style="color:#ff0000;padding:2px;">Monthly Rental Rate (Php)</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'MONTHLY RENTAL RATE')}</td></tr>
            <tr><td style="padding:2px;">COL Start Date</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'COL START DATE')}</td><td></td><td colspan="2" style="color:#ff0000;padding:2px;">Percentage Rent</td><td colspan="5" style="background:#f8f9fa;padding:2px;"></td></tr>
            <tr><td style="padding:2px;">COL End Date</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'COL END DATE')}</td><td></td><td colspan="2" style="color:#ff0000;padding:2px;">Minimum Guaranteed Rent</td><td colspan="5" style="background:#f8f9fa;padding:2px;"></td></tr>
            <tr><td style="padding:2px;">Lease Terms</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'LEASE TERMS')}</td><td></td><td colspan="2" style="color:#ff0000;padding:2px;">Annual Escalation Rate (%)</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'ESCALATION')}</td></tr>
            <tr><td colspan="7" style="font-weight:bold;border-bottom:1px solid #bfbfbf;padding:2px;">Technical Info</td><td></td><td colspan="2" style="color:#ff0000;padding:2px;">Advance Rental (Php)</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'ADVANCE RENTAL')}</td></tr>
            <tr><td colspan="2" style="padding:2px;">Lot /Floor Area (in sqm)</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'LOT/FLOOR AREA SQM')}</td><td></td><td colspan="2" style="color:#ff0000;padding:2px;">Security Deposit Amount (Php)</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'SECURITY DEPOSIT')}</td></tr>
            <tr><td style="padding:2px;">Frontage (in m)</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'FRONTAGE')}</td><td></td><td colspan="2" style="color:#ff0000;padding:2px;">CUSA Dues</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'CUSA')}</td></tr>
            <tr><td colspan="2" style="padding:2px;">Type of Structure(if Bldg Lessee)</td><td colspan="5" style="background:#f8f9fa;padding:2px;"></td><td></td><td colspan="7" style="font-weight:bold;border-bottom:1px solid #bfbfbf;padding:2px;">Provisions</td></tr>
            <tr><td style="padding:2px;">Soil Profile</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;"></td><td></td><td colspan="2" style="padding:2px;">Lease Type</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'LEASE TYPE')}</td></tr>
            <tr><td colspan="7" style="font-weight:bold;border-bottom:1px solid #bfbfbf;padding:2px;">Lessor and Tenant Details</td><td></td><td colspan="7" style="font-weight:bold;border-bottom:1px solid #bfbfbf;padding:2px;">If with Sub-Lessor/Sub-Lessee</td></tr>
            <tr><td style="padding:2px;">Name of Lessor</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'LESSOR')}</td><td></td><td colspan="2" style="padding:2px;">Name of Sub-Lessor</td><td colspan="5" style="background:#f8f9fa;padding:2px;"></td></tr>
            <tr><td colspan="2" style="padding:2px;">Name of Authorized Representative</td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'CONTACT PERSON/SOURCE')}</td><td></td><td colspan="2" style="padding:2px;">Name of Authorized Representative</td><td colspan="5" style="background:#f8f9fa;padding:2px;"></td></tr>
            <tr><td style="padding:2px;">Contact No.</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'CONTACT NUMBER')}</td><td></td><td colspan="2" style="padding:2px;">Contact No.</td><td colspan="5" style="background:#f8f9fa;padding:2px;"></td></tr>
            <tr><td style="padding:2px;">E-mail Address</td><td></td><td colspan="5" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'EMAIL ADDRESS')}</td><td></td><td colspan="2" style="padding:2px;">E-mail Address</td><td colspan="5" style="background:#f8f9fa;padding:2px;"></td></tr>
            <tr><td colspan="15" style="background:#b7b7b7;font-weight:bold;color:#ff0000;padding:2px;">Regulatory</td></tr>
            <tr><td style="color:#ff0000;padding:2px;">Setback Requirement</td><td colspan="4"></td><td colspan="2" style="color:#ff0000;padding:2px;">Perm Traffic Re-Routing</td><td></td><td colspan="2"></td><td colspan="5" style="color:#ff0000;padding:2px;">Future Development</td></tr>
            <tr><td style="color:#ff0000;padding:2px;">Road Widening</td><td colspan="4"></td><td colspan="2" style="color:#ff0000;padding:2px;">Perm Road Closure</td><td></td><td colspan="2"></td><td colspan="5" style="color:#ff0000;padding:2px;">Zoning Clearance</td></tr>
            <tr><td style="color:#ff0000;padding:2px;">Pedestrian Overpass</td><td colspan="4"></td><td colspan="2" style="color:#ff0000;padding:2px;">Infrastructure Programs</td><td></td><td colspan="2"></td><td colspan="5" style="color:#ff0000;padding:2px;">Gas Station</td></tr>
            <tr><td style="font-weight:bold;padding:2px;">Site Acquirability:</td><td colspan="13"></td><td></td></tr>
            <tr><td style="padding:2px;">Confidence Level</td><td colspan="2" style="background:#f8f9fa;padding:2px;"></td><td colspan="11"></td><td></td></tr>
            <tr><td style="padding:2px;">Site Availability</td><td colspan="2" style="background:#f8f9fa;padding:2px;">{process_val(site_row_data, 'SITE AVAILABILITY CLASS')}</td><td colspan="10"></td><td></td></tr>
            <tr><td style="padding:2px;white-space:nowrap;vertical-align:top;">Other Remarks:</td><td colspan="7" style="white-space:normal;word-wrap:break-word;padding:8px 6px;">{process_val(site_row_data, 'REMARKS')}</td><td colspan="7"></td></tr>
        </table>
    </div>
    """
    return html

# Get trade areas and sites for selectors
trade_areas_list = ["Select Trade Area..."] + sorted(df["TRADE AREA"].dropna().unique().tolist())

# Create the full HTML UI
def build_full_ui(selected_ta=None, selected_site=None, site_row_data=None, media_row_data=None, valid_photos=None, valid_docs=None):
    # Build options for selectors
    ta_options = '<option value="">Select Trade Area...</option>'
    for ta in sorted(df["TRADE AREA"].dropna().unique().tolist()):
        selected = 'selected' if ta == selected_ta else ''
        ta_options += f'<option value="{ta}" {selected}>{ta}</option>'
    
    site_options = '<option value="">Select Site...</option>'
    if selected_ta and selected_ta != "Select Trade Area...":
        raw_sites = df[df["TRADE AREA"] == selected_ta]["SITE_DISPLAY"].dropna().unique().tolist()
        sorted_sites = sorted(raw_sites, key=parse_site_number)
        for site in sorted_sites:
            selected = 'selected' if site == selected_site else ''
            site_options += f'<option value="{site}" {selected}>{site}</option>'
    
    # Build content based on selection
    content_html = ""
    if selected_site and selected_site != "Select Site...":
        # Information tab content
        info_html = build_info_html(site_row_data) if site_row_data is not None else ""
        
        # Photos tab content
        photos_html = ""
        if valid_photos:
            photos_html = '<div class="grid-3">'
            for label, thumb_url, full_url in valid_photos:
                photos_html += f'''
                    <div class="grid-item">
                        <a href="{full_url}" target="_blank">
                            <img src="{thumb_url}" alt="{label}" loading="lazy">
                            <div class="label">{label}</div>
                        </a>
                    </div>
                '''
            photos_html += '</div>'
        else:
            photos_html = '<p style="padding:20px;text-align:center;color:#5f6368;">No photo links configured.</p>'
        
        # Docs tab content
        docs_html = ""
        if valid_docs:
            docs_html = '<div class="grid-3">'
            for label, thumb_url, full_url in valid_docs:
                docs_html += f'''
                    <div class="grid-item">
                        <a href="{full_url}" target="_blank">
                            <img src="{thumb_url}" alt="{label}" loading="lazy">
                            <div class="label">{label}</div>
                        </a>
                    </div>
                '''
            docs_html += '</div>'
        else:
            docs_html = '<p style="padding:20px;text-align:center;color:#5f6368;">No document links configured.</p>'
        
        content_html = f'''
            <div class="tab-bar">
                <div class="tab active" onclick="switchTab('info')">INFORMATION</div>
                <div class="tab" onclick="switchTab('photos')">PHOTOS</div>
                <div class="tab" onclick="switchTab('docs')">DOCS</div>
            </div>
            <div id="info" class="tab-content">{info_html}</div>
            <div id="photos" class="tab-content hidden">{photos_html}</div>
            <div id="docs" class="tab-content hidden">{docs_html}</div>
        '''
    else:
        content_html = '<div style="padding:40px;text-align:center;color:#5f6368;">Select a Trade Area and Site to view details.</div>'
    
    return f'''
    <!DOCTYPE html>
    <html style="height:100%;margin:0;padding:0;">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            html, body {{ 
                height:100%; 
                overflow:hidden;
                font-family: 'Google Sans', Arial, sans-serif;
                background:#ffffff;
            }}
            .app-container {{
                display:flex;
                flex-direction:column;
                height:100vh;
                max-height:100vh;
                overflow:hidden;
            }}
            .controls {{
                flex:0 0 auto;
                padding:6px 12px;
                background:#f0f4f9;
                border-bottom:1px solid #dadce0;
                display:flex;
                gap:12px;
                align-items:center;
                flex-wrap:wrap;
            }}
            .controls select {{
                flex:1;
                min-width:150px;
                padding:4px 8px;
                border-radius:4px;
                border:1px solid #dadce0;
                background:#fff;
                font-size:0.8rem;
                height:28px;
            }}
            .controls button {{
                padding:4px 16px;
                border-radius:100px;
                border:none;
                background:#0b57d0;
                color:#fff;
                font-size:0.8rem;
                font-weight:500;
                cursor:pointer;
                height:28px;
                white-space:nowrap;
            }}
            .controls button:hover {{ background:#0b4cb4; }}
            .content {{
                flex:1;
                overflow:auto;
                padding:4px 8px;
                min-height:0;
            }}
            .tab-bar {{
                display:flex;
                gap:0;
                border-bottom:2px solid #dadce0;
                margin-bottom:8px;
                position:sticky;
                top:0;
                background:#fff;
                z-index:10;
            }}
            .tab {{
                padding:8px 20px;
                cursor:pointer;
                border-bottom:3px solid transparent;
                font-size:0.85rem;
                font-weight:500;
                color:#5f6368;
                transition:all 0.2s;
            }}
            .tab:hover {{
                color:#1a73e8;
                background:#f8f9fa;
            }}
            .tab.active {{
                color:#1a73e8;
                border-bottom-color:#1a73e8;
            }}
            .tab-content {{
                display:block;
                padding:2px 0;
            }}
            .tab-content.hidden {{
                display:none;
            }}
            .grid-3 {{
                display:grid;
                grid-template-columns:repeat(3,1fr);
                gap:12px;
                padding:4px 0;
            }}
            .grid-item {{
                border:1px solid #dadce0;
                border-radius:8px;
                overflow:hidden;
                background:#f8f9fa;
                transition:transform 0.2s;
                aspect-ratio:4/3;
                display:flex;
                flex-direction:column;
            }}
            .grid-item:hover {{
                transform:scale(1.02);
                box-shadow:0 4px 12px rgba(0,0,0,0.15);
            }}
            .grid-item img {{
                width:100%;
                height:100%;
                object-fit:cover;
                flex:1;
            }}
            .grid-item .label {{
                padding:4px 8px;
                font-size:0.7rem;
                font-weight:600;
                color:#5f6368;
                background:#fff;
                text-align:center;
                border-top:1px solid #dadce0;
                flex-shrink:0;
            }}
            .grid-item a {{
                text-decoration:none;
                color:inherit;
                display:flex;
                flex-direction:column;
                height:100%;
            }}
            @media (max-width:768px) {{
                .grid-3 {{ grid-template-columns:repeat(2,1fr); }}
                .controls select {{ min-width:120px; }}
            }}
            @media (max-width:480px) {{
                .grid-3 {{ grid-template-columns:1fr; }}
                .controls {{ flex-direction:column; align-items:stretch; }}
                .controls select {{ width:100%; }}
            }}
        </style>
        <script>
            function switchTab(tabName) {{
                document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
                document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
                document.getElementById(tabName).classList.remove('hidden');
                // Find the clicked tab by the tab name
                const tabs = document.querySelectorAll('.tab');
                const tabMap = {{'info':0, 'photos':1, 'docs':2}};
                if (tabMap[tabName] !== undefined && tabs[tabMap[tabName]]) {{
                    tabs[tabMap[tabName]].classList.add('active');
                }}
            }}
            
            function submitForm() {{
                const ta = document.getElementById('trade_area').value;
                const site = document.getElementById('site_name').value;
                if (ta && site) {{
                    // Use Streamlit's component communication
                    const data = {{'trade_area': ta, 'site_name': site}};
                    window.parent.postMessage({{'type': 'streamlit:setComponentValue', 'value': JSON.stringify(data)}}, '*');
                }}
            }}
            
            document.addEventListener('DOMContentLoaded', function() {{
                // Auto-submit when selections change
                document.getElementById('trade_area').addEventListener('change', function() {{
                    // Reload page with new trade area
                    const ta = this.value;
                    window.parent.location.href = window.parent.location.pathname + '?ta=' + encodeURIComponent(ta);
                }});
                document.getElementById('site_name').addEventListener('change', function() {{
                    const ta = document.getElementById('trade_area').value;
                    const site = this.value;
                    if (ta && site) {{
                        window.parent.location.href = window.parent.location.pathname + '?ta=' + encodeURIComponent(ta) + '&site=' + encodeURIComponent(site);
                    }}
                }});
            }});
        </script>
    </head>
    <body>
        <div class="app-container">
            <div class="controls">
                <select id="trade_area" style="flex:1;">
                    {ta_options}
                </select>
                <select id="site_name" style="flex:1;">
                    {site_options}
                </select>
                <button onclick="submitForm()">Export</button>
            </div>
            <div class="content">
                {content_html}
            </div>
        </div>
    </body>
    </html>
    '''

# --- MAIN APP LOGIC ---
# Get query parameters for state management
query_params = st.query_params
ta_param = query_params.get('ta', '')
site_param = query_params.get('site', '')

# Determine selected values
selected_ta = ta_param if ta_param in df["TRADE AREA"].dropna().unique().tolist() else "Select Trade Area..."
selected_site = site_param if site_param in df["SITE_DISPLAY"].dropna().unique().tolist() else "Select Site..."

# If we have a valid selection, get the data
site_row_data = None
media_row_data = None
valid_photos = []
valid_docs = []

if selected_ta != "Select Trade Area..." and selected_site != "Select Site...":
    site_data = df[df["SITE_DISPLAY"] == selected_site]
    if not site_data.empty:
        site_row_data = site_data.iloc[0]
        
        target_ta = str(site_row_data.get('TRADE AREA', '')).strip()
        target_sn = str(site_row_data.get('SITE NAME', '')).strip()
        
        for m in media_data_list:
            if m['TRADE AREA'] == target_ta and m['SITE NAME'] == target_sn:
                media_row_data = m
                break
        if not media_row_data:
            media_row_data = site_row_data
        
        # Build photos
        direct_photo_mapping = {
            "PROPERTY PHOTOS 1": "__DIRECT_PHOTO_1",
            "PROPERTY PHOTOS 2": "__DIRECT_PHOTO_2",
            "PROPERTY PHOTOS 3": "__DIRECT_PHOTO_3",
            "PROPERTY PHOTOS 4": "__DIRECT_PHOTO_4",
            "PROPERTY PHOTOS 5": "__DIRECT_PHOTO_5"
        }
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
        
        # Build docs
        direct_doc_mapping = {
            "TCT": "__DIRECT_TCT",
            "LOT PLAN": "__DIRECT_LOT_PLAN",
            "BLDG PLAN": "__DIRECT_BLDG_PLAN",
            "TAX MAP": "__DIRECT_TAX_MAP"
        }
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

# Build and render the full HTML UI
full_html = build_full_ui(
    selected_ta=selected_ta,
    selected_site=selected_site,
    site_row_data=site_row_data,
    media_row_data=media_row_data,
    valid_photos=valid_photos,
    valid_docs=valid_docs
)

# Render using components.html - high height to fill viewport
components.html(full_html, height=1000, scrolling=False)
