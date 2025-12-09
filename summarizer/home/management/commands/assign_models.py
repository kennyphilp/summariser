from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from home.models import OpenAIModel

class Command(BaseCommand):
    help = 'Assign AI models to users for access control'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to assign models to')
        parser.add_argument(
            '--models',
            nargs='+',
            help='Model names to assign (space-separated)',
            default=[]
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Assign all available models to the user'
        )
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Remove model assignments instead of adding'
        )

    def handle(self, *args, **options):
        username = options['username']
        model_names = options['models']
        assign_all = options['all']
        remove_models = options['remove']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
            return

        if assign_all:
            models = OpenAIModel.objects.all()
        else:
            models = OpenAIModel.objects.filter(name__in=model_names)
            
        if not models.exists():
            self.stdout.write(
                self.style.WARNING('No models found with the specified names')
            )
            return

        if remove_models:
            user.assigned_models.remove(*models)
            action = 'removed from'
        else:
            user.assigned_models.add(*models)
            action = 'assigned to'

        model_list = ', '.join([model.name for model in models])
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully {action} user "{username}": {model_list}'
            )
        )

        # Show current assignments
        current_models = user.assigned_models.all()
        if current_models.exists():
            current_list = ', '.join([model.name for model in current_models])
            self.stdout.write(f'Current assignments: {current_list}')
        else:
            self.stdout.write('User has no model assignments')