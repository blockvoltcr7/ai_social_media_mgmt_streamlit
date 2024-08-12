import os
from openai import OpenAI
from utils.logger import setup_logger

logger = setup_logger()

class OpenAIModel:
    def __init__(self, model_name, max_tokens):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def process_image(self, image_file, prompt):
        try:
            logger.info(f"Starting image processing with OpenAI. Model: {self.model_name}")
            
            # Read the image file
            image_data = image_file.getvalue()
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data.encode('base64').decode()}"}
                            }
                        ],
                    }
                ],
                max_tokens=self.max_tokens
            )
            
            logger.info("Content generated successfully by OpenAI model")
            return response.choices[0].message.content if response.choices else None
        except Exception as e:
            logger.error(f"An error occurred while processing the image with OpenAI: {str(e)}")
            return None
