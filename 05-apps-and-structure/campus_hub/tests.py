from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.test import TestCase


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

    def test_admin_login_page_loads(self):
        self.assertEqual(self.client.get("/admin/login/").status_code, 200)
