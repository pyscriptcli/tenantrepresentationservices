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

#--- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="trs.sitesourcing.viewer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#--- GLOBAL STYLESHEET ENFORCER ---
st.markdown("""
<style >
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');
* { font-family: 'Google Sans', 'Roboto', 'Segoe UI', sans-serif !important; }
div[data-testid="stTextInput"] label, div[data-testid="stTextInput"] button { display: none !important; }
html, body { overflow: hidden !important; height: 100% !important; margin: 0px !important; padding: 0px !important; background-color: #ffffff !important; }
header[data-testid="stHeader"], [data-testid="stHeader"], .stApp > header, div[data-testid="stDecoration"] { display: none !important; height: 0px !important; min-height: 0px !important; padding: 0px !important; margin: 0px !important; opacity: 0 !important; }
.stApp, .appview-container, .main, [data-testid="stAppViewContainer"], [data-testid="stMain"], .block-container, [data-testid="stMainBlockContainer"] { padding: 0px !important; margin: 0px !important; overflow: visible !important; height: 100vh !important; max-height: 100vh !important; }
div[data-testid="stVerticalBlock"] > div:has(style), div[data-testid="stVerticalBlock"] > div:empty { display: none !important; height: 0px !important; margin: 0px !important; padding: 0px !important; }
iframe[title="streamlit_components.components.html"] { border: none !important; width: 100% !important; }
._profilePreview_gzau3_63, ._link_gzau3_10, [class*='_profilePreview'], [class*='_link_gzau3'], a[href*='share.streamlit.io'], a[href*='streamlit.io'], img[src*='avatar'], [class*='avatar'], #MainMenu, button[title="View source"], .stAppDeployButton, div[data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; opacity: 0 !important; height: 0 !important; width: 0 !important; pointer-events: none !important; }
</style>
""", unsafe_allow_html=True)

#--- SECURITY PROTOCOLS ---
def deploy_workspace_security_protocols():
    injected_js = """
    <script>
    (function() {
        const restrictedUrls = ["https://share.streamlit.io/user/pyscriptcli", "https://streamlit.io/cloud"];
        function checkAndBlockUrl(url) {
            if (!url) return false;
            const shouldBlock = restrictedUrls.some(blockedUrl => url.toLowerCase().trim().includes(blockedUrl.toLowerCase().trim()));
            if (shouldBlock) { window.stop(); if (window.top) window.top.location.href = window.location.origin; else window.location.href = window.location.origin; return true; }
            return false;
        }
        document.addEventListener('click', function(e) {
            const target = e.target.closest('a');
            if (target && target.href) { if (checkAndBlockUrl(target.href)) { e.preventDefault(); e.stopPropagation(); } }
        }, true);
        const originalAssign = window.location.assign;
        window.location.assign = function(url) { if (!checkAndBlockUrl(url)) { originalAssign.apply(this, arguments); } };
        const originalReplace = window.location.replace;
        window.location.replace = function(url) { if (!checkAndBlockUrl(url)) { originalReplace.apply(this, arguments); } };
        function purgeTargetElements() {
            const targetSelectors = ["._profilePreview_gzau3_63", "._link_gzau3_10", "[class*='_profilePreview']", "[class*='_link_gzau3']", "a[href*='share.streamlit.io']", "a[href*='streamlit.io']", "img[src*='avatar']", "[class*='avatar']"];
            targetSelectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => el.style.setProperty('display', 'none', 'important'));
                if (window.top && window.top.document) { try { window.top.document.querySelectorAll(selector).forEach(el => el.style.setProperty('display', 'none', 'important')); } catch(err) {} }
            });
        }
        purgeTargetElements();
        const layoutObserver = new MutationObserver(function() { purgeTargetElements(); });
        if (document.body) layoutObserver.observe(document.body, { childList: true, subtree: true });
        if (window.top && window.top.document && window.top.document.body) { try { layoutObserver.observe(window.top.document.body, { childList: true, subtree: true }); } catch(e) {} }
        setInterval(function() { purgeTargetElements(); try { checkAndBlockUrl(window.location.href); if (window.top && window.top !== window) { checkAndBlockUrl(window.top.location.href); } } catch(e) {} }, 1000);
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

#--- LOGIN VERIFICATION LOGIC ---
TARGET_HASH = "6e7dfba0b39da481db37c3263c61cac6"
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest() == TARGET_HASH

#--- CONFIGURATION ---
SOURCE_URL = "https://docs.google.com/spreadsheets/d/14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE/export?format=xlsx"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/1uS3xmnPi0o4c_EayQtURYDSMMPRDRGSb/export?format=xlsx"
MY_MAPS_KML_URL = "https://www.google.com/maps/d/kml?mid=1CSUoDxCi-trQTTz_D6NjI3m0Kc5OQhM"

#--- HELPER FUNCTIONS ---
def download_file(url):
    try:
        headers = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
        response = requests.get(url, headers=headers, timeout=30)
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

#--- COMPLETE HTML BLUEPRINT FOR REPORT MODAL ---
HTML_FRAMEWORK = """
<!DOCTYPE html>
<html>
<head>
<style type="text/css">
html, body { margin: 0; padding: 0; background-color: transparent; font-family: Arial, sans-serif; height: 100%; overflow: auto; }
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
    return df, placeholders, template_bytes_raw, media_data_list

