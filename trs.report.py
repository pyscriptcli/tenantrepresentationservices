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
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
import pyarrow as pa
import pyarrow.parquet as pq
import json
import traceback

#--- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="trs.sitesourcing.viewer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#--- FULL SCREEN LOADING OVERLAY ---
def get_loading_overlay_html(message="Loading data..."):
    return f"""
    <div id="loading-overlay" style="
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(255, 255, 255, 0.98);
        z-index: 999999; 
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        font-family: 'Google Sans', 'Roboto', 'Segoe UI', sans-serif;
    ">
        <div style="
            width: 45px; height: 45px;
            border: 4px solid #f0f2f6;
            border-top: 4px solid #003366;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        "></div>
        <div style="font-size: 1.1rem; color: #202124; font-weight: 500; letter-spacing: 0.5px;">
            {message}
        </div>
    </div>
    <style>
        @keyframes spin {{ 
            0% {{ transform: rotate(0deg); }} 
            100% {{ transform: rotate(360deg); }} 
        }}
    </style>
    """

#--- GLOBAL STYLES ---
st.markdown("""
<style >
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');
* { font-family: 'Google Sans', 'Roboto', 'Segoe UI', sans-serif !important; }
div[data-testid="stTextInput"] label { display: none !important; }
div[data-testid="stTextInput"] button { display: none !important; }
html, body { overflow-y: auto !important; overflow-x: hidden !important; height: 100% !important; margin: 0px !important; padding: 0px !important; background-color: #ffffff !important; }
header[data-testid="stHeader"], [data-testid="stHeader"], .stApp > header, div[data-testid="stDecoration"] { display: none !important; height: 0px !important; min-height: 0px !important; padding: 0px !important; margin: 0px !important; opacity: 0 !important; }
.stApp, .appview-container, .main, [data-testid="stAppViewContainer"], [data-testid="stMain"], .block-container, [data-testid="stMainBlockContainer"] { padding-top: 0.2rem !important; margin-top: 0px !important; padding-bottom: 0px !important; padding-left: 0.4rem !important; padding-right: 0.4rem !important; overflow: visible !important; height: auto !important; max-height: none !important; min-height: calc(100vh + 100px) !important; }
div[data-testid="stVerticalBlock"] > div:has(style), div[data-testid="stVerticalBlock"] > div:empty { display: none !important; height: 0px !important; margin: 0px !important; padding: 0px !important; }
iframe[title="streamlit_components.components.html"] { height: 1200px !important; max-height: none !important; border: none !important; margin-bottom: 10px !important; width: 100% !important; overflow: hidden !important; }
button[data-baseweb="tab"] { padding-top: 0.1rem !important; padding-bottom: 0.1rem !important; font-size: 0.85rem !important; }
div[data-testid="stTabs"] { margin-top: -5px !important; }
div[data-testid="stHorizontalBlock"] { gap: 0.5rem !important; align-items: flex-end !important; background: #ffffff; padding: 0.4rem 0.5rem !important; border-radius: 8px; margin-top: 0px !important; margin-bottom: 10px !important; }
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) { align-self: flex-end !important; padding-bottom: 4px !important; }
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) div[data-testid="stElementWrapper"] { margin-bottom: 0px !important; padding-bottom: 0px !important; }
.stSelectbox > div > div { background-color: #fff !important; border: 1px solid #747775 !important; border-radius: 4px !important; min-height: 28px !important; height: 28px !important; }
.stSelectbox > div > div > div { padding-top: 0px !important; padding-bottom: 0px !important; font-size: 0.8rem !important; line-height: 26px !important; }
.stButton > button, .stDownloadButton > button { background-color: #003366 !important; color: #ffffff !important; border: none !important; border-radius: 100px !important; padding: 0.1rem 0.5rem !important; font-size: 0.7rem !important; font-weight: 500 !important; min-height: 28px !important; height: 28px !important; width: 100% !important; box-shadow: 0 1px 2px 0 rgba(60,64,67,0.2) !important; line-height: 1 !important; }
.stButton > button:hover, .stDownloadButton > button:hover { background-color: #0b4cb4 !important; }
._profilePreview_gzau3_63, ._link_gzau3_10, [class*='_profilePreview'], [class*='_link_gzau3'], a[href*='share.streamlit.io'], a[href*='streamlit.io'], img[src*='avatar'], [class*='avatar'], #MainMenu, button[title="View source"], .stAppDeployButton, div[data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; opacity: 0 !important; height: 0 !important; width: 0 !important; pointer-events: none !important; }
</style>
""", unsafe_allow_html=True)

