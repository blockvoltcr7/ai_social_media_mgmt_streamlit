import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
import base64
import requests
import anthropic
from utils.logger import setup_logger

# Set up logging
logger = setup_logger()

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
    api_choice = st.sidebar.radio("Choose API:", ("Gemini", "OpenAI Vision", "Claude"))
    
    if api_choice == "Gemini":
        model = st.sidebar.radio("Choose LLM:", ("gemini-1.5-flash", "gemini-1.5-pro"))
        temp = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=1.0, step=0.25)
        topp = st.sidebar.slider("Top P:", min_value=0.0, max_value=1.0, value=0.94, step=0.01)
        max_tokens = st.sidebar.slider("Maximum Tokens:", min_value=100, max_value=8194, value=2000, step=100)
        logger.info(f"API choice: Gemini, Model: {model}, Temperature: {temp}, Top P: {topp}, Max Tokens: {max_tokens}")
        return api_choice, model, temp, topp, max_tokens
    elif api_choice == "OpenAI Vision":
        openai_model = st.sidebar.radio("Choose OpenAI Model:", ("gpt-4o", "gpt-4o-mini", "gpt-4-turbo"))
        max_tokens = st.sidebar.slider("Maximum Tokens:", min_value=100, max_value=300, value=300, step=50)
        logger.info(f"API choice: OpenAI Vision, Model: {openai_model}, Max Tokens: {max_tokens}")
        return api_choice, openai_model, None, None, max_tokens
    else:  # Claude
        claude_model = st.sidebar.radio("Choose Claude Model:", ("claude-3-5-sonnet-20240620", "claude-3-opus-20240229"))
        max_tokens = st.sidebar.slider("Maximum Tokens:", min_value=100, max_value=4096, value=1024, step=100)
        logger.info(f"API choice: Claude, Model: {claude_model}, Max Tokens: {max_tokens}")
        return api_choice, claude_model, None, None, max_tokens

def process_image_gemini(image_file, prompt, gemini_model, temperature, top_p, max_tokens):
    try:
        logger.info(f"Starting image processing with Gemini. Model: {gemini_model}, Temperature: {temperature}, Top P: {top_p}, Max Tokens: {max_tokens}")
        with open(image_file.name, "wb") as f:
            f.write(image_file.getbuffer())
        logger.debug(f"Image saved temporarily as {image_file.name}")
        uploaded_image = genai.upload_file(path=image_file.name)
        logger.debug(f"Image uploaded to Gemini API")
        while uploaded_image.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_image = genai.get_file(uploaded_image.name)
        if uploaded_image.state.name == "FAILED":
            raise ValueError("Image processing failed")
        logger.info("Image processed successfully by Gemini API")
        response = gemini_model.generate_content(
            [uploaded_image, prompt],
            generation_config={
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_tokens,
            },
            request_options={"timeout": 120}
        )
        logger.info("Content generated successfully by Gemini model")
        os.remove(image_file.name)
        genai.delete_file(uploaded_image.name)
        logger.debug("Temporary image file and uploaded image deleted")
        return response.text if response and response.parts else None
    except Exception as e:
        logger.error(f"An error occurred while processing the image with Gemini: {str(e)}")
        if os.path.exists(image_file.name):
            os.remove(image_file.name)
            logger.debug("Temporary image file deleted after error")
        return None

def process_image_openai(image_file, prompt, openai_model, max_tokens):
    try:
        logger.info(f"Starting image processing with OpenAI. Model: {openai_model}, Max Tokens: {max_tokens}")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable is not set")
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        base64_image = base64.b64encode(image_file.getvalue()).decode('utf-8')
        logger.debug("Image encoded to base64")

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

        logger.debug("Sending request to OpenAI API")
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_json = response.json()
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            logger.info("Successfully received response from OpenAI API")
            return response_json['choices'][0]['message']['content']
        else:
            logger.error(f"Unexpected response from OpenAI: {response_json}")
            return None
    except Exception as e:
        logger.error(f"An error occurred while processing the image with OpenAI: {str(e)}")
        return None

def process_image_claude(image_file, prompt, claude_model, max_tokens):
    try:
        logger.info(f"Using Claude model: {claude_model} with max_tokens {max_tokens}")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

        client = anthropic.Anthropic(api_key=api_key)

        # Determine the media type based on the file extension
        file_extension = image_file.name.split('.')[-1].lower()
        media_type = f"image/{file_extension}"
        if file_extension == 'jpg':
            media_type = "image/jpeg"

        # Encode the image
        base64_image = base64.b64encode(image_file.getvalue()).decode('utf-8')

        message = client.messages.create(
            model=claude_model,
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        return message.content[0].text
    except Exception as e:
        logger.error(f"An error occurred while processing the image with Claude: {str(e)}")
        return None

def analyze_image(section_id, image_file, api_choice, model, temperature, top_p, max_tokens):
    if image_file is not None:
        logger.info(f"Starting analysis for Image {section_id}")
        st.image(image_file, caption=f"Image {section_id}", use_column_width=True)
        
        prompt = st.text_area(f"Enter a prompt for Image {section_id}", key=f"prompt_{section_id}", height=100)
        
        analyze_button = st.button(f"Analyze Image {section_id}")
        analysis_result_key = f"analysis_{section_id}"

        if analyze_button and prompt:
            with st.spinner("Analyzing image..."):
                logger.info(f"Starting analysis for image {section_id}. API: {api_choice}, Model: {model}, Temperature: {temperature}, Top P: {top_p}, Max Tokens: {max_tokens}")
                if api_choice == "Gemini":
                    gemini_model = genai.GenerativeModel(model_name=model)
                    analysis = process_image_gemini(image_file, prompt, gemini_model, temperature, top_p, max_tokens)
                elif api_choice == "OpenAI Vision":
                    analysis = process_image_openai(image_file, prompt, model, max_tokens)
                else:  # Claude
                    analysis = process_image_claude(image_file, prompt, model, max_tokens)
                
                if analysis:
                    logger.info(f"Successfully analyzed image {section_id} with API: {api_choice}, Model: {model}")
                    # Store the analysis in session state, overwriting any previous response
                    st.session_state[analysis_result_key] = analysis
                else:
                    logger.warning(f"Analysis for image {section_id} returned no results")

        # Display the analysis if it exists in session state
        if analysis_result_key in st.session_state:
            st.subheader(f"Image {section_id} Analysis")
            st.write(st.session_state[analysis_result_key])
            logger.debug(f"Displayed analysis for Image {section_id}")

def main():
    page_setup()
    api_choice, model, temperature, top_p, max_tokens = get_api_info()

    if api_choice == "Gemini":
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if GEMINI_API_KEY is None:
            st.error("GEMINI_API_KEY environment variable is not set")
            return
        genai.configure(api_key=GEMINI_API_KEY)
    elif api_choice == "OpenAI Vision":
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if OPENAI_API_KEY is None:
            st.error("OPENAI_API_KEY environment variable is not set")
            return
    else:  # Claude
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        if ANTHROPIC_API_KEY is None:
            st.error("ANTHROPIC_API_KEY environment variable is not set")
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
