import streamlit as st
import os

def upload_image():
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        # Create the uploads directory if it doesn't exist
        os.makedirs("data/uploads", exist_ok=True)
        
        # Save the file
        with open(os.path.join("data/uploads", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return uploaded_file
    return None
