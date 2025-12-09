from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import SupportedOpenAIModel

@admin.register(SupportedOpenAIModel)
class SupportedOpenAIModelAdmin(admin.ModelAdmin):
    """
    Admin interface for managing OpenAI models.

    Provides a user-friendly interface for administrators to:
    - View and edit model configurations
    - Manage cost settings
    - Assign models to users for access control
    """
    # Display these fields in the admin list view
    list_display = ('name', 'input_cost', 'cached_input_cost', 'output_cost')

    # Enable search functionality on model names
    search_fields = ('name',)

    # Use horizontal filter widget for many-to-many user assignments
    # This provides a better UX for selecting multiple users
    filter_horizontal = ('assigned_users',)


# Create a separate admin for managing user-model assignments
@admin.register(User.assigned_models.through)
class UserModelAssignmentAdmin(admin.ModelAdmin):
    """
    Admin interface for managing AI model assignments to users.

    This provides a dedicated interface for administrators to:
    - View all user-model assignments
    - Add new assignments
    - Remove existing assignments
    - Search and filter assignments
    """
    list_display = ('user', 'supportedopenaimodel', 'assignment_date')
    list_filter = ('user', 'supportedopenaimodel')
    search_fields = ('user__username', 'user__email', 'supportedopenaimodel__name')
    autocomplete_fields = ['user', 'supportedopenaimodel']

    def assignment_date(self, obj):
        """Display when the assignment was created."""
        return obj.id  # Using ID as a proxy for creation date
    assignment_date.short_description = 'Assignment ID'


class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model with AI model assignment management.

    Extends Django's default UserAdmin to include:
    - Display of assigned model count
    - Link to manage assignments via separate admin
    """
    # Add assigned_models to the list display
    list_display = BaseUserAdmin.list_display + ('assigned_models_count',)

    def assigned_models_count(self, obj):
        """Display the count of assigned models for this user."""
        return obj.assigned_models.count()
    assigned_models_count.short_description = 'Assigned Models'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)