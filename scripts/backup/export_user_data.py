#!/usr/bin/env python3
"""
User Data Export Script for Disaster Recovery

This script exports all user-related data from the Django SQLite database
including users, groups, permissions, and model assignments for disaster recovery.

Usage:
    python scripts/backup/export_user_data.py [output_file]

Arguments:
    output_file: Optional path to output JSON file (default: user_data_backup_YYYYMMDD_HHMMSS.json)

Output:
    JSON file containing all user-related data that can be used to recreate the database.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add the Django project to the path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
summarizer_dir = project_root / 'summarizer'

sys.path.insert(0, str(summarizer_dir))
os.chdir(str(summarizer_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'summarizer.settings')

import django
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from summarizer.home.models import SupportedOpenAIModel


def export_users():
    """Export all user data including passwords and metadata."""
    users = []
    for user in User.objects.all():
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password': user.password,  # Already hashed
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'groups': list(user.groups.values_list('id', flat=True)),
            'user_permissions': list(user.user_permissions.values_list('id', flat=True)),
        }
        users.append(user_data)
    return users


def export_groups():
    """Export all groups and their permissions."""
    groups = []
    for group in Group.objects.all():
        group_data = {
            'id': group.id,
            'name': group.name,
            'permissions': list(group.permissions.values_list('id', flat=True)),
        }
        groups.append(group_data)
    return groups


def export_permissions():
    """Export all permissions with their content types."""
    permissions = []
    for perm in Permission.objects.all():
        perm_data = {
            'id': perm.id,
            'name': perm.name,
            'codename': perm.codename,
            'content_type': {
                'app_label': perm.content_type.app_label,
                'model': perm.content_type.model,
            }
        }
        permissions.append(perm_data)
    return permissions


def export_openai_models():
    """Export OpenAI models and their user assignments."""
    models = []
    for model in SupportedOpenAIModel.objects.all():
        model_data = {
            'id': model.id,
            'name': model.name,
            'input_cost': str(model.input_cost),
            'cached_input_cost': str(model.cached_input_cost) if model.cached_input_cost else None,
            'output_cost': str(model.output_cost) if model.output_cost else None,
            'assigned_users': list(model.assigned_users.values_list('id', flat=True)),
        }
        models.append(model_data)
    return models


def export_all_data():
    """Export all user-related data."""
    print("Exporting user data...")
    
    data = {
        'export_date': datetime.now().isoformat(),
        'django_version': django.get_version(),
        'users': export_users(),
        'groups': export_groups(),
        'permissions': export_permissions(),
        'openai_models': export_openai_models(),
    }
    
    print(f"Exported {len(data['users'])} users")
    print(f"Exported {len(data['groups'])} groups")
    print(f"Exported {len(data['permissions'])} permissions")
    print(f"Exported {len(data['openai_models'])} OpenAI models")
    
    return data


def main():
    """Main entry point for the script."""
    # Determine output file
    if len(sys.argv) > 1:
        output_file = Path(sys.argv[1])
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = script_dir / f'user_data_backup_{timestamp}.json'
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Export data
    data = export_all_data()
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nData exported successfully to: {output_file}")
    print(f"File size: {output_file.stat().st_size:,} bytes")


if __name__ == '__main__':
    main()
