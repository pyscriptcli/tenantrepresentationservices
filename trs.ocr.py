import streamlit as st
import pytesseract
from PIL import Image
import cv2
import numpy as np

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
        st.error("Tesseract OCR not found. Please install Tesseract OCR on your system.")
        st.markdown("""
        Installation instructions:
        
        Ubuntu/Debian:
        sudo apt-get install tesseract-ocr
        
        macOS:
        brew install tesseract
        
        Windows:
        Download from: https://github.com/UB-Mannheim/tesseract/wiki
        """)
        return None
        
    except Exception as e:
        st.error(f"OCR Error: {str(e)}")
        return None

def main():
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
            st.image(image, use_column_width=True)
            
            # Show image info
            st.caption(f"Size: {image.size[0]}x{image.size[1]} pixels")
            st.caption(f"Format: {image.format}")
        
        # Perform OCR and display results
        with col2:
            st.subheader("Extracted Text")
            
            with st.spinner("Processing image and extracting text..."):
                text = perform_ocr(image)
            
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
                    """)

if __name__ == "__main__":
    main()
