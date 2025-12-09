#!/usr/bin/env python3
"""
Test script to simulate URL summarization request
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.test.utils import get_runner

# Add the project directory to the Python path
sys.path.insert(0, '/Users/kenny.w.philp/training/djangotest/summarizer')
sys.path.insert(0, '/Users/kenny.w.philp/training/djangotest')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'summarizer.settings')
django.setup()

# Now we can import Django models and use the ORM
import importlib.util
spec = importlib.util.spec_from_file_location("home.models", "/Users/kenny.w.philp/training/djangotest/summarizer/home/models.py")
home_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(home_models)
OpenAIModel = home_models.OpenAIModel
from django.contrib.auth.models import User

def test_url_summary():
    # Create a test client
    client = Client()

    # Get or create a test user
    User = get_user_model()
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(username='testuser', password='testpass')

    # Get or create a test model
    try:
        model = OpenAIModel.objects.get(name='gpt-3.5-turbo')
    except OpenAIModel.DoesNotExist:
        model = OpenAIModel.objects.create(
            name='gpt-3.5-turbo', 
            input_cost=0.0015,  # $0.0015 per 1K tokens
            output_cost=0.002
        )
        user.assigned_models.add(model)

    # Log in the user
    client.login(username='testuser', password='testpass')

    # Make a POST request to the URL summary view
    response = client.post('/url-summary/', {
        'url': 'https://www.bbc.com/news',
        'model': 'gpt-3.5-turbo'
    })

    print(f"Response status: {response.status_code}")
    print(f"Response content length: {len(response.content)}")

    # Check if summary is in the response
    if b'summary =' in response.content:
        # Extract the debug line
        content_str = response.content.decode('utf-8')
        start = content_str.find('<!-- Debug: summary = "')
        if start != -1:
            end = content_str.find('" (length:', start)
            if end != -1:
                summary_value = content_str[start+23:end]
                print(f"Summary value: '{summary_value}'")

    return response

if __name__ == '__main__':
    test_url_summary()