import streamlit as st
from PIL import Image
import io

# Function to create a section for each image
def create_section(image, hashtags_key, captions_key, tips_key):
    if image is not None:
        st.image(image, use_column_width=True)
    
    with st.expander("Social Media Hashtags"):
        st.text_area("Enter hashtags here", height=100, key=hashtags_key)
    
    with st.expander("Captions"):
        st.text_area("Enter captions here", height=100, key=captions_key)
    
    with st.expander("AI Tips and Suggestions"):
        if image is not None:
            # Here you would integrate your AI model to generate tips
            # For now, we'll just display a placeholder message
            st.text_area("AI-generated tips will appear here", value="Coming soon: AI-generated tips based on your image!", height=100, key=tips_key, disabled=True)
        else:
            st.write("Upload an image to get AI-generated tips.")

# Set up the main app
st.title("Social Media Content Manager")

# Create three columns for image upload
col1, col2, col3 = st.columns(3)

# List to store uploaded images
uploaded_images = []

# Image upload for each column
with col1:
    uploaded_file1 = st.file_uploader("Upload Image 1", type=["png", "jpg", "jpeg"])
    if uploaded_file1 is not None:
        image = Image.open(uploaded_file1)
        uploaded_images.append(image)

with col2:
    uploaded_file2 = st.file_uploader("Upload Image 2", type=["png", "jpg", "jpeg"])
    if uploaded_file2 is not None:
        image = Image.open(uploaded_file2)
        uploaded_images.append(image)

with col3:
    uploaded_file3 = st.file_uploader("Upload Image 3", type=["png", "jpg", "jpeg"])
    if uploaded_file3 is not None:
        image = Image.open(uploaded_file3)
        uploaded_images.append(image)

# Limit to 3 images
if len(uploaded_images) > 3:
    st.warning("You can only upload up to 3 images. Please remove one before adding another.")
    uploaded_images = uploaded_images[:3]

# Create sections for each uploaded image
for i, image in enumerate(uploaded_images):
    st.subheader(f"Image {i+1}")
    create_section(image, f"hashtags{i+1}", f"captions{i+1}", f"tips{i+1}")

# If less than 3 images are uploaded, create empty sections
for i in range(len(uploaded_images), 3):
    st.subheader(f"Image {i+1}")
    create_section(None, f"hashtags{i+1}", f"captions{i+1}", f"tips{i+1}")