#--- SECURITY OBSERVERS ---
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

#--- LIGHT MODE LOCK ---
_config_dir = ".streamlit"
_config_file = os.path.join(_config_dir, "config.toml")
if not os.path.exists(_config_file):
    os.makedirs(_config_dir, exist_ok=True)
    with open(_config_file, "w", encoding="utf-8") as f:
        f.write('[theme]\nbase="light"\n')

#--- LOCAL JSON STORE CLASS (WITH DEFAULT USERS) ---
class LocalUserStore:
    def __init__(self, json_path):
        self.json_path = json_path
        self.backup_data = None  # Cache fallback if file can't be accessed

    def _get_default_data(self):
        """Return the default user data (used when file is missing or unreadable)."""
        return {
            "users": {
                "regis": {
                    "password": "trs.jfc",
                    "permissions": {"view_sir": True, "export_sir": True},
                    "is_admin": False
                },
                "trs.aims": {
                    "password": "trs.jfc",
                    "permissions": {"view_sir": True, "export_sir": True},
                    "is_admin": False
                },
                "jfc": {
                    "password": "trs.prime",
                    "permissions": {"view_sir": True, "export_sir": False},
                    "is_admin": False
                },
                "admin": {
                    "password": "@47t00M!!",
                    "permissions": {"view_sir": True, "export_sir": True},
                    "is_admin": True
                }
            },
            "audit": [],
            "refresh_logs": []
        }

    def _read(self):
        """Read from local JSON file, fallback to default data if file not accessible."""
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.backup_data = data
                return data
            else:
                # File doesn't exist: create with default data
                default_data = self._get_default_data()
                self._write(default_data)  # This will create the file
                return default_data
        except Exception as e:
            st.warning(f"Cannot access local JSON file: {e}. Using default/cached data.")
            if self.backup_data is not None:
                return self.backup_data
            # No cache, return default
            return self._get_default_data()

    def _write(self, data):
        """Write to local JSON file, with cache backup."""
        try:
            dirname = os.path.dirname(self.json_path)
            if dirname and not os.path.exists(dirname):
                os.makedirs(dirname, exist_ok=True)
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.backup_data = data
            return True
        except Exception as e:
            st.error(f"Cannot write to local JSON file: {e}")
            self.backup_data = data  # Keep in cache
            return False

    def load_users(self):
        data = self._read()
        return data.get("users", {})

    def save_users(self, users):
        data = self._read()
        data["users"] = users
        return self._write(data)

    def log_audit(self, username):
        data = self._read()
        if "audit" not in data:
            data["audit"] = []
        data["audit"].append({"user": username, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        return self._write(data)

    def log_refresh(self):
        data = self._read()
        if "refresh_logs" not in data:
            data["refresh_logs"] = []
        data["refresh_logs"].append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return self._write(data)

    def get_refresh_log(self):
        data = self._read()
        return data.get("refresh_logs", [])

    def get_audit_log(self):
        data = self._read()
        return data.get("audit", [])

    def get_file_content(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            return "Unable to read file."

    def get_file_path(self):
        return os.path.abspath(self.json_path)

#--- INITIALIZE USER STORE WITH LOCAL PATH ---
ADMINLOG_PATH = r"C:\Users\PRIME_Dave\Desktop\adminlog.json"

if 'user_store' not in st.session_state:
    st.session_state.user_store = LocalUserStore(ADMINLOG_PATH)

if 'users' not in st.session_state:
    st.session_state.users = st.session_state.user_store.load_users()
if 'refresh_log' not in st.session_state:
    st.session_state.refresh_log = st.session_state.user_store.get_refresh_log()
if 'write_errors' not in st.session_state:
    st.session_state.write_errors = []

#--- SESSION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = "member"
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'placeholders' not in st.session_state:
    st.session_state.placeholders = None
if 'template_bytes_raw' not in st.session_state:
    st.session_state.template_bytes_raw = None
if 'media_data_list' not in st.session_state:
    st.session_state.media_data_list = None
if 'cache_version' not in st.session_state:
    st.session_state.cache_version = 0

#--- LOGIN FUNCTION ---
def authenticate(username, password):
    users = st.session_state.users
    if username in users and users[username]["password"] == password:
        st.session_state.authenticated = True
        st.session_state.username = username
        if users[username].get("is_admin", False):
            st.session_state.role = "admin"
        else:
            st.session_state.role = "member"
        success = st.session_state.user_store.log_audit(username)
        if not success:
            st.warning("Audit log could not be written. Please check file permissions.")
        return True
    return False

#--- CONFIGURATION ---
SOURCE_URL = "https://docs.google.com/spreadsheets/d/14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE/export?format=xlsx"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/1uS3xmnPi0o4c_EayQtURYDSMMPRDRGSb/export?format=xlsx"

#--- HELPER FUNCTIONS ---
def download_file(url):
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return io.BytesIO(response.content)
        return None
    except:
        return None

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

def extract_google_drive_id(clean_url):
    if not clean_url:
        return None
    match = re.search(r'(?:id=|/d/|/uc?.*?id=)([a-zA-Z0-9_-]{25,})', clean_url)
    return match.group(1) if match else None

def get_placeholders_optimized(template_bytes):
    try:
        wb = load_workbook(io.BytesIO(template_bytes), data_only=False)
        sheet = wb.active
        placeholders = set()
        for row in sheet.iter_rows(values_only=True):
            for val in row:
                if isinstance(val, str):
                    matches = re.findall(r"{{(.*?)}}", val)
                    for match in matches:
                        name = match.split(":")[0].strip() if ":" in match else match.strip()
                        placeholders.add(name)
        wb.close()
        return sorted(list(placeholders))
    except Exception as e:
        st.error(f"Error extracting placeholders: {e}")
        return []

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

def load_main_data_optimized(source_bytes):
    try:
        wb = load_workbook(io.BytesIO(source_bytes), data_only=False)
        ws = wb.active
        header_row = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        headers = [str(h).strip().upper() if h else "" for h in header_row]
        parsed_data_list = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            row_dict = {}
            has_val = False
            for idx, val in enumerate(row):
                if idx < len(headers) and headers[idx]:
                    cleaned_val = clean_and_extract_url(val)
                    row_dict[headers[idx]] = cleaned_val
                    if cleaned_val != "":
                        has_val = True
            if has_val:
                parsed_data_list.append(row_dict)
        wb.close()
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
        return df
    except Exception as e:
        st.error(f"Error loading main data: {e}")
        return None

def load_media_data_optimized(source_bytes):
    try:
        wb = load_workbook(io.BytesIO(source_bytes), data_only=False)
        media_data_list = []
        media_ws = None
        for sheet_name in wb.sheetnames:
            if "PHOTO" in sheet_name.upper() or "DOC" in sheet_name.upper() or "MEDIA" in sheet_name.upper():
                media_ws = wb[sheet_name]
                break
        if not media_ws:
            media_ws = wb.active
        for row in media_ws.iter_rows(values_only=True):
            t_area = str(row[13] if len(row) > 13 and row[13] is not None else "").strip()
            s_name = str(row[15] if len(row) > 15 and row[15] is not None else "").strip()
            if t_area and s_name and t_area.upper() != "TRADE AREA":
                media_data_list.append({
                    'TRADE AREA': t_area,
                    'SITE NAME': s_name,
                    '__DIRECT_TCT': clean_and_extract_url(row[2] if len(row) > 2 else ""),
                    '__DIRECT_LOT_PLAN': clean_and_extract_url(row[3] if len(row) > 3 else ""),
                    '__DIRECT_BLDG_PLAN': clean_and_extract_url(row[4] if len(row) > 4 else ""),
                    '__DIRECT_TAX_MAP': clean_and_extract_url(row[5] if len(row) > 5 else ""),
                    '__DIRECT_PHOTO_1': clean_and_extract_url(row[7] if len(row) > 7 else ""),
                    '__DIRECT_PHOTO_2': clean_and_extract_url(row[8] if len(row) > 8 else ""),
                    '__DIRECT_PHOTO_3': clean_and_extract_url(row[9] if len(row) > 9 else ""),
                    '__DIRECT_PHOTO_4': clean_and_extract_url(row[10] if len(row) > 10 else ""),
                    '__DIRECT_PHOTO_5': clean_and_extract_url(row[11] if len(row) > 11 else ""),
                })
        wb.close()
        return media_data_list
    except Exception as e:
        st.error(f"Error loading media data: {e}")
        return []

def load_data_parallel():
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_source = executor.submit(download_file, SOURCE_URL)
        future_template = executor.submit(download_file, TEMPLATE_URL)
        source_bytes = future_source.result()
        template_bytes = future_template.result()
    if source_bytes is None or template_bytes is None:
        return None, None, None, [], None
    source_data = source_bytes.getvalue()
    template_data = template_bytes.getvalue()
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_main = executor.submit(load_main_data_optimized, source_data)
        future_media = executor.submit(load_media_data_optimized, source_data)
        df = future_main.result()
        media_data_list = future_media.result()
    if df is None:
        return None, None, None, [], None
    placeholders = get_placeholders_optimized(template_data)
    elapsed = time.time() - start_time
    print(f"Data loaded in {elapsed:.2f} seconds")
    return df, placeholders, template_data, media_data_list, datetime.now()

@st.cache_data(ttl=None, show_spinner=False)
def get_cached_data(cache_version):
    return load_data_parallel()

@st.cache_data(ttl=None, show_spinner=False)
def generate_trade_area_report_cached(trade_area, df, template_bytes_raw, placeholders_tuple, cache_version):
    placeholders = list(placeholders_tuple)
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
                            if pd.isna(raw_data_val) or raw_data_val is None:
                                raw_data_val = ""
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

#--- HTML FRAMEWORK (unchanged) ---
HTML_FRAMEWORK = """
<!DOCTYPE html>
<html>
<head>
<style type="text/css">
html, body { margin: 0; padding: 0; background-color: #ffffff; font-family: Arial, sans-serif; height: 100%; overflow-y: auto !important; overflow-x: hidden !important; }
.report-wrapper { width: 100%; overflow-y: visible !important; overflow-x: hidden !important; display: flex; justify-content: center; align-items: flex-start; padding: 0; margin: 0; min-height: 100%; }
.report-scaler { transform-origin: center top; width: 100%; display: inline-block; overflow: visible; text-align: center; }
.ritz.grid-container { height: auto; overflow: visible !important; padding: 10px; box-sizing: border-box; width: 100%; display: inline-block; text-align: left; }
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
    const observer = new MutationObserver(function() { setTimeout(scaleReportToFit, 100); });
    const tableBody = document.querySelector('.waffle tbody');
    if (tableBody) { observer.observe(tableBody, { childList: true, subtree: true, characterData: true }); }
    window.addEventListener('load', function() { setTimeout(scaleReportToFit, 200); });
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

#--- MAIN APP ---

# --- LOGIN ---
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<h3 style='text-align: center; margin-top:50px;'>TRS Site Information Report</h3>", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter username", key="login_username")
        password = st.text_input("Password", placeholder="Enter password", type="password", key="login_password")
        if st.button("Login", use_container_width=True):
            if username and password:
                if authenticate(username, password):
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.warning("Please enter both username and password.")
    st.stop()

# --- DATA LOADING ---
if not st.session_state.data_loaded:
    loading_placeholder = st.empty()
    loading_placeholder.markdown(get_loading_overlay_html(
        message="Fetching Site Information..."
    ), unsafe_allow_html=True)

    result = get_cached_data(st.session_state.cache_version)
    if result and result[0] is not None:
        df, placeholders, template_bytes_raw, media_data_list, data_timestamp = result
        st.session_state.df = df
        st.session_state.placeholders = placeholders
        st.session_state.template_bytes_raw = template_bytes_raw
        st.session_state.media_data_list = media_data_list
        st.session_state.data_timestamp = data_timestamp
        st.session_state.data_loaded = True
        loading_placeholder.empty()
        st.rerun()
    else:
        loading_placeholder.empty()
        st.error("Failed to load data assets. Please verify link paths.")
        st.stop()

# --- MAIN UI ---
df = st.session_state.df
placeholders = st.session_state.placeholders
template_bytes_raw = st.session_state.template_bytes_raw
media_data_list = st.session_state.media_data_list

deploy_workspace_security_protocols()

# --- SIDEBAR ---
if st.session_state.role == "admin":
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Admin Panel", "Viewer"], index=0)
else:
    page = "Viewer"

# --- ADMIN PANEL ---
if st.session_state.role == "admin" and page == "Admin Panel":
    st.title("Admin Control Panel")

    # --- Debug info (collapsible) ---
    with st.expander("Debug: JSON File Location & Content", expanded=False):
        store = st.session_state.user_store
        st.write(f"**Absolute path:** `{store.get_file_path()}`")
        st.write(f"**File exists:** {os.path.exists(store.json_path)}")
        if os.path.exists(store.json_path):
            st.write(f"**File size:** {os.path.getsize(store.json_path)} bytes")
            st.write("**Raw content (first 500 chars):**")
            st.code(store.get_file_content()[:500], language="json")
        st.write("**Using cached data:**", store.backup_data is not None and not os.path.exists(store.json_path))

    # --- Save to Local File Button ---
    st.subheader("Sync to Local File")
    col_sync, col_status = st.columns([1, 3])
    with col_sync:
        if st.button("Save to Local File", use_container_width=True):
            success = st.session_state.user_store.save_users(st.session_state.users)
            if success:
                st.success(f"Successfully saved to {st.session_state.user_store.get_file_path()}")
            else:
                st.error("Failed to save to local file. Check permissions.")
    with col_status:
        st.write(f"Current file path: `{st.session_state.user_store.get_file_path()}`")

    st.divider()

    # --- Refresh Data ---
    st.subheader("Data Refresh")
    col_refresh, col_status = st.columns([1, 3])
    with col_refresh:
        if st.button("Refresh Data Now", use_container_width=True):
            st.cache_data.clear()
            st.session_state.cache_version += 1
            st.session_state.data_loaded = False
            success = st.session_state.user_store.log_refresh()
            if success:
                st.session_state.refresh_log = st.session_state.user_store.get_refresh_log()
                st.success("Refresh logged.")
            else:
                st.error("Could not log refresh. Check file permissions.")
            st.rerun()
    with col_status:
        if st.session_state.refresh_log:
            last = st.session_state.refresh_log[-1]
            st.write(f"Last refresh: {last}  |  Total: {len(st.session_state.refresh_log)}")
            if len(st.session_state.refresh_log) > 1:
                st.write("Previous: " + ", ".join(st.session_state.refresh_log[-5:]))
        else:
            st.write("No refresh performed yet.")

    st.divider()

    # --- User Management (compact) ---
    st.subheader("User Management")
    users = st.session_state.users
    usernames = list(users.keys())

    # Header
    cols = st.columns([1.5, 1.2, 0.8, 0.8, 1.5, 0.5])
    cols[0].write("**Username**")
    cols[1].write("**Password**")
    cols[2].write("**View SIR**")
    cols[3].write("**Export SIR**")
    cols[4].write("**Change Password**")
    cols[5].write("**Delete**")

    for uname in usernames:
        cols = st.columns([1.5, 1.2, 0.8, 0.8, 1.5, 0.5])
        cols[0].write(uname)
        cols[1].write(users[uname]["password"])
        view_sir = cols[2].checkbox("", value=users[uname]["permissions"]["view_sir"], key=f"view_{uname}", label_visibility="collapsed")
        export_sir = cols[3].checkbox("", value=users[uname]["permissions"]["export_sir"], key=f"export_{uname}", label_visibility="collapsed")
        users[uname]["permissions"]["view_sir"] = view_sir
        users[uname]["permissions"]["export_sir"] = export_sir

        # Only allow deleting non-admin users (you can customize this logic)
        if uname != "admin":  # prevent deleting the main admin
            new_pw = cols[4].text_input("", type="password", key=f"pw_{uname}", placeholder="New password", label_visibility="collapsed")
            if new_pw:
                users[uname]["password"] = new_pw
                st.success(f"Password for {uname} updated locally.")
            if cols[5].button("Delete", key=f"del_{uname}", use_container_width=True):
                del st.session_state.users[uname]
                success = st.session_state.user_store.save_users(users)
                if success:
                    st.success(f"User {uname} deleted.")
                else:
                    st.error("Failed to delete user. Check file permissions.")
                st.rerun()
        else:
            new_pw = cols[4].text_input("", type="password", key=f"pw_{uname}", placeholder="New password", label_visibility="collapsed")
            if new_pw:
                users[uname]["password"] = new_pw
                st.success(f"Password for {uname} updated locally.")
            cols[5].write("—")  # no delete button for admin

    # Add user
    st.write("---")
    st.write("**Add new user**")
    col_a, col_b, col_c, col_d, col_e = st.columns([1.5, 1.2, 0.8, 0.8, 1])
    with col_a:
        new_uname = st.text_input("Username", placeholder="New username", key="new_uname", label_visibility="collapsed")
    with col_b:
        new_pw = st.text_input("Password", type="password", placeholder="Password", key="new_pw", label_visibility="collapsed")
    with col_c:
        view_sir_new = st.checkbox("View", value=True, key="new_view", label_visibility="collapsed")
    with col_d:
        export_sir_new = st.checkbox("Export", value=True, key="new_export", label_visibility="collapsed")
    with col_e:
        if st.button("Add User", use_container_width=True):
            if new_uname and new_pw:
                if new_uname in st.session_state.users:
                    st.error("Username already exists.")
                else:
                    st.session_state.users[new_uname] = {
                        "password": new_pw,
                        "permissions": {"view_sir": view_sir_new, "export_sir": export_sir_new},
                        "is_admin": False
                    }
                    success = st.session_state.user_store.save_users(st.session_state.users)
                    if success:
                        st.success(f"User {new_uname} added.")
                    else:
                        st.error("Failed to save user. Check file permissions.")
                    st.rerun()
            else:
                st.warning("Fill in both fields.")

    # Force sync button
    if st.button("Force Sync to File", use_container_width=True):
        success = st.session_state.user_store.save_users(st.session_state.users)
        if success:
            st.success("Data synced to local file.")
        else:
            st.error("Sync failed.")

    st.divider()

    # --- Audit Log with counts and timestamps ---
    st.subheader("Audit Log")
    audits = st.session_state.user_store.get_audit_log()
    if audits:
        df_audit = pd.DataFrame(audits)
        summary = df_audit.groupby("user")["timestamp"].agg(["count", lambda x: list(x)]).reset_index()
        summary.columns = ["User", "Login Count", "Timestamps"]
        st.write("**Login summary per user**")
        st.dataframe(summary, use_container_width=True)
        st.write("**Detailed audit log (chronological)**")
        st.dataframe(df_audit.sort_values("timestamp", ascending=False), use_container_width=True, height=300)
    else:
        st.write("No audit records yet.")

# --- VIEWER (unchanged) ---
else:
    # Determine default selections
    trade_areas = sorted(df["TRADE AREA"].dropna().unique().tolist())
    first_row = df.iloc[0] if not df.empty else None
    first_trade_area = first_row["TRADE AREA"] if first_row is not None else ""
    first_site_display = first_row["SITE_DISPLAY"] if first_row is not None else ""
    default_ta_index = trade_areas.index(first_trade_area) if first_trade_area in trade_areas else 0

    col1, col2, col3 = st.columns([1.2, 1.2, 0.9])
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
            if st.session_state.users[st.session_state.username]["permissions"]["export_sir"]:
                report_bytes = generate_trade_area_report_cached(
                    selected_ta,
                    df,
                    template_bytes_raw,
                    tuple(placeholders),
                    st.session_state.cache_version
                )
                st.download_button(
                    label="Export",
                    data=report_bytes,
                    file_name=f"{selected_ta}_Site_Information_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="export_btn"
                )
            else:
                st.button("Export", disabled=True, help="You do not have permission to export.")

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

        if st.session_state.users[st.session_state.username]["permissions"]["view_sir"]:
            tab_report, tab_photos, tab_docs = st.tabs([
                "PROPERTY INFORMATION",
                "PROPERTY PHOTOS",
                "PROPERTY DOCS"
            ])

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
                        components.html(rendered_view, height=1600, scrolling=False)
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
        else:
            st.warning("You do not have permission to view site information reports.")
