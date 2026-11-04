from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.test import TestCase
from django.urls import resolve, reverse


class ProjectSetupTests(TestCase):
    def test_system_check_passes(self):
        call_command("check")

    def test_default_apps_are_installed(self):
        for app in ("admin", "auth", "contenttypes", "sessions", "messages", "staticfiles"):
            self.assertIn(f"django.contrib.{app}", settings.INSTALLED_APPS)

    def test_project_uses_sqlite(self):
        self.assertEqual(connection.vendor, "sqlite")

    def test_time_zone_is_philippine_time(self):
        self.assertEqual(settings.TIME_ZONE, "Asia/Manila")
        self.assertTrue(settings.USE_TZ)

    def test_builtin_migrations_were_applied(self):
        self.assertTrue(MigrationRecorder.Migration.objects.filter(app="auth", name="0001_initial").exists())

    def test_admin_login_page_loads(self):
        self.assertEqual(self.client.get("/admin/login/").status_code, 200)


class ProjectDesignTests(TestCase):
    def test_our_three_apps_are_registered(self):
        for app in ("rooms", "bookings", "holiday_api"):
            self.assertIn(app, settings.INSTALLED_APPS)

    def test_the_home_page_and_the_navbar(self):
        response = self.client.get("/")
        self.assertContains(response, 'href="/rooms/"')
        self.assertContains(response, 'href="/bookings/new/"')
        self.assertContains(response, "/holidays/")

    def test_each_app_owns_a_namespace_and_a_prefix(self):
        self.assertEqual(reverse("rooms:room_list"), "/rooms/")
        self.assertEqual(reverse("bookings:booking_list"), "/bookings/")
        self.assertEqual(reverse("holiday_api:holiday_list", args=[2027]), "/holidays/2027/")

    def test_resolve_finds_the_app_and_view(self):
        match = resolve("/bookings/new/")
        self.assertEqual(match.app_names, ["bookings"])
        self.assertEqual(match.url_name, "booking_create")

    def test_tests_never_call_the_holidays_network_by_default(self):
        self.assertFalse(settings.HOLIDAYS_ENABLED)
