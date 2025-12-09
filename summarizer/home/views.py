import os
import json
import uuid
import logging
from typing import Dict, Any
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
import openai
from .models import OpenAIModel
from .tts_utils import speak_summary, get_summary_audio_file, tts_manager, BrowserTTSTTS
from .summarizer_service import SummaryService
from .views_base import BaseSummarizationView

# Get logger for this module
logger = logging.getLogger(__name__)

def index(request):
    """
    Render the home page of the AI Text Summarizer application.

    This view displays the landing page with information about the application
    and a call-to-action to start summarizing text.
    """
    logger.info("Home page accessed")
    return render(request, 'home/index.html')

@login_required
def summary(request):
    """
    Handle text summarization requests.

    This view processes POST requests containing text to summarize using OpenAI's API.
    It filters available models to show only those assigned to the current user.
    """
    return TextSummarizationView.as_view()(request)


class TextSummarizationView(BaseSummarizationView):
    """View for text summarization."""

    template_name = 'home/summary.html'
    system_message = "You are a helpful assistant that summarizes text."

    def process_input(self, request, selected_model: str) -> str:
        """Process text input and return summary."""
        text = request.POST.get('text', '').strip()
        if not text:
            raise ValueError("Please enter some text to summarize.")

        logger.info(f"Summarization request received - User: {request.user.username}, "
                   f"Text length: {len(text)}, Model: {selected_model}")

        return SummaryService.summarize_text(text, selected_model, self.system_message)

@login_required
def url_summary(request):
    """
    Handle URL summarization requests.

    This view processes POST requests containing a URL to summarize using OpenAI's API.
    It fetches the content from the URL and summarizes it.
    """
    return URLSummarizationView.as_view()(request)


class URLSummarizationView(BaseSummarizationView):
    """View for URL summarization."""

    template_name = 'home/url_summary.html'

    def get_base_context(self, models, selected_model: str, **kwargs) -> Dict[str, Any]:
        """Get base context with URL support."""
        context = super().get_base_context(models, selected_model, **kwargs)
        context['url'] = kwargs.get('url', '')
        return context

    def process_input(self, request, selected_model: str) -> str:
        """Process URL input and return summary."""
        url = request.POST.get('url', '').strip()
        if not url:
            raise ValueError("Please enter a valid URL.")

        logger.info(f"URL summarization request received - User: {request.user.username}, "
                   f"URL: {url}, Model: {selected_model}")

        return SummaryService.summarize_url(url, selected_model)

@login_required
def logout_view(request):
    """
    Handle user logout with confirmation.

    GET request: Display logout confirmation page
    POST request: Process logout and redirect to home page

    This provides a better user experience by confirming logout intent
    rather than logging out immediately.
    """
    if request.method == 'POST':
        username = request.user.username
        logout(request)
        logger.info(f"User {username} logged out successfully")
        messages.success(request, "You have been successfully logged out.")
        return redirect('index')

    logger.debug(f"User {request.user.username} accessed logout confirmation page")
    return render(request, 'home/logout.html')

@login_required
def profile_view(request):
    """
    Display user profile information and assigned permissions.

    Shows comprehensive user account details including:
    - Basic account information (username, email, names)
    - Account type and status
    - Join date and last login
    - Assigned AI models (permissions)

    Superusers see a notice about having access to all models.
    """
    user = request.user
    assigned_models = user.assigned_models.all().order_by('name')

    logger.info(f"User {user.username} accessed profile page")

    context = {
        'user': user,
        'assigned_models': assigned_models,
        'is_superuser': user.is_superuser,
    }

    return render(request, 'home/profile.html', context)


