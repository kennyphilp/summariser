from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import OpenAIModel
import os
import openai

class Command(BaseCommand):
    help = 'Health check for the AI Text Summarizer application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix common issues'
        )

    def handle(self, *args, **options):
        fix_issues = options['fix']
        issues_found = []

        self.stdout.write(self.style.SUCCESS('=== AI Text Summarizer Health Check ==='))
        
        # Check environment variables
        self.stdout.write('\n1. Checking Environment Configuration...')
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            issues_found.append('OPENAI_API_KEY not set')
            self.stdout.write(self.style.ERROR('   ✗ OPENAI_API_KEY not configured'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ OPENAI_API_KEY configured'))

        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or secret_key == 'your-secret-key-here':
            issues_found.append('SECRET_KEY not properly set')
            self.stdout.write(self.style.ERROR('   ✗ SECRET_KEY not properly configured'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ SECRET_KEY configured'))

        # Check database
        self.stdout.write('\n2. Checking Database...')
        try:
            user_count = User.objects.count()
            model_count = OpenAIModel.objects.count()
            self.stdout.write(self.style.SUCCESS(f'   ✓ Database accessible ({user_count} users, {model_count} models)'))
        except Exception as e:
            issues_found.append(f'Database error: {e}')
            self.stdout.write(self.style.ERROR(f'   ✗ Database error: {e}'))

        # Check OpenAI API
        self.stdout.write('\n3. Checking OpenAI API...')
        if openai_key:
            try:
                client = openai.OpenAI(api_key=openai_key)
                # Test with a minimal request
                response = client.models.list()
                self.stdout.write(self.style.SUCCESS('   ✓ OpenAI API accessible'))
            except Exception as e:
                issues_found.append(f'OpenAI API error: {e}')
                self.stdout.write(self.style.ERROR(f'   ✗ OpenAI API error: {e}'))
        
        # Check model assignments
        self.stdout.write('\n4. Checking Model Assignments...')
        users_without_models = User.objects.filter(assigned_models__isnull=True, is_superuser=False)
        if users_without_models.exists():
            count = users_without_models.count()
            issues_found.append(f'{count} users have no model assignments')
            self.stdout.write(self.style.WARNING(f'   ⚠ {count} users have no model assignments'))
            
            if fix_issues and OpenAIModel.objects.exists():
                # Assign a default model to users without assignments
                default_model = OpenAIModel.objects.first()
                for user in users_without_models:
                    user.assigned_models.add(default_model)
                self.stdout.write(self.style.SUCCESS(f'   ✓ Fixed: Assigned {default_model.name} to {count} users'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ All users have model assignments'))

        # Check log directory
        self.stdout.write('\n5. Checking Logging...')
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            issues_found.append('Log directory missing')
            self.stdout.write(self.style.ERROR('   ✗ Log directory missing'))
            if fix_issues:
                os.makedirs(log_dir, exist_ok=True)
                self.stdout.write(self.style.SUCCESS('   ✓ Fixed: Created log directory'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ Log directory exists'))

        # Summary
        self.stdout.write(f'\n=== Health Check Summary ===')
        if issues_found:
            self.stdout.write(self.style.ERROR(f'Found {len(issues_found)} issue(s):'))
            for issue in issues_found:
                self.stdout.write(f'  - {issue}')
            if not fix_issues:
                self.stdout.write('\nRun with --fix to attempt automatic fixes')
        else:
            self.stdout.write(self.style.SUCCESS('✓ All checks passed! Application is healthy.'))