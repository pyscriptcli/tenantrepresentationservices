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
from datetime import datetime
import time
import pickle
from concurrent.futures import ThreadPoolExecutor
import threading

#--- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="trs.sitesourcing.viewer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#--- LINE 1 GLOBAL STYLESHEET ENFORCER (MAX REAL ESTATE & OUTER SCROLLBAR) ---
st.markdown("""
<style >
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');

* { font-family: 'Google Sans', 'Roboto', 'Segoe UI', sans-serif !important; }

/* Hide the label of the password input on the login screen */
div[data-testid="stTextInput"] label {
    display: none !important;
}

/* Hide the broken visibility text/icon inside the password input */
div[data-testid="stTextInput"] button {
    display: none !important;
}

/* 1. FIXED: MAIN VIEWPORT WITH OUTER SCROLLBAR ONLY */
html, body {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: 100% !important;
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

/* 3. FIXED: ALLOW SCROLLING WITH INCREASED GLOBAL HEIGHT (+100px) */
.stApp,
.appview-container, 
.main, 
[data-testid="stAppViewContainer"], 
[data-testid="stMain"],
.block-container, 
[data-testid="stMainBlockContainer"] {
    padding-top: 0.2rem !important;
    margin-top: 0px !important;
    padding-bottom: 0px !important;
    padding-left: 0.4rem !important;
    padding-right: 0.4rem !important;
    overflow: visible !important;
    height: auto !important;
    max-height: none !important;
    min-height: calc(100vh + 100px) !important;
}

/* Catch and crush any empty layout blocks */
div[data-testid="stVerticalBlock"] > div:has(style),
div[data-testid="stVerticalBlock"] > div:empty {
    display: none !important;
    height: 0px !important;
    margin: 0px !important;
    padding: 0px !important;
}

/* 4. FIXED: REPORT VIEWER - HIDE INNER SCROLLBARS & INCREASE HEIGHT */
iframe[title="streamlit_components.components.html"] {
    height: 1200px !important;
    max-height: none !important;
    border: none !important;
    margin-bottom: 10px !important;
    width: 100% !important;
    overflow: hidden !important;
}

/* Optimize Tab Headers Matrix for High Density Views */
button[data-baseweb="tab"] {
    padding-top: 0.1rem !important;
    padding-bottom: 0.1rem !important;
    font-size: 0.85rem !important;
}

div[data-testid="stTabs"] {
    margin-top: -5px !important;
}

/* 5. Ultra-Compact Control Bar layout matrix definitions */
div[data-testid="stHorizontalBlock"] { 
    gap: 0.5rem !important; 
    align-items: flex-end !important; 
    background: #ffffff;
    padding: 0.4rem 0.5rem !important; 
    border-radius: 8px;
    margin-top: 0px !important; 
    margin-bottom: 10px !important;
}

/* Hard pixel alignment lock for the export column element wrapper */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) {
    align-self: flex-end !important;
    padding-bottom: 4px !important;
}

/* Force Streamlit's inner widget wrapper to drop any hidden margin blocks */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) div[data-testid="stElementWrapper"] {
    margin-bottom: 0px !important;
    padding-bottom: 0px !important;
}

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
    background-color: #003366 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 100px !important;
    padding: 0.1rem 0.5rem !important;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    min-height: 28px !important; 
    height: 28px !important;
    width: 100% !important;
    box-shadow: 0 1px 2px 0 rgba(60,64,67,0.2) !important;
    line-height: 1 !important;
}
.stButton > button:hover, .stDownloadButton > button:hover { background-color: #0b4cb4 !important; }

/* CSS Blocking Engine to Hide Deployment Watermarks */
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

/* Hide iframe scrollbars */
iframe[title="streamlit_components.components.html"] {
    height: auto !important;
    min-height: 600px !important;
    max-height: none !important;
    border: none !important;
    margin-bottom: 10px !important;
    width: 100% !important;
    overflow: hidden !important;
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}
iframe[title="streamlit_components.components.html"]::-webkit-scrollbar {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
}

/* Full Screen Loading Overlay */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 999999;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}
.loading-overlay .spinner {
    width: 50px;
    height: 50px;
    border: 4px solid #e0e0e0;
    border-top: 4px solid #003366;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.loading-overlay .loading-text {
    margin-top: 20px;
    font-size: 18px;
    color: #003366;
    font-weight: 500;
    letter-spacing: 0.5px;
}
.loading-overlay .loading-subtext {
    margin-top: 8px;
    font-size: 14px;
    color: #666;
}
.loading-overlay .progress-bar {
    width: 300px;
    height: 4px;
    background: #e0e0e0;
    border-radius: 2px;
    margin-top: 20px;
    overflow: hidden;
}
.loading-overlay .progress-bar .progress-fill {
    height: 100%;
    background: #003366;
    border-radius: 2px;
    transition: width 0.3s ease;
    width: 0%;
}
</style>

<!-- Full Screen Loading Overlay HTML -->
<div id="loading-overlay" class="loading-overlay">
    <div class="spinner"></div>
    <div class="loading-text">Loading Data...</div>
    <div class="loading-subtext">Please wait while we prepare your report</div>
    <div class="progress-bar">
        <div id="progress-fill" class="progress-fill" style="width: 0%;"></div>
    </div>
</div>

<script>
// Function to update loading progress
function updateProgress(percent) {
    const fill = document.getElementById('progress-fill');
    if (fill) {
        fill.style.width = percent + '%';
    }
}

// Function to remove loading overlay
function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(function() {
            overlay.style.display = 'none';
        }, 300);
    }
}

// Remove loading overlay when page is fully loaded
window.addEventListener('load', function() {
    setTimeout(hideLoadingOverlay, 100);
});

// Also remove when Streamlit is ready
if (window.Streamlit) {
    window.Streamlit.events.addEventListener('streamlit:render', function() {
        setTimeout(hideLoadingOverlay, 200);
    });
}
</script>
""", unsafe_allow_html=True)

