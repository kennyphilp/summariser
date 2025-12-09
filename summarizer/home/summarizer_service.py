"""
OpenAI service utilities for the AI Summarizer application.

This module provides utilities for interacting with OpenAI's API,
including model configuration and API call handling.
"""

import os
import logging
from typing import Dict, Any, Optional
import openai

from .constants import (
    OPENAI_API_KEY_ENV_VAR, MAX_TEXT_LENGTH, MAX_URL_CONTENT_LENGTH,
    DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS, GPT5_MAX_TOKENS,
    NEWER_MODELS, RESTRICTED_TEMP_MODELS, GPT5_NANO_MODELS, URL_REQUEST_TIMEOUT
)

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service class for handling OpenAI API interactions."""

    # Model configurations
    NEWER_MODELS = NEWER_MODELS
    RESTRICTED_TEMP_MODELS = RESTRICTED_TEMP_MODELS
    GPT5_NANO_MODELS = GPT5_NANO_MODELS

    # Default API parameters
    DEFAULT_TEMPERATURE = DEFAULT_TEMPERATURE
    DEFAULT_MAX_TOKENS = DEFAULT_MAX_TOKENS
    GPT5_MAX_TOKENS = GPT5_MAX_TOKENS

    @staticmethod
    def get_api_params(model_name: str, system_message: str, user_content: str) -> Dict[str, Any]:
        """Generate API parameters for OpenAI chat completion."""
        use_max_completion_tokens = any(model in model_name for model in OpenAIService.NEWER_MODELS)
        use_restricted_temp = any(model in model_name for model in OpenAIService.RESTRICTED_TEMP_MODELS)
        is_gpt5_nano = any(model in model_name for model in OpenAIService.GPT5_NANO_MODELS)

        api_params = {
            'model': model_name,
            'messages': [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content}
            ],
        }

        # Set temperature
        api_params['temperature'] = 1 if use_restricted_temp else OpenAIService.DEFAULT_TEMPERATURE

        # Set token limits
        if is_gpt5_nano:
            api_params['max_completion_tokens'] = OpenAIService.GPT5_MAX_TOKENS
        elif use_max_completion_tokens:
            api_params['max_completion_tokens'] = OpenAIService.DEFAULT_MAX_TOKENS
        else:
            api_params['max_tokens'] = OpenAIService.DEFAULT_MAX_TOKENS

        return api_params

    @staticmethod
    def call_openai_api(api_params: Dict[str, Any]) -> Optional[str]:
        """Make API call to OpenAI and return the response content."""
        try:
            client = openai.OpenAI(api_key=os.getenv(OPENAI_API_KEY_ENV_VAR))
            response = client.chat.completions.create(**api_params)
            content = response.choices[0].message.content

            if content and content.strip():
                return content.strip()

            logger.warning("Empty or whitespace-only response from OpenAI API")
            return None

        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {str(e)}")
            raise ValueError("Authentication error with AI service. Please check your API key configuration.")
        except openai.RateLimitError as e:
            logger.warning(f"OpenAI rate limit exceeded: {str(e)}")
            raise ValueError("Rate limit exceeded. Please try again in a few minutes.")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            error_msg = str(e).lower()
            if "max_tokens" in error_msg:
                raise ValueError("Model configuration error. Please contact support.")
            elif "context_length" in error_msg:
                raise ValueError("Text is too long for this model. Please try with shorter text.")
            else:
                raise ValueError("AI service temporarily unavailable. Please try again.")
        except Exception as e:
            logger.error(f"Unexpected OpenAI API error: {str(e)}", exc_info=True)
            raise ValueError("An unexpected error occurred. Our team has been notified.")


class ContentProcessor:
    """Utility class for processing different types of content."""

    MAX_TEXT_LENGTH = MAX_TEXT_LENGTH
    MAX_URL_CONTENT_LENGTH = MAX_URL_CONTENT_LENGTH

    @staticmethod
    def validate_text_length(text: str) -> None:
        """Validate text length and raise ValueError if too long."""
        if len(text) > ContentProcessor.MAX_TEXT_LENGTH:
            raise ValueError(f"Text is too long ({len(text):,} characters). Maximum allowed is {ContentProcessor.MAX_TEXT_LENGTH:,} characters.")

    @staticmethod
    def extract_text_from_url(url: str) -> str:
        """Extract text content from a URL."""
        import requests
        from bs4 import BeautifulSoup

        try:
            response = requests.get(url, timeout=URL_REQUEST_TIMEOUT)
            response.raise_for_status()
            content = response.text

            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)

            return text[:ContentProcessor.MAX_URL_CONTENT_LENGTH]

        except requests.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            raise ValueError(f"Error fetching the URL: {str(e)}")


class SummaryService:
    """Service class for handling summarization operations."""

    @staticmethod
    def summarize_text(text: str, model_name: str, system_message: str) -> str:
        """Summarize text using OpenAI API."""
        ContentProcessor.validate_text_length(text)

        api_params = OpenAIService.get_api_params(
            model_name=model_name,
            system_message=system_message,
            user_content=f"Summarize the following text:\n\n{text}"
        )

        summary = OpenAIService.call_openai_api(api_params)
        if not summary:
            raise ValueError("The AI model returned an empty response. Please try again.")

        return summary

    @staticmethod
    def summarize_url(url: str, model_name: str) -> str:
        """Summarize URL content using OpenAI API."""
        text = ContentProcessor.extract_text_from_url(url)

        system_message = "You are a helpful assistant that summarizes web page content."
        user_content = f"Summarize the following web page content:\n\n{text}"

        api_params = OpenAIService.get_api_params(
            model_name=model_name,
            system_message=system_message,
            user_content=user_content
        )

        summary = OpenAIService.call_openai_api(api_params)
        if not summary:
            raise ValueError("The AI model returned an empty response. Please try again.")

        return summary