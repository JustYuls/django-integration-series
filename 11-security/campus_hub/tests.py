import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.test import TestCase
from django.urls import resolve, reverse

BASE_DIR = Path(settings.BASE_DIR)
PRODUCTION = {"DJANGO_DEBUG": "0", "DJANGO_SECRET_KEY": "k9Xv2mQ7pLz4TnR8sW1bYc6HdF3gJ5uA0eKq9VtZxN2oMiPwBr4Cy7LaDh1Ef8SG", "DJANGO_ALLOWED_HOSTS": "campus.example.com",
              "EMAIL_HOST": "smtp.example.com"}


def run_manage(*args, **env):
    """Run manage.py in a fresh process with a production-like environment."""
    full_env = {k: v for k, v in os.environ.items() if not k.startswith(("DJANGO_", "EMAIL_"))}
    full_env.update(env)
    return subprocess.run([sys.executable, "manage.py", *args], cwd=BASE_DIR, env=full_env, capture_output=True, text=True, timeout=120)


class ProjectSetupTests(TestCase):
    def test_system_check_passes(self):
        call_command("check")

    def test_default_apps_are_installed(self):
        for app in ("admin", "auth", "contenttypes", "sessions", "messages", "staticfiles"):
            self.assertIn(f"django.contrib.{app}", settings.INSTALLED_APPS)

    def test_project_uses_sqlite_and_philippine_time(self):
        self.assertEqual(connection.vendor, "sqlite")
        self.assertEqual(settings.TIME_ZONE, "Asia/Manila")

    def test_builtin_migrations_were_applied(self):
        self.assertTrue(MigrationRecorder.Migration.objects.filter(app="auth", name="0001_initial").exists())

    def test_admin_login_page_loads(self):
        self.assertEqual(self.client.get("/admin/login/").status_code, 200)

    def test_all_four_of_our_apps_are_registered(self):
        for app in ("accounts", "rooms", "bookings", "holiday_api"):
            self.assertIn(app, settings.INSTALLED_APPS)


class RoutingTests(TestCase):
    def test_the_home_page_and_the_anonymous_navbar(self):
        response = self.client.get("/")
        self.assertContains(response, 'href="/rooms/"')
        self.assertContains(response, "Log in")
        self.assertContains(response, "Sign up")
        self.assertNotContains(response, "New booking")

    def test_each_app_owns_a_namespace_and_a_prefix(self):
        self.assertEqual(reverse("rooms:room_list"), "/rooms/")
        self.assertEqual(reverse("bookings:booking_list"), "/bookings/")
        self.assertEqual(reverse("holiday_api:holiday_list", args=[2027]), "/holidays/2027/")
        self.assertEqual(reverse("login"), "/accounts/login/")
        self.assertEqual(resolve("/bookings/new/").app_names, ["bookings"])

    def test_tests_never_call_the_holidays_network_by_default(self):
        self.assertFalse(settings.HOLIDAYS_ENABLED)


class SecuritySettingsTests(TestCase):
    """These run manage.py in a separate process, with a production-like environment."""

    def test_check_deploy_has_issues_with_the_development_defaults(self):
        result = run_manage("check", "--deploy")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("security.W018", result.stdout + result.stderr)

    def test_check_deploy_is_clean_in_a_production_environment(self):
        result = run_manage("check", "--deploy", "--fail-level", "WARNING", **PRODUCTION)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("no issues", result.stdout + result.stderr)

    def test_production_refuses_to_start_without_a_secret_key(self):
        env = {k: v for k, v in PRODUCTION.items() if k != "DJANGO_SECRET_KEY"}
        result = run_manage("check", **env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY", result.stderr)

    def test_production_turns_on_https_and_secure_cookies(self):
        code = ("import django, os; os.environ['DJANGO_SETTINGS_MODULE']='campus_hub.settings'; django.setup(); "
                "from django.conf import settings as s; print(s.DEBUG, s.SECURE_SSL_REDIRECT, s.SESSION_COOKIE_SECURE, s.CSRF_COOKIE_SECURE, s.SECURE_HSTS_SECONDS, s.ALLOWED_HOSTS)")
        result = subprocess.run([sys.executable, "-c", code], cwd=BASE_DIR, env={**os.environ, **PRODUCTION}, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.stdout.strip(), "False True True True 31536000 ['campus.example.com']", result.stderr)

    def test_the_secret_key_is_not_in_the_settings_file(self):
        source = (BASE_DIR / "campus_hub" / "settings.py").read_text(encoding="utf-8")
        self.assertIn('os.environ.get("DJANGO_SECRET_KEY"', source)
        self.assertNotIn(PRODUCTION["DJANGO_SECRET_KEY"], source)

    def test_the_real_env_file_is_git_ignored_and_an_example_exists(self):
        self.assertTrue((BASE_DIR / ".env.example").exists())
        ignore = (BASE_DIR.parent / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", ignore.splitlines())