#--- RUNTIME WORKSPACE SECURITY OBSERVERS ---
def deploy_workspace_security_protocols():
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
if 'data_timestamp' not in st.session_state:
    st.session_state.data_timestamp = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

def check_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest() == TARGET_HASH

#--- CONFIGURATION ---
SOURCE_URL = "https://docs.google.com/spreadsheets/d/14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE/export?format=xlsx"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/1uS3xmnPi0o4c_EayQtURYDSMMPRDRGSb/export?format=xlsx"
CACHE_TTL = 86400  # 24 hours in seconds
CACHE_DIR = ".cache"

# Create cache directory if it doesn't exist
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

#--- HELPER FUNCTIONS ---
@st.cache_data(ttl=3600)
def download_file(url):
    try:
        response = requests.get(url, timeout=30)
        return io.BytesIO(response.content) if response.status_code == 200 else None
    except:
        return None

def clean_and_extract_url(cell_value):
    """Bypasses formula blocks like =IMAGE("url") to get the clean direct link string."""
    if cell_value is None:
        return ""
    val_str = str(cell_value).strip()
    formula_match = re.search(r'IMAGE\s*\(\s*["\'](https://[^"\']+)["\']', val_str, re.IGNORECASE)
    if formula_match:
        return formula_match.group(1)
    url_match = re.search(r'(https://[^\s"\']+)', val_str)
    if url_match:
        return url_match.group(1)
    return val_str

def get_cell_val_safe(row_cells, index):
    """Safely fetch and clean a cell value by fixed column index. Checks hyperlinks too."""
    if index < len(row_cells):
        cell = row_cells[index]
        if cell.hyperlink and cell.hyperlink.target:
            return clean_and_extract_url(cell.hyperlink.target)
        return clean_and_extract_url(cell.value)
    return ""

def extract_google_drive_id(clean_url):
    """Extracts unique file ID from verified URL strings."""
    if not clean_url:
        return None
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

#--- OPTIMIZED LOAD DATA FUNCTION ---
def parse_main_data(source_bytes):
    """Parse main data from Excel bytes"""
    try:
        # Use read_only and data_only for speed
        src_wb = load_workbook(io.BytesIO(source_bytes.getvalue()), data_only=True, read_only=True)
        src_ws = src_wb.active
        
        # Get all values at once - fastest method
        all_values = list(src_ws.values)
        
        if not all_values:
            return None, None
        
        # Parse header
        header_row = [str(cell).strip().upper() if cell else "" for cell in all_values[0]]
        
        # Parse data - optimized loop
        parsed_data_list = []
        for row in all_values[1:]:
            row_dict = {}
            has_val = False
            for idx, cell in enumerate(row):
                if idx < len(header_row) and header_row[idx]:
                    # Fast type conversion without formatting
                    if isinstance(cell, (int, float)):
                        raw_val = str(int(cell)) if cell == int(cell) else str(cell)
                    else:
                        raw_val = str(cell) if cell is not None else ""
                    
                    row_dict[header_row[idx]] = raw_val
                    if raw_val:
                        has_val = True
            if has_val:
                parsed_data_list.append(row_dict)
        
        df = pd.DataFrame(parsed_data_list)
        df = df.loc[:, ~df.columns.str.contains('^$')]
        
        # Add SITE_DISPLAY
        def create_site_display(row):
            site_no = row.get('SITE NO', '')
            site_name = row.get('SITE NAME', '')
            if pd.notna(site_no) and site_no:
                try:
                    site_no_clean = str(site_no).replace(',', '')
                    return f"{int(float(site_no_clean))} - {site_name}"
                except:
                    return f"{site_no} - {site_name}"
            return str(site_name)
        
        df["SITE_DISPLAY"] = df.apply(create_site_display, axis=1)
        
        return df, header_row
    
    except Exception as e:
        return None, None

def parse_media_data(source_bytes):
    """Parse media data from Excel bytes"""
    try:
        src_wb = load_workbook(io.BytesIO(source_bytes.getvalue()), data_only=True, read_only=True)
        media_data_list = []
        media_ws = None
        
        # Find media sheet quickly
        for sheet_name in src_wb.sheetnames:
            if "PHOTO" in sheet_name.upper() or "DOC" in sheet_name.upper():
                media_ws = src_wb[sheet_name]
                break
        
        if media_ws:
            media_values = list(media_ws.values)
            for row in media_values:
                t_area = str(row[13]).strip() if len(row) > 13 else ""
                s_name = str(row[15]).strip() if len(row) > 15 else ""
                
                if t_area and s_name and t_area.upper() != "TRADE AREA":
                    media_data_list.append({
                        'TRADE AREA': t_area,
                        'SITE NAME': s_name,
                        '__DIRECT_TCT': row[2] if len(row) > 2 else "",
                        '__DIRECT_LOT_PLAN': row[3] if len(row) > 3 else "",
                        '__DIRECT_BLDG_PLAN': row[4] if len(row) > 4 else "",
                        '__DIRECT_TAX_MAP': row[5] if len(row) > 5 else "",
                        '__DIRECT_PHOTO_1': row[7] if len(row) > 7 else "",
                        '__DIRECT_PHOTO_2': row[8] if len(row) > 8 else "",
                        '__DIRECT_PHOTO_3': row[9] if len(row) > 9 else "",
                        '__DIRECT_PHOTO_4': row[10] if len(row) > 10 else "",
                        '__DIRECT_PHOTO_5': row[11] if len(row) > 11 else "",
                    })
        
        return media_data_list
    except:
        return []

def parse_template(template_bytes):
    """Parse template from Excel bytes"""
    try:
        temp_wb = load_workbook(io.BytesIO(template_bytes))
        placeholders = get_placeholders(temp_wb.active)
        template_bytes_raw = template_bytes.getvalue()
        template_bytes.seek(0)
        return placeholders, template_bytes_raw
    except:
        return None, None

