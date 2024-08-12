import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def page_setup():
    st.title("Social Media Content Manager")
    st.header("AI-Powered Image Analysis", divider="blue")
    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def get_llm_info():
    st.sidebar.header("AI Model Options", divider='rainbow')
    model = st.sidebar.radio("Choose LLM:", ("gemini-1.5-flash", "gemini-1.5-pro"))
    temp = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=1.0, step=0.25)
    topp = st.sidebar.slider("Top P:", min_value=0.0, max_value=1.0, value=0.94, step=0.01)
    maxtokens = st.sidebar.slider("Maximum Tokens:", min_value=100, max_value=8194, value=2000, step=100)
    return model, temp, topp, maxtokens

def process_image(image_file, prompt, gemini_model, temperature, top_p, max_tokens):
    try:
        # Save the uploaded image to a file
        with open(image_file.name, "wb") as f:
            f.write(image_file.getbuffer())
        
        # Upload the image to the generative AI service
        uploaded_image = genai.upload_file(path=image_file.name)
        
        # Wait for the image to be processed
        while uploaded_image.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_image = genai.get_file(uploaded_image.name)
        
        if uploaded_image.state.name == "FAILED":
            raise ValueError("Image processing failed")
        
        # Generate the content based on the image and the prompt
        response = gemini_model.generate_content(
            [uploaded_image, prompt],
            generation_config={
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_tokens,
            },
            request_options={"timeout": 120}
        )
        
        # Clean up the local file
        os.remove(image_file.name)
        genai.delete_file(uploaded_image.name)
        
        return response
    except Exception as e:
        logger.error(f"An error occurred while processing the image: {str(e)}")
        if os.path.exists(image_file.name):
            os.remove(image_file.name)
        return None

def analyze_image(section_id, image_file, gemini_model, temperature, top_p, max_tokens):
    if image_file is not None:
        st.image(image_file, caption=f"Image {section_id}", use_column_width=True)
        
        prompt = st.text_area(f"Enter a prompt for Image {section_id}", key=f"prompt_{section_id}", height=100)
        
        if st.button(f"Analyze Image {section_id}"):
            if prompt:
                with st.spinner("Analyzing image..."):
                    logger.info(f"Starting analysis for image {section_id}")
                    response = process_image(image_file, prompt, gemini_model, temperature, top_p, max_tokens)
                    if response and response.parts:
                        analysis = response.text
                        logger.info(f"Successfully analyzed image {section_id}")
                        
                        # Store the analysis in session state, overwriting any previous response
                        st.session_state[f"analysis_{section_id}"] = analysis

                    else:
                        st.error("Failed to analyze the image. Please try again.")
            else:
                st.warning("Please enter a prompt for the image.")
        
        # Display the analysis if it exists in session state
        if f"analysis_{section_id}" in st.session_state:
            st.subheader(f"Image {section_id} Analysis")
            st.write(st.session_state[f"analysis_{section_id}"])

def main():
    page_setup()
    model, temperature, top_p, max_tokens = get_llm_info()

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY is None:
        st.error("GEMINI_API_KEY environment variable is not set")
        return
    genai.configure(api_key=GEMINI_API_KEY)

    gemini_model = genai.GenerativeModel(model_name=model)

    # Image upload section
    st.header("Upload Images")
    uploaded_files = st.file_uploader("Choose up to 3 images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        num_files = len(uploaded_files)
        if num_files > 3:
            st.warning("You can only upload up to 3 images. Only the first 3 will be processed.")
            uploaded_files = uploaded_files[:3]
        
        cols = st.columns(num_files)
        for i, file in enumerate(uploaded_files):
            with cols[i]:
                analyze_image(i + 1, file, gemini_model, temperature, top_p, max_tokens)

    # Clear All button
    if st.button("🧹 Clear All"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == '__main__':
    main()
