import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter
import io
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image as PILImage
import base64
from io import BytesIO
import re

# Add these imports at the top
from openpyxl import load_workbook
from openpyxl.utils import range_boundaries
import tempfile
import os

# --- CONFIGURATION ---
# Google Sheets API configuration
SCOPE = ["https://spreadsheets.google.com/feeds", 
         "https://www.googleapis.com/auth/drive",
         "https://www.googleapis.com/auth/spreadsheets"]

# Path to your service account JSON file
# You'll need to create this from Google Cloud Console
SERVICE_ACCOUNT_FILE = 'service_account.json'  # Update this path

# Your spreadsheet ID (already in your config)
SPREADSHEET_ID = '14nhO9u7zJRcOoux8I7l2IzwU7iQZNW9fRX6TCip47CE'
DRIVE_FOLDER_ID = '13sLmXzxQvV12_ypTBRG2QW1yVIHaanba'  # Your Drive folder ID

# --- GOOGLE SHEETS AUTHENTICATION ---
@st.cache_resource
def get_gsheet_client():
    """Initialize Google Sheets client"""
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPE)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Failed to authenticate with Google Sheets: {str(e)}")
        return None

def get_photo_from_drive(filename, folder_id=DRIVE_FOLDER_ID):
    """Get image from Google Drive folder by filename"""
    try:
        # You'll need to implement Drive API search
        # This is a placeholder - you'll need full Drive API integration
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPE)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Search for the file
        query = f"name='{filename}' and '{folder_id}' in parents and mimeType contains 'image/'"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        if files:
            file_id = files[0]['id']
            # Download the file
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.seek(0)
            return fh
        return None
    except Exception as e:
        st.warning(f"Could not fetch image: {str(e)}")
        return None

def extract_photo_paths(row_data, source_columns):
    """Extract photo paths from source columns"""
    photo_paths = []
    
    # Get column indices (0-based)
    col_start1 = openpyxl.utils.column_index_from_string(source_columns['start1']) - 1
    col_end1 = openpyxl.utils.column_index_from_string(source_columns['end1']) - 1
    col_start2 = openpyxl.utils.column_index_from_string(source_columns['start2']) - 1
    col_end2 = openpyxl.utils.column_index_from_string(source_columns['end2']) - 1
    
    # Extract from first range (AI-AL)
    for i in range(col_start1, col_end1 + 1):
        if i < len(row_data):
            photo_paths.append(row_data[i] if row_data[i] else '')
    
    # Extract from second range (AN-AR)
    for i in range(col_start2, col_end2 + 1):
        if i < len(row_data):
            photo_paths.append(row_data[i] if row_data[i] else '')
    
    return photo_paths

def process_row_with_photos(row_data, source_columns=SOURCE_COLUMNS):
    """Process a row and extract photo information"""
    photo_paths = extract_photo_paths(row_data, source_columns)
    
    # Filter out empty paths
    valid_photos = [p for p in photo_paths if p and str(p).strip()]
    
    # Get image data for each valid photo
    photo_data = []
    for path in valid_photos:
        filename = str(path).split('/')[-1].split('\\')[-1]
        image_data = get_photo_from_drive(filename)
        photo_data.append({
            'path': path,
            'filename': filename,
            'image_data': image_data
        })
    
    return photo_data

def create_excel_with_photos(site_data, placeholders, template_bytes):
    """Create Excel report with photos embedded"""
    wb = load_workbook(io.BytesIO(template_bytes))
    ws = wb.active
    ws.title = "Report"
    
    # Process placeholders in template
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and "{{" in cell.value:
                new_val = cell.value
                for ph in placeholders:
                    target_regex = r"\{\{\s*" + re.escape(ph) + r"(\s*:.*?)?\}\}"
                    if re.search(target_regex, new_val):
                        raw_val = site_data.get(ph.upper(), "")
                        if pd.isna(raw_val) or raw_val is None:
                            val_str = ""
                        else:
                            val_str = str(raw_val)
                        new_val = re.sub(target_regex, val_str, new_val)
                cell.value = new_val.strip()
    
    # Add photos to the report (you need to define where to place them)
    # This is a simplified example - adjust column positions as needed
    PHOTO_COLUMNS = ['C', 'D', 'E', 'F', 'H', 'I', 'J', 'K', 'L']
    
    # Get photo paths from site data
    photo_paths = []
    for col in SOURCE_COLUMNS:
        # You'll need to extract photo paths from the actual data
        pass
    
    # Place photos in the Excel file
    row_num = 2  # Start from row 2
    for col, path in zip(PHOTO_COLUMNS, photo_paths):
        if path and str(path).strip():
            filename = str(path).split('/')[-1].split('\\')[-1]
            image_data = get_photo_from_drive(filename)
            
            if image_data:
                try:
                    # Create PIL Image and resize
                    pil_img = PILImage.open(image_data)
                    pil_img.thumbnail((100, 100))  # Resize to fit cell
                    
                    # Save to BytesIO
                    img_bytes = BytesIO()
                    pil_img.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    # Add to Excel
                    img = XLImage(img_bytes)
                    cell_ref = f"{col}{row_num}"
                    ws.add_image(img, cell_ref)
                except Exception as e:
                    st.warning(f"Could not embed image {filename}: {str(e)}")
    
    # Save workbook
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()

