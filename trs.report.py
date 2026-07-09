import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from openpyxl.utils import get_column_letter, range_boundaries
import re
import io
import requests
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

#--- LINE 1 GLOBAL STYLESHEET ENFORCER (MAX REAL ESTATE & OUTER SCROLLBAR) ---
st.markdown("""
<style >
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');

* { font-family: 'Google Sans', 'Roboto', 'Segoe UI', sans-serif !important; }

/* Hide the label of the password input on the login screen */
div[data-testid="stTextInput"] label { display: none !important; }
div[data-testid="stTextInput"] button { display: none !important; }

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
.stApp, .appview-container, .main, [data-testid="stAppViewContainer"], 
[data-testid="stMain"], .block-container, [data-testid="stMainBlockContainer"] {
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

div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) {
    align-self: flex-end !important;
    padding-bottom: 4px !important;
}

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

._profilePreview_gzau3_63, ._link_gzau3_10, [class*='_profilePreview'],
[class*='_link_gzau3'], a[href*='share.streamlit.io'], a[href*='streamlit.io'],
img[src*='avatar'], [class*='avatar'], #MainMenu, button[title="View source"],
.stAppDeployButton, div[data-testid="stStatusWidget"] {
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
        const restrictedUrls = ["https://share.streamlit.io/user/pyscriptcli", "https://streamlit.io/cloud"];
        function checkAndBlockUrl(url) {
            if (!url) return false;
            const shouldBlock = restrictedUrls.some(blockedUrl => url.toLowerCase().trim().includes(blockedUrl.toLowerCase().trim()));
            if (shouldBlock) {
                window.stop();
                window.top ? window.top.location.href = window.location.origin : window.location.href = window.location.origin;
                return true;
            }
            return false;
        }
        document.addEventListener('click', function(e) {
            const target = e.target.closest('a');
            if (target && target.href && checkAndBlockUrl(target.href)) { e.preventDefault(); e.stopPropagation(); }
        }, true);
        const originalAssign = window.location.assign;
        window.location.assign = function(url) { if (!checkAndBlockUrl(url)) originalAssign.apply(this, arguments); };
        const originalReplace = window.location.replace;
        window.location.replace = function(url) { if (!checkAndBlockUrl(url)) originalReplace.apply(this, arguments); };
        function purgeTargetElements() {
            const targetSelectors = ["._profilePreview_gzau3_63", "._link_gzau3_10", "[class*='_profilePreview']", "[class*='_link_gzau3']", "a[href*='share.streamlit.io']", "a[href*='streamlit.io']", "img[src*='avatar']", "[class*='avatar']"];
            targetSelectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => el.style.setProperty('display', 'none', 'important'));
                if (window.top && window.top.document) {
                    try { window.top.document.querySelectorAll(selector).forEach(el => el.style.setProperty('display', 'none', 'important')); } catch(err) {}
                }
            });
        }
        purgeTargetElements();
        const layoutObserver = new MutationObserver(purgeTargetElements);
        if (document.body) layoutObserver.observe(document.body, { childList: true, subtree: true });
        setInterval(function() {
            purgeTargetElements();
            try { checkAndBlockUrl(window.location.href); if (window.top && window.top !== window) checkAndBlockUrl(window.top.location.href); } catch(e) {}
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

# --- 1. ISOLATED LOGIN SEQUENCE (Prevents UI Overlap & Blank Screens) ---
if not st.session_state.authenticated:
    login_placeholder = st.empty()
    with login_placeholder.container():
        r1_col1, r1_col2, r1_col3 = st.columns([1, 1.2, 1])
        with r1_col2:
            st.markdown("<h3 style='text-align: center; margin-top:50px;'>TRS Site Information Report</h3>", unsafe_allow_html=True)
            password_input = st.text_input("", placeholder="Enter password", type="password")
            if st.button("Login", use_container_width=True) or (password_input and len(password_input) > 0):
                if check_password(password_input):
                    st.session_state.authenticated = True
                    login_placeholder.empty() # Instantly clears the login UI
                    st.rerun()
                else:
                    st.error("Invalid token string provided.")
    st.stop() # Execution absolutely stops here if not authenticated

#--- CONFIGURATION (Refactored for Live Pandas API) ---
SPREADSHEET_ID = "14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE"
# GID=0 targets the main primary sheet
MAIN_DATA_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
# Optional: Set the explicit name of your Media tab if it resides on a different sheet index
MEDIA_SHEET_NAME = "PHOTOS" 
MEDIA_DATA_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&sheet={MEDIA_SHEET_NAME}"

# The template remains an .xlsx so openpyxl can inject the data into it properly
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/1uS3xmnPi0o4c_EayQtURYDSMMPRDRGSb/export?format=xlsx"

#--- HELPER FUNCTIONS ---
def clean_and_extract_url(val_str):
    """Parses live strings from pandas to extract hidden URL links."""
    if pd.isna(val_str) or not val_str:
        return ""
    val_str = str(val_str).strip()
    formula_match = re.search(r'IMAGE\s*\(\s*["\'](https://[^"\']+)["\']', val_str, re.IGNORECASE)
    if formula_match: return formula_match.group(1)
    url_match = re.search(r'(https://[^\s"\']+)', val_str)
    if url_match: return url_match.group(1)
    return val_str

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

@st.cache_data(ttl=3600, show_spinner=False)
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
    if "TEMPLATE_TO_DELETE" in wb.sheetnames: wb.remove(wb["TEMPLATE_TO_DELETE"])
    for name in original_sheets:
        if name in wb.sheetnames and name != "TEMPLATE_TO_DELETE": wb.remove(wb[name])
    wb_buffer = io.BytesIO()
    wb.save(wb_buffer)
    wb_buffer.seek(0)
    return wb_buffer.getvalue()

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
    overflow: auto; 
}
.ritz.grid-container { height: auto; overflow: visible !important; padding: 10px; box-sizing: border-box; }
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
.ritz .waffle .s13{background-color:#bfbfbf;text-align:left;font-weight:bold;color:#ff0000;font-size:8pt;white-space:nowrap;direction:ltr;border: none !important;}
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

# --- 2. SINGLETON DATA LOAD (Triggers only ONCE right after login) ---
def fetch_live_data():
    """Fetches direct live strings from Google Sheets via fast CSV endpoints"""
    # 1. Fetch Main Data (Milliseconds)
    df = pd.read_csv(MAIN_DATA_URL, dtype=str).fillna("")
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains('^$')]
    
    def create_site_display(row):
        site_no = row.get('SITE NO', '')
        site_name = row.get('SITE NAME', '')
        if pd.notna(site_no) and str(site_no).strip() != '':
            try: return f"{int(float(str(site_no)))} - {site_name}"
            except: return f"{site_no} - {site_name}"
        return str(site_name)
        
    df["SITE_DISPLAY"] = df.apply(create_site_display, axis=1)
    
    # 2. Fetch Media Data (Fallback to main if specific tab fails)
    media_df = df.copy() 
    try:
        temp_media = pd.read_csv(MEDIA_DATA_URL, dtype=str).fillna("")
        if not temp_media.empty:
            media_df = temp_media
    except:
        pass
        
    media_data_list = []
    # Map back to exact column index logic used in original setup
    for _, row in media_df.iterrows():
        try:
            t_area = clean_and_extract_url(row.iloc[13])
            s_name = clean_and_extract_url(row.iloc[15])
            if t_area and s_name and t_area.upper() != "TRADE AREA":
                media_data_list.append({
                    'TRADE AREA': t_area,
                    'SITE NAME': s_name,
                    '__DIRECT_TCT': clean_and_extract_url(row.iloc[2]),
                    '__DIRECT_LOT_PLAN': clean_and_extract_url(row.iloc[3]),
                    '__DIRECT_BLDG_PLAN': clean_and_extract_url(row.iloc[4]),
                    '__DIRECT_TAX_MAP': clean_and_extract_url(row.iloc[5]),
                    '__DIRECT_PHOTO_1': clean_and_extract_url(row.iloc[7]),
                    '__DIRECT_PHOTO_2': clean_and_extract_url(row.iloc[8]),
                    '__DIRECT_PHOTO_3': clean_and_extract_url(row.iloc[9]),
                    '__DIRECT_PHOTO_4': clean_and_extract_url(row.iloc[10]),
                    '__DIRECT_PHOTO_5': clean_and_extract_url(row.iloc[11]),
                })
        except IndexError:
            continue
            
    # 3. Fetch Export Template Base (Cached)
    template_bytes = None
    placeholders = []
    try:
        t_req = requests.get(TEMPLATE_URL, timeout=30)
        if t_req.status_code == 200:
            template_bytes = io.BytesIO(t_req.content)
            temp_wb = load_workbook(template_bytes)
            placeholders = get_placeholders(temp_wb.active)
            template_bytes.seek(0)
    except: pass
    
    return df, media_data_list, template_bytes, placeholders

# Lock all live data strictly into session memory
if "master_data_loaded" not in st.session_state:
    with st.spinner("Loading Data..."):
        df, media_list, t_bytes, p_holders = fetch_live_data()
        st.session_state.master_df = df
        st.session_state.media_data_list = media_list
        st.session_state.template_bytes = t_bytes
        st.session_state.placeholders = p_holders
        st.session_state.master_data_loaded = True

df = st.session_state.master_df
media_data_list = st.session_state.media_data_list
template_bytes_raw = st.session_state.template_bytes.getvalue() if st.session_state.template_bytes else None
placeholders = st.session_state.placeholders

if df is None or df.empty or template_bytes_raw is None:
    st.error("Failed to load source data. Please verify the spreadsheet links.")
    st.stop()

# --- 3. DISPLAY REPORT (ZERO LATENCY UI) ---
trade_areas = sorted(df["TRADE AREA"].dropna().unique().tolist())
first_row = df.iloc[0] if not df.empty else None
first_trade_area = first_row["TRADE AREA"] if first_row is not None else ""
first_site_display = first_row["SITE_DISPLAY"] if first_row is not None else ""
default_ta_index = trade_areas.index(first_trade_area) if first_trade_area in trade_areas else 0

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
            label="Export Trade Area",
            data=generate_trade_area_report(selected_ta, df, template_bytes_raw, placeholders),
            file_name=f"{selected_ta}_Site_Information_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

#--- MULTI-TAB REPORT & MEDIA VIEWER FRAME ---
if selected_ta and selected_site_display:
    site_data = df[df["SITE_DISPLAY"] == selected_site_display]
    site_row_data = site_data.iloc[0] if not site_data.empty else None

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
                    .image-grid-3x3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; padding: 10px 0; max-width: 100%; }
                    .image-grid-item { border: 1px solid #dadce0; border-radius: 8px; overflow: hidden; background: #f8f9fa; transition: transform 0.2s; aspect-ratio: 4/3; display: flex; flex-direction: column; }
                    .image-grid-item:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
                    .image-grid-item img { width: 100%; height: 100%; object-fit: cover; display: block; flex: 1; }
                    .image-grid-item .label { padding: 6px 8px; font-size: 0.7rem; font-weight: 600; color: #5f6368; background: white; text-align: center; border-top: 1px solid #dadce0; flex-shrink: 0; }
                    .image-grid-item a { text-decoration: none; color: inherit; display: flex; flex-direction: column; height: 100%; }
                    @media (max-width: 768px) { .image-grid-3x3 { grid-template-columns: repeat(2, 1fr); } }
                    @media (max-width: 480px) { .image-grid-3x3 { grid-template-columns: 1fr; } }
                </style>
                <div class="image-grid-3x3">
                '''
                for label, thumb_url, full_url in valid_photos:
                    grid_html += f'<div class="image-grid-item"><a href="{full_url}" target="_blank"><img src="{thumb_url}" alt="{label}" loading="lazy"><div class="label">{label}</div></a></div>'
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
                    .image-grid-3x3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; padding: 10px 0; max-width: 100%; }
                    .image-grid-item { border: 1px solid #dadce0; border-radius: 8px; overflow: hidden; background: #f8f9fa; transition: transform 0.2s; aspect-ratio: 4/3; display: flex; flex-direction: column; }
                    .image-grid-item:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
                    .image-grid-item img { width: 100%; height: 100%; object-fit: cover; display: block; flex: 1; }
                    .image-grid-item .label { padding: 6px 8px; font-size: 0.7rem; font-weight: 600; color: #5f6368; background: white; text-align: center; border-top: 1px solid #dadce0; flex-shrink: 0; }
                    .image-grid-item a { text-decoration: none; color: inherit; display: flex; flex-direction: column; height: 100%; }
                    @media (max-width: 768px) { .image-grid-3x3 { grid-template-columns: repeat(2, 1fr); } }
                    @media (max-width: 480px) { .image-grid-3x3 { grid-template-columns: 1fr; } }
                </style>
                <div class="image-grid-3x3">
                '''
                for label, thumb_url, full_url in valid_docs:
                    grid_html += f'<div class="image-grid-item"><a href="{full_url}" target="_blank"><img src="{thumb_url}" alt="{label}" loading="lazy"><div class="label">{label}</div></a></div>'
                grid_html += '</div>'
                components.html(grid_html, height=1200, scrolling=False)
            else:
                st.info("No layout documents configured for this property record selection.")
        else:
             st.info("No data available for the selected site.")
