import streamlit as st
import cv2
import numpy as np
from PIL import Image
import easyocr
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Preprocessing Functions ---
def apply_grayscale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def apply_threshold(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

def apply_deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 5: return image
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# --- EasyOCR Integration ---
LANGUAGE_MAP = {
    "English": ["en"], "Spanish": ["es"], "French": ["fr"],
    "German": ["de"], "Italian": ["it"], "Portuguese": ["pt"],
    "English + Spanish": ["en", "es"]
}

@st.cache_resource(show_spinner=False)
def load_ocr_reader(langs_tuple):
    """Load and cache the EasyOCR reader."""
    langs = list(langs_tuple)
    logger.info(f"Initializing EasyOCR Reader for: {langs}")
    # gpu=False for Streamlit Cloud CPU environments
    return easyocr.Reader(langs, gpu=False, download_enabled=True)

def perform_ocr(image, reader):
    try:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = reader.readtext(rgb_image)
        if not results: return "No text detected."
        return "\n".join([f"{text} ({conf:.1%})" for bbox, text, conf in results])
    except Exception as e:
        logger.error(f"OCR failed: {str(e)}")
        raise RuntimeError(f"OCR processing failed: {str(e)}")

# --- Streamlit UI ---
def main():
    st.set_page_config(page_title="EasyOCR Document Scanner", layout="wide")
    st.title("Document Scanner & OCR (EasyOCR)")
    
    with st.sidebar:
        st.header("Settings")
        uploaded_file = st.file_uploader("Upload Document Image", type=["png", "jpg", "jpeg"])
        
        selected_lang = st.selectbox("Select OCR Language", options=list(LANGUAGE_MAP.keys()))
        langs = LANGUAGE_MAP[selected_lang]
        
        st.subheader("Preprocessing")
        apply_gray = st.checkbox("Grayscale")
        apply_thresh = st.checkbox("Threshold (Binarize)")
        apply_skew = st.checkbox("Deskew")
        
        # LAZY LOADING: Initialize engine only when user clicks
        st.divider()
        st.subheader("OCR Engine")
        if "ocr_reader" not in st.session_state:
            st.warning("Model not loaded. Click below to download (~500MB).")
            if st.button("Initialize OCR Engine", type="primary"):
                # st.status keeps the WebSocket alive during long downloads
                with st.status("Downloading and loading EasyOCR models...", expanded=True) as status:
                    st.write("Connecting to model repository...")
                    try:
                        st.session_state.ocr_reader = load_ocr_reader(tuple(langs))
                        status.update(label="Model loaded successfully!", state="complete", expanded=False)
                        st.rerun()
                    except Exception as e:
                        status.update(label=f"Failed to load model: {e}", state="error")
        else:
            st.success("OCR Engine Ready")

    # Main Content
    if uploaded_file is not None:
        if "ocr_reader" not in st.session_state:
            st.info("Please initialize the OCR Engine in the sidebar first.")
            return

        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            st.error("Failed to load image.")
            return

        processed_image = image.copy()
        if apply_gray: processed_image = apply_grayscale(processed_image)
        if apply_thresh: processed_image = apply_threshold(processed_image)
        if apply_skew: processed_image = apply_deskew(processed_image)
            
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_column_width=True)
        with col2:
            st.subheader("Processed")
            st.image(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB), use_column_width=True)
            
        st.subheader("Extracted Text")
        try:
            with st.spinner("Extracting text..."):
                ocr_text = perform_ocr(processed_image, st.session_state.ocr_reader)
                
            st.text_area("OCR Results", value=ocr_text, height=300)
            st.download_button("Download Text", data=ocr_text, file_name="extracted_text.txt", mime="text/plain")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.info("Please upload an image to begin.")

if __name__ == "__main__":
    main()
