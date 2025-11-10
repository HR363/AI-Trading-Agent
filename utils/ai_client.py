"""
AI Client Wrapper
Provides a simple abstraction over different AI providers (OpenAI, Gemini)
so the rest of the code can call `AIClient().chat(messages)` and get a string
response.

This module uses:
- OpenAI (openai package) when Config.AI_PROVIDER == 'openai'
- Google Generative AI (google-generativeai) when Config.AI_PROVIDER == 'gemini'

The client is synchronous under the hood but exposes an async `chat` method
which runs the blocking calls in a thread.
"""

import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger

from config.config import Config


class AIClient:
    def __init__(self):
        self.provider = getattr(Config, "AI_PROVIDER", "openai").lower()
        logger.info(f"AI provider set to: {self.provider}")

        if self.provider == "openai":
            try:
                import openai
                self._openai = openai
                if Config.OPENAI_API_KEY:
                    self._openai.api_key = Config.OPENAI_API_KEY
            except Exception as e:
                logger.error("OpenAI package not available or failed to initialize")
                raise
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                self._genai = genai
                # Configure using API key if provided, otherwise rely on ADC or env
                if Config.GEMINI_API_KEY:
                    try:
                        self._genai.configure(api_key=Config.GEMINI_API_KEY)
                    except Exception:
                        # Older versions may use genai.configure(api_key=...)
                        pass
            except Exception as e:
                logger.error("google-generativeai package not available or failed to initialize")
                raise
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    async def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> str:
        """Send chat-style messages to the configured AI provider and return text.

        messages: list of {'role': 'system'|'user'|'assistant', 'content': '...'}
        model: optional model override
        kwargs: provider-specific options forwarded
        """

        if self.provider == "openai":
            return await asyncio.to_thread(self._chat_openai, messages, model, kwargs)
        elif self.provider == "gemini":
            return await asyncio.to_thread(self._chat_gemini, messages, model, kwargs)
        else:
            raise ValueError("Unsupported AI provider")

    def _chat_openai(self, messages: List[Dict[str, str]], model: Optional[str], options: Dict[str, Any]) -> str:
        client = self._openai
        model = model or Config.OPENAI_MODEL
        try:
            # Use ChatCompletion API
            resp = client.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=options.get("temperature", 0.1),
                max_tokens=options.get("max_tokens", 500),
            )
            return resp.choices[0].message["content"].strip()
        except Exception as e:
            logger.exception(f"OpenAI chat error: {e}")
            raise

    def _chat_gemini(self, messages: List[Dict[str, str]], model: Optional[str], options: Dict[str, Any]) -> str:
        genai = self._genai
        model = model or Config.GEMINI_MODEL
        try:
            # google-generativeai expects messages as list of dict with 'role' and 'content'
            resp = genai.chat.create(model=model, messages=messages)

            # Try multiple strategies to extract text from response (works across versions)
            # 1. resp.last
            if hasattr(resp, "last") and resp.last:
                return str(resp.last)

            # 2. resp.candidates -> candidate.content or candidate["content"]
            if hasattr(resp, "candidates") and resp.candidates:
                candidate = resp.candidates[0]
                if hasattr(candidate, "content"):
                    return candidate.content
                if isinstance(candidate, dict):
                    return candidate.get("content") or candidate.get("message", {}).get("content", "")

            # 3. resp.output or resp["output"]
            if hasattr(resp, "output"):
                out = resp.output
                # If output has 'text' or 'content'
                if isinstance(out, str):
                    return out
                if isinstance(out, dict):
                    return out.get("text") or out.get("content", "")

            # Fallback to string repr
            return str(resp)
        except Exception as e:
            logger.exception(f"Gemini chat error: {e}")
            raise


# Convenience singleton
_ai_client: Optional[AIClient] = None

def get_ai_client() -> AIClient:
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client
