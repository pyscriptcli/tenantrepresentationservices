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
import folium
from streamlit_folium import folium_static
from folium.plugins import Draw
import branca.colormap as cm

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

/* Hide the label of the password input on the login screen */
div[data-testid="stTextInput"] label {
    display: none !important;
}

div[data-testid="stTextInput"] button {
    display: none !important;
}

/* Main viewport with outer scrollbar only */
html, body {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: 100% !important;
    margin: 0px !important;
    padding: 0px !important;
    background-color: #f0f2f6 !important;
}

/* Hide Streamlit header */
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

/* Main container styling */
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

/* Control bar styling */
div[data-testid="stHorizontalBlock"] { 
    gap: 0.5rem !important; 
    align-items: flex-end !important; 
    background: #ffffff;
    padding: 0.4rem 0.5rem !important; 
    border-radius: 8px;
    margin-top: 0px !important; 
    margin-bottom: 10px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
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
button[data-baseweb="tab"] {
    padding-top: 0.3rem !important;
    padding-bottom: 0.3rem !important;
    font-size: 0.85rem !important;
}

div[data-testid="stTabs"] {
    margin-top: -5px !important;
}

/* Map container */
.folium-map {
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    overflow: hidden;
}

/* Popup styling */
.popup-content {
    font-family: 'Google Sans', sans-serif;
    padding: 10px;
    max-width: 300px;
}

.popup-content h4 {
    margin: 0 0 8px 0;
    color: #003366;
    font-size: 14px;
}

.popup-content p {
    margin: 4px 0;
    font-size: 12px;
    color: #333;
}

.popup-content .site-link {
    display: inline-block;
    margin-top: 8px;
    padding: 4px 12px;
    background-color: #003366;
    color: white !important;
    text-decoration: none;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
}

/* Hide deployment watermarks */
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
    st.session_state.selected_site = None
    st.session_state.active_tab = "PROPERTY INFORMATION"

def check_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest() == TARGET_HASH

#--- CONFIGURATION ---
SOURCE_URL = "https://docs.google.com/spreadsheets/d/14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE/export?format=xlsx"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/1uS3xmnPi0o4c_EayQtURYDSMMPRDRGSb/export?format=xlsx"
KML_URL = "https://www.google.com/maps/d/kml?mid=1CSUoDxCi-trQTTz_D6NjI3m0Kc5OQhM&1"

#--- HELPER FUNCTIONS ---
@st.cache_data(ttl=3600)
def download_file(url):
    try:
        response = requests.get(url, timeout=30)
        return io.BytesIO(response.content) if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=3600)
def fetch_kml_data():
    """Fetch and parse KML data from Google My Maps"""
    try:
        response = requests.get(KML_URL, timeout=30)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return None

def parse_kml_for_polygons(kml_content):
    """Extract polygons and their properties from KML"""
    import xml.etree.ElementTree as ET
    
    if not kml_content:
        return []
    
    try:
        # Register KML namespace
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        root = ET.fromstring(kml_content)
        
        polygons = []
        placemarks = root.findall('.//kml:Placemark', ns)
        
        for placemark in placemarks:
            name_elem = placemark.find('kml:name', ns)
            name = name_elem.text if name_elem is not None else ""
            
            # Get coordinates
            polygon_elem = placemark.find('.//kml:Polygon', ns)
            if polygon_elem is None:
                polygon_elem = placemark.find('.//kml:MultiGeometry', ns)
                if polygon_elem is not None:
                    polygon_elem = polygon_elem.find('.//kml:Polygon', ns)
            
            if polygon_elem is not None:
                coords_elem = polygon_elem.find('.//kml:coordinates', ns)
                if coords_elem is not None:
                    coords_text = coords_elem.text.strip()
                    coords = []
                    for coord in coords_text.split():
                        parts = coord.split(',')
                        if len(parts) >= 2:
                            coords.append([float(parts[1]), float(parts[0])])
                    
                    # Get extended data
                    site_name = name
                    trade_area = ""
                    ext_data = placemark.find('.//kml:ExtendedData', ns)
                    if ext_data is not None:
                        for data in ext_data.findall('.//kml:Data', ns):
                            name_attr = data.get('name')
                            value_elem = data.find('.//kml:value', ns)
                            if name_attr and value_elem is not None:
                                if name_attr == "SITE_NAME":
                                    site_name = value_elem.text
                                elif name_attr == "TRADE_AREA":
                                    trade_area = value_elem.text
                    
                    if coords:
                        polygons.append({
                            'name': site_name,
                            'trade_area': trade_area,
                            'coordinates': coords,
                            'description': name
                        })
        
        return polygons
    except Exception as e:
        st.error(f"Error parsing KML: {str(e)}")
        return []

