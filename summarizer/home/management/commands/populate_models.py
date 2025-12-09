from django.core.management.base import BaseCommand
from home.models import OpenAIModel

class Command(BaseCommand):
    """
    Django management command to populate the database with OpenAI model pricing data.

    This command creates or updates OpenAIModel instances with current pricing
    information for various OpenAI models including GPT series, O1/O3 models,
    and specialized models like audio and image processing.

    Usage: python manage.py populate_models
    """
    help = 'Populate OpenAI models with costs'

    def handle(self, *args, **options):
        """
        Execute the command to populate OpenAI models.

        Iterates through predefined model data and creates database entries
        using get_or_create to avoid duplicates. Pricing data includes input,
        cached input, and output costs per token.
        """
        # Comprehensive list of OpenAI models with their pricing (in USD per million tokens)
        # Data structure: name, input_cost, cached_input_cost, output_cost
        models_data = [
            {'name': 'gpt-5.1', 'input': 1.25, 'cached': 0.125, 'output': 10.00},
            {'name': 'gpt-5', 'input': 1.25, 'cached': 0.125, 'output': 10.00},
            {'name': 'gpt-5-mini', 'input': 0.25, 'cached': 0.025, 'output': 2.00},
            {'name': 'gpt-5-nano', 'input': 0.05, 'cached': 0.005, 'output': 0.40},
            {'name': 'gpt-5.1-chat-latest', 'input': 1.25, 'cached': 0.125, 'output': 10.00},
            {'name': 'gpt-5-chat-latest', 'input': 1.25, 'cached': 0.125, 'output': 10.00},
            {'name': 'gpt-5.1-codex-max', 'input': 1.25, 'cached': 0.125, 'output': 10.00},
            {'name': 'gpt-5.1-codex', 'input': 1.25, 'cached': 0.125, 'output': 10.00},
            {'name': 'gpt-5-codex', 'input': 1.25, 'cached': 0.125, 'output': 10.00},
            {'name': 'gpt-5-pro', 'input': 15.00, 'cached': None, 'output': 120.00},
            {'name': 'gpt-4.1', 'input': 2.00, 'cached': 0.50, 'output': 8.00},
            {'name': 'gpt-4.1-mini', 'input': 0.40, 'cached': 0.10, 'output': 1.60},
            {'name': 'gpt-4.1-nano', 'input': 0.10, 'cached': 0.025, 'output': 0.40},
            {'name': 'gpt-4o', 'input': 2.50, 'cached': 1.25, 'output': 10.00},
            {'name': 'gpt-4o-2024-05-13', 'input': 5.00, 'cached': None, 'output': 15.00},
            {'name': 'gpt-4o-mini', 'input': 0.15, 'cached': 0.075, 'output': 0.60},
            {'name': 'gpt-realtime', 'input': 4.00, 'cached': 0.40, 'output': 16.00},
            {'name': 'gpt-realtime-mini', 'input': 0.60, 'cached': 0.06, 'output': 2.40},
            {'name': 'gpt-4o-realtime-preview', 'input': 5.00, 'cached': 2.50, 'output': 20.00},
            {'name': 'gpt-4o-mini-realtime-preview', 'input': 0.60, 'cached': 0.30, 'output': 2.40},
            {'name': 'gpt-audio', 'input': 2.50, 'cached': None, 'output': 10.00},
            {'name': 'gpt-audio-mini', 'input': 0.60, 'cached': None, 'output': 2.40},
            {'name': 'gpt-4o-audio-preview', 'input': 2.50, 'cached': None, 'output': 10.00},
            {'name': 'gpt-4o-mini-audio-preview', 'input': 0.15, 'cached': None, 'output': 0.60},
            {'name': 'o1', 'input': 15.00, 'cached': 7.50, 'output': 60.00},
            {'name': 'o1-pro', 'input': 150.00, 'cached': None, 'output': 600.00},
            {'name': 'o3-pro', 'input': 20.00, 'cached': None, 'output': 80.00},
            {'name': 'o3', 'input': 2.00, 'cached': 0.50, 'output': 8.00},
            {'name': 'o3-deep-research', 'input': 10.00, 'cached': 2.50, 'output': 40.00},
            {'name': 'o4-mini', 'input': 1.10, 'cached': 0.275, 'output': 4.40},
            {'name': 'o4-mini-deep-research', 'input': 2.00, 'cached': 0.50, 'output': 8.00},
            {'name': 'o3-mini', 'input': 1.10, 'cached': 0.55, 'output': 4.40},
            {'name': 'o1-mini', 'input': 1.10, 'cached': 0.55, 'output': 4.40},
            {'name': 'gpt-5.1-codex-mini', 'input': 0.25, 'cached': 0.025, 'output': 2.00},
            {'name': 'codex-mini-latest', 'input': 1.50, 'cached': 0.375, 'output': 6.00},
            {'name': 'gpt-5-search-api', 'input': 1.25, 'cached': 0.125, 'output': 10.00},
            {'name': 'gpt-4o-mini-search-preview', 'input': 0.15, 'cached': None, 'output': 0.60},
            {'name': 'gpt-4o-search-preview', 'input': 2.50, 'cached': None, 'output': 10.00},
            {'name': 'computer-use-preview', 'input': 3.00, 'cached': None, 'output': 12.00},
            {'name': 'gpt-image-1', 'input': 5.00, 'cached': 1.25, 'output': None},
            {'name': 'gpt-image-1-mini', 'input': 2.00, 'cached': 0.20, 'output': None},
        ]

        # Create or update each model in the database
        for data in models_data:
            OpenAIModel.objects.get_or_create(
                name=data['name'],
                defaults={
                    'input_cost': data['input'],
                    'cached_input_cost': data['cached'],
                    'output_cost': data['output'],
                }
            )

        # Report successful completion
        self.stdout.write(self.style.SUCCESS('Successfully populated OpenAI models'))