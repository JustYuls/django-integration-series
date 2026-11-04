from django.apps import apps
from django.test import TestCase
from django.urls import NoReverseMatch, resolve, reverse

from bookings import views


class FunctionBasedViewTests(TestCase):
    def test_home_page_loads(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_room_detail_shows_the_room(self):
        response = self.client.get("/rooms/2/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lab A")
        self.assertTemplateUsed(response, "bookings/room_detail.html")

    def test_unknown_room_is_404(self):
        self.assertEqual(self.client.get("/rooms/99/").status_code, 404)

    def test_room_detail_only_allows_get(self):
        self.assertEqual(self.client.post("/rooms/1/").status_code, 405)


class ClassBasedViewTests(TestCase):
    def test_room_list_puts_every_room_in_the_context(self):
        response = self.client.get("/rooms/")
        self.assertEqual(len(response.context["rooms"]), 3)
        self.assertTemplateUsed(response, "bookings/rooms.html")

    def test_room_list_has_a_link_to_each_room(self):
        self.assertContains(self.client.get("/rooms/"), 'href="/rooms/3/"')

    def test_a_class_based_view_without_post_answers_405(self):
        self.assertEqual(self.client.post("/rooms/").status_code, 405)


class RoutingTests(TestCase):
    def test_int_converter_rejects_text(self):
        self.assertEqual(self.client.get("/rooms/abc/").status_code, 404)

    def test_re_path_keeps_the_old_link_style_working(self):
        response = self.client.get("/room-2/")
        self.assertContains(response, "Lab A")

    def test_re_path_is_anchored_so_extra_text_is_404(self):
        self.assertEqual(self.client.get("/room-2/extra/").status_code, 404)

    def test_calendar_converters_pass_integers_to_the_view(self):
        self.assertContains(self.client.get("/calendar/2027/4/"), "2027-04")

    def test_calendar_rejects_month_13(self):
        self.assertEqual(self.client.get("/calendar/2027/13/").status_code, 404)

    def test_resolve_maps_an_address_to_the_view(self):
        self.assertIs(resolve("/rooms/1/").func, views.room_detail)
        self.assertIs(resolve("/rooms/").func.view_class, views.RoomListView)


class ReverseAndNamespaceTests(TestCase):
    def test_reverse_builds_addresses_from_names(self):
        self.assertEqual(reverse("home"), "/")
        self.assertEqual(reverse("bookings:room_list"), "/rooms/")
        self.assertEqual(reverse("bookings:room_detail", args=[1]), "/rooms/1/")
        self.assertEqual(reverse("bookings:calendar", kwargs={"year": 2027, "month": 4}), "/calendar/2027/4/")

    def test_a_name_without_its_namespace_is_not_found(self):
        with self.assertRaises(NoReverseMatch):
            reverse("room_list")

    def test_the_navbar_uses_reversed_addresses(self):
        response = self.client.get("/")
        self.assertContains(response, 'href="/rooms/"')

    def test_the_bookings_app_is_still_registered(self):
        self.assertTrue(apps.is_installed("bookings"))
