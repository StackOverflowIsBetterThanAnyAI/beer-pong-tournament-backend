import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv("DJANGO_SU_NAME")
password = os.getenv("DJANGO_SU_PASSWORD")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password)
