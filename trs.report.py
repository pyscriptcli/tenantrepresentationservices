import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import re
import io
import requests
import hashlib
import streamlit.components.v1 as components

# --- IMMEDIATE SECURITY PROTOCOL (RUNS FIRST) ---
def deploy_workspace_security_protocols():
    """Deploys runtime JavaScript observers immediately to intercept asynchronously generated components."""
    components.html("""
    <script>
        (function() {
            // Block specific URLs
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
                    console.warn("Navigation blocked.");
                    window.stop();
                    (window.top || window).location.href = window.location.origin;
                    return true;
                }
                return false;
            }

            // Block clicks
            document.addEventListener('click', function(e) {
                const target = e.target.closest('a');
                if (target && target.href && checkAndBlockUrl(target.href)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }, true);

            // Override location methods
            ['assign', 'replace'].forEach(method => {
                const original = window.location[method];
                window.location[method] = function(url) {
                    if (!checkAndBlockUrl(url)) {
                        original.apply(this, arguments);
                    }
                };
            });

            // Remove branding elements
            function purgeTargetElements() {
                const selectors = [
                    "._profilePreview_gzau3_63",
                    "._link_gzau3_10",
                    "[class*='_profilePreview']",
                    "[class*='_link_gzau3']",
                    "a[href*='share.streamlit.io']",
                    "a[href*='streamlit.io']",
                    "img[src*='avatar']",
                    "[class*='avatar']"
                ];
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => 
                        el.style.setProperty('display', 'none', 'important')
                    );
                });
            }

            // Immediate execution
            purgeTargetElements();
            
            // Observer for dynamic content
            const observer = new MutationObserver(purgeTargetElements);
            observer.observe(document.body, { childList: true, subtree: true });

            // Periodic cleanup
            setInterval(function() {
                purgeTargetElements();
                checkAndBlockUrl(window.location.href);
            }, 200);
        })();
    </script>
    """, height=0, width=0)

