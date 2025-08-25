# 📍 LOCAL - Create this new file
import os
import sys

# Add your project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nurseprepportal.settings')  # ⚠️ Change 'nurseprepportal' to your project name!

# Import and run Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()