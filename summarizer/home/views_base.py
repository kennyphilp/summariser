"""
Base views for summarization functionality.

This module provides base classes and utilities for handling
summarization requests with reduced code duplication.
"""

import logging
from typing import Optional, Dict, Any
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

from .models import OpenAIModel

logger = logging.getLogger(__name__)


class SummarizationMixin:
    """Mixin class providing common summarization functionality."""

    def get_user_models(self, request) -> tuple:
        """Get user's assigned models and check availability."""
        models = request.user.assigned_models.all().order_by('name')

        if not models.exists():
            logger.warning(f"User {request.user.username} has no assigned models available")
            messages.error(request, "No AI models are currently assigned to your account. Please contact an administrator.")
            return models, None

        selected_model = models.first().name
        return models, selected_model

    def validate_model_access(self, request, models, selected_model: str) -> bool:
        """Validate that the selected model is available to the user."""
        if not models.filter(name=selected_model).exists():
            logger.warning(f"User {request.user.username} attempted to use unauthorized model: {selected_model}")
            messages.error(request, "Selected model is not available for your account.")
            return False
        return True

    def handle_summarization_error(self, request, error: Exception, context: str) -> None:
        """Handle summarization errors with appropriate messaging."""
        try:
            # Re-raise ValueError messages as Django messages
            raise error
        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            logger.error(f"Unexpected error during {context}: {str(e)}", exc_info=True)
            messages.error(request, "An unexpected error occurred. Our team has been notified.")

    def get_base_context(self, models, selected_model: str, **kwargs) -> Dict[str, Any]:
        """Get base context for summarization views."""
        context = {
            'models': models,
            'selected_model': selected_model,
            'summary': None,
        }
        context.update(kwargs)
        return context


@method_decorator(login_required, name='dispatch')
class BaseSummarizationView(SummarizationMixin, View):
    """Base view class for summarization functionality."""

    template_name: str = None
    system_message: str = "You are a helpful assistant that summarizes text."

    def get(self, request):
        """Handle GET requests."""
        models, selected_model = self.get_user_models(request)
        context = self.get_base_context(models, selected_model)
        return render(request, self.template_name, context)

    def post(self, request):
        """Handle POST requests."""
        models, selected_model = self.get_user_models(request)
        if not models.exists():
            context = self.get_base_context(models, None)
            return render(request, self.template_name, context)

        # Get form data
        selected_model = request.POST.get('model', selected_model)

        if not self.validate_model_access(request, models, selected_model):
            context = self.get_base_context(models, selected_model)
            return render(request, self.template_name, context)

        try:
            # Process the input and generate summary
            summary = self.process_input(request, selected_model)
            logger.info(f"{self.__class__.__name__} completed successfully for user {request.user.username}")

        except Exception as e:
            self.handle_summarization_error(request, e, self.__class__.__name__.lower())
            summary = None

        context = self.get_base_context(models, selected_model, summary=summary)
        return render(request, self.template_name, context)

    def process_input(self, request, selected_model: str) -> str:
        """Process input and return summary. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement process_input method")