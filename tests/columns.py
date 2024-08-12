import os
import streamlit as st

# Get the base directory of your project
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Construct the absolute paths for the images
image1_path = os.path.join(base_dir, "images", "image1.png")
image2_path = os.path.join(base_dir, "images", "image2.png")
image3_path = os.path.join(base_dir, "images", "image3.jpg")

# Debugging: Print the paths to verify
print(f"Image 1 Path: {image1_path}")
print(f"Image 2 Path: {image2_path}")
print(f"Image 3 Path: {image3_path}")

# Function to check if the file exists
def check_file_exists(file_path):
    if not os.path.exists(file_path):
        st.error(f"Error: File '{file_path}' not found.")
        return False
    return True

# Helper function to create a section
def create_section(image_path, caption, hashtags_key, captions_key, tips_key):
    if check_file_exists(image_path):
        st.image(image_path, caption=caption, use_column_width=True)
    
    # Use expanders for better organization
    with st.expander("Social Media Hashtags"):
        st.text_area("Enter hashtags here", height=100, key=hashtags_key)
    
    with st.expander("Captions"):
        st.text_area("Enter captions here", height=100, key=captions_key)
    
    with st.expander("AI Tips and Suggestions"):
        st.text_area("Generated tips and suggestions will appear here", height=100, key=tips_key)
    


# Set up the layout with three columns
col1, col2, col3 = st.columns(3)

# Column 1
with col1:
    create_section(image1_path, "Image 1", "hashtags1", "captions1", "tips1")

# Column 2
with col2:
    create_section(image2_path, "Image 2", "hashtags2", "captions2", "tips2")

# Column 3
with col3:
    create_section(image3_path, "Image 3", "hashtags3", "captions3", "tips3")
