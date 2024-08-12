import base64
import os
import time
import requests
import google.generativeai as genai
import anthropic
from utils.logger import setup_logger

logger = setup_logger()

def process_image(image_file, prompt, api_choice, model, temperature=None, top_p=None, max_tokens=None):
    if api_choice == "Gemini":
        return process_image_gemini(image_file, prompt, model, temperature, top_p, max_tokens)
    elif api_choice == "OpenAI":
        return process_image_openai(image_file, prompt, model, max_tokens)
    elif api_choice == "Claude":
        return process_image_claude(image_file, prompt, model, max_tokens)
    elif api_choice == "Meta-Llama":
        logger.info("Meta-Llama selected, defaulting to Gemini Vision for image processing")
        return process_image_gemini(image_file, prompt, model, temperature, top_p, max_tokens)
    else:
        logger.error(f"Unsupported API choice: {api_choice}")
        return None

def process_image_gemini(image_file, prompt, model, temperature, top_p, max_tokens):
    try:
        logger.info(f"Starting image processing with Gemini. Model: {model}, Temperature: {temperature}, Top P: {top_p}, Max Tokens: {max_tokens}")
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
        gemini_model = genai.GenerativeModel(model_name=model)
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

def process_image_openai(image_file, prompt, model, max_tokens):
    try:
        logger.info(f"Starting image processing with OpenAI. Model: {model}, Max Tokens: {max_tokens}")
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
            "model": model,
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

def process_image_claude(image_file, prompt, model, max_tokens):
    try:
        logger.info(f"Using Claude model: {model} with max_tokens {max_tokens}")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

        client = anthropic.Anthropic(api_key=api_key)

        file_extension = image_file.name.split('.')[-1].lower()
        media_type = f"image/{file_extension}"
        if file_extension == 'jpg':
            media_type = "image/jpeg"

        base64_image = base64.b64encode(image_file.getvalue()).decode('utf-8')

        message = client.messages.create(
            model=model,
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