@login_required
@require_POST
def speak_summary_text(request):
    """
    AJAX endpoint to speak summary text using TTS.

    Expects POST data with 'text' and optional 'engine' parameters.
    Returns JSON response indicating success/failure.
    """
    text = request.POST.get('text', '').strip()
    engine = request.POST.get('engine', 'pyttsx3')

    if not text:
        return JsonResponse({'success': False, 'error': 'No text provided'})

    logger.info(f"User {request.user.username} requested TTS for summary (engine: {engine})")

    try:
        success = speak_summary(text, engine)
        if success:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': f'TTS engine "{engine}" failed or not available'})
    except Exception as e:
        logger.error(f"TTS error for user {request.user.username}: {str(e)}")
        return JsonResponse({'success': False, 'error': 'TTS service error'})


@login_required
def get_summary_audio(request):
    """
    Generate and return audio file for summary text.

    Expects GET parameters 'text' and optional 'engine'.
    Returns audio file as HTTP response.
    """
    text = request.GET.get('text', '').strip()
    engine = request.GET.get('engine', 'google')

    if not text:
        return HttpResponse('No text provided', status=400)

    logger.info(f"User {request.user.username} requested audio file for summary (engine: {engine})")

    try:
        audio_file = get_summary_audio_file(text, engine)
        if audio_file and os.path.exists(audio_file):
            # Return audio file
            with open(audio_file, 'rb') as f:
                response = HttpResponse(f.read(), content_type='audio/mpeg')
                response['Content-Disposition'] = 'attachment; filename="summary.mp3"'
            # Clean up temp file
            os.unlink(audio_file)
            return response
        else:
            return HttpResponse(f'Audio generation failed with engine "{engine}"', status=500)
    except Exception as e:
        logger.error(f"Audio generation error for user {request.user.username}: {str(e)}")
        return HttpResponse('Audio generation error', status=500)


@login_required
def create_blog(request):
    """
    Create a blog post from a summary using AI.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})

    try:
        data = json.loads(request.body)
        summary = data.get('summary', '').strip()
        source_url = data.get('source_url', '')

        if not summary:
            return JsonResponse({'success': False, 'error': 'No summary provided'})

        # Generate blog content using OpenAI
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Create blog post prompt
        blog_prompt = f"""
        Create an engaging blog post based on this summary. The blog post should be well-structured with:
        1. An attention-grabbing title
        2. An introduction paragraph
        3. 2-3 main body paragraphs expanding on key points
        4. A conclusion
        5. Include relevant keywords for SEO

        Summary to convert to blog post:
        {summary}

        Format the response as a complete HTML blog post with proper heading tags.
        """

        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a professional blog writer who creates engaging, well-structured blog posts."},
                {"role": "user", "content": blog_prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        blog_content = response.choices[0].message.content.strip()

        # Generate unique filename
        filename = f"blog_{request.user.username}_{uuid.uuid4().hex[:8]}.html"
        filepath = os.path.join(settings.MEDIA_ROOT, 'blogs', filename)

        # Ensure blogs directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Create HTML blog post
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Generated Blog - {request.user.username}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        p {{
            color: #555;
            margin-bottom: 15px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #777;
            font-size: 0.9em;
            text-align: center;
        }}
        .source {{
            font-style: italic;
            color: #666;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        {blog_content}
        <div class="source">
            <p>Source: <a href="{source_url}" target="_blank">{source_url}</a></p>
            <p>Generated by AI Text Summarizer</p>
        </div>
        <div class="footer">
            <p>Generated on {timezone.now().strftime('%B %d, %Y')} by {request.user.username}</p>
        </div>
    </div>
</body>
</html>"""

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Return success response
        blog_url = f"{request.scheme}://{request.get_host()}/media/blogs/{filename}"
        return JsonResponse({
            'success': True,
            'blog_url': blog_url,
            'message': 'Blog post created successfully!'
        })

    except Exception as e:
        logger.error(f"Blog creation error for user {request.user.username}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_tts_engines(request):
    """
    Return available TTS engines as JSON.

    Returns JSON object with engine names and availability status.
    """
    engines = tts_manager.get_available_engines()
    return JsonResponse({
        'engines': engines,
        'browser_tts_js': BrowserTTSTTS.get_javascript()
    })