# --- MAIN LOGIC BEGINS ---

# --- Step 1: Display Login Function ---
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

# At this point, user is authenticated

# --- Step 2: Initialize Data ---
if 'data_loaded' not in st.session_state:
    with st.spinner("Fetching latest data from source..."):
        df, placeholders, template_bytes_raw, media_data_list = load_data()
        if df is None or template_bytes_raw is None:
            st.error("Failed to load data assets. Please verify link paths.")
            st.stop()
        st.session_state.df = df
        st.session_state.placeholders = placeholders
        st.session_state.template_bytes_raw = template_bytes_raw
        st.session_state.media_data_list = media_data_list
        st.session_state.data_loaded = True

df = st.session_state.df
placeholders = st.session_state.placeholders
template_bytes_raw = st.session_state.template_bytes_raw
media_data_list = st.session_state.media_data_list

trade_areas = sorted(df["TRADE AREA"].dropna().unique().tolist())

# --- Step 3: Map-Centric UI Architecture ---
deploy_workspace_security_protocols()

# Initialize session state for map interaction
if 'selected_site_name' not in st.session_state:
    st.session_state.selected_site_name = ""
if 'selected_ta' not in st.session_state:
    st.session_state.selected_ta = trade_areas[0] if trade_areas else ""

# Create the main map container
map_container = st.container()

