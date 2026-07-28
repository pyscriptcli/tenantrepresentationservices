import streamlit as st
import cv2
import numpy as np
from PIL import Image
import easyocr
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Preprocessing Functions ---

def apply_grayscale(image):
    """Convert image to grayscale and back to 3-channel for consistent processing."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def apply_threshold(image):
    """Apply Otsu's thresholding to binarize the image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

def apply_deskew(image):
    """Deskew the image using the minimum area rectangle of the text contours."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 5:
        return image
        
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
        
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# --- EasyOCR Integration ---

LANGUAGE_MAP = {
    "English": ["en"],
    "Spanish": ["es"],
    "French": ["fr"],
    "German": ["de"],
    "Italian": ["it"],
    "Portuguese": ["pt"],
    "English + Spanish": ["en", "es"]
}

@st.cache_resource
def load_ocr_reader(langs):
    """Load and cache the EasyOCR reader to prevent reloading on every interaction."""
    logger.info(f"Initializing EasyOCR Reader for languages: {langs}")
    # gpu=False ensures compatibility with Streamlit Cloud and CPU-only environments
    return easyocr.Reader(langs, gpu=False)

def perform_ocr(image, reader):
    """
    Extract text from an image using EasyOCR.
    Converts BGR (OpenCV) to RGB (EasyOCR requirement).
    """
    try:
        # EasyOCR expects RGB format
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # readtext returns: list of (bounding_box, text, confidence)
        results = reader.readtext(rgb_image)
        
        if not results:
            return "No text detected."
            
        # Extract and concatenate text. 
        # Format: "Text (Confidence%)"
        extracted_text = []
        for bbox, text, conf in results:
            extracted_text.append(f"{text} ({conf:.1%})")
            
        return "\n".join(extracted_text)
        
    except Exception as e:
        logger.error(f"OCR failed: {str(e)}")
        raise RuntimeError(f"OCR processing failed: {str(e)}")

# --- Streamlit UI ---

def main():
    st.set_page_config(page_title="EasyOCR Document Scanner", layout="wide")
    st.title("Document Scanner & OCR (EasyOCR)")
    
    # Sidebar Controls
    with st.sidebar:
        st.header("Settings")
        
        uploaded_file = st.file_uploader("Upload Document Image", type=["png", "jpg", "jpeg"])
        
        st.subheader("Language")
        selected_lang = st.selectbox("Select OCR Language", options=list(LANGUAGE_MAP.keys()))
        
        st.subheader("Preprocessing")
        apply_gray = st.checkbox("Grayscale")
        apply_thresh = st.checkbox("Threshold (Binarize)")
        apply_skew = st.checkbox("Deskew")
        
    # Main Content
    if uploaded_file is not None:
        # Load image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            st.error("Failed to load image. Please try a different file.")
            return

        # Apply Preprocessing
        processed_image = image.copy()
        if apply_gray:
            processed_image = apply_grayscale(processed_image)
        if apply_thresh:
            processed_image = apply_threshold(processed_image)
        if apply_skew:
            processed_image = apply_deskew(processed_image)
            
        # Display Images Side-by-Side
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_column_width=True)
        with col2:
            st.subheader("Processed")
            st.image(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB), use_column_width=True)
            
        # Perform OCR
        st.subheader("Extracted Text")
        with st.spinner("Extracting text... (First run may take longer to download models)"):
            try:
                langs = LANGUAGE_MAP[selected_lang]
                reader = load_ocr_reader(tuple(langs)) # Tuple for hashability in cache
                ocr_text = perform_ocr(processed_image, reader)
                
                st.text_area("OCR Results", value=ocr_text, height=300)
                
                # Download extracted text
                st.download_button(
                    "Download Text",
                    data=ocr_text,
                    file_name="extracted_text.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"An error occurred during OCR: {e}")
    else:
        st.info("Please upload an image to begin.")

if __name__ == "__main__":
    main()