# Deploy security FIRST before anything else
deploy_workspace_security_protocols()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="trs.sitesourcing.viewer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONSOLIDATED CSS (Minified) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');
    *{font-family:'Google Sans','Roboto',sans-serif!important}
    .block-container{padding:1rem 1.5rem!important;max-width:100%!important}
    ._profilePreview_gzau3_63,._link_gzau3_10,[class*='_profilePreview'],[class*='_link_gzau3'],a[href*='share.streamlit.io'],a[href*='streamlit.io'],img[src*='avatar'],[class*='avatar'],#MainMenu,footer,header,button[title="View source"],.stAppDeployButton,div[data-testid="stStatusWidget"]{display:none!important;visibility:hidden!important;opacity:0!important;height:0!important;width:0!important;pointer-events:none!important}
    .stButton>button,.stDownloadButton>button{background:#0b57d0!important;color:#fff!important;border:none!important;border-radius:100px!important;padding:.5rem 1.2rem!important;font-size:.85rem!important;font-weight:500!important;min-height:38px!important;height:38px!important;width:100%!important;box-shadow:0 1px 2px 0 rgba(60,64,67,.3),0 1px 3px 1px rgba(60,64,67,.15)!important;transition:background-color .2s,box-shadow .2s}
    .stButton>button:hover,.stDownloadButton>button:hover{background:#0b4cb4!important;box-shadow:0 1px 3px 0 rgba(60,64,67,.3),0 4px 8px 3px rgba(60,64,67,.15)!important}
    .stSelectbox label{font-size:.75rem!important;font-weight:500!important;color:#444746!important;margin-bottom:4px!important}
    .stSelectbox>div>div{background:#fff!important;border:1px solid #747775!important;border-radius:4px!important;min-height:38px!important;height:38px!important}
    .stSelectbox>div>div>div{padding-top:2px!important;font-size:.875rem!important}
    div[data-testid="stHorizontalBlock"]{gap:1rem!important;align-items:flex-end!important;background:#f0f4f9;padding:.75rem 1rem;border-radius:12px;margin-bottom:1rem}
    div[data-testid="stTextInput"] button{background:transparent!important;border:none!important;box-shadow:none!important;min-height:unset!important;height:auto!important;width:auto!important;padding:4px 8px!important;font-size:16px!important;color:#5f6368!important}
    div[data-testid="stTextInput"] button:hover{background:transparent!important;box-shadow:none!important}
    div[data-testid="stTextInput"] button span{display:none!important}
    div[data-testid="stTextInput"] button::before{content:"\\25C9";font-size:16px;color:#1f1f1f}
    .login-container{max-width:400px;margin:0 auto;padding:20px}
</style>
""", unsafe_allow_html=True)

# --- LOGIN VERIFICATION ---
TARGET_HASH = "6e7dfba0b39da481db37c3263c61cac6"
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest() == TARGET_HASH

if not st.session_state.authenticated:
    # Re-deploy security to ensure it's active on login page
    deploy_workspace_security_protocols()
    
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

# --- CONFIGURATION ---
SOURCE_URL = "https://docs.google.com/spreadsheets/d/14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE/export?format=xlsx"
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/1uS3xmnPi0o4c_EayQtURYDSMMPRDRGSb/export?format=xlsx"

# --- OPTIMIZED HELPER FUNCTIONS ---
@st.cache_data(ttl=3600)
def download_file(url):
    try:
        response = requests.get(url, timeout=30)
        return io.BytesIO(response.content) if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=3600)
def get_placeholders_from_template(template_bytes):
    """Extract placeholders from template - cached separately for speed"""
    wb = load_workbook(io.BytesIO(template_bytes))
    placeholders = set()
    for row in wb.active.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                matches = re.findall(r"\{\{(.*?)\}\}", cell.value)
                for match in matches:
                    name = match.split(":")[0].strip() if ":" in match else match.strip()
                    placeholders.add(name)
    return sorted(list(placeholders))

def sanitize_tab_name(name, existing_names):
    clean_name = re.sub(r'[\\/*?\[\]:]', '', str(name))[:31]
    if not clean_name: 
        clean_name = "Sheet"
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
def generate_trade_area_report(trade_area, df_hash=None):
    """Generate report with hash to invalidate cache when data changes"""
    global df, template_bytes_raw, placeholders
    
    ta_data = df[df["TRADE AREA"] == trade_area]
    wb = load_workbook(io.BytesIO(template_bytes_raw))
    
    original_sheets = wb.sheetnames
    base_sheet = wb.active
    base_sheet.title = "TEMPLATE_TO_DELETE"
    existing_tabs = set()
    
    # Pre-compile regex patterns for speed
    placeholder_patterns = {}
    for ph in placeholders:
        placeholder_patterns[ph] = re.compile(r"\{\{\s*" + re.escape(ph) + r"(\s*:.*?)?\}\}")
    
    for _, r_row in ta_data.iterrows():
        s_name = r_row.get("SITE NAME", "Unknown")
        safe_tab_name = sanitize_tab_name(s_name, existing_tabs)
        new_sheet = wb.copy_worksheet(base_sheet)
        new_sheet.title = safe_tab_name
        
        # Process cells in bulk for speed
        for row_cells in new_sheet.iter_rows():
            for cell in row_cells:
                if isinstance(cell.value, str) and "{{" in cell.value:
                    new_val = cell.value
                    for ph, pattern in placeholder_patterns.items():
                        if pattern.search(new_val):
                            raw_data_val = r_row.get(ph.upper(), "")
                            if pd.isna(raw_data_val) or raw_data_val is None:
                                raw_data_val = ""
                            if isinstance(raw_data_val, float) and raw_data_val.is_integer():
                                val_str = str(int(raw_data_val))
                            elif hasattr(raw_data_val, 'strftime'):
                                val_str = raw_data_val.strftime('%B %d, %Y')
                            else:
                                val_str = str(raw_data_val)
                            new_val = pattern.sub(val_str, new_val)
                    
                    # Remove any remaining placeholders
                    new_val = re.sub(r"\{\{.*?\}\}", "", new_val)
                    cell.value = new_val.strip() if new_val else ""

    # Clean up sheets
    if "TEMPLATE_TO_DELETE" in wb.sheetnames:
        wb.remove(wb["TEMPLATE_TO_DELETE"])
    for name in original_sheets:
        if name in wb.sheetnames and name != "TEMPLATE_TO_DELETE":
            wb.remove(wb[name])
            
    wb_buffer = io.BytesIO()
    wb.save(wb_buffer)
    wb_buffer.seek(0)
    return wb_buffer.getvalue()

# --- LOAD DATA ASSETS (Optimized Loading) ---
@st.cache_data(ttl=3600)
def load_data():
    """Load all data with optimized caching"""
    source_data = download_file(SOURCE_URL)
    template_data = download_file(TEMPLATE_URL)
    
    if source_data is None or template_data is None:
        return None, None, None
    
    # Load and process DataFrame
    df = pd.read_excel(source_data)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.strip().str.upper()
    
    # Create display column
    df["SITE_DISPLAY"] = df.apply(
        lambda row: f"{int(row['SITE NO'])} - {row['SITE NAME']}" 
        if pd.notna(row.get('SITE NO')) and isinstance(row.get('SITE NO'), (int, float)) 
        else f"{row.get('SITE NO', '')} - {row.get('SITE NAME', '')}".strip(" -"), 
        axis=1
    )
    
    # Get template bytes
    template_bytes = template_data.getvalue()
    
    # Extract placeholders from template (cached separately)
    placeholders = get_placeholders_from_template(template_bytes)
    
    return df, placeholders, template_bytes

# Show loading spinner while data loads
with st.spinner("Loading data assets..."):
    df, placeholders, template_bytes_raw = load_data()

if df is None or template_bytes_raw is None:
    st.error("Failed to load data. Please check connection profiles.")
    st.stop()

# --- MINIFIED HTML TEMPLATE ---
HTML_FRAMEWORK = """
<!DOCTYPE html>
<html>
<head>
<style>
body{margin:0;padding:0;background:#fff;font-family:Arial,sans-serif}
.ritz .waffle a{color:inherit}
.ritz .waffle td{padding:2px 3px!important;vertical-align:middle;border:none!important}
.freezebar-origin-ltr,.column-headers-background,.row-headers-background{background:#f8f9fa;text-align:center;font-size:8pt;color:#444746;font-weight:400;border:none!important}
.ritz .waffle .s0{background:#800000;text-align:center;font-weight:700;color:#fff;font-size:8pt;white-space:nowrap;padding:4px 3px!important;border:none!important}
.ritz .waffle .s1{background:#fff;text-align:left;font-weight:700;color:#000;font-size:8pt;white-space:nowrap;padding:4px 3px!important;border:none!important}
.ritz .waffle .s2{background:#fff;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s3{background:#fff;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s4{background:#f8f9fa;text-align:left;color:#000;font-size:8pt;vertical-align:middle;white-space:nowrap;padding:4px 3px!important;line-height:1.4;max-width:0;overflow:hidden;text-overflow:ellipsis;border:none!important}
.ritz .waffle .s4.wrap-text{white-space:normal!important;word-wrap:break-word!important;word-break:break-word!important;overflow-wrap:break-word!important;max-width:100%!important;overflow:visible!important;text-overflow:clip!important;height:auto!important}
.ritz .waffle .s5{background:#fff;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s6{background:#fff;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s7{background:#fff;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s8{background:#fff;text-align:left;color:#f00;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s9{background:#f8f9fa;text-align:left;color:#000;font-size:8pt;vertical-align:middle;white-space:nowrap;padding:4px 3px!important;line-height:1.4;max-width:0;overflow:hidden;text-overflow:ellipsis;border:none!important}
.ritz .waffle .s9.wrap-text{white-space:normal!important;word-wrap:break-word!important;word-break:break-word!important;overflow-wrap:break-word!important;max-width:100%!important;overflow:visible!important;text-overflow:clip!important;height:auto!important}
.ritz .waffle .s10{background:#bfbfbf;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s11{background:#fff;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s12{background:#fff;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s13{background:#b7b7b7;text-align:left;font-weight:700;color:#f00;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s14{background:#b7b7b7;text-align:left;color:#f00;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s15{background:#b7b7b7;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s16{background:#b7b7b7;text-align:left;color:#f00;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s17{background:#b7b7b7;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s18{background:#b7b7b7;text-align:left;color:#f00;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s19{background:#b7b7b7;text-align:left;color:#f00;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s20{background:#b7b7b7;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s21{background:#b7b7b7;text-align:left;color:#f00;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s22{background:#fff;text-align:left;font-weight:700;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s23{background:#fff;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s24{background:#fff;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle .s25{background:#fff;text-align:left;color:#000;font-size:8pt;white-space:nowrap;border:none!important}
.ritz .waffle{border-collapse:collapse;width:100%}
.ritz .waffle tr{height:auto!important}
.ritz .waffle td[class*="s4"],.ritz .waffle td[class*="s9"]{height:auto!important;min-height:20px}
.remarks-row{height:auto!important}
.remarks-row td{height:auto!important;padding:6px 3px!important;vertical-align:top!important}
.remarks-row td.s5{white-space:normal!important;word-wrap:break-word!important;word-break:break-word!important;overflow-wrap:break-word!important;max-width:100%!important;overflow:visible!important;text-overflow:clip!important;height:auto!important;line-height:1.6!important;padding:8px 6px!important}
.remarks-label{white-space:nowrap!important;vertical-align:top!important;padding-top:8px!important}
</style>
<script>
document.addEventListener('DOMContentLoaded',function(){
function checkAndWrapCells(){
document.querySelectorAll('.s4, .s9').forEach(c=>{
if(c.textContent&&c.textContent.trim().length>0){
if(c.scrollWidth>c.offsetWidth+5)c.classList.add('wrap-text');
else c.classList.remove('wrap-text')}});
const r=document.querySelector('.remarks-row td.s5');
if(r){r.style.whiteSpace='normal';r.style.wordWrap='break-word';r.style.wordBreak='break-word';r.style.overflowWrap='break-word';
const p=r.closest('tr');if(p)p.style.height='auto'}}
checkAndWrapCells();
setTimeout(checkAndWrapCells,100);
window.addEventListener('resize',checkAndWrapCells);
const o=new MutationObserver(checkAndWrapCells);
const t=document.querySelector('.waffle tbody');
if(t)o.observe(t,{childList:true,subtree:true,characterData:true})});
</script>
</head>
<body>
<div class="ritz grid-container" dir="ltr">
<table class="waffle" cellspacing="0" cellpadding="0" style="table-layout:fixed;width:100%;border-collapse:collapse">
<colgroup><col style="width:223px"><col style="width:100px"><col style="width:86px"><col style="width:100px"><col style="width:94px"><col style="width:100px"><col style="width:81px"><col style="width:15px"><col style="width:148px"><col style="width:176px"><col style="width:100px"><col style="width:100px"><col style="width:100px"><col style="width:125px"><col style="width:29px"></colgroup>
<tbody>
<tr><td class="s0" colspan="15">SITE INFORMATION REPORT</td></tr>
<tr><td class="s1" colspan="7">General Information</td><td class="s1"></td><td class="s1" colspan="7">Location</td></tr>
<tr><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td></tr>
<tr><td class="s2">Trade Area Name</td><td class="s2"></td><td class="s4" colspan="5">_TRADE_AREA_</td><td class="s3"></td><td class="s5" colspan="2">Site Name</td><td class="s4" colspan="5">_SITE_NAME_</td></tr>
<tr><td class="s2">Site Name:</td><td class="s2"></td><td class="s4" colspan="5">_SITE_NAME_</td><td class="s3"></td><td class="s5" colspan="2">Unit #, Bldg/St # and St Name</td><td class="s4" colspan="5">_UNIT_BLDG_ST_NAME_</td></tr>
<tr><td class="s2">Site Number:</td><td class="s2"></td><td class="s4" colspan="5">_SITE_NO_</td><td class="s3"></td><td class="s5" colspan="2">Barangay/District Name</td><td class="s4" colspan="5">_BARANGAY_DISTRICT_NAME_</td></tr>
<tr><td class="s2">Date Started</td><td class="s2"></td><td class="s4" colspan="5">_TIMESTAMP_</td><td class="s3"></td><td class="s5" colspan="2">City/Municipality</td><td class="s4" colspan="5">_CITY_MUNICIPALITY_</td></tr>
<tr><td class="s5" colspan="2">Date Report Submitted</td><td class="s4" colspan="5">_DATE_OF_REPORT_</td><td class="s3"></td><td class="s5" colspan="2">Region</td><td class="s4" colspan="5">_REGION_</td></tr>
<tr><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td><td class="s5" colspan="2">Postal Code</td><td class="s4" colspan="5">_POSTAL_CODE_</td></tr>
<tr><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s3"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s7"></td></tr>
<tr><td class="s1" colspan="7">Terms</td><td class="s3"></td><td class="s1" colspan="7">Rates</td></tr>
<tr><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td></tr>
<tr><td class="s2">Site Availability Date</td><td class="s2"></td><td class="s4" colspan="5">_SITE_AVAILABILITY_DATE_</td><td class="s3"></td><td class="s8" colspan="2">Monthly Rental Rate (Php)</td><td class="s4" colspan="5">_MONTHLY_RENTAL_RATE_</td></tr>
<tr><td class="s2">COL Start Date</td><td class="s2"></td><td class="s4" colspan="5">_COL_START_DATE_</td><td class="s3"></td><td class="s8" colspan="2">Percentage Rent</td><td class="s4" colspan="5"></td></tr>
<tr><td class="s2">COL End Date</td><td class="s2"></td><td class="s4" colspan="5">_COL_END_DATE_</td><td class="s3"></td><td class="s8" colspan="2">Minimum Guaranteed Rent</td><td class="s4" colspan="5"></td></tr>
<tr><td class="s2">Lease Terms</td><td class="s2"></td><td class="s4" colspan="5">_LEASE_TERMS_</td><td class="s3"></td><td class="s8" colspan="2">Annual Escalation Rate (%)</td><td class="s4" colspan="5">_ESCALATION_</td></tr>
<tr><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s3"></td><td class="s8" colspan="2">Advance Rental (Php)</td><td class="s4" colspan="5">_ADVANCE_RENTAL_</td></tr>
<tr><td class="s1" colspan="7">Technical Info</td><td class="s3"></td><td class="s8" colspan="2">Security Deposit Amount (Php)</td><td class="s4" colspan="5">_SECURITY_DEPOSIT_</td></tr>
<tr><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td><td class="s8" colspan="2">CUSA Dues</td><td class="s4" colspan="5">_CUSA_</td></tr>
<tr><td class="s5" colspan="2">Lot /Floor Area (in sqm)</td><td class="s4" colspan="5">_LOT_FLOOR_AREA_SQM_</td><td class="s3"></td><td class="s8" colspan="2">Estimated Revenue Per Mo.</td><td class="s4" colspan="5"></td></tr>
<tr><td class="s2">Frontage (in m)</td><td class="s2"></td><td class="s4" colspan="5">_FRONTAGE_</td><td class="s3"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s7"></td></tr>
<tr><td class="s2">Depth (in m)</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s1" colspan="7">Provisions</td></tr>
<tr><td class="s5" colspan="2">Floor to Slab Height (in m) - if Bldg</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s2" colspan="7"></td></tr>
<tr><td class="s5" colspan="2">No. of Storeys (If Bldg Lessee)</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Tenant is the Owner</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s5" colspan="2">Type of Structure(if Bldg Lessee)</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Lease Type</td><td class="s9" colspan="5">_LEASE_TYPE_</td></tr>
<tr><td class="s2">Soil Profile</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Principal COL</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">Supply Access:</td><td class="s2"></td><td class="s2" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Sub-Lease Provision</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">Power</td><td class="s10"></td><td class="s2">Aircon</td><td class="s10"></td><td class="s5" colspan="2">LPG Fire Pro</td><td class="s10"></td><td class="s3"></td><td class="s5" colspan="2">Pre-Term/Partial Term</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">Water</td><td class="s10"></td><td class="s2">Exhaust</td><td class="s10"></td><td class="s5" colspan="2">Drainage TP</td><td class="s10"></td><td class="s3"></td><td class="s5" colspan="2">Tripartite Agreement</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s3"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s7"></td></tr>
<tr><td class="s1" colspan="7">Lessor and Tenant Details</td><td class="s3"></td><td class="s1" colspan="7">If with Sub-Lessor/ Sub-Lessee</td></tr>
<tr><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td></tr>
<tr><td class="s2">Name of Lessor</td><td class="s2"></td><td class="s4" colspan="5">_LESSOR_</td><td class="s3"></td><td class="s5" colspan="2">Name of Sub-Lessor</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">Contact No.</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Contact No.</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">E-mail Address</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">E-mail Address</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">Type of Ownership</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Type of Ownership</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">Company Name</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Company Name</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s5" colspan="2">Developer Account Name</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Developer Account Name</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">Business Address</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Business Address</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s5" colspan="2">Name of Authorized Representative</td><td class="s4" colspan="5">_CONTACT_PERSON_SOURCE_</td><td class="s3"></td><td class="s5" colspan="2">Name of Authorized Representative</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s5" colspan="2">Residence Address of Authorized Representative</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Residence Address of Authorized Representative</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">Contact No.</td><td class="s2"></td><td class="s4" colspan="5">_CONTACT_NUMBER_</td><td class="s3"></td><td class="s5" colspan="2">Contact No.</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">E-mail Address</td><td class="s2"></td><td class="s4" colspan="5">_EMAIL_ADDRESS_</td><td class="s3"></td><td class="s5" colspan="2">E-mail Address</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s2"></td><td class="s3"></td><td class="s2"></td><td class="s2"></td><td class="s3" colspan="5"></td></tr>
<tr><td class="s2">Name of Lessee</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Name of Sub-Lessee</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">Position</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Position</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">Contact No.</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Contact No.</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">E-mail Address</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">E-mail Address</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s5" colspan="2">Name of Authorized Representative</td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Name of Authorized Representative</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s2">Business Address</td><td class="s2"></td><td class="s4" colspan="5"></td><td class="s3"></td><td class="s5" colspan="2">Business Address</td><td class="s9" colspan="5"></td></tr>
<tr><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s12"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s11"></td><td class="s12"></td></tr>
<tr><td class="s13" colspan="15">Regulatory</td></tr>
<tr><td class="s14">Setback Requirement</td><td class="s15" colspan="4"></td><td class="s16" colspan="2">Perm Traffic Re-Routing</td><td class="s17"></td><td class="s15" colspan="2"></td><td class="s18" colspan="5">Future Development</td></tr>
<tr><td class="s14">Road Widening</td><td class="s15" colspan="4"></td><td class="s16" colspan="2">Perm Road Closure</td><td class="s17"></td><td class="s15" colspan="2"></td><td class="s18" colspan="5">Zoning Clearance</td></tr>
<tr><td class="s19">Pedestrian Overpass</td><td class="s20" colspan="4"></td><td class="s19" colspan="2">Infrastructure Programs</td><td class="s20"></td><td class="s20" colspan="2"></td><td class="s21" colspan="5">Gas Station</td></tr>
<tr><td class="s2" colspan="14"></td><td class="s3"></td></tr>
<tr><td class="s22">Site Acquirability:</td><td class="s2" colspan="13"></td><td class="s3"></td></tr>
<tr><td class="s2">Confidence Level</td><td class="s4" colspan="2"></td><td class="s2" colspan="11"></td><td class="s3"></td></tr>
<tr><td class="s2">Site Availability</td><td class="s23" colspan="2"><div style="width:184px;left:-1px">_SITE_AVAILABILITY_CLASS_</div></td><td class="s24"></td><td class="s25"></td><td class="s2" colspan="10"></td><td class="s3"></td></tr>
<tr class="remarks-row"><td class="s6 remarks-label" style="white-space:nowrap;vertical-align:top;padding-top:8px">Other Remarks:</td><td class="s5" colspan="7" style="white-space:normal;word-wrap:break-word;word-break:break-word;overflow-wrap:break-word;max-width:100%;overflow:visible;text-overflow:clip;height:auto;line-height:1.6;padding:8px 6px">_REMARKS_</td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s6"></td><td class="s7"></td></tr>
</tbody></table></div></body></html>
"""

# --- UI CONTROLS ---
trade_areas = ["Select Trade Area..."] + sorted(df["TRADE AREA"].dropna().unique().tolist())
col1, col2, col3 = st.columns([1.5, 1.5, 1.0])

with col1:
    st.markdown("<p style='font-size:0.75rem;font-weight:500;color:#444746;margin:0'>Trade Area</p>", unsafe_allow_html=True)
    selected_ta = st.selectbox("Trade Area", options=trade_areas, index=0, label_visibility="collapsed")
    
with col2:
    st.markdown("<p style='font-size:0.75rem;font-weight:500;color:#444746;margin:0'>Site View</p>", unsafe_allow_html=True)
    if selected_ta and selected_ta != "Select Trade Area...":
        raw_sites = df[df["TRADE AREA"] == selected_ta]["SITE_DISPLAY"].dropna().unique().tolist()
        sorted_sites = sorted(raw_sites, key=parse_site_number)
        sites_in_ta = ["Select Site..."] + sorted_sites
    else:
        sites_in_ta = ["Select Site..."]
    selected_site_display = st.selectbox("Site Name", options=sites_in_ta, index=0, label_visibility="collapsed")

with col3:
    if selected_ta and selected_ta != "Select Trade Area...":
        # Use df hash to invalidate cache when data changes
        df_hash = hash(pd.util.hash_pandas_object(df).sum())
        st.download_button(
            label="Export",
            data=generate_trade_area_report(selected_ta, df_hash),
            file_name=f"{selected_ta}_Full_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# --- RENDER VIEW ---
if selected_ta != "Select Trade Area..." and selected_site_display != "Select Site...":
    site_data = df[df["SITE_DISPLAY"] == selected_site_display]
    if not site_data.empty:
        site_row_data = site_data.iloc[0]
        try:
            def process_val(key_string):
                val = site_row_data.get(key_string.upper(), "")
                if pd.isna(val) or val is None:
                    return ""
                if isinstance(val, float) and val.is_integer():
                    return str(int(val))
                if hasattr(val, 'strftime'):
                    return val.strftime('%B %d, %Y')
                return str(val).strip()

            # Batch replace for speed
            replacements = {
                "_TRADE_AREA_": "TRADE AREA",
                "_SITE_NAME_": "SITE NAME",
                "_SITE_NO_": "SITE NO",
                "_TIMESTAMP_": "TIMESTAMP",
                "_DATE_OF_REPORT_": "DATE OF REPORT",
                "_UNIT_BLDG_ST_NAME_": "UNIT #, BLDG/ST # AND ST NAME",
                "_BARANGAY_DISTRICT_NAME_": "BARANGAY/DISTRICT NAME",
                "_CITY_MUNICIPALITY_": "CITY/MUNICIPALITY",
                "_REGION_": "REGION",
                "_POSTAL_CODE_": "POSTAL CODE",
                "_SITE_AVAILABILITY_DATE_": "SITE AVAILABILITY DATE",
                "_MONTHLY_RENTAL_RATE_": "MONTHLY RENTAL RATE",
                "_COL_START_DATE_": "COL START DATE",
                "_COL_END_DATE_": "COL END DATE",
                "_LEASE_TERMS_": "LEASE TERMS",
                "_ESCALATION_": "ESCALATION",
                "_ADVANCE_RENTAL_": "ADVANCE RENTAL",
                "_SECURITY_DEPOSIT_": "SECURITY DEPOSIT",
                "_CUSA_": "CUSA",
                "_LOT_FLOOR_AREA_SQM_": "LOT/FLOOR AREA SQM",
                "_FRONTAGE_": "FRONTAGE",
                "_LEASE_TYPE_": "LEASE TYPE",
                "_LESSOR_": "LESSOR",
                "_CONTACT_PERSON_SOURCE_": "CONTACT PERSON/SOURCE",
                "_CONTACT_NUMBER_": "CONTACT NUMBER",
                "_EMAIL_ADDRESS_": "EMAIL ADDRESS",
                "_SITE_AVAILABILITY_CLASS_": "SITE AVAILABILITY CLASS",
                "_REMARKS_": "REMARKS"
            }
            
            rendered_view = HTML_FRAMEWORK
            for placeholder, key in replacements.items():
                rendered_view = rendered_view.replace(placeholder, process_val(key))
            
            rendered_view = re.sub(r"_[A-Z0-9_]+_", "", rendered_view)
            components.html(rendered_view, height=850, scrolling=True)
                
        except Exception as e:
            st.error(f"Error compiling visual matrix framework: {str(e)}")
else:
    st.info("Please select a Trade Area and a Site to view the specific report.")
