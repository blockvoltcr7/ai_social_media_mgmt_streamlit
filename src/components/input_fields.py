import streamlit as st

def create_input_fields():
    description = st.text_area("Description", "")
    caption = st.text_input("Caption", "")
    hashtags = st.text_input("Hashtags", "")
    return description, caption, hashtags
