import google.generativeai as genai
import os
import time
from utils.logger import setup_logger

logger = setup_logger()

class GeminiModel:
    def __init__(self, model_name, temperature, top_p, max_tokens):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.model = genai.GenerativeModel(model_name=model_name)

    def process_image(self, image_file, prompt):
        try:
            logger.info(f"Starting image processing with Gemini. Model: {self.model_name}")
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
            response = self.model.generate_content(
                [uploaded_image, prompt],
                generation_config={
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "max_output_tokens": self.max_tokens,
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
