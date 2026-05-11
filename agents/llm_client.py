from typing import Optional
from openai import OpenAI
from utils.logger import setup_logger
from config import config

logger = setup_logger(__name__)

class OpenAIClient:
    def __init__(self):
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in configuration")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.default_model = config.DEFAULT_MODEL
        self.max_tokens = config.MAX_TOKENS

    def generate_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,  # unused for gpt-5.5; kept for call-site compat
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None
    ) -> str:
        used_model = model or self.default_model
        try:
            kwargs = dict(
                model=used_model,
                input=prompt,
                reasoning={"effort": "low"},
                max_output_tokens=max_tokens or self.max_tokens,
            )
            if system_message:
                kwargs["instructions"] = system_message
            response = self.client.responses.create(**kwargs)
            return response.output_text or ""
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return ""

    def generate_with_retry(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        import time
        for attempt in range(max_retries):
            result = self.generate_completion(prompt, **kwargs)
            if result:
                return result
            logger.warning(f"Empty response on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(2)
        logger.error(f"All {max_retries} attempts failed")
        return ""
