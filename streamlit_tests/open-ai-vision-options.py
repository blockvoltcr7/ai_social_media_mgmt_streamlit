import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
import logging
import base64
import requests

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

def get_api_info():
    st.sidebar.header("API Options", divider='rainbow')
    api_choice = st.sidebar.radio("Choose API:", ("Gemini", "OpenAI Vision"))
    
    if api_choice == "Gemini":
        model = st.sidebar.radio("Choose LLM:", ("gemini-1.5-flash", "gemini-1.5-pro"))
        temp = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=1.0, step=0.25)
        topp = st.sidebar.slider("Top P:", min_value=0.0, max_value=1.0, value=0.94, step=0.01)
        max_tokens = st.sidebar.slider("Maximum Tokens:", min_value=100, max_value=8194, value=2000, step=100)
        return api_choice, model, temp, topp, max_tokens
    else:
        openai_model = st.sidebar.radio("Choose OpenAI Model:", ("gpt-4o", "gpt-4o-mini", "gpt-4-turbo"))
        max_tokens = st.sidebar.slider("Maximum Tokens:", min_value=100, max_value=300, value=300, step=50)
        return api_choice, openai_model, None, None, max_tokens

def process_image_gemini(image_file, prompt, gemini_model, temperature, top_p, max_tokens):
    try:
        logger.info(f"Using Gemini model: {gemini_model} with temperature {temperature}, top_p {top_p}, max_tokens {max_tokens}")
        with open(image_file.name, "wb") as f:
            f.write(image_file.getbuffer())
        uploaded_image = genai.upload_file(path=image_file.name)
        while uploaded_image.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_image = genai.get_file(uploaded_image.name)
        if uploaded_image.state.name == "FAILED":
            raise ValueError("Image processing failed")
        response = gemini_model.generate_content(
            [uploaded_image, prompt],
            generation_config={
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_tokens,
            },
            request_options={"timeout": 120}
        )
        os.remove(image_file.name)
        genai.delete_file(uploaded_image.name)
        return response.text if response and response.parts else None
    except Exception as e:
        logger.error(f"An error occurred while processing the image with Gemini: {str(e)}")
        if os.path.exists(image_file.name):
            os.remove(image_file.name)
        return None

def process_image_openai(image_file, prompt, openai_model, max_tokens):
    try:
        logger.info(f"Using OpenAI model: {openai_model} with max_tokens {max_tokens}")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        # Encode the image directly from the UploadedFile object
        base64_image = base64.b64encode(image_file.getvalue()).decode('utf-8')

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": openai_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": max_tokens
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_json = response.json()
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices'][0]['message']['content']
        else:
            logger.error(f"Unexpected response from OpenAI: {response_json}")
            return None
    except Exception as e:
        logger.error(f"An error occurred while processing the image with OpenAI: {str(e)}")
        return None

def analyze_image(section_id, image_file, api_choice, model, temperature, top_p, max_tokens):
    if image_file is not None:
        st.image(image_file, caption=f"Image {section_id}", use_column_width=True)
        
        prompt = st.text_area(f"Enter a prompt for Image {section_id}", key=f"prompt_{section_id}", height=100)
        
        analyze_button = st.button(f"Analyze Image {section_id}")
        analysis_result_key = f"analysis_{section_id}"

        if analyze_button and prompt:
            with st.spinner("Analyzing image..."):
                logger.info(f"Starting analysis for image {section_id} using API: {api_choice}, Model: {model}")
                if api_choice == "Gemini":
                    gemini_model = genai.GenerativeModel(model_name=model)
                    analysis = process_image_gemini(image_file, prompt, gemini_model, temperature, top_p, max_tokens)
                else:
                    analysis = process_image_openai(image_file, prompt, model, max_tokens)
                
                if analysis:
                    logger.info(f"Successfully analyzed image {section_id} with API: {api_choice}, Model: {model}")
                    # Store the analysis in session state, overwriting any previous response
                    st.session_state[analysis_result_key] = analysis

        # Display the analysis if it exists in session state
        if analysis_result_key in st.session_state:
            st.subheader(f"Image {section_id} Analysis")
            st.write(st.session_state[analysis_result_key])

def main():
    page_setup()
    api_choice, model, temperature, top_p, max_tokens = get_api_info()

    if api_choice == "Gemini":
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if GEMINI_API_KEY is None:
            st.error("GEMINI_API_KEY environment variable is not set")
            return
        genai.configure(api_key=GEMINI_API_KEY)
    else:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if OPENAI_API_KEY is None:
            st.error("OPENAI_API_KEY environment variable is not set")
            return

    # Image upload section
    st.header("Upload Images")
    uploaded_files = st.file_uploader("Choose up to 3 images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        num_files = len(uploaded_files)
        if num_files > 3:
            st.warning("You can only upload up to 3 images. Only the first 3 will be processed.")
            uploaded_files = uploaded_files[:3]
        
        cols = st.columns(3)
        for i, file in enumerate(uploaded_files):
            with cols[i]:
                analyze_image(i+1, file, api_choice, model, temperature, top_p, max_tokens)

    # Clear All button
    if st.button("🧹 Clear All"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == '__main__':
    main()