with map_container:
    # FIX: Use correct column names with spaces ("SITE NAME", "TRADE AREA")
    sites_json = df[["SITE NAME", "TRADE AREA", "SITE_DISPLAY"]].to_json(orient='records')
    
    # Custom HTML/JS for Map + Dropdown Bridge + Floating Modal
    map_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>TRS Map Viewer</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; font-family: 'Google Sans', sans-serif; }}
            #map {{ width: 100vw; height: 100vh; z-index: 1; }}
            
            /* REPLACED SEARCH BAR WITH DROPDOWNS */
            .custom-controls {{
                position: absolute;
                top: 10px;
                left: 50px; /* Offset to avoid zoom controls */
                z-index: 1000;
                background: white;
                padding: 8px 12px;
                border-radius: 4px;
                box-shadow: 0 1px 5px rgba(0,0,0,0.4);
                display: flex;
                gap: 10px;
                align-items: center;
            }}
            .custom-controls select {{
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 13px;
                min-width: 150px;
            }}
            
            /* FLOATING REPORT MODAL */
            .report-modal {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 80%;
                max-width: 900px;
                height: 80%;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                z-index: 2000;
                display: none;
                flex-direction: column;
                overflow: hidden;
            }}
            .modal-header {{
                padding: 15px 20px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: #f8f9fa;
            }}
            .modal-title {{ font-size: 16px; font-weight: 600; color: #333; }}
            .close-btn {{ cursor: pointer; font-size: 20px; color: #666; border: none; background: none; }}
            .modal-tabs {{ display: flex; border-bottom: 1px solid #eee; background: white; }}
            .tab-btn {{
                padding: 10px 20px;
                cursor: pointer;
                border: none;
                background: none;
                font-size: 13px;
                font-weight: 500;
                color: #666;
                border-bottom: 2px solid transparent;
            }}
            .tab-btn.active {{ color: #d32f2f; border-bottom-color: #d32f2f; }}
            .modal-content {{ flex: 1; overflow: auto; padding: 0; position: relative; }}
            .tab-pane {{ display: none; width: 100%; height: 100%; }}
            .tab-pane.active {{ display: block; }}
            
            /* PHOTO GRID INSIDE MODAL */
            .photo-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; padding: 20px; }}
            .photo-item {{ aspect-ratio: 4/3; background: #f0f0f0; border-radius: 8px; overflow: hidden; }}
            .photo-item img {{ width: 100%; height: 100%; object-fit: cover; }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        
        <!-- CUSTOM DROPDOWN CONTROLS -->
        <div class="custom-controls">
            <select id="ta-select">
                <option value="">Select Trade Area...</option>
                {"".join([f'<option value="{ta}">{ta}</option>' for ta in trade_areas])}
            </select>
            <select id="site-select">
                <option value="">Select Site...</option>
            </select>
        </div>
        
        <!-- FLOATING REPORT MODAL -->
        <div class="report-modal" id="reportModal">
            <div class="modal-header">
                <div class="modal-title">SITE INFORMATION REPORT | PHOTOS | DOCS</div>
                <button class="close-btn" onclick="closeModal()">✕</button>
            </div>
            <div class="modal-tabs">
                <button class="tab-btn active" onclick="switchTab('report')">PROPERTY INFORMATION</button>
                <button class="tab-btn" onclick="switchTab('photos')">PROPERTY PHOTOS</button>
                <button class="tab-btn" onclick="switchTab('docs')">PROPERTY DOCS</button>
            </div>
            <div class="modal-content">
                <div id="tab-report" class="tab-pane active"></div>
                <div id="tab-photos" class="tab-pane"></div>
                <div id="tab-docs" class="tab-pane"></div>
            </div>
        </div>

        <script>
            // Initialize Map
            var map = L.map('map').setView([14.6091, 121.0223], 12); 
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {{
                attribution: '&copy; OpenStreetMap contributors'
            }}).addTo(map);

            // Load Google My Maps KML
            var kmlUrl = "{MY_MAPS_KML_URL}";
            fetch(kmlUrl)
                .then(response => response.text())
                .then(kmlText => {{
                    var parser = new DOMParser();
                    var kml = parser.parseFromString(kmlText, "application/xml");
                    var placemarks = kml.getElementsByTagName("Placemark");
                    
                    for (var i = 0; i < placemarks.length; i++) {{
                        var pm = placemarks[i];
                        var name = pm.getElementsByTagName("name")[0]?.textContent || "";
                        
                        // Try to find polygon coordinates
                        var coords = [];
                        var poly = pm.getElementsByTagName("Polygon")[0];
                        if (poly) {{
                            var outerBoundary = poly.getElementsByTagName("outerBoundaryIs")[0];
                            if (outerBoundary) {{
                                var linearRing = outerBoundary.getElementsByTagName("LinearRing")[0];
                                if (linearRing) {{
                                    var coordStr = linearRing.getElementsByTagName("coordinates")[0]?.textContent || "";
                                    coords = coordStr.trim().split("\\\\s+").map(c => {{
                                        var parts = c.split(",");
                                        return [parseFloat(parts[1]), parseFloat(parts[0])]; // Leaflet uses [lat, lng]
                                    }});
                                }}
                            }}
                        }}
                        
                        if (coords.length > 0) {{
                            var polygon = L.polygon(coords, {{
                                color: '#3388ff',
                                weight: 2,
                                fillColor: '#3388ff',
                                fillOpacity: 0.3
                            }}).addTo(map);
                            
                            // Store site name in polygon options
                            polygon.siteName = name;
                            
                            // Click handler
                            polygon.on('click', function(e) {{
                                var siteName = this.siteName;
                                if (siteName) {{
                                    // Send to Streamlit
                                    window.parent.postMessage({{type: 'site_selected', siteName: siteName}}, '*');
                                    
                                    // Update dropdowns
                                    updateDropdowns(siteName);
                                    
                                    // Show modal
                                    showModal(siteName);
                                }}
                            }});
                        }}
                    }}
                }})
                .catch(err => console.error("KML Load Error:", err));

            // Dropdown Logic
            var sitesData = {sites_json};
            var taSelect = document.getElementById('ta-select');
            var siteSelect = document.getElementById('site-select');
            
            taSelect.addEventListener('change', function() {{
                var selectedTA = this.value;
                siteSelect.innerHTML = '<option value="">Select Site...</option>';
                
                if (selectedTA) {{
                    // FIX: Use bracket notation for keys with spaces
                    var filteredSites = sitesData.filter(s => s["TRADE AREA"] === selectedTA);
                    filteredSites.sort((a,b) => parseInt(a.SITE_DISPLAY) - parseInt(b.SITE_DISPLAY));
                    
                    filteredSites.forEach(site => {{
                        var opt = document.createElement('option');
                        opt.value = site["SITE NAME"];
                        opt.textContent = site.SITE_DISPLAY;
                        siteSelect.appendChild(opt);
                    }});
                }}
                
                // Notify Streamlit
                window.parent.postMessage({{type: 'ta_selected', ta: selectedTA}}, '*');
            }});
            
            siteSelect.addEventListener('change', function() {{
                var selectedSite = this.value;
                if (selectedSite) {{
                    window.parent.postMessage({{type: 'site_selected', siteName: selectedSite}}, '*');
                    showModal(selectedSite);
                }}
            }});
            
            function updateDropdowns(siteName) {{
                // Find TA for this site
                // FIX: Use bracket notation for keys with spaces
                var siteObj = sitesData.find(s => s["SITE NAME"] === siteName);
                if (siteObj) {{
                    taSelect.value = siteObj["TRADE AREA"];
                    // Trigger change to populate sites
                    taSelect.dispatchEvent(new Event('change'));
                    // Wait a tick then set site
                    setTimeout(() => {{ siteSelect.value = siteName; }}, 50);
                }}
            }}
            
            // Modal Functions
            function showModal(siteName) {{
                document.getElementById('reportModal').style.display = 'flex';
                // Request report content from Streamlit
                window.parent.postMessage({{type: 'request_report', siteName: siteName}}, '*');
            }}
            
            function closeModal() {{
                document.getElementById('reportModal').style.display = 'none';
                window.parent.postMessage({{type: 'close_modal'}}, '*');
            }}
            
            function switchTab(tabName) {{
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                
                event.target.classList.add('active');
                document.getElementById('tab-' + tabName).classList.add('active');
            }}
            
            // Listen for messages from Streamlit (e.g., to populate modal)
            window.addEventListener('message', function(e) {{
                if (e.data.type === 'update_report_html') {{
                    document.getElementById('tab-report').innerHTML = e.data.html;
                }}
                if (e.data.type === 'update_photos_html') {{
                    document.getElementById('tab-photos').innerHTML = e.data.html;
                }}
                if (e.data.type === 'update_docs_html') {{
                    document.getElementById('tab-docs').innerHTML = e.data.html;
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    # Render the map
    components.html(map_html, height=1000, scrolling=False)

# --- Step 4: Handle Map Interactions via Session State ---
if st.session_state.selected_ta:
    col1, col2 = st.columns([3, 1])
    with col2:
        st.download_button(
            label="Export Trade Area",
            data=generate_trade_area_report(st.session_state.selected_ta, df, template_bytes_raw, placeholders),
            file_name=f"{st.session_state.selected_ta}_Site_Information_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
