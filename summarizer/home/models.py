from django.db import models
from django.contrib.auth.models import User

class OpenAIModel(models.Model):
    """
    Model representing an OpenAI language model with cost information and user assignments.

    This model stores information about different OpenAI models available for text summarization,
    including their pricing structure and which users have access to them.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The OpenAI model identifier (e.g., 'gpt-3.5-turbo', 'gpt-4')"
    )
    input_cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text="Cost per million input tokens in USD"
    )
    cached_input_cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Cost per million cached input tokens in USD (optional)"
    )
    output_cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Cost per million output tokens in USD (optional)"
    )
    assigned_users = models.ManyToManyField(
        User,
        blank=True,
        related_name='assigned_models',
        help_text="Users who can access this model for summarization"
    )

    def __str__(self):
        """Return the model name as the string representation."""
        return self.name

    class Meta:
        """Meta options for the OpenAIModel."""
        verbose_name = "OpenAI Model"
        verbose_name_plural = "OpenAI Models"
        ordering = ['name']