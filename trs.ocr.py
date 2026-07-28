import streamlit as st
from PIL import Image
import cv2
import numpy as np
import io
from google.cloud import vision
from google.oauth2 import service_account

# Set page config
st.set_page_config(
    page_title="Document OCR Scanner",
    page_icon=":page_facing_up:",
    layout="wide"
)

# Hardcoded credentials for testing only
CREDENTIALS_JSON = {
    "type": "service_account",
    "project_id": "crafty-granite-503802-d8",
    "private_key_id": "9b543441635ab8f870f5876cf8f5ad9469e6ecca",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDQh08E+/k/JtJh\nnELNjg07+EAG3BkjTiWgezWdfTGf17d47ZuBoGgeT8SD5XqPTYWA/XvEsmJ6MZAp\nZ3mRGeWuue4g6l53p/XwTxefGr3unY9eEoqcmRZ0+7DFbd8hPt0GUTSi3Zd4igFs\n3QDIVRnbecteigVex20n/3uH8+4lLGPCw7Ys2smf5U4eNiMUmGDgNuKJ6gL7xwgc\nbdhB8ZK0Q+cq43y0gOgPRW2D57fc6AQytOQHIVHcmzIIXJE5cyjm+ay9E8kw2gVx\nQGkH/JhLdWUxVbbz16L/jJciuWNztqtiAkOeSGd3MkuEvliFFlN7lUoDEfXpXg0j\nNrcKjsrnAgMBAAECggEAREPPgAu3BFACtlav3df/iB7UYwqBpjeqhLdhDW4TJUc6\ntnlem5h2DVpCtIUW0rvnlRsmffWB3IvGLG/F8dT/Bmyywo7HHzfagPF7g6f+/pMR\nAJRkUTCik+hjbbZywdDxDWTfLOQK9riDD+7nly2Y2esswwW/DVCO8PWnrJGT6BHh\nOb0CD/Jd//5mKv3JHmeTQxvkFh3uHklAeZdogqSsG7fbJbDwALGnOed8VvHpZLYO\n8NL059irq6tX01sUEiJvYGqRlEY2X9UF//ov1nKEjJk3gvNXO8cdGQn42gq9MA7P\nqXjd9g69LRzTlCiT5OnGakEVs0uPD51Hsi/m5l6r1QKBgQDuo8MJcac7cy9Z6jGq\nqYHOeKtwUrCPY0ycuZy/ipDt6TxpdzVGTivchmyxBjciftkbHouU/PwWKPf9gaKP\nATiHf+2j3xKjPWorg9wFqmr2hzJFWJYEmpekN0B9PTyPuGVPSALhpTu0v8ce9AGS\nWTqwK7/B+mM0yDwYD6Q253IJiwKBgQDfssfO4DjS9zInkRhp7ilQwEt4HDKeFvSV\noMIk7aew8P9/f0Lfstb87EBh98uVAgsew2SxVW5RYm02P4QlwFP03UEY6XY/1l2B\n6kmbxH32L49BtVXx8izdB8CE7aj8SrILQ2bubxlFmp7ESjEzw1La2Z2U6otxVKDJ\niUCxL/NXlQKBgB7zdnRfHUWEpvuOeGqeGYvh8rpavzOZuXIKUN425p00xvUW1P4N\nXXr4pFhBah07PoVZ7NiiB0AIiEGE8sSBcAeC/Bto703kxURnkb3aYI0g89AysSJf\nupM950tXCefKDrm9qUIC4D+NMBI/q4SDtizrP6+0/fD2l3S3cqD8W7oJAoGBAJAr\n6zbbsAPXqY1yqCdthVcz9+/bTIwzA0OELlwahx8005ZacME3w/OSWBRL3fuVK5GS\nIM1h4A23v+dcnFCwWevQxWnG3Z1bDTzzwKkRxJTsJgoVUuTyThPOMTf67BReF83G\njQpStBj2BClCH9/anQXLhxI479IE1vPM79LCsrTZAoGBALZuNpwi0Jsu2Z5UUdJt\n7hroGgrvp1vTsVdtbLctSCiNfaWlK3O6WSg0ltKaV0mzuxl6oOXdT970sEKO+y0l\ni+Ql7J+qX/pnWSV5HQuIHcmGWr1Y4PsBZlBafzqD7VnFaN1IQXCjMHGh7T7CIeZr\nQ+FOlTnI/pycZ8WvRIbRrXgy\n-----END PRIVATE KEY-----\n",
    "client_email": "vision-ocr-service@crafty-granite-503802-d8.iam.gserviceaccount.com",
    "client_id": "102920982682321468266",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/vision-ocr-service%40crafty-granite-503802-d8.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Title and description
st.title("Document OCR Scanner")
st.markdown("Upload a document image to extract all text using Google Cloud Vision OCR")

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
    
    st.header("Google Cloud Vision Settings")
    st.markdown("""
    Free Tier: 1,000 images per month free
    After Free Tier: $1.50 per 1,000 images
    New User Credits: $300 free credits for 90 days
    """)

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
    """Perform OCR using Google Cloud Vision API with hardcoded credentials"""
    try:
        # Create credentials from hardcoded JSON
        credentials = service_account.Credentials.from_service_account_info(
            CREDENTIALS_JSON
        )
        
        # Initialize the Vision client
        client = vision.ImageAnnotatorClient(credentials=credentials)
        
        # Convert PIL image to bytes
        if isinstance(image, Image.Image):
            img = image
        else:
            img = Image.fromarray(image)
        
        # Apply preprocessing if selected
        if preprocessing and preprocessing != 'None':
            # Convert to OpenCV for preprocessing
            img_np = np.array(img)
            img_np = preprocess_image(img_np, preprocessing)
            img = Image.fromarray(img_np)
        
        # Convert to bytes for Google Cloud Vision
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        content = img_byte_arr.getvalue()
        
        # Create Vision image object
        vision_image = vision.Image(content=content)
        
        # Perform text detection
        response = client.text_detection(image=vision_image)
        texts = response.text_annotations
        
        # Check for errors
        if response.error.message:
            st.error(f"Google Cloud Vision API Error: {response.error.message}")
            return None
        
        # Extract text
        if texts:
            # The first element contains the full text
            extracted_text = texts[0].description
            return extracted_text.strip()
        else:
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
            st.image(image, width=400)
            
            # Show image info
            st.caption(f"Size: {image.size[0]}x{image.size[1]} pixels")
            st.caption(f"Format: {image.format}")
        
        # Perform OCR and display results
        with col2:
            st.subheader("Extracted Text")
            
            with st.spinner("Processing image with Google Cloud Vision..."):
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
                    - Google Cloud Vision works best with clear, straight text
                    """)

if __name__ == "__main__":
    main()