def get_cache_files():
    """Get cache file paths"""
    timestamp = datetime.now().strftime("%Y%m%d")
    return {
        'df': os.path.join(CACHE_DIR, f"df_{timestamp}.parquet"),
        'placeholders': os.path.join(CACHE_DIR, f"placeholders_{timestamp}.pkl"),
        'template': os.path.join(CACHE_DIR, f"template_{timestamp}.bin"),
        'media': os.path.join(CACHE_DIR, f"media_{timestamp}.pkl"),
        'timestamp': os.path.join(CACHE_DIR, f"timestamp_{timestamp}.pkl")
    }

def save_to_cache(df, placeholders, template_bytes_raw, media_data_list, timestamp):
    """Save data to cache files"""
    try:
        cache_files = get_cache_files()
        df.to_parquet(cache_files['df'])
        with open(cache_files['placeholders'], 'wb') as f:
            pickle.dump(placeholders, f)
        with open(cache_files['template'], 'wb') as f:
            f.write(template_bytes_raw)
        with open(cache_files['media'], 'wb') as f:
            pickle.dump(media_data_list, f)
        with open(cache_files['timestamp'], 'wb') as f:
            pickle.dump(timestamp, f)
        return True
    except:
        return False

def load_from_cache():
    """Load data from cache files"""
    try:
        cache_files = get_cache_files()
        if all(os.path.exists(path) for path in cache_files.values()):
            df = pd.read_parquet(cache_files['df'])
            with open(cache_files['placeholders'], 'rb') as f:
                placeholders = pickle.load(f)
            with open(cache_files['template'], 'rb') as f:
                template_bytes_raw = f.read()
            with open(cache_files['media'], 'rb') as f:
                media_data_list = pickle.load(f)
            with open(cache_files['timestamp'], 'rb') as f:
                timestamp = pickle.load(f)
            
            # Check if cache is still valid
            cache_age = (datetime.now() - timestamp).total_seconds()
            if cache_age < CACHE_TTL:
                return df, placeholders, template_bytes_raw, media_data_list, timestamp
    
    except:
        pass
    return None, None, None, None, None

#--- LOAD DATA ASSETS ---
@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_data():
    """Load data with 24-hour caching and timestamp tracking"""
    
    # Try to load from cache first
    cached_data = load_from_cache()
    if cached_data[0] is not None:
        return cached_data
    
    try:
        # Download files in parallel
        source_bytes = download_file(SOURCE_URL)
        template_data = download_file(TEMPLATE_URL)
        
        if source_bytes is None or template_data is None:
            return None, None, None, [], None
        
        # Parse main data and media data in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            main_future = executor.submit(parse_main_data, source_bytes)
            media_future = executor.submit(parse_media_data, source_bytes)
            
            df, _ = main_future.result()
            media_data_list = media_future.result()
        
        if df is None:
            return None, None, None, [], None
        
        # Parse template
        placeholders, template_bytes_raw = parse_template(template_data)
        
        if placeholders is None:
            return None, None, None, [], None
        
        timestamp = datetime.now()
        
        # Save to cache
        save_to_cache(df, placeholders, template_bytes_raw, media_data_list, timestamp)
        
        return df, placeholders, template_bytes_raw, media_data_list, timestamp
    
    except Exception as e:
        return None, None, None, [], None

