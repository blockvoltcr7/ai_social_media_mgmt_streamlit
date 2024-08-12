from .gemini_model import GeminiModel
from .openai_model import OpenAIModel
from .claude_model import ClaudeModel

class ModelFactory:
    @staticmethod
    def get_model(model_type: str):
        if model_type == "Gemini":
            return GeminiModel()
        elif model_type == "OpenAI Vision":
            return OpenAIModel()
        elif model_type == "Claude":
            return ClaudeModel()
        else:
            raise ValueError(f"Unsupported model type: {model_type}")