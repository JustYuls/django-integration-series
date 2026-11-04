from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.test import TestCase, override_settings


class ProjectSetupTests(TestCase):
    def test_system_check_passes(self):
        call_command("check")  # raises an error if the project is misconfigured

    def test_default_apps_are_installed(self):
        for app in ("admin", "auth", "contenttypes", "sessions", "messages", "staticfiles"):
            self.assertIn(f"django.contrib.{app}", settings.INSTALLED_APPS)

    def test_project_uses_sqlite(self):
        self.assertEqual(connection.vendor, "sqlite")

    def test_time_zone_is_philippine_time(self):
        self.assertEqual(settings.TIME_ZONE, "Asia/Manila")
        self.assertTrue(settings.USE_TZ)

    def test_builtin_migrations_were_applied(self):
        applied = MigrationRecorder.Migration.objects.filter(app="auth", name="0001_initial")
        self.assertTrue(applied.exists())


class DevServerPageTests(TestCase):
    @override_settings(DEBUG=True)  # the test runner turns DEBUG off, the welcome page needs it on
    def test_welcome_page_shows_when_debug_is_on(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The install worked successfully")

    def test_admin_login_page_loads(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)

    def test_home_page_is_not_found_when_debug_is_off(self):
        self.assertEqual(self.client.get("/").status_code, 404)
