from django.core.management.base import BaseCommand, CommandError
from mlpipe.models import Pipe
from django.contrib.auth.models import User; 
import os
from mlpipe.settings  import * 
import mlpipe.apps.core as mlpipe_core 
from django.core.management import call_command
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'create user mlpipe and group mlpipe'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--job_id', type = int, default=-1)

    def _ensure_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def handle(self, *args, **options):
        #create database
        call_command('makemigrations', 'mlpipe')
        call_command('migrate','mlpipe')

        #create user and group
        try:
            new_group, created = Group.objects.get_or_create(name='mlpipe')
            User.objects.create_superuser('mlpipe', 'mlpipe@example.com', 'mlpipeadmin')
        except:
            pass

        #create directories
        self._ensure_dir(MLPIPE_ROOT)
        self._ensure_dir(working_directory)
        self._ensure_dir(cached_data_directory)
        self._ensure_dir(storage_directory)
        self._ensure_dir(resource_directory)


        #create core app
        app_path =  os.path.dirname(mlpipe_core.__file__)
        app_name = 'core'
        if os.path.exists(app_path):
            os.symlink(app_path, os.path.join(resource_directory, app_name))