# --- UPDATE YOUR EXISTING FUNCTIONS ---

def update_generate_trade_area_report(trade_area):
    """Updated version of generate_trade_area_report with photo support"""
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
        
        # Process placeholders
        for row_cells in new_sheet.iter_rows():
            for cell in row_cells:
                if isinstance(cell.value, str) and "{{" in cell.value:
                    new_val = cell.value
                    for ph in placeholders:
                        target_regex = r"\{\{\s*" + re.escape(ph) + r"(\s*:.*?)?\}\}"
                        if re.search(target_regex, new_val):
                            raw_val = r_row.get(ph.upper(), "")
                            if pd.isna(raw_val) or raw_val is None:
                                val_str = ""
                            else:
                                val_str = str(raw_val)
                            new_val = re.sub(target_regex, val_str, new_val)
                    cell.value = new_val.strip()
        
        # Add photos to this sheet
        # Define where to place photos (adjust as needed)
        photo_cols = ['C', 'D', 'E', 'F', 'H', 'I', 'J', 'K', 'L']
        row_for_photos = 2  # Start from row 2
        
        # Extract photo paths from the row data
        photo_paths = []
        # You need to know which columns contain photo paths
        # For example, if your data has columns for photos
        photo_columns = ['PROPERTY PHOTOS 1', 'PROPERTY PHOTOS 2', 'PROPERTY PHOTOS 3', 'PROPERTY PHOTOS 4', 'PROPERTY PHOTOS 5']
        for col_name in photo_columns:
            if col_name in r_row.index:
                photo_paths.append(r_row[col_name])
        
        # Embed photos
        for col_idx, path in enumerate(photo_cols[:len(photo_paths)]):
            if col_idx < len(photo_paths) and photo_paths[col_idx]:
                filename = str(photo_paths[col_idx]).split('/')[-1].split('\\')[-1]
                image_data = get_photo_from_drive(filename)
                
                if image_data:
                    try:
                        pil_img = PILImage.open(image_data)
                        pil_img.thumbnail((100, 100))
                        
                        img_bytes = BytesIO()
                        pil_img.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        
                        img = XLImage(img_bytes)
                        cell_ref = f"{path}{row_for_photos}"
                        new_sheet.add_image(img, cell_ref)
                    except Exception as e:
                        st.warning(f"Could not embed photo {filename}: {str(e)}")
        
        # Auto-size rows
        for row in new_sheet.iter_rows():
            max_len = max([len(str(cell.value or '')) for cell in row])
            if max_len > 45:
                new_sheet.row_dimensions[row[0].row].height = None
    
    # Clean up
    if "TEMPLATE_TO_DELETE" in wb.sheetnames:
        wb.remove(wb["TEMPLATE_TO_DELETE"])
    for name in original_sheets:
        if name in wb.sheetnames and name != "TEMPLATE_TO_DELETE":
            wb.remove(wb[name])
    
    wb_buffer = io.BytesIO()
    wb.save(wb_buffer)
    wb_buffer.seek(0)
    return wb_buffer.getvalue()

# --- UPDATE THE DOWNLOAD BUTTON SECTION ---
# Replace the existing download button code with:

with col3:
    if selected_ta and selected_ta != "Select Trade Area...":
        st.download_button(
            label="📊 Export with Photos",
            data=update_generate_trade_area_report(selected_ta),
            file_name=f"{selected_ta}_Full_Report_with_Photos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
