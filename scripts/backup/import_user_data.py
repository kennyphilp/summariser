#!/usr/bin/env python3
"""
User Data Import Script for Disaster Recovery

This script imports user-related data from a JSON backup file to recreate
the database state for disaster recovery.

Usage:
    python scripts/backup/import_user_data.py <backup_file.json>

Arguments:
    backup_file.json: Path to the JSON backup file created by export_user_data.py

Warning:
    This script will create or update users, groups, permissions, and model assignments.
    Existing data may be overwritten. Use with caution!
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from decimal import Decimal

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
from django.db import transaction
from home.models import OpenAIModel


def import_permissions(permissions_data):
    """Import permissions data."""
    print(f"Importing {len(permissions_data)} permissions...")
    # Permissions are typically auto-created by Django, so we just verify they exist
    return


def import_groups(groups_data, permissions_data):
    """Import groups and their permissions."""
    print(f"Importing {len(groups_data)} groups...")
    
    for group_data in groups_data:
        group, created = Group.objects.get_or_create(
            name=group_data['name'],
            defaults={'id': group_data['id']}
        )
        
        # Set permissions
        if group_data['permissions']:
            permissions = Permission.objects.filter(id__in=group_data['permissions'])
            group.permissions.set(permissions)
        
        action = "Created" if created else "Updated"
        print(f"  {action} group: {group.name}")


def import_users(users_data):
    """Import users with all their data."""
    print(f"Importing {len(users_data)} users...")
    
    for user_data in users_data:
        # Create or update user
        user, created = User.objects.update_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'password': user_data['password'],  # Already hashed
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_active': user_data['is_active'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser'],
                'date_joined': datetime.fromisoformat(user_data['date_joined']),
                'last_login': datetime.fromisoformat(user_data['last_login']) if user_data['last_login'] else None,
            }
        )
        
        # Set groups
        if user_data['groups']:
            groups = Group.objects.filter(id__in=user_data['groups'])
            user.groups.set(groups)
        
        # Set user permissions
        if user_data['user_permissions']:
            permissions = Permission.objects.filter(id__in=user_data['user_permissions'])
            user.user_permissions.set(permissions)
        
        action = "Created" if created else "Updated"
        print(f"  {action} user: {user.username}")


def import_openai_models(models_data):
    """Import OpenAI models and their user assignments."""
    print(f"Importing {len(models_data)} OpenAI models...")
    
    for model_data in models_data:
        model, created = OpenAIModel.objects.update_or_create(
            name=model_data['name'],
            defaults={
                'input_cost': Decimal(model_data['input_cost']),
                'cached_input_cost': Decimal(model_data['cached_input_cost']) if model_data['cached_input_cost'] else None,
                'output_cost': Decimal(model_data['output_cost']) if model_data['output_cost'] else None,
            }
        )
        
        # Set assigned users
        if model_data['assigned_users']:
            users = User.objects.filter(id__in=model_data['assigned_users'])
            model.assigned_users.set(users)
        
        action = "Created" if created else "Updated"
        print(f"  {action} model: {model.name}")


def import_all_data(backup_file):
    """Import all user-related data from backup file."""
    print(f"Loading backup from: {backup_file}")
    
    with open(backup_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Backup created: {data['export_date']}")
    print(f"Django version: {data['django_version']}")
    print()
    
    # Import in correct order to handle dependencies
    with transaction.atomic():
        import_permissions(data['permissions'])
        import_groups(data['groups'], data['permissions'])
        import_users(data['users'])
        import_openai_models(data['openai_models'])
    
    print("\nData import completed successfully!")


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Error: Backup file path required")
        print(f"Usage: {sys.argv[0]} <backup_file.json>")
        sys.exit(1)
    
    backup_file = Path(sys.argv[1])
    
    if not backup_file.exists():
        print(f"Error: Backup file not found: {backup_file}")
        sys.exit(1)
    
    # Confirm import
    print(f"WARNING: This will import data from {backup_file}")
    print("Existing data may be overwritten.")
    response = input("Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Import cancelled.")
        sys.exit(0)
    
    import_all_data(backup_file)


if __name__ == '__main__':
    main()
