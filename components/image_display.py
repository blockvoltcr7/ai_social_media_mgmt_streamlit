import streamlit as st
from PIL import Image

def display_images(image):
    st.image(image, caption='Uploaded Image', use_column_width=True)