def clean_and_extract_url(cell_value):
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
    if index < len(row_cells):
        cell = row_cells[index]
        if cell.hyperlink and cell.hyperlink.target:
            return clean_and_extract_url(cell.hyperlink.target)
        return clean_and_extract_url(cell.value)
    return ""

def extract_google_drive_id(clean_url):
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

#--- COMPLETE HTML BLUEPRINT FOR SITE REPORT ---
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
    overflow: auto; 
}
.ritz.grid-container {
    height: auto;
    overflow: visible !important;
    padding: 10px;
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
</body>
</html>
"""

#--- LOAD DATA ASSETS ---
@st.cache_data(ttl=3600, show_spinner=True)
def load_data():
    source_bytes = download_file(SOURCE_URL)
    template_data = download_file(TEMPLATE_URL)
    kml_data = fetch_kml_data()
    
    if source_bytes is None or template_data is None:
        return None, None, None, [], []
    
    # Parse KML for polygons
    polygons = parse_kml_for_polygons(kml_data) if kml_data else []
    
    # Ingest openpyxl layout
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
    
    # Extract media data
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
    template_bytes_raw = template_data.getvalue()
    template_data.seek(0)
    
    return df, placeholders, template_bytes_raw, media_data_list, polygons

#--- CREATE FOLIUM MAP WITH POLYGONS ---
def create_site_map(polygons, df, selected_ta=None, selected_site=None):
    # Calculate center
    center_lat, center_lon = 14.5995, 120.9842  # Default to Manila
    
    if polygons:
        all_coords = []
        for poly in polygons:
            all_coords.extend(poly['coordinates'])
        if all_coords:
            center_lat = sum(c[0] for c in all_coords) / len(all_coords)
            center_lon = sum(c[1] for c in all_coords) / len(all_coords)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    
    # Add Draw plugin for polygon interaction
    Draw(export=True).add_to(m)
    
    # Create color map for trade areas
    trade_areas = df["TRADE AREA"].dropna().unique().tolist()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
    color_map = {}
    for i, ta in enumerate(trade_areas):
        color_map[ta] = colors[i % len(colors)]
    
    # Add polygons
    for poly in polygons:
        site_name = poly['name']
        trade_area = poly['trade_area']
        coords = poly['coordinates']
        
        # Determine color
        color = color_map.get(trade_area, '#808080')
        
        # Create popup
        popup_html = f"""
        <div class="popup-content">
            <h4>{site_name}</h4>
            <p><strong>Trade Area:</strong> {trade_area}</p>
            <p><strong>Click polygon to view details</strong></p>
        </div>
        """
        popup = folium.Popup(popup_html, max_width=300)
        
        # Add polygon
        folium.Polygon(
            locations=coords,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.4,
            popup=popup,
            tooltip=site_name
        ).add_to(m)
        
        # Add marker at center of polygon
        center = [sum(c[0] for c in coords) / len(coords), sum(c[1] for c in coords) / len(coords)]
        folium.Marker(
            location=center,
            icon=folium.DivIcon(
                html=f'<div style="background-color:{color};color:white;border-radius:50%;width:12px;height:12px;border:2px solid white;"></div>'
            )
        ).add_to(m)
    
    return m

#--- RENDER SITE INFORMATION IN TABS ---
def render_site_tabs(site_row_data, media_row_data, selected_site_display):
    tab_report, tab_photos, tab_docs = st.tabs([
        "🏢 PROPERTY INFORMATION",
        "📸 PROPERTY PHOTOS", 
        "📄 PROPERTY DOCS"
    ])
    
    with tab_report:
        if site_row_data is not None:
            try:
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
                
                components.html(rendered_view, height=1200, scrolling=False)
            except Exception as e:
                st.error(f"Error compiling visual matrix framework: {str(e)}")
        else:
            st.info("No data available for the selected site.")
    
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
                    .image-grid {
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
                        .image-grid { grid-template-columns: repeat(2, 1fr); }
                    }
                    @media (max-width: 480px) {
                        .image-grid { grid-template-columns: 1fr; }
                    }
                </style>
                <div class="image-grid">
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
                    .image-grid {
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
                        .image-grid { grid-template-columns: repeat(2, 1fr); }
                    }
                    @media (max-width: 480px) {
                        .image-grid { grid-template-columns: 1fr; }
                    }
                </style>
                <div class="image-grid">
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

#--- MAIN LOGIC ---

# LOGIN
if not st.session_state.authenticated:
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

# Load data
df, placeholders, template_bytes_raw, media_data_list, polygons = load_data()

if df is None or template_bytes_raw is None:
    st.error("Failed to load data assets. Please verify link paths.")
    st.stop()

# --- LAYOUT: MAP + CONTROLS ---
st.markdown("""
    <div style="background: linear-gradient(90deg, #003366 0%, #1a5276 100%); padding: 8px 16px; border-radius: 8px; margin-bottom: 12px;">
        <h2 style="color: white; margin: 0; font-size: 1.2rem; font-weight: 500;">📍 Site Sourcing Viewer</h2>
    </div>
""", unsafe_allow_html=True)

# --- TWO COLUMN LAYOUT ---
col_map, col_sidebar = st.columns([2.2, 1])

with col_map:
    # Create and display map
    m = create_site_map(polygons, df)
    folium_static(m, width=None, height=600)

with col_sidebar:
    st.markdown("### 🔍 Site Details")
    
    # Trade Area dropdown
    trade_areas = sorted(df["TRADE AREA"].dropna().unique().tolist())
    selected_ta = st.selectbox("Trade Area", options=trade_areas, index=0, key="ta_select")
    
    # Site Name dropdown (filtered by trade area)
    if selected_ta:
        sites_in_ta = df[df["TRADE AREA"] == selected_ta]["SITE_DISPLAY"].dropna().unique().tolist()
        sites_in_ta = sorted(sites_in_ta, key=parse_site_number)
    else:
        sites_in_ta = []
    
    selected_site_display = st.selectbox("Site Name", options=sites_in_ta, index=0, key="site_select")
    
    # Export button
    if selected_ta:
        st.download_button(
            label="📥 Export Trade Area Report",
            data=generate_trade_area_report(selected_ta, df, template_bytes_raw, placeholders),
            file_name=f"{selected_ta}_Site_Information_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    # Quick info preview
    if selected_site_display:
        site_data = df[df["SITE_DISPLAY"] == selected_site_display]
        if not site_data.empty:
            site_row = site_data.iloc[0]
            st.markdown("---")
            st.markdown("### 📋 Quick Info")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Site #:** {site_row.get('SITE NO', 'N/A')}")
                st.markdown(f"**Address:** {site_row.get('UNIT #, BLDG/ST # AND ST NAME', 'N/A')}")
            with col_b:
                st.markdown(f"**City:** {site_row.get('CITY/MUNICIPALITY', 'N/A')}")
                st.markdown(f"**Region:** {site_row.get('REGION', 'N/A')}")

# --- SITE INFORMATION TABS ---
if selected_site_display:
    st.markdown("---")
    st.markdown(f"### 📊 Site Report: {selected_site_display}")
    
    # Get site data
    site_data = df[df["SITE_DISPLAY"] == selected_site_display]
    site_row_data = site_data.iloc[0] if not site_data.empty else None
    
    # Get media data
    target_ta = str(site_row_data["TRADE AREA"]) if site_row_data is not None else ""
    target_sn = str(site_row_data["SITE NAME"]) if site_row_data is not None else ""
    media_row_data = {}
    if site_row_data is not None:
        for m in media_data_list:
            if m['TRADE AREA'] == target_ta and m['SITE NAME'] == target_sn:
                media_row_data = m
                break
    
    # Render tabs
    render_site_tabs(site_row_data, media_row_data, selected_site_display)
