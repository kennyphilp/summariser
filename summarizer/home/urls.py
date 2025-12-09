from django.urls import path
from django.shortcuts import render
from . import views

# URL patterns for the home app
# These routes handle the main application functionality
urlpatterns = [
    # Home page - landing page with app information
    path('', views.index, name='index'),

    # Text summarization page - requires authentication
    path('summary/', views.summary, name='summary'),

    # URL summarization page - requires authentication
    path('url-summary/', views.url_summary, name='url_summary'),

    # Custom logout page with confirmation
    path('logout/', views.logout_view, name='logout'),

    # User profile page - shows account details and permissions
    path('profile/', views.profile_view, name='profile'),

    # Text-to-Speech endpoints
    path('speak-summary/', views.speak_summary_text, name='speak_summary'),
    path('get-audio/', views.get_summary_audio, name='get_audio'),
    path('tts-engines/', views.get_tts_engines, name='tts_engines'),

    # Blog creation endpoint
    path('create-blog/', views.create_blog, name='create_blog'),

    # Temporary test URL for 404 page
    path('test-404/', lambda request: render(request, '404.html'), name='test_404'),
]