import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from utils.logger import setup_logger
from utils.image_processing import process_image
from utils.text_processing import process_text

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
    api_choice = st.sidebar.radio("Choose API:", ("Gemini", "OpenAI", "Claude"))
    
    if api_choice == "Gemini":
        model = st.sidebar.radio("Choose LLM:", ("gemini-1.5-flash", "gemini-1.5-pro"))
        temp = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=1.0, step=0.25)
        topp = st.sidebar.slider("Top P:", min_value=0.0, max_value=1.0, value=0.94, step=0.01)
        max_tokens = st.sidebar.slider("Maximum Tokens:", min_value=100, max_value=8194, value=200, step=50)
        logger.info(f"API choice: Gemini, Model: {model}, Temperature: {temp}, Top P: {topp}, Max Tokens: {max_tokens}")
        return api_choice, model, temp, topp, max_tokens
    elif api_choice == "OpenAI":
        openai_model = st.sidebar.radio("Choose OpenAI Model:", ("gpt-4o", "gpt-4o-mini", "gpt-4-turbo"))
        max_tokens = st.sidebar.slider("Maximum Tokens:", min_value=100, max_value=8000, value=300, step=50)
        logger.info(f"API choice: OpenAI, Model: {openai_model}, Max Tokens: {max_tokens}")
        return api_choice, openai_model, None, None, max_tokens
    else:  # Claude
        claude_model = st.sidebar.radio("Choose Claude Model:", ("claude-3-5-sonnet-20240620", "claude-3-opus-20240229"))
        max_tokens = st.sidebar.slider("Maximum Tokens:", min_value=100, max_value=4096, value=1024, step=100)
        logger.info(f"API choice: Claude, Model: {claude_model}, Max Tokens: {max_tokens}")
        return api_choice, claude_model, None, None, max_tokens

def generate_final_content(section_id, api_choice, model, temperature, top_p, max_tokens):
    analysis_result_key = f"analysis_{section_id}"
    caption = st.session_state[f"caption_{section_id}"]
    hashtags = st.session_state[f"hashtags_{section_id}"]
    
    content = f"""
    Original image analysis: {st.session_state[analysis_result_key]}
    
    User's caption: {caption}
    
    User's hashtags: {hashtags}
    """
    
    prompt = """
    Based on the provided information, generate a final, cohesive social media post that incorporates:
    1. Key insights from the image analysis
    2. The user's caption
    3. The provided hashtags
    
    The post should be:
    - Engaging and relevant to the image content
    - Optimized for social media engagement
    - Formatted appropriately for the platform (assume it's for Instagram)
    - No longer than 2200 characters (Instagram's caption limit)
    
    Structure the response as follows:
    1. Final Caption (including emojis if appropriate)
    2. Hashtags (list the most relevant hashtags, max 30)
    3. Brief explanation of how the final content incorporates the original analysis and user input
    """
    
    with st.spinner("Generating final content..."):
        final_result = process_text(content, prompt, api_choice, model, temperature, top_p, max_tokens)
        if final_result:
            st.subheader(f"Final Content for Image {section_id}")
            st.write(final_result)
            logger.info(f"Generated and displayed final content for Image {section_id}")
        else:
            st.error(f"Failed to generate final content for Image {section_id}")
            logger.error(f"Failed to generate final content for Image {section_id}")


def analyze_image(section_id, image_file, api_choice, model, temperature, top_p, max_tokens):
    if image_file is not None:
        logger.info(f"Starting analysis for Image {section_id}")
        st.image(image_file, caption=f"Image {section_id}", use_column_width=True)
        
        prompt = st.text_area(f"Enter a prompt for Image {section_id}", key=f"prompt_{section_id}", height=100)
        
        analyze_button = st.button(f"Analyze Image {section_id}")
        analysis_result_key = f"analysis_{section_id}"

        if analyze_button and prompt:
            with st.spinner("Analyzing image..."):
                logger.info(f"Starting analysis for image {section_id}. API: {api_choice}, Model: {model}")
                analysis = process_image(image_file, prompt, api_choice, model, temperature, top_p, max_tokens)
                
                if analysis:
                    logger.info(f"Successfully analyzed image {section_id} with API: {api_choice}, Model: {model}")
                    st.session_state[analysis_result_key] = analysis
                else:
                    logger.warning(f"Analysis for image {section_id} returned no results")
                    st.error("Failed to analyze the image. Please try again.")

        if analysis_result_key in st.session_state:
            st.subheader(f"Image {section_id} Analysis")
            st.write(st.session_state[analysis_result_key])
            
            caption = st.text_area(f"Enter your caption for Image {section_id}:", key=f"caption_{section_id}")
            hashtags = st.text_area(f"Enter hashtags (comma-separated) for Image {section_id}:", key=f"hashtags_{section_id}")
            
            if st.button(f"Generate Final Content for Image {section_id}"):
                generate_final_content(section_id, api_choice, model, temperature, top_p, max_tokens)



def main():
    page_setup()
    api_choice, model, temperature, top_p, max_tokens = get_api_info()

    if api_choice == "Gemini":
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if GEMINI_API_KEY is None:
            st.error("GEMINI_API_KEY environment variable is not set")
            return
        genai.configure(api_key=GEMINI_API_KEY)
    elif api_choice == "OpenAI":
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
