from django.apps import apps
from django.contrib.staticfiles import finders
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.test import TestCase, override_settings


class AppStructureTests(TestCase):
    def test_bookings_app_is_registered(self):
        self.assertTrue(apps.is_installed("bookings"))
        self.assertEqual(apps.get_app_config("bookings").name, "bookings")

    def test_home_and_rooms_pages_load(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/rooms/").status_code, 200)

    def test_home_page_uses_the_base_template_and_both_partials(self):
        response = self.client.get("/")
        for name in ("home.html", "base.html", "partials/_navbar.html", "partials/_footer.html"):
            self.assertTemplateUsed(response, name)

    def test_rooms_page_comes_from_the_app_template_folder(self):
        self.assertTemplateUsed(self.client.get("/rooms/"), "bookings/rooms.html")

    def test_navbar_appears_on_every_page(self):
        for path in ("/", "/rooms/"):
            self.assertContains(self.client.get(path), 'class="navbar"')

    def test_static_css_is_found_and_linked(self):
        self.assertIsNotNone(finders.find("css/site.css"))
        self.assertContains(self.client.get("/"), "/static/css/site.css")


class CommonMistakeTests(TestCase):
    def test_a_template_in_an_unregistered_app_is_not_found(self):
        without_bookings = [app for app in apps.get_app_configs() if app.name != "bookings"]
        names = [app.name for app in without_bookings]
        with override_settings(INSTALLED_APPS=names):
            with self.assertRaises(TemplateDoesNotExist):
                get_template("bookings/rooms.html")

    def test_a_wrong_template_folder_hides_the_shared_templates(self):
        from django.conf import settings
        wrong = [dict(settings.TEMPLATES[0], DIRS=[settings.BASE_DIR / "template"])]
        with override_settings(TEMPLATES=wrong):
            with self.assertRaises(TemplateDoesNotExist):
                get_template("home.html")