#--- COMPLETE HTML BLUEPRINT ---
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
    overflow-y: auto !important;
    overflow-x: hidden !important;
}
.report-wrapper {
    width: 100%;
    overflow-y: visible !important;
    overflow-x: hidden !important;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 0;
    margin: 0;
    min-height: 100%;
}
.report-scaler {
    transform-origin: center top;
    width: 100%;
    display: inline-block;
    overflow: visible;
    text-align: center;
}
.ritz.grid-container {
    height: auto;
    overflow: visible !important;
    padding: 10px;
    box-sizing: border-box;
    width: 100%;
    display: inline-block;
    text-align: left;
}
.ritz .waffle a { color: inherit; }
.ritz .waffle td { padding: 2px 3px !important; vertical-align: middle; border: none !important; }
.freezebar-origin-ltr { background-color: #f8f9fa; border: none !important; }
.column-headers-background { background-color: #f8f9fa; text-align: center; font-size: 10pt; color: #444746; font-weight: normal; border: none !important; }
.row-headers-background { background-color: #f8f9fa; text-align: center; font-size: 10pt; color: #444746; font-weight: normal; border: none !important; }
.ritz .waffle .s0 {border-bottom:1px SOLID #bfbfbf;border-right:1px SOLID #bfbfbf;background-color:#800000;text-align:center;font-weight:bold;color:#ffffff;font-size:10pt;white-space:nowrap;direction:ltr;padding: 4px 3px !important;}
.ritz .waffle .s1 {border-bottom:1px SOLID #bfbfbf;border-right:1px SOLID #bfbfbf;background-color:#ffffff;text-align:left;font-weight:bold;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;padding: 4px 3px !important;}
.ritz .waffle .s2 {background-color:#ffffff;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;border: none !important;}
.ritz .waffle .s3 {border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s4 {border: none !important;background-color:#f8f9fa;text-align:left;color:#000000;font-size:10pt;vertical-align:middle;white-space:nowrap;direction:ltr;padding: 4px 3px !important;line-height: 1.4;max-width: 0;overflow: hidden;text-overflow: ellipsis;}
.ritz .waffle .s4.wrap-text {white-space:normal !important;word-wrap:break-word !important;word-break:break-word !important;overflow-wrap:break-word !important;max-width: 100% !important;overflow: visible !important;text-overflow: clip !important;height: auto !important;}
.ritz .waffle .s5 {background-color:#ffffff;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;border: none !important;}
.ritz .waffle .s6 {border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s7 {border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s8 {border: none !important;background-color:#ffffff;text-align:left;color:#ff0000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s9 {border: none !important;background-color:#f8f9fa;text-align:left;color:#000000;font-size:10pt;vertical-align:middle;white-space:nowrap;direction:ltr;padding: 4px 3px !important;line-height: 1.4;max-width: 0;overflow: hidden;text-overflow: ellipsis;}
.ritz .waffle .s9.wrap-text {white-space:normal !important;word-wrap:break-word !important;word-break:break-word !important;overflow-wrap:break-word !important;max-width: 100% !important;overflow: visible !important;text-overflow: clip !important;height: auto !important;}
.ritz .waffle .s10{background-color:#bfbfbf;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;border: none !important;}
.ritz .waffle .s11{border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s12{border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s13{background-color:#b7b7b7;text-align:left;font-weight:bold;color:#ff0000;font-size:10pt;white-space:nowrap;direction:ltr;border: none !important;}
.ritz .waffle .s14{background-color:#b7b7b7;text-align:left;color:#ff0000;font-size:10pt;white-space:nowrap;direction:ltr;border: none !important;}
.ritz .waffle .s15{border: none !important;background-color:#b7b7b7;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s16{border: none !important;background-color:#b7b7b7;text-align:left;color:#ff0000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s17{background-color:#b7b7b7;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;border: none !important;}
.ritz .waffle .s18{border: none !important;background-color:#b7b7b7;text-align:left;color:#ff0000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s19{border: none !important;background-color:#b7b7b7;text-align:left;color:#ff0000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s20{border: none !important;background-color:#b7b7b7;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s21{border: none !important;background-color:#b7b7b7;text-align:left;color:#ff0000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s22{background-color:#ffffff;text-align:left;font-weight:bold;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;border: none !important;}
.ritz .waffle .s23{border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s24{border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;}
.ritz .waffle .s25{border: none !important;background-color:#ffffff;text-align:left;color:#000000;font-size:10pt;white-space:nowrap;direction:ltr;}
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
    function scaleReportToFit() {
        const wrapper = document.querySelector('.report-wrapper');
        const scaler = document.querySelector('.report-scaler');
        const container = document.querySelector('.ritz.grid-container');
        
        if (!wrapper || !scaler || !container) return;
        
        const table = document.querySelector('.waffle');
        if (!table) return;
        
        const containerWidth = wrapper.parentElement ? wrapper.parentElement.clientWidth : window.innerWidth;
        const availableWidth = containerWidth - 40;
        
        table.style.width = 'auto';
        const naturalWidth = table.scrollWidth;
        table.style.width = '100%';
        
        let scale = 1;
        if (naturalWidth > availableWidth) {
            scale = (availableWidth / naturalWidth) * 0.95;
            if (scale < 0.4) scale = 0.4;
        }
        
        if (scale < 1) {
            scaler.style.transform = 'scale(' + scale + ')';
            scaler.style.transformOrigin = 'center top';
            scaler.style.width = (100 / scale) + '%';
            scaler.style.marginBottom = '0px';
            scaler.style.display = 'inline-block';
            scaler.style.textAlign = 'center';
        } else {
            scaler.style.transform = 'none';
            scaler.style.width = '100%';
            scaler.style.marginBottom = '0px';
            scaler.style.display = 'inline-block';
            scaler.style.textAlign = 'center';
        }
        
        container.style.display = 'inline-block';
        container.style.textAlign = 'left';
        container.style.margin = '0 auto';
        
        wrapper.style.overflowY = 'visible';
        wrapper.style.overflowX = 'hidden';
        wrapper.style.width = '100%';
        wrapper.style.display = 'flex';
        wrapper.style.justifyContent = 'center';
        wrapper.style.alignItems = 'flex-start';
        wrapper.style.minHeight = '100%';
        
        container.style.overflowX = 'visible';
        container.style.overflowY = 'visible';
        container.style.width = '100%';
        
        document.body.style.overflowY = 'auto';
        document.body.style.overflowX = 'hidden';
        document.documentElement.style.overflowY = 'auto';
        document.documentElement.style.overflowX = 'hidden';
        
        const tableHeight = table.scrollHeight;
        if (scale < 1) {
            scaler.style.height = (tableHeight * scale + 50) + 'px';
        } else {
            scaler.style.height = 'auto';
        }
    }
    
    setTimeout(scaleReportToFit, 100);
    
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(scaleReportToFit, 100);
    });
    
    const observer = new MutationObserver(function() { 
        setTimeout(scaleReportToFit, 100);
    });
    const tableBody = document.querySelector('.waffle tbody');
    if (tableBody) { 
        observer.observe(tableBody, { childList: true, subtree: true, characterData: true }); 
    }
    
    window.addEventListener('load', function() {
        setTimeout(scaleReportToFit, 200);
    });
});
</script>
</head>
<body>
<div class="report-wrapper">
    <div class="report-scaler">
        <div class="ritz grid-container" dir="ltr">
        <table class="waffle" cellspacing="0" cellpadding="0" style="table-layout: fixed; width: 100%; border-collapse: collapse;">
        <colgroup>
        <col style="width:223px;"> <col style="width:100px;"> <col style="width:86px;"> <col style="width:100px;"> <col style="width:94px;"> <col style="width:100px;"> <col style="width:81px;"> <col style="width:15px;"> <col style="width:148px;"> <col style="width:176px;"> <col style="width:100px;"> <col style="width:100px;"> <col style="width:100px;"> <col style="width:125px;"> <col style="width:29px;">
        </colgroup>
        <tbody>
        <tr style="height: auto;"> <td class="s0" colspan="15">SITE INFORMATION REPORT</td> </tr>
        <tr style="height: auto"> <td class="s1" colspan="7">General Information</td> <td class="s1"></td> <td class="s1" colspan="7">Location</td> </tr>
        <tr style="height: auto"> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s3"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s3"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Trade Area Name</td> <td class="s2"></td> <td class="s4" colspan="5">_TRADE_AREA_</td> <td class="s3"></td> <td class="s5" colspan="2">Site Name</td> <td class="s4" colspan="5">_SITE_NAME_</td> </tr>
        <tr style="height: auto;"> <td class="s2">Site Name:</td> <td class="s2"></td> <td class="s4" colspan="5">_SITE_NAME_</td> <td class="s3"></td> <td class="s5" colspan="2">Unit #, Bldg/St # and St Name</td> <td class="s4" colspan="5">_UNIT_BLDG_ST_NAME_</td> </tr>
        <tr style="height: auto;"> <td class="s2">Site Number:</td> <td class="s2"></td> <td class="s4" colspan="5">_SITE_NO_</td> <td class="s3"></td> <td class="s5" colspan="2">Barangay/District Name</td> <td class="s4" colspan="5">_BARANGAY_DISTRICT_NAME_</td> </tr>
        <tr style="height: auto;"> <td class="s2">Date Started</td> <td class="s2"></td> <td class="s4" colspan="5">_TIMESTAMP_</td> <td class="s3"></td> <td class="s5" colspan="2">City/Municipality</td> <td class="s4" colspan="5">_CITY_MUNICIPALITY_</td> </tr>
        <tr style="height: auto;"> <td class="s5" colspan="2">Date Report Submitted</td> <td class="s4" colspan="5">_DATE_OF_REPORT_</td> <td class="s3"></td> <td class="s5" colspan="2">Region</td> <td class="s4" colspan="5">_REGION_</td> </tr>
        <tr style="height: auto;"> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s3"></td> <td class="s5" colspan="2">Postal Code</td> <td class="s4" colspan="5">_POSTAL_CODE_</td> </tr>
        <tr style="height: 9px"> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s3"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s7"></td> </tr>
        <tr style="height: 19px"> <td class="s1" colspan="7">Terms</td> <td class="s3"></td> <td class="s1" colspan="7">Rates</td> </tr>
        <tr style="height: 19px"> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s3"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s3"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Site Availability Date</td> <td class="s2"></td> <td class="s4" colspan="5">_SITE_AVAILABILITY_DATE_</td> <td class="s3"></td> <td class="s8" colspan="2">Monthly Rental Rate (Php)</td> <td class="s4" colspan="5">_MONTHLY_RENTAL_RATE_</td> </tr>
        <tr style="height: auto;"> <td class="s2">COL Start Date</td> <td class="s2"></td> <td class="s4" colspan="5">_COL_START_DATE_</td> <td class="s3"></td> <td class="s8" colspan="2">Percentage Rent</td> <td class="s4" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">COL End Date</td> <td class="s2"></td> <td class="s4" colspan="5">_COL_END_DATE_</td> <td class="s3"></td> <td class="s8" colspan="2">Minimum Guaranteed Rent</td> <td class="s4" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Lease Terms</td> <td class="s2"></td> <td class="s4" colspan="5">_LEASE_TERMS_</td> <td class="s3"></td> <td class="s8" colspan="2">Annual Escalation Rate (%)</td> <td class="s4" colspan="5">_ESCALATION_</td> </tr>
        <tr style="height: 19px"> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s3"></td> <td class="s8" colspan="2">Advance Rental (Php)</td> <td class="s4" colspan="5">_ADVANCE_RENTAL_</td> </tr>
        <tr style="height: 19px"> <td class="s1" colspan="7">Technical Info</td> <td class="s3"></td> <td class="s8" colspan="2">Security Deposit Amount (Php)</td> <td class="s4" colspan="5">_SECURITY_DEPOSIT_</td> </tr>
        <tr style="height: 19px"> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s3"></td> <td class="s8" colspan="2">CUSA Dues</td> <td class="s4" colspan="5">_CUSA_</td> </tr>
        <tr style="height: auto;"> <td class="s5" colspan="2">Lot /Floor Area (in sqm)</td> <td class="s4" colspan="5">_LOT_FLOOR_AREA_SQM_</td> <td class="s3"></td> <td class="s8" colspan="2">Estimated Revenue Per Mo.</td> <td class="s4" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Frontage (in m)</td> <td class="s2"></td> <td class="s4" colspan="5">_FRONTAGE_</td> <td class="s3"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s7"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Depth (in m)</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s1" colspan="7">Provisions</td> </tr>
        <tr style="height: auto;"> <td class="s5" colspan="2">Floor to Slab Height (in m) - if Bldg</td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s2" colspan="7"></td> </tr>
        <tr style="height: auto;"> <td class="s5" colspan="2">No. of Storeys (If Bldg Lessee)</td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Tenant is the Owner</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s5" colspan="2">Type of Structure(if Bldg Lessee)</td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Lease Type</td> <td class="s9" colspan="5">_LEASE_TYPE_</td> </tr>
        <tr style="height: auto;"> <td class="s2">Soil Profile</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Principal COL</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Supply Access:</td> <td class="s2"></td> <td class="s2" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Sub-Lease Provision</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Power</td> <td class="s10"></td> <td class="s2">Aircon</td> <td class="s10"></td> <td class="s5" colspan="2">LPG Fire Pro</td> <td class="s10"></td> <td class="s3"></td> <td class="s5" colspan="2">Pre-Term/Partial Term</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Water</td> <td class="s10"></td> <td class="s2">Exhaust</td> <td class="s10"></td> <td class="s5" colspan="2">Drainage TP</td> <td class="s10"></td> <td class="s3"></td> <td class="s5" colspan="2">Tripartite Agreement</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: 9px;"> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s3"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s7"></td> </tr>
        <tr style="height: 19px;"> <td class="s1" colspan="7">Lessor and Tenant Details</td> <td class="s3"></td> <td class="s1" colspan="7">If with Sub-Lessor/ Sub-Lessee</td> </tr>
        <tr style="height: 9px;"> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s3"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s3"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Name of Lessor</td> <td class="s2"></td> <td class="s4" colspan="5">_LESSOR_</td> <td class="s3"></td> <td class="s5" colspan="2">Name of Sub-Lessor</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Contact No.</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Contact No.</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">E-mail Address</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">E-mail Address</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Type of Ownership</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Type of Ownership</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Company Name</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Company Name</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s5" colspan="2">Developer Account Name</td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Developer Account Name</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Business Address</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Business Address</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s5" colspan="2">Name of Authorized Representative</td> <td class="s4" colspan="5">_CONTACT_PERSON_SOURCE_</td> <td class="s3"></td> <td class="s5" colspan="2">Name of Authorized Representative</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s5" colspan="2">Residence Address of Authorized Representative</td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Residence Address of Authorized Representative</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Contact No.</td> <td class="s2"></td> <td class="s4" colspan="5">_CONTACT_NUMBER_</td> <td class="s3"></td> <td class="s5" colspan="2">Contact No.</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">E-mail Address</td> <td class="s2"></td> <td class="s4" colspan="5">_EMAIL_ADDRESS_</td> <td class="s3"></td> <td class="s5" colspan="2">E-mail Address</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s3"></td> <td class="s2"></td> <td class="s2"></td> <td class="s2"></td> <td class="s3" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Name of Lessee</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Name of Sub-Lessee</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Position</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Position</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Contact No.</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Contact No.</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">E-mail Address</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">E-mail Address</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s5" colspan="2">Name of Authorized Representative</td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Name of Authorized Representative</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Business Address</td> <td class="s2"></td> <td class="s4" colspan="5"></td> <td class="s3"></td> <td class="s5" colspan="2">Business Address</td> <td class="s9" colspan="5"></td> </tr>
        <tr style="height: 9px;"> <td class="s11"></td> <td class="s11"></td> <td class="s11"></td> <td class="s11"></td> <td class="s11"></td> <td class="s11"></td> <td class="s11"></td> <td class="s12"></td> <td class="s11"></td> <td class="s11"></td> <td class="s11"></td> <td class="s11"></td> <td class="s11"></td> <td class="s11"></td> <td class="s12"></td> </tr>
        <tr style="height: 19px;"> <td class="s13" colspan="15">Regulatory</td> </tr>
        <tr style="height: auto;"> <td class="s14">Setback Requirement</td> <td class="s15" colspan="4"></td> <td class="s16" colspan="2">Perm Traffic Re-Routing</td> <td class="s17"></td> <td class="s15" colspan="2"></td> <td class="s18" colspan="5">Future Development</td> </tr>
        <tr style="height: auto;"> <td class="s14">Road Widening</td> <td class="s15" colspan="4"></td> <td class="s16" colspan="2">Perm Road Closure</td> <td class="s17"></td> <td class="s15" colspan="2"></td> <td class="s18" colspan="5">Zoning Clearance</td> </tr>
        <tr style="height: auto;"> <td class="s19">Pedestrian Overpass</td> <td class="s20" colspan="4"></td> <td class="s19" colspan="2">Infrastructure Programs</td> <td class="s20"></td> <td class="s20" colspan="2"></td> <td class="s21" colspan="5">Gas Station</td> </tr>
        <tr style="height: auto;"> <td class="s2" colspan="14"></td> <td class="s3"></td> </tr>
        <tr style="height: 19px;"> <td class="s22">Site Acquirability:</td> <td class="s2" colspan="13"></td> <td class="s3"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Confidence Level</td> <td class="s4" colspan="2"></td> <td class="s2" colspan="11"></td> <td class="s3"></td> </tr>
        <tr style="height: auto;"> <td class="s2">Site Availability</td> <td class="s23" colspan="2"><div style="width:184px;left:-1px">_SITE_AVAILABILITY_CLASS_</div></td> <td class="s24"></td> <td class="s25"></td> <td class="s2" colspan="10"></td> <td class="s3"></td> </tr>
        <tr class="remarks-row" style="height: auto;"> <td class="s6 remarks-label" style="white-space: nowrap; vertical-align: top; padding-top: 8px;">Other Remarks:</td> <td class="s5" colspan="7" style="white-space: normal; word-wrap: break-word; word-break: break-word; overflow-wrap: break-word; max-width: 100%; overflow: visible; text-overflow: clip; height: auto; line-height: 1.6; padding: 8px 6px;">_REMARKS_</td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s6"></td> <td class="s7"></td> </tr>
        </tbody>
        </table>
        </div>
    </div>
</div>
</body>
</html>
"""

# --- MAIN LOGIC BEGINS ---

# --- Step 1: Display Login Function ---
if not st.session_state.authenticated:
    # Hide loading overlay during login
    st.markdown("""
    <style>
    #loading-overlay { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    r1_col1, r1_col2, r1_col3 = st.columns([1, 1.2, 1])
    with r1_col2:
        st.markdown("<h3 style='text-align: center; margin-top:50px;'>TRS Site Information Report</h3>", unsafe_allow_html=True)
        password_input = st.text_input("", placeholder="Enter password", type="password")
        if st.button("Login", use_container_width=True) or (password_input and len(password_input) > 0):
            if check_password(password_input):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid token string provided.")
    st.stop()

# At this point, user is authenticated

# --- Step 2: Initialize load_data() and derive defaults (this happens post-login) ---
# Show loading spinner while data loads
with st.spinner("Loading Data..."):
    data = load_data()
    df, placeholders, template_bytes_raw, media_data_list, data_timestamp = data

if df is None or template_bytes_raw is None:
    st.error("Failed to load data assets. Please verify link paths.")
    st.stop()

# Store timestamp in session state if not set or if it's None
if st.session_state.data_timestamp is None and data_timestamp is not None:
    st.session_state.data_timestamp = data_timestamp

# Mark data as loaded
st.session_state.data_loaded = True

# --- Step 3: Determine Default Selections (Preset Logic) ---
trade_areas = sorted(df["TRADE AREA"].dropna().unique().tolist())
first_row = df.iloc[0] if not df.empty else None
first_trade_area = first_row["TRADE AREA"] if first_row is not None else ""
first_site_display = first_row["SITE_DISPLAY"] if first_row is not None else ""
default_ta_index = trade_areas.index(first_trade_area) if first_trade_area in trade_areas else 0

# --- Step 4: Apply Presets and Render UI (Row 1 and Row 2) ---
deploy_workspace_security_protocols()

# Remove loading overlay after all content is rendered
st.markdown("""
<script>
// Hide the loading overlay when everything is rendered
setTimeout(function() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(function() {
            overlay.style.display = 'none';
        }, 300);
    }
}, 500);
</script>
""", unsafe_allow_html=True)

#--- ROW 1: CONTROLS ROW (ULTRA-COMPACT) ---
col1, col2, col3 = st.columns([1.5, 1.5, 1.0])

with col1:
    selected_ta = st.selectbox("Trade Area", options=trade_areas, index=default_ta_index, label_visibility="visible")

with col2:
    if selected_ta:
        raw_sites = df[df["TRADE AREA"] == selected_ta]["SITE_DISPLAY"].dropna().unique().tolist()
        sites_in_ta = sorted(raw_sites, key=parse_site_number)

        if selected_ta == first_trade_area and first_site_display in sites_in_ta:
            default_site_index = sites_in_ta.index(first_site_display)
        else:
            default_site_index = 0
    else:
        sites_in_ta = []
        default_site_index = 0

    selected_site_display = st.selectbox("Site Name", options=sites_in_ta, index=default_site_index, label_visibility="visible")

with col3:
    if selected_ta:
        st.download_button(
            label="Export",
            data=generate_trade_area_report(selected_ta, df, template_bytes_raw, placeholders),
            file_name=f"{selected_ta}_Site_Information_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="export_button"
        )

#--- ROW 2: MULTI-TAB REPORT & MEDIA VIEWER FRAME ---
if selected_ta and selected_site_display:
    # Get site data based on the selected/preset site
    site_data = df[df["SITE_DISPLAY"] == selected_site_display]
    site_row_data = site_data.iloc[0] if not site_data.empty else None

    # Get corresponding media data
    target_ta = str(site_row_data["TRADE AREA"]) if site_row_data is not None else ""
    target_sn = str(site_row_data["SITE NAME"]) if site_row_data is not None else ""
    media_row_data = {}
    if site_row_data is not None:
        for m in media_data_list:
            if m['TRADE AREA'] == target_ta and m['SITE NAME'] == target_sn:
                media_row_data = m
                break
        if not media_row_data:
            media_row_data = site_row_data.to_dict() if hasattr(site_row_data, 'to_dict') else {}

    # Instantiate Workspace Tabs instantly *after* controls are defined
    tab_report, tab_photos, tab_docs = st.tabs([
        "PROPERTY INFORMATION",
        "PROPERTY PHOTOS",
        "PROPERTY DOCS"
    ])

    # --- TAB 1: SITE INFORMATION REPORT ---
    with tab_report:
        if site_row_data is not None:
            try:
                def process_val(key_string):
                    val = site_row_data.get(key_string.upper(), "")
                    if pd.isna(val) or val is None: 
                        return ""
                    return val
                
                rendered_view = HTML_FRAMEWORK
                rendered_view = rendered_view.replace("_TRADE_AREA_", str(process_val("TRADE AREA")))
                rendered_view = rendered_view.replace("_SITE_NAME_", str(process_val("SITE NAME")))
                rendered_view = rendered_view.replace("_SITE_NO_", str(process_val("SITE NO")))
                rendered_view = rendered_view.replace("_TIMESTAMP_", str(process_val("TIMESTAMP")))
                rendered_view = rendered_view.replace("_DATE_OF_REPORT_", str(process_val("DATE OF REPORT")))
                rendered_view = rendered_view.replace("_UNIT_BLDG_ST_NAME_", str(process_val("UNIT #, BLDG/ST # AND ST NAME")))
                rendered_view = rendered_view.replace("_BARANGAY_DISTRICT_NAME_", str(process_val("BARANGAY/DISTRICT NAME")))
                rendered_view = rendered_view.replace("_CITY_MUNICIPALITY_", str(process_val("CITY/MUNICIPALITY")))
                rendered_view = rendered_view.replace("_REGION_", str(process_val("REGION")))
                rendered_view = rendered_view.replace("_POSTAL_CODE_", str(process_val("POSTAL CODE")))
                rendered_view = rendered_view.replace("_SITE_AVAILABILITY_DATE_", str(process_val("SITE AVAILABILITY DATE")))
                rendered_view = rendered_view.replace("_MONTHLY_RENTAL_RATE_", str(process_val("MONTHLY RENTAL RATE")))
                rendered_view = rendered_view.replace("_COL_START_DATE_", str(process_val("COL START DATE")))
                rendered_view = rendered_view.replace("_COL_END_DATE_", str(process_val("COL END DATE")))
                rendered_view = rendered_view.replace("_LEASE_TERMS_", str(process_val("LEASE TERMS")))
                rendered_view = rendered_view.replace("_ESCALATION_", str(process_val("ESCALATION")))
                rendered_view = rendered_view.replace("_ADVANCE_RENTAL_", str(process_val("ADVANCE RENTAL")))
                rendered_view = rendered_view.replace("_SECURITY_DEPOSIT_", str(process_val("SECURITY DEPOSIT")))
                rendered_view = rendered_view.replace("_CUSA_", str(process_val("CUSA")))
                rendered_view = rendered_view.replace("_LOT_FLOOR_AREA_SQM_", str(process_val("LOT/FLOOR AREA SQM")))
                rendered_view = rendered_view.replace("_FRONTAGE_", str(process_val("FRONTAGE")))
                rendered_view = rendered_view.replace("_LEASE_TYPE_", str(process_val("LEASE TYPE")))
                rendered_view = rendered_view.replace("_LESSOR_", str(process_val("LESSOR")))
                rendered_view = rendered_view.replace("_CONTACT_PERSON_SOURCE_", str(process_val("CONTACT PERSON/SOURCE")))
                rendered_view = rendered_view.replace("_CONTACT_NUMBER_", str(process_val("CONTACT NUMBER")))
                rendered_view = rendered_view.replace("_EMAIL_ADDRESS_", str(process_val("EMAIL ADDRESS")))
                rendered_view = rendered_view.replace("_SITE_AVAILABILITY_CLASS_", str(process_val("SITE AVAILABILITY CLASS")))
                rendered_view = rendered_view.replace("_REMARKS_", str(process_val("REMARKS")))
                
                rendered_view = re.sub(r"_[A-Z0-9_]+_", "", rendered_view)
                
                components.html(rendered_view, height=1200, scrolling=False)
            except Exception as e:
                st.error(f"Error compiling visual matrix framework: {str(e)}")
        else:
             st.info("No data available for the selected site.")
            
    # --- TAB 2: PROPERTY PHOTOS (3x3 LAYOUT) ---
    with tab_photos:
        if site_row_data is not None and media_row_data:
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
                grid_html = '''
                <style>
                    .image-grid-3x3 {
                        display: grid;
                        grid-template-columns: repeat(3, 1fr);
                        gap: 15px;
                        padding: 10px 0;
                        max-width: 100%;
                    }
                    .image-grid-item {
                        border: 1px solid #dadce0;
                        border-radius: 8px;
                        overflow: hidden;
                        background: #f8f9fa;
                        transition: transform 0.2s;
                        aspect-ratio: 4/3;
                        display: flex;
                        flex-direction: column;
                    }
                    .image-grid-item:hover {
                        transform: scale(1.02);
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    }
                    .image-grid-item img {
                        width: 100%;
                        height: 100%;
                        object-fit: cover;
                        display: block;
                        flex: 1;
                    }
                    .image-grid-item .label {
                        padding: 6px 8px;
                        font-size: 0.7rem;
                        font-weight: 600;
                        color: #5f6368;
                        background: white;
                        text-align: center;
                        border-top: 1px solid #dadce0;
                        flex-shrink: 0;
                    }
                    .image-grid-item a {
                        text-decoration: none;
                        color: inherit;
                        display: flex;
                        flex-direction: column;
                        height: 100%;
                    }
                    @media (max-width: 768px) {
                        .image-grid-3x3 {
                            grid-template-columns: repeat(2, 1fr);
                        }
                    }
                    @media (max-width: 480px) {
                        .image-grid-3x3 {
                            grid-template-columns: 1fr;
                        }
                    }
                </style>
                <div class="image-grid-3x3">
                '''
                for label, thumb_url, full_url in valid_photos:
                    grid_html += f'''
                        <div class="image-grid-item">
                            <a href="{full_url}" target="_blank">
                                <img src="{thumb_url}" alt="{label}" loading="lazy">
                                <div class="label">{label}</div>
                            </a>
                        </div>
                    '''
                grid_html += '</div>'
                components.html(grid_html, height=1200, scrolling=False)
            else:
                st.info("No photo links configured for this property record selection.")
        else:
             st.info("No data available for the selected site.")

    # --- TAB 3: PROPERTY DOCS (3x3 LAYOUT) ---
    with tab_docs:
        if site_row_data is not None and media_row_data:
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
                grid_html = '''
                <style>
                    .image-grid-3x3 {
                        display: grid;
                        grid-template-columns: repeat(3, 1fr);
                        gap: 15px;
                        padding: 10px 0;
                        max-width: 100%;
                    }
                    .image-grid-item {
                        border: 1px solid #dadce0;
                        border-radius: 8px;
                        overflow: hidden;
                        background: #f8f9fa;
                        transition: transform 0.2s;
                        aspect-ratio: 4/3;
                        display: flex;
                        flex-direction: column;
                    }
                    .image-grid-item:hover {
                        transform: scale(1.02);
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    }
                    .image-grid-item img {
                        width: 100%;
                        height: 100%;
                        object-fit: cover;
                        display: block;
                        flex: 1;
                    }
                    .image-grid-item .label {
                        padding: 6px 8px;
                        font-size: 0.7rem;
                        font-weight: 600;
                        color: #5f6368;
                        background: white;
                        text-align: center;
                        border-top: 1px solid #dadce0;
                        flex-shrink: 0;
                    }
                    .image-grid-item a {
                        text-decoration: none;
                        color: inherit;
                        display: flex;
                        flex-direction: column;
                        height: 100%;
                    }
                    @media (max-width: 768px) {
                        .image-grid-3x3 {
                            grid-template-columns: repeat(2, 1fr);
                        }
                    }
                    @media (max-width: 480px) {
                        .image-grid-3x3 {
                            grid-template-columns: 1fr;
                        }
                    }
                </style>
                <div class="image-grid-3x3">
                '''
                for label, thumb_url, full_url in valid_docs:
                    grid_html += f'''
                        <div class="image-grid-item">
                            <a href="{full_url}" target="_blank">
                                <img src="{thumb_url}" alt="{label}" loading="lazy">
                                <div class="label">{label}</div>
                            </a>
                        </div>
                    '''
                grid_html += '</div>'
                components.html(grid_html, height=1200, scrolling=False)
            else:
                st.info("No layout documents configured for this property record selection.")
        else:
             st.info("No data available for the selected site.")
