"""
Constants and configuration values for the AI Summarizer application.
"""

# API Configuration
OPENAI_API_KEY_ENV_VAR = 'OPENAI_API_KEY'

# Content Limits
MAX_TEXT_LENGTH = 50000
MAX_URL_CONTENT_LENGTH = 10000

# API Parameters
DEFAULT_TEMPERATURE = 0.5
DEFAULT_MAX_TOKENS = 150
GPT5_MAX_TOKENS = 300

# Model Lists
NEWER_MODELS = ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o-mini', 'gpt-5-nano']
RESTRICTED_TEMP_MODELS = ['gpt-5-nano']
GPT5_NANO_MODELS = ['gpt-5-nano']

# Request Timeouts
URL_REQUEST_TIMEOUT = 10

# Logging
LOG_FORMAT = '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
SIMPLE_LOG_FORMAT = '%(levelname)s %(message)s'