# dump_fixed.py
import os
import sys
from django.core.management import execute_from_command_line
from django.core import serializers
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourproject.settings') # Change 'yourproject' to your actual project name
import django
django.setup()

# Dump the data and write it with explicit UTF-8 encoding
from django.core.management import call_command
with open('datadump.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', '--exclude=contenttypes', '--exclude=auth.Permission', '--natural-primary', '--natural-foreign', stdout=f)