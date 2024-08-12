# AI-Powered Content Optimization Tool

## Overview

The AI-Powered Content Optimization Tool is designed to help users transform their images into engaging social media posts. Leveraging advanced AI models, this tool provides insights into image content, assists in creating captions and hashtags, and generates optimized final content for social media platforms like Instagram.

## Features

- **Image Analysis**: Analyze images using various AI models to extract key insights.
- **Caption and Hashtag Generation**: Create engaging captions and relevant hashtags for your images.
- **Final Content Generation**: Combine image analysis, captions, and hashtags to generate cohesive and optimized social media posts.
- **Multi-API Support**: Choose from multiple AI models including Gemini, OpenAI, Claude, and Meta-Llama.
- **PDF Document Querying**: Upload and analyze PDF documents.
- **Customizable AI Settings**: Adjust AI settings such as temperature, top_p, and max_tokens for personalized responses.
- **Session Management**: Save and clear session data as needed.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/ai-content-optimization-tool.git
    cd ai-content-optimization-tool
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    - Create a [`.env`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fsamisabir-idrissi%2Fcode%2Fpython%2Fai_social_media_mgmt_streamlit%2F.env%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/Users/samisabir-idrissi/code/python/ai_social_media_mgmt_streamlit/.env") file in the root directory.
    - Add your API keys and other environment variables:
        ```
        GEMINI_API_KEY=your_gemini_api_key
        OPENAI_API_KEY=your_openai_api_key
        TOGETHER_API_KEY=your_together_api_key
        ```

## Usage

1. Run the application:
    ```sh
    streamlit run 01_content_social_analysis.py
    ```

2. Open your web browser and navigate to the provided URL (usually `http://localhost:8501`).

3. Follow the on-screen instructions to upload images, generate captions and hashtags, and create final content.

## Project Structure

- [`01_content_social_analysis.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fsamisabir-idrissi%2Fcode%2Fpython%2Fai_social_media_mgmt_streamlit%2Fsrc%2Fpages%2F01_content_social_analysis.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/Users/samisabir-idrissi/code/python/ai_social_media_mgmt_streamlit/src/pages/01_content_social_analysis.py"): Main script for the content optimization tool.
- [`utils/logger.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fsamisabir-idrissi%2Fcode%2Fpython%2Fai_social_media_mgmt_streamlit%2Fsrc%2Futils%2Flogger.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/Users/samisabir-idrissi/code/python/ai_social_media_mgmt_streamlit/src/utils/logger.py"): Logger setup for the application.
- [`utils/image_processing.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fsamisabir-idrissi%2Fcode%2Fpython%2Fai_social_media_mgmt_streamlit%2Fsrc%2Futils%2Fimage_processing.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/Users/samisabir-idrissi/code/python/ai_social_media_mgmt_streamlit/src/utils/image_processing.py"): Functions for processing images using different AI models.
- [`utils/text_processing.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fsamisabir-idrissi%2Fcode%2Fpython%2Fai_social_media_mgmt_streamlit%2Fsrc%2Futils%2Ftext_processing.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/Users/samisabir-idrissi/code/python/ai_social_media_mgmt_streamlit/src/utils/text_processing.py"): Functions for processing text using different AI models.
- [`welcome.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fsamisabir-idrissi%2Fcode%2Fpython%2Fai_social_media_mgmt_streamlit%2Fsrc%2Fwelcome.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/Users/samisabir-idrissi/code/python/ai_social_media_mgmt_streamlit/src/welcome.py"): Script for the welcome page and initial setup.
- [`requirements.txt`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fsamisabir-idrissi%2Fcode%2Fpython%2Fai_social_media_mgmt_streamlit%2Frequirements.txt%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/Users/samisabir-idrissi/code/python/ai_social_media_mgmt_streamlit/requirements.txt"): List of required Python packages.

## How to Use

### Image Analysis

1. Upload images using the "Upload Images" section.
2. Choose the AI model and adjust settings in the sidebar.
3. Click the "Analyze Image" button to get insights about the image content.

### Caption and Hashtag Generation

1. Enter a caption and relevant hashtags for the analyzed image.
2. Click the "Generate Final Content" button to create a cohesive social media post.

### Final Content Generation

1. The AI combines the image analysis, your caption, and hashtags to generate an optimized post.
2. Save the generated content or clear all session data to start fresh with new images.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the web application framework.
- [OpenAI](https://openai.com/) for the AI models.
- [Together](https://together.xyz/) for the Meta-Llama model.
- [PyPDF2](https://pypdf2.readthedocs.io/) for PDF processing.

## Contact

For any questions or suggestions, please open an issue on the GitHub repository or contact the project maintainer at admin@samisabiridrissi.com