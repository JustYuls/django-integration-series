"""Deliberately flawed settings for the AI structure review (Part 5). Never use these in a real project."""
from django.conf import settings

# A template that uses {% static %} without {% load static %} at the top.
BAD_TEMPLATE = "<link rel=\"stylesheet\" href=\"{% static 'css/site.css' %}\">"


def flawed_settings():
    engine = dict(settings.TEMPLATES[0])
    engine["DIRS"] = [settings.BASE_DIR / "template"]       # 2. typo
    apps = [a for a in settings.INSTALLED_APPS if a != "bookings"]   # 1. not registered
    return {
        "INSTALLED_APPS": apps,
        "TEMPLATES": [engine],
        "STATICFILES_DIRS": [settings.BASE_DIR / "statics"],  # 3. missing
    }
    # 5. DEBUG = True and ALLOWED_HOSTS = [] are already the project's development defaults.
