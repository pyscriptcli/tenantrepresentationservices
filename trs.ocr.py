import streamlit as st
import pytesseract
from PIL import Image
import cv2
import numpy as np

# Set page config
st.set_page_config(
    page_title="Document OCR Scanner",
    page_icon="📄",
    layout="wide"
)

# Title and description
st.title("📄 Document OCR Scanner")
st.markdown("Upload a document image to extract all text using OCR")

# Sidebar for instructions
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. Upload an image (JPG, PNG, or PDF)
    2. The app will extract all text
    3. View the extracted text alongside your image
    4. Copy or download the results
    """)
    
    st.header("⚙️ Settings")
    preprocessing = st.selectbox(
        "Image Preprocessing",
        options=['None', 'Grayscale', 'Threshold', 'Deskew', 'All'],
        index=4,
        help="Preprocessing can improve OCR accuracy for poor quality images"
    )

def preprocess_image(image, method):
    """Apply preprocessing to improve OCR accuracy"""
    if method == 'None':
        return image
    
    # Convert PIL to OpenCV format
    if isinstance(image, Image.Image):
        img = np.array(image)
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    else:
        img = image
    
    if method in ['Grayscale', 'All']:
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    if method in ['Threshold', 'All']:
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    if method in ['Deskew', 'All']:
        # Simple deskew using minAreaRect
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        coords = np.column_stack(np.where(gray > 128))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            if abs(angle) > 0.5:
                (h, w) = img.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                img = cv2.warpAffine(img, M, (w, h), 
                                   flags=cv2.INTER_CUBIC,
                                   borderMode=cv2.BORDER_REPLICATE)
    
    return img

def perform_ocr(image):
    """Perform OCR on the image"""
    try:
        # Convert PIL to OpenCV if needed
        if isinstance(image, Image.Image):
            img = np.array(image)
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        else:
            img = image
        
        # Preprocess
        if preprocessing and preprocessing != 'None':
            img = preprocess_image(img, preprocessing)
            
            # Convert back to PIL for pytesseract
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
        
        # Perform OCR - English only, optimized for documents
        custom_config = r'--oem 3 --psm 6 -l eng'
        text = pytesseract.image_to_string(img, config=custom_config)
        
        return text.strip()
        
    except pytesseract.TesseractNotFoundError:
        st.error("""
        ⚠️ **Tesseract OCR not found!**
        
