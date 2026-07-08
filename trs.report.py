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
from PIL import Image
from io import BytesIO
import tempfile
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="trs.sitesourcing.viewer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LINE 1 GLOBAL STYLESHEET ENFORCER (KILL WHITE SPACE & PARENT SCROLLBARS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');
    
    * { font-family: 'Google Sans', 'Roboto', 'Segoe UI', sans-serif !important; }

    /* 1. COMPLETELY LOCK MAIN VIEWPORT AND KILL NATIVE SCROLLBARS */
    html, body {
        overflow: hidden !important;
        height: 100vh !important;
        margin: 0px !important;
        padding: 0px !important;
        background-color: #ffffff !important;
    }

    /* 2. NUKE STREAMLIT HEADER & PADDING GHOSTS */
    header[data-testid="stHeader"], 
    [data-testid="stHeader"], 
    .stApp > header,
    div[data-testid="stDecoration"] {
        display: none !important;
        height: 0px !important;
        min-height: 0px !important;
        padding: 0px !important;
        margin: 0px !important;
        opacity: 0 !important;
    }

    /* 3. ZERO-OUT PADDING ON ALL MAIN CONTAINERS */
    .appview-container, 
    .main, 
    [data-testid="stAppViewContainer"], 
    [data-testid="stMain"],
    .block-container, 
    [data-testid="stMainBlockContainer"] {
        padding-top: 0px !important;
        margin-top: 0px !important;
        padding-bottom: 0px !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        overflow: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
    }

    /* Catch and crush any empty layout blocks */
    div[data-testid="stVerticalBlock"] > div:has(style),
    div[data-testid="stVerticalBlock"] > div:empty {
        display: none !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    /* 4. DYNAMIC REPORT VIEWER SIZING */
    iframe[title="streamlit_components.components.html"] {
        height: calc(100vh - 45px) !important;
        max-height: calc(100vh - 45px) !important;
        border: none !important;
        margin-bottom: 0px !important;
    }
    
    /* 5. Ultra-Compact Control Bar layout matrix definitions */
    div[data-testid="stHorizontalBlock"] { 
        gap: 0.5rem !important; 
        align-items: center !important; 
        background: #f0f4f9;
        padding: 0.2rem 0.5rem !important; 
        border-radius: 8px;
        margin-top: 0px !important; 
        margin-bottom: 0px !important;
    }
    
    .stSelectbox label { display: none !important; } 
    .stSelectbox > div > div {
        background-color: #fff !important;
        border: 1px solid #747775 !important;
        border-radius: 4px !important;
        min-height: 28px !important;
        height: 28px !important;
    }
    
    .stSelectbox > div > div > div { 
        padding-top: 0px !important; 
        padding-bottom: 0px !important;
        font-size: 0.8rem !important; 
        line-height: 26px !important;
    }
    
    .stButton > button, .stDownloadButton > button {
        background-color: #0b57d0 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 100px !important;
        padding: 0.1rem 1rem !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        min-height: 28px !important; 
        height: 28px !important;
        width: 100% !important;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.2) !important;
        line-height: 1 !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover { background-color: #0b4cb4 !important; }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f0f4f9;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Photo gallery styling */
    .photo-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 15px;
        padding: 10px 0;
    }
    .photo-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px;
        background: white;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .photo-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .photo-card img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 4px;
    }
    .photo-card .label {
        font-size: 11px;
        color: #666;
        margin-top: 5px;
        font-weight: 500;
    }
    .photo-card .filename {
        font-size: 10px;
        color: #999;
        margin-top: 2px;
        word-break: break-all;
    }
    
    /* Instant CSS blocking engine */
    ._profilePreview_gzau3_63,
    ._link_gzau3_10,
    [class*='_profilePreview'],
    [class*='_link_gzau3'],
    a[href*='share.streamlit.io'],
    a[href*='streamlit.io'],
    img[src*='avatar'],
    [class*='avatar'],
    #MainMenu,
    button[title="View source"],
    .stAppDeployButton,
    div[data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
        pointer-events: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- RUNTIME WORKSPACE SECURITY OBSERVERS ---
def deploy_workspace_security_protocols():
    """Manages active navigation hooks and runtime layout observation frames."""
    injected_js = """
    <script>
        (function() {
            const restrictedUrls = [
                "https://share.streamlit.io/user/pyscriptcli",
                "https://streamlit.io/cloud"
            ];

            function checkAndBlockUrl(url) {
                if (!url) return false;
                const shouldBlock = restrictedUrls.some(blockedUrl => 
                    url.toLowerCase().trim().includes(blockedUrl.toLowerCase().trim())
                );
                if (shouldBlock) {
                    window.stop();
                    if (window.top) {
                        window.top.location.href = window.location.origin;
                    } else {
                        window.location.href = window.location.origin;
                    }
                    return true;
                }
                return false;
            }

            document.addEventListener('click', function(e) {
                const target = e.target.closest('a');
                if (target && target.href) {
                    if (checkAndBlockUrl(target.href)) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                }
            }, true);

            const originalAssign = window.location.assign;
            window.location.assign = function(url) {
                if (!checkAndBlockUrl(url)) { originalAssign.apply(this, arguments); }
            };

            const originalReplace = window.location.replace;
            window.location.replace = function(url) {
                if (!checkAndBlockUrl(url)) { originalReplace.apply(this, arguments); }
            };

            function purgeTargetElements() {
                const targetSelectors = [
                    "._profilePreview_gzau3_63", "._link_gzau3_10",
                    "[class*='_profilePreview']", "[class*='_link_gzau3']",
                    "a[href*='share.streamlit.io']", "a[href*='streamlit.io']",
                    "img[src*='avatar']", "[class*='avatar']"
                ];
                targetSelectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => el.style.setProperty('display', 'none', 'important'));
                    if (window.top && window.top.document) {
                        try {
                            window.top.document.querySelectorAll(selector).forEach(el => el.style.setProperty('display', 'none', 'important'));
                        } catch(err) {}
                    }
                });
            }

            purgeTargetElements();
            const layoutObserver = new MutationObserver(function() { purgeTargetElements(); });
            if (document.body) layoutObserver.observe(document.body, { childList: true, subtree: true });
            if (window.top && window.top.document && window.top.document.body) {
                try { layoutObserver.observe(window.top.document.body, { childList: true, subtree: true }); } catch(e) {}
            }

            setInterval(function() {
                purgeTargetElements();
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

# --- PROGRAMMATIC LIGHT MODE LOCK ---
_config_dir = ".streamlit"
_config_file = os.path.join(_config_dir, "config.toml")
if not os.path.exists(_config_file):
    os.makedirs(_config_dir, exist_ok=True)
    with open(_config_file, "w", encoding="utf-8") as f:
        f.write("[theme]\nbase=\"light\"\n")

# --- LOGIN VERIFICATION LOGIC ---
TARGET_HASH = "6e7dfba0b39da481db37c3263c61cac6"
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest() == TARGET_HASH

if not st.session_state.authenticated:
    r1_col1, r1_col2, r1_col3 = st.columns([1, 1.2, 1])
    with r1_col2:
        st.markdown("<h3 style='text-align: center; margin-top:50px;'>Access Required</h3>", unsafe_allow_html=True)
        password_input = st.text_input("Enter password:", type="password", label_visibility="collapsed")
        if st.button("Login", use_container_width=True) or password_input:
            if check_password(password_input):
                st.session_state.authenticated = True
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Invalid token string provided.")
    st.stop()

deploy_workspace_security_protocols()

# --- CONFIGURATION ---
SOURCE_URL = "https://docs.google.com/spreadsheets/d/14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE/export?format=csv"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/1uS3xmnPi0o4c_EayQtURYDSMMPRDRGSb/export?format=xlsx"

# Google Drive Folder ID for photos (shared publicly)
DRIVE_FOLDER_ID = "13sLmXzxQvV12_ypTBRG2QW1yVIHaanba"

# Photo columns in your data
PHOTO_COLUMNS = ['PROPERTY PHOTOS 1', 'PROPERTY PHOTOS 2', 'PROPERTY PHOTOS 3', 'PROPERTY PHOTOS 4', 'PROPERTY PHOTOS 5']

# --- HELPER FUNCTIONS ---
@st.cache_data(ttl=3600)
def download_file(url):
    try:
        response = requests.get(url, timeout=30)
        return io.BytesIO(response.content) if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=3600)
def get_image_from_drive(filename):
    """Fetch image from Google Drive using direct URL (publicly shared)"""
    try:
        # Since the folder is shared with "Anyone with the link can view"
        # We can use the direct download URL format
        # First, try to find the file ID using a search (we'll use the folder ID)
        
        # Construct the Google Drive direct download URL
        # Format: https://drive.google.com/uc?export=view&id=FILE_ID
        
        # For now, we'll use a search approach since we have the folder ID
        # This requires the file to be in the shared folder
        
        # Build a Google Drive search URL (this is a workaround)
        # Actually, since the folder is public, we can construct URLs differently
        
        # Try multiple URL formats
        url_formats = [
            f"https://drive.google.com/uc?export=view&id={DRIVE_FOLDER_ID}&filename={filename}",
            f"https://drive.google.com/uc?export=download&id={DRIVE_FOLDER_ID}&filename={filename}",
        ]
        
        for url in url_formats:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Check if it's actually an image
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        return Image.open(BytesIO(response.content))
            except:
                continue
        
        # If direct URLs don't work, try using the file ID if we can find it
        # This is a simplified approach - in production, use Drive API
        return None
        
    except Exception as e:
        st.warning(f"Could not fetch image {filename}: {str(e)}")
        return None

@st.cache_data(ttl=600)
def get_photo_data(photo_path):
    """Extract filename and fetch image from path"""
    if not photo_path or pd.isna(photo_path):
        return None
    
    photo_path = str(photo_path).strip()
    if not photo_path:
        return None
    
    # Extract filename from path
    filename = photo_path.split('/')[-1].split('\\')[-1]
    
    # Try to fetch image
    image = get_image_from_drive(filename)
    
    return {
        'filename': filename,
        'path': photo_path,
        'image': image
    }

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
def generate_trade_area_report(trade_area):
    global df, placeholders, template_bytes_raw
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
                            if isinstance(raw_data_val, float) and raw_data_val.is_integer(): val_str = str(int(raw_data_val))
                            elif hasattr(raw_data_val, 'strftime'): val_str = r_row.get(ph.upper(), "").strftime('%B %d, %Y')
                            else: val_str = str(raw_data_val)
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

# --- COMPLETE HTML BLUEPRINT ---
HTML_FRAMEWORK = """
<!DOCTYPE html>
<html>
<head>
    <style type="text/css">
        html, body { 
            margin: 0; 
            padding: 0; 
            background-color: #ffffff; 
            font-family: Arial, sans-serif; 
            height: 100%;
            overflow: hidden; 
        }
        
        .ritz.grid-container {
            height: 100vh;
            overflow: auto !important;
            padding-bottom: 40px;
            box-sizing: border-box;
        }

        .ritz .waffle a { color: inherit; }
        .ritz .waffle td { padding: 2px 3px !important; vertical-align: middle; border: none !important; }
        .freezebar-origin-ltr { background-color: #f8f9fa; border: none !important; }
        .column-headers-background { background-color: #f8f9fa; text-align: center; font-size: 8pt; color: #444746; font-weight: normal; border: none !important; }
        .row-headers-background { background-color: #f8f9fa; text-align: center; font-size: 8pt; color: #444746; font-weight: normal; border: none !important; }
        
        .ritz .waffle .s0 {border-bottom:1px SOLID #bfbfbf;border-right:1px SOLID #bfbfbf;background-color:#800000;text-align:center;font-weight:bold;color:#ffffff;font-size:8pt;white-space:nowrap;direction:ltr;padding: 4px 3px !important;}
        .ritz .waffle .s1 {border-bottom:1px SOLID #bfbfbf;border-right:1px SOLID #bfbfbf;background-color:#ffffff;text-align:left;font-weight:bold;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;padding: 4px 3px !important;}
        .ritz .waffle .s2 {background-color:#ffffff;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;border: none !important;}
        .ritz .waffle .s3 {border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s4 {border: none !important;background-color:#f8f9fa;text-align:left;color:#000000;font-size:8pt;vertical-align:middle;white-space:nowrap;direction:ltr;padding: 4px 3px !important;line-height: 1.4;max-width: 0;overflow: hidden;text-overflow: ellipsis;}
        .ritz .waffle .s4.wrap-text {white-space:normal !important;word-wrap:break-word !important;word-break:break-word !important;overflow-wrap:break-word !important;max-width: 100% !important;overflow: visible !important;text-overflow: clip !important;height: auto !important;}
        .ritz .waffle .s5 {background-color:#ffffff;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;border: none !important;}
        .ritz .waffle .s6 {border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s7 {border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s8 {border: none !important;background-color:#ffffff;text-align:left;color:#ff0000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s9 {border: none !important;background-color:#f8f9fa;text-align:left;color:#000000;font-size:8pt;vertical-align:middle;white-space:nowrap;direction:ltr;padding: 4px 3px !important;line-height: 1.4;max-width: 0;overflow: hidden;text-overflow: ellipsis;}
        .ritz .waffle .s9.wrap-text {white-space:normal !important;word-wrap:break-word !important;word-break:break-word !important;overflow-wrap:break-word !important;max-width: 100% !important;overflow: visible !important;text-overflow: clip !important;height: auto !important;}
        
        .ritz .waffle .s10{background-color:#bfbfbf;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;border: none !important;}
        .ritz .waffle .s11{border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s12{border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s13{background-color:#b7b7b7;text-align:left;font-weight:bold;color:#ff0000;font-size:8pt;white-space:nowrap;direction:ltr;border: none !important;}
        .ritz .waffle .s14{background-color:#b7b7b7;text-align:left;color:#ff0000;font-size:8pt;white-space:nowrap;direction:ltr;border: none !important;}
        .ritz .waffle .s15{border: none !important;background-color:#b7b7b7;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s16{border: none !important;background-color:#b7b7b7;text-align:left;color:#ff0000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s17{background-color:#b7b7b7;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;border: none !important;}
        .ritz .waffle .s18{border: none !important;background-color:#b7b7b7;text-align:left;color:#ff0000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s19{border: none !important;background-color:#b7b7b7;text-align:left;color:#ff0000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s20{border: none !important;background-color:#b7b7b7;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s21{border: none !important;background-color:#b7b7b7;text-align:left;color:#ff0000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s22{background-color:#ffffff;text-align:left;font-weight:bold;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;border: none !important;}
        .ritz .waffle .s23{border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s24{border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;}
        .ritz .waffle .s25{border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:8pt;white-space:nowrap;direction:ltr;}
        
        .ritz .waffle { border-collapse: collapse; width: 100%; }
        .ritz .waffle tr { height: auto !important; }
        .ritz .waffle td[class*="s4"], .ritz .waffle td[class*="s9"] { height: auto !important; min-height: 20px; }
        .remarks-row { height: auto !important; }
        .remarks-row td { height: auto !important; padding: 6px 3px !important; vertical-align: top !important; }
        .remarks-row td.s5 { white-space: normal !important; word-wrap: break-word !important; word-break: break-word !important; overflow-wrap: break-word !important; max-width: 100% !important; overflow: visible !important; text-overflow: clip !important; height: auto !important; line-height: 1.6 !important; padding: 8px 6px !important; }
        .remarks-label { white-space: nowrap !important; vertical-align: top !important; padding-top: 8px !important; }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            function checkAndWrapCells() {
                const dataCells = document.querySelectorAll('.s4, .s9');
                dataCells.forEach(function(cell) {
                    if (cell.textContent && cell.textContent.trim().length > 0) {
                        const contentWidth = cell.scrollWidth;
                        const columnWidth = cell.offsetWidth;
                        if (contentWidth > columnWidth + 5) { cell.classList.add('wrap-text'); } else { cell.classList.remove('wrap-text'); }
                    }
                });
                const remarksCell = document.querySelector('.remarks-row td.s5');
                if (remarksCell) {
                    remarksCell.style.whiteSpace = 'normal';
                    remarksCell.style.wordWrap = 'break-word';
                    remarksCell.style.wordBreak = 'break-word';
                    remarksCell.style.overflowWrap = 'break-word';
                    const parentRow = remarksCell.closest('tr');
                    if (parentRow) { parentRow.style.height = 'auto'; }
                }
            }
            checkAndWrapCells();
            setTimeout(checkAndWrapCells, 100);
            window.addEventListener('resize', checkAndWrapCells);
            const observer = new MutationObserver(function() { checkAndWrapCells(); });
            const tableBody = document.querySelector('.waffle tbody');
            if (tableBody) { observer.observe(tableBody, { childList: true, subtree: true, characterData: true }); }
        });
    </script>
</head>
<body>
<div class="ritz grid-container" dir="ltr">
<table class="waffle" cellspacing="0" cellpadding="0" style="table-layout: fixed; width: 100%; border-collapse: collapse;">
    <colgroup>
        <col style="width:223px;"><col style="width:100px;"><col style="width:86px;"><col style="width:100px;"><col style="width:94px;"><col style="width:100px;"><col style="width:81px;"><col style="width:15px;"><col style="width:148px;"><col style="width:176px;"><col style="width:100px;"><col style="width:100px;"><col style="width:100px;"><col style="width:125px;"><col style="width:29px;">
    </colgroup>
    <tbody>
        <tr style="height: auto;"><td class="s0" colspan="15">SITE INFORMATION REPORT</td></tr>
        <tr style="height: auto"><td class="s1" colspan="7">General Information</td><td class="s1"></td><td class="s1" colspan="7">Location</td></tr>
        <tr style="height: auto"><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td></tr>
        <tr style="height: auto;">
            <td class="s2">Trade Area Name</td><td class="s2"></td>
            <td class="s4" colspan="5">_TRADE_AREA_</td>
            <td class="s3"></td>
            <td class="s5" colspan="2">Site Name</td>
            <td class="s4" colspan="5">_SITE_NAME_</td>
        </tr>
        <tr style="height: auto;">
            <td class="s2">Site Name:</td><td class="s2"></td>
            <td class="s4" colspan="5">_SITE_NAME_</td>
            <td class="s3"></td>
            <td class="s5" colspan="2">Unit #, Bldg/St # and St Name</td>
            <td class="s4" colspan="5">_UNIT_BLDG_ST_NAME_</td>
        </tr>
        <tr style="height: auto;">
            <td class="s2">Site Number:</td><td class="s2"></td>
            <td class="s4" colspan="5">_SITE_NO_</td>
            <td class="s3"></td>
            <td class="s5" colspan="2">Barangay/District Name</td>
            <td class="s4" colspan="5">_BARANGAY_DISTRICT_NAME_</td>
        </tr>
        <tr style="height: auto;">
            <td class="s2">Date Started</td><td class="s2"></td>
            <td class="s4" colspan="5">_TIMESTAMP_</td>
            <td class="s3"></td>
            <td class="s5" colspan="2">City/Municipality</td>
            <td class="s4" colspan="5">_CITY_MUNICIPALITY_</td>
        </tr>
        <tr style="height: auto;">
            <td class="s5" colspan="2">Date Report Submitted</td>
            <td class="s4" colspan="5">_DATE_OF_REPORT_</td>
            <td class="s3"></td>
            <td class="s5" colspan="2">Region</td>
            <td class="s4" colspan="5">_REGION_</td>
        </tr>
        <tr style="height: auto;">
            <td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td>
            <td class="s5" colspan="2">Postal Code</td>
            <td class="s4" colspan="5">_POSTAL_CODE_</td>
        </tr>
        <tr style="height: 9px"><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s3"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s7"></td></tr>
        <tr style="height: 19px"><td class="s1" colspan="7">Terms</td><td class="s3"></td><td class="s1" colspan="7">Rates</td></tr>
        <tr style="height: 19px"><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td></tr>
        <tr style="height: auto;">
            <td class="s2">Site Availability Date</td><td class="s2"></td>
            <td class="s4" colspan="5">_SITE_AVAILABILITY_DATE_</td>
            <td class="s3"></td>
            <td class="s8" colspan="2">Monthly Rental Rate (Php)</td>
            <td class="s4" colspan="5">_MONTHLY_RENTAL_RATE_</td>
        </tr>
        <tr style="height: auto;">
            <td class="s2">COL Start Date</td><td class="s2"></td>
            <td class="s4" colspan="5">_COL_START_DATE_</td>
            <td class="s3"></td>
            <td class="s8" colspan="2">Percentage Rent</td>
            <td class="s4" colspan="5"></td>
        </tr>
        <tr style="height: auto;">
            <td class="s2">COL End Date</td><td class="s2"></td>
            <td class="s4" colspan="5">_COL_END_DATE_</td>
            <td class="s3"></td>
            <td class="s8" colspan="2">Minimum Guaranteed Rent</td>
            <td class="s4" colspan="5"></td>
        </tr>
        <tr style="height: auto;">
            <td class="s2">Lease Terms</td><td class="s2"></td>
            <td class="s4" colspan="5">_LEASE_TERMS_</td>
            <td class="s3"></td>
            <td class="s8" colspan="2">Annual Escalation Rate (%)</td>
            <td class="s4" colspan="5">_ESCALATION_</td>
        </tr>
        <tr style="height: 19px"><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s3"></td><td class="s8" colspan="2">Advance Rental (Php)</td><td class="s4" colspan="5">_ADVANCE_RENTAL_</td></tr>
        <tr style="height: 19px"><td class="s1" colspan="7">Technical Info</td><td class="s3"></td><td class="s8" colspan="2">Security Deposit Amount (Php)</td><td class="s4" colspan="5">_SECURITY_DEPOSIT_</td></tr>
        <tr style="height: 19px"><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td><td class="s8" colspan="2">CUSA Dues</td><td class="s4" colspan="5">_CUSA_</td></tr>
        <tr style="height: auto;">
            <td class="s5" colspan="2">Lot /Floor Area (in sqm)</td>
            <td class="s4" colspan="5">_LOT_FLOOR_AREA_SQM_</td>
            <td class="s3"></td>
            <td class="s8" colspan="2">Estimated Revenue Per Mo.</td>
            <td class="s4" colspan="5"></td>
        </tr>
        <tr style="height: auto;"><td class="s2">Frontage (in m)</td><td class="s2"></td><td class="s4" colspan="5">_FRONTAGE_</td><td class="s3"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s7"></td></tr>
        <tr style="height: auto;"><td class="s2">Depth (in m)</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s1" colspan="7">Provisions</td></tr>
        <tr style="height: 19px;"><td class="s5" colspan="2">Floor to Slab Height (in m) - if Bldg</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s2" colspan="7"></td></tr>
        <tr style="height: 19px;"><td class="s5" colspan="2">No. of Storeys (If Bldg Lessee)</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Tenant is the Owner</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: 19px;"><td class="s5" colspan="2">Type of Structure(if Bldg Lessee)</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Lease Type</td><td class="s9" colspan="5">_LEASE_TYPE_</td></tr>
        <tr style="height: 19px;"><td class="s2">Soil Profile</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Principal COL</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;">
            <td class="s2">Supply Access:</td><td class="s2"></td><td class="s2" colspan="5"></td>
            <td class="s3"></td>
            <td class="s5" colspan="2">Sub-Lease Provision</td>
            <td class="s9" colspan="5"></td>
        </tr>
        <tr style="height: 19px;"><td class="s2">Power</td><td class="s10"></td><td class="s2">Aircon</td><td class="s10"></td><td class="s5" colspan="2">LPG Fire Pro</td><td class="s10"></td><td class="s3"></td><td class="s5" colspan="2">Pre-Term/Partial Term</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: 19px;"><td class="s2">Water</td><td class="s10"></td><td class="s2">Exhaust</td><td class="s10"></td><td class="s5" colspan="2">Drainage TP</td><td class="s10"></td><td class="s3"></td><td class="s5" colspan="2">Tripartite Agreement</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: 9px;"><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s3"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s7"></td></tr>
        <tr style="height: 19px;"><td class="s1" colspan="7">Lessor and Tenant Details</td><td class="s3"></td><td class="s1" colspan="7">If with Sub-Lessor/ Sub-Lessee</td></tr>
        <tr style="height: 9px;"><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td></tr>
        <tr style="height: auto;">
            <td class="s2">Name of Lessor</td><td class="s2"></td>
            <td class="s4" colspan="5">_LESSOR_</td>
            <td class="s3"></td>
            <td class="s5" colspan="2">Name of Sub-Lessor</td>
            <td class="s9" colspan="5"></td>
        </tr>
        <tr style="height: auto;"><td class="s2">Contact No.</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Contact No.</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2">E-mail Address</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">E-mail Address</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2">Type of Ownership</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Type of Ownership</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2">Company Name</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Company Name</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s5" colspan="2">Developer Account Name</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Developer Account Name</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2">Business Address</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Business Address</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s5" colspan="2">Name of Authorized Representative</td><td class="s4" colspan="5">_CONTACT_PERSON_SOURCE_</td>
            <td class="s3"></td>
            <td class="s5" colspan="2">Name of Authorized Representative</td>
            <td class="s9" colspan="5"></td>
        </tr>
        <tr style="height: auto;"><td class="s5" colspan="2">Residence Address of Authorized Representative</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Residence Address of Authorized Representative</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2">Contact No.</td><td class="s2"></td><td class="s4" colspan="5">_CONTACT_NUMBER_</td><td class="s3"></td><td class="s5" colspan="2">Contact No.</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2">E-mail Address</td><td class="s2"></td><td class="s4" colspan="5">_EMAIL_ADDRESS_</td><td class="s3"></td><td class="s5" colspan="2">E-mail Address</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td><td class="s2"></td><td class="s2"></td><td class="s3" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2">Name of Lessee</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Name of Sub-Lessee</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2">Position</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Position</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2">Contact No.</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Contact No.</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2">E-mail Address</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">E-mail Address</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s5" colspan="2">Name of Authorized Representative</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Name of Authorized Representative</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: auto;"><td class="s2">Business Address</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Business Address</td><td class="s9" colspan="5"></td></tr>
        <tr style="height: 9px;"><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s12"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s12"></td></tr>
        <tr style="height: 19px;"><td class="s13" colspan="15">Regulatory</td></tr>
        <tr style="height: auto;">
            <td class="s14">Setback Requirement</td><td class="s15" colspan="4"></td>
            <td class="s16" colspan="2">Perm Traffic Re-Routing</td><td class="s17"></td>
            <td class="s15" colspan="2"></td>
            <td class="s18" colspan="5">Future Development</td>
        </tr>
        <tr style="height: auto;">
            <td class="s14">Road Widening</td><td class="s15" colspan="4"></td>
            <td class="s16" colspan="2">Perm Road Closure</td><td class="s17"></td>
            <td class="s15" colspan="2"></td>
            <td class="s18" colspan="5">Zoning Clearance</td>
        </tr>
        <tr style="height: auto;">
            <td class="s19">Pedestrian Overpass</td><td class="s20" colspan="4"></td>
            <td class="s19" colspan="2">Infrastructure Programs</td><td class="s20"></td>
            <td class="s20" colspan="2"></td>
            <td class="s21" colspan="5">Gas Station</td>
        </tr>
        <tr style="height: auto;"><td class="s2" colspan="14"></td><td class="s3"></td></tr>
        <tr style="height: 19px;"><td class="s22">Site Acquirability:</td><td class="s2" colspan="13"></td><td class="s3"></td></tr>
        <tr style="height: auto;"><td class="s2">Confidence Level</td><td class="s4" colspan="2"></td><td class="s2" colspan="11"></td><td class="s3"></td></tr>
        <tr style="height: auto;">
            <td class="s2">Site Availability</td>
            <td class="s23" colspan="2"><div style="width:184px;left:-1px">_SITE_AVAILABILITY_CLASS_</div></td>
            <td class="s24"></td><td class="s25"></td><td class="s2" colspan="10"></td><td class="s3"></td>
        </tr>
        <tr class="remarks-row" style="height: auto;">
            <td class="s6 remarks-label" style="white-space: nowrap; vertical-align: top; padding-top: 8px;">Other Remarks:</td>
            <td class="s5" colspan="7" style="white-space: normal; word-wrap: break-word; word-break: break-word; overflow-wrap: break-word; max-width: 100%; overflow: visible; text-overflow: clip; height: auto; line-height: 1.6; padding: 8px 6px;">_REMARKS_</td>
            <td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s7"></td>
        </tr>
    </tbody>
</table>
</div>
</body>
</html>
"""

# --- LOAD DATA ASSETS ---
@st.cache_data(ttl=3600)
def load_data():
    source_data = download_file(SOURCE_URL)
    template_data = download_file(TEMPLATE_URL)
    if source_data is None or template_data is None: return None, None, None
    
    df = pd.read_csv(source_data)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.strip().str.upper()
    
    df["SITE_DISPLAY"] = df.apply(
        lambda row: f"{int(row['SITE NO'])} - {row['SITE NAME']}" 
        if pd.notna(row.get('SITE NO')) and isinstance(row.get('SITE NO'), (int, float)) 
        else f"{row.get('SITE NO', '')} - {row.get('SITE NAME', '')}".strip(" -"), 
        axis=1
    )
    
    temp_wb = load_workbook(template_data)
    placeholders = get_placeholders(temp_wb.active)
    template_data.seek(0)
    return df, placeholders, template_data.getvalue()

with st.spinner("Loading Data Assets..."):
    df, placeholders, template_bytes_raw = load_data()

if df is None or template_bytes_raw is None:
    st.error("Failed to load data. Please check connection profiles.")
    st.stop()

# --- POST-LOGIN SECURITY PROTOCOLS RE-ENFORCEMENT ---
deploy_workspace_security_protocols()

# --- PHOTO DISPLAY FUNCTION ---
def get_photo_direct_url(file_id):
    """Get direct URL for a Google Drive image"""
    return f"https://drive.google.com/uc?export=view&id={file_id}"

def get_file_id_from_drive(filename):
    """Get file ID from Google Drive using direct URL search"""
    # Since the folder is publicly shared, we can try to construct the URL
    # This is a simplified approach - in production, use Drive API
    try:
        # Try to search for the file using Google's public search
        # This might not work for all cases, but it's a start
        search_url = f"https://www.googleapis.com/drive/v3/files?q=name='{filename}' and '{DRIVE_FOLDER_ID}' in parents&fields=files(id,name)&key=AIzaSyCPVoj1E5HhQ-4PxR2-syjf5lY8Oo8KZ38"  # Public API key
        response = requests.get(search_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            if files:
                return files[0]['id']
    except:
        pass
    return None

def display_site_photos(site_data):
    """Display photos for a site in Streamlit with photo grid"""
    st.markdown("### 📸 Property Photos")
    
    # Get photo data from the site row
    photo_data = []
    for col in PHOTO_COLUMNS:
        if col in site_data.index:
            photo_path = site_data[col]
            if photo_path and str(photo_path).strip():
                filename = str(photo_path).split('/')[-1].split('\\')[-1]
                photo_data.append({
                    'filename': filename,
                    'path': photo_path,
                    'column': col
                })
    
    if not photo_data:
        st.info("No photos available for this site.")
        return
    
    # Display photos in a grid using columns
    cols_per_row = 3
    rows = (len(photo_data) + cols_per_row - 1) // cols_per_row
    
    for row in range(rows):
        row_cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            idx = row * cols_per_row + col_idx
            if idx < len(photo_data):
                with row_cols[col_idx]:
                    photo = photo_data[idx]
                    # Use a placeholder image since we can't reliably get file IDs
                    # The actual images would need Drive API access
                    st.markdown(f"""
                    <div class="photo-card">
                        <div style="background: #f0f4f9; border-radius: 4px; height: 180px; display: flex; align-items: center; justify-content: center; flex-direction: column;">
                            <div style="font-size: 48px; margin-bottom: 10px;">🖼️</div>
                            <div style="font-size: 12px; color: #666; text-align: center; padding: 0 10px;">
                                {photo['column'].replace('PROPERTY PHOTOS ', 'Photo ')}
                            </div>
                        </div>
                        <div class="label">{photo['column']}</div>
                        <div class="filename">{photo['filename'][:30]}{'...' if len(photo['filename']) > 30 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)

def display_site_docs(site_data):
    """Display documents for a site"""
    st.markdown("### 📄 Documents")
    
    # Check for document columns - you can customize these
    doc_columns = ['TCT', 'LOT PLAN', 'BLDG PLAN', 'TAX MAP']
    
    docs_found = False
    for col in doc_columns:
        if col in site_data.index:
            doc_value = site_data[col]
            if doc_value and str(doc_value).strip():
                docs_found = True
                st.markdown(f"""
                <div style="
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 10px;
                    background: white;
                ">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 24px;">📎</span>
                        <div>
                            <div style="font-weight: 500;">{col}</div>
                            <div style="font-size: 12px; color: #666;">{str(doc_value)[:100]}{'...' if len(str(doc_value)) > 100 else ''}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    if not docs_found:
        st.info("No documents available for this site.")

# --- ROW 1: CONTROLS ROW ---
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
            label="📊 Export Report",
            data=generate_trade_area_report(selected_ta),
            file_name=f"{selected_ta}_Full_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# --- ROW 2: TABS SECTION ---
if selected_ta != "Select Trade Area..." and selected_site_display != "Select Site...":
    site_data = df[df["SITE_DISPLAY"] == selected_site_display]
    if not site_data.empty:
        site_row_data = site_data.iloc[0]
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["📋 INFORMATION", "📸 PHOTOS", "📄 DOCS"])
        
        with tab1:
            # INFORMATION TAB - Display the HTML report
            try:
                def process_val(key_string):
                    val = site_row_data.get(key_string.upper(), "")
                    if pd.isna(val) or val is None: return ""
                    if isinstance(val, float) and val.is_integer(): return str(int(val))
                    if hasattr(val, 'strftime'): return val.strftime('%B %d, %Y')
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
                    
            except Exception as e:
                st.error(f"Error displaying information: {str(e)}")
        
        with tab2:
            # PHOTOS TAB
            display_site_photos(site_row_data)
        
        with tab3:
            # DOCS TAB
            display_site_docs(site_row_data)
else:
    st.info("Please select a Trade Area and a Site to view the specific report.")

# --- FOOTER ---
st.markdown("""
<style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #f8f9fa;
        padding: 5px 10px;
        font-size: 10px;
        color: #666;
        text-align: center;
        border-top: 1px solid #e0e0e0;
        z-index: 999;
    }
</style>
<div class="footer">
    trs.sitesourcing.viewer v1.0 | Data sourced from Google Sheets
</div>
""", unsafe_allow_html=True)
