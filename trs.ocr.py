import streamlit as st
import easyocr
from PIL import Image
import cv2
import numpy as np
import time

# Set page config
st.set_page_config(
    page_title="Document OCR Scanner",
    page_icon=":page_facing_up:",
    layout="wide"
)

# Title and description
st.title("Document OCR Scanner")
st.markdown("Upload a document image to extract all text using OCR")

# Sidebar for instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. Upload an image (JPG, PNG, or PDF)
    2. The app will extract all text
    3. View the extracted text alongside your image
    4. Copy or download the results
    """)
    
    st.header("Settings")
    preprocessing = st.selectbox(
        "Image Preprocessing",
        options=['None', 'Grayscale', 'Threshold', 'Deskew', 'All'],
        index=4,
        help="Preprocessing can improve OCR accuracy for poor quality images"
    )
    
    # Language selection for EasyOCR
    st.header("OCR Language")
    language = st.selectbox(
        "Select language for OCR",
        options=['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese'],
        index=0,
        help="Select the language of the text in your document"
    )
    
    # Map user-friendly names to EasyOCR language codes
    language_map = {
        'English': 'en',
        'Spanish': 'es',
        'French': 'fr',
        'German': 'de',
        'Italian': 'it',
        'Portuguese': 'pt'
    }

# Cache the EasyOCR reader to avoid reloading models
@st.cache_resource
def load_reader(lang_code):
    """Load the EasyOCR reader with caching and progress indication"""
    # Show a progress message since model download takes time
    with st.spinner("Loading EasyOCR models for the first time. This may take a few minutes..."):
        # Initialize the reader with explicit parameters to optimize for CPU
        return easyocr.Reader([lang_code], gpu=False, download_enabled=True)

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

def perform_ocr(image, lang_code):
    """Perform OCR using EasyOCR with error handling"""
    try:
        # Load the EasyOCR reader (cached)
        reader = load_reader(lang_code)
        
        # Convert PIL image to numpy array for EasyOCR
        if isinstance(image, Image.Image):
            img = np.array(image)
            # EasyOCR expects RGB format
            if len(img.shape) == 3 and img.shape[2] == 3:
                # If it's BGR (from OpenCV), convert to RGB
                if img[0,0,0] > img[0,0,2]:  # Simple heuristic to check if it's BGR
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img = image
        
        # Apply preprocessing if selected
        if preprocessing and preprocessing != 'None':
            img = preprocess_image(img, preprocessing)
        
        # Perform OCR using EasyOCR
        # The result is a list of tuples: (bounding_box, text, confidence)
        result = reader.readtext(img)
        
        # Extract just the text from the results
        extracted_text = ""
        for detection in result:
            text = detection[1]
            confidence = detection[2]
            extracted_text += text + "\n"
        
        return extracted_text.strip()
        
    except Exception as e:
        st.error(f"OCR Error: {str(e)}")
        return None

def main():
    # Check if models are already loaded
    if 'models_loaded' not in st.session_state:
        st.session_state.models_loaded = False
        
        # Show a message about first-time setup
        info_placeholder = st.empty()
        info_placeholder.info("""
        First-time setup: EasyOCR needs to download model files (~500MB).
        This will happen once and may take 2-5 minutes depending on your internet speed.
        The app will start working after the download completes.
        """)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
        help="Upload a clear image of your document for text extraction"
    )
    
    if uploaded_file is not None:
        # Create two columns for layout
        col1, col2 = st.columns([1, 1])
        
        # Load and display image
        with col1:
            st.subheader("Original Image")
            image = Image.open(uploaded_file)
            # Fix for deprecation warning - use width parameter instead
            st.image(image, width=400)  # Changed from use_column_width
            
            # Show image info
            st.caption(f"Size: {image.size[0]}x{image.size[1]} pixels")
            st.caption(f"Format: {image.format}")
        
        # Perform OCR and display results
        with col2:
            st.subheader("Extracted Text")
            
            # Get the selected language code
            lang_code = language_map.get(language, 'en')
            
            with st.spinner("Processing image and extracting text..."):
                text = perform_ocr(image, lang_code)
            
            if text:
                # Display text in a nice text area
                st.text_area(
                    "Extracted Text",
                    value=text,
                    height=400,
                    key="ocr_output"
                )
                
                # Download button
                st.download_button(
                    label="Download Text File",
                    data=text,
                    file_name="extracted_text.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
                # Show statistics
                words = len(text.split())
                chars = len(text)
                st.caption(f"Words: {words} | Characters: {chars}")
                
                # Mark models as loaded
                st.session_state.models_loaded = True
                
            else:
                st.warning("No text was extracted. Try a different image or preprocessing method.")
                
                # Show tips for better results
                with st.expander("Tips for better OCR results"):
                    st.markdown("""
                    - Use a clear, well-lit photo
                    - Keep the document flat and straight
                    - Use the 'All' preprocessing option for poor quality images
                    - Ensure text is at least 12pt or larger
                    - Avoid shadows and glare
                    - For best results, try the 'All' preprocessing option
                    """)

if __name__ == "__main__":
    main()
