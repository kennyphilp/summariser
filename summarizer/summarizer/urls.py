"""
URL configuration for summarizer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Main URL configuration for the summarizer project
# Routes requests to appropriate apps and Django's built-in functionality
urlpatterns = [
    # Django admin interface - for managing models and users
    path('admin/', admin.site.urls),

    # Django authentication URLs - login, logout, password reset, etc.
    # Includes our custom login template and logout view
    path('accounts/', include('django.contrib.auth.urls')),

    # Home app URLs - main application functionality
    path('', include('home.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
