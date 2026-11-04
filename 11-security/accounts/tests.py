from django.conf import global_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.roles import STAFF, STUDENT

User = get_user_model()


class RoleTests(TestCase):
    def test_both_roles_exist_after_migrate(self):
        self.assertTrue(Group.objects.filter(name=STUDENT).exists())
        self.assertTrue(Group.objects.filter(name=STAFF).exists())

    def test_students_can_book_but_not_manage_rooms_or_everyone_s_bookings(self):
        codes = set(Group.objects.get(name=STUDENT).permissions.values_list("codename", flat=True))
        self.assertIn("add_booking", codes)
        self.assertNotIn("add_room", codes)
        self.assertNotIn("manage_all_bookings", codes)

    def test_staff_can_do_everything_a_student_can_plus_rooms_and_all_bookings(self):
        student = set(Group.objects.get(name=STUDENT).permissions.values_list("codename", flat=True))
        staff = set(Group.objects.get(name=STAFF).permissions.values_list("codename", flat=True))
        self.assertTrue(student < staff)
        self.assertLessEqual({"add_room", "change_room", "delete_room", "manage_all_bookings"}, staff)


class SignUpTests(TestCase):
    DATA = {"username": "ana", "email": "ana@example.com", "password1": "Correct-Horse-2027", "password2": "Correct-Horse-2027"}

    def test_signup_creates_a_student_and_logs_them_in(self):
        response = self.client.post(reverse("signup"), self.DATA, follow=True)
        user = User.objects.get(username="ana")
        self.assertTrue(user.groups.filter(name=STUDENT).exists())
        self.assertContains(response, "Your account is ready.")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    @override_settings(PASSWORD_HASHERS=global_settings.PASSWORD_HASHERS)  # Django's real default, not the fast test hasher
    def test_the_password_is_stored_as_a_salted_hash(self):
        self.client.post(reverse("signup"), self.DATA)
        stored = User.objects.get(username="ana").password
        self.assertTrue(stored.startswith("pbkdf2_sha256$"))
        self.assertNotIn("Correct-Horse-2027", stored)

    def test_weak_passwords_are_rejected(self):
        for weak in ("12345678", "password", "short1"):
            response = self.client.post(reverse("signup"), dict(self.DATA, password1=weak, password2=weak))
            self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="ana").exists())

    def test_an_email_address_is_required(self):
        self.client.post(reverse("signup"), dict(self.DATA, email=""))
        self.assertFalse(User.objects.filter(username="ana").exists())

    def test_the_signup_form_needs_a_csrf_token(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post(reverse("signup"), self.DATA).status_code, 403)


class LoginLogoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("ben", "ben@example.com", "Correct-Horse-2027")

    def test_login_with_the_right_password(self):
        response = self.client.post(reverse("login"), {"username": "ben", "password": "Correct-Horse-2027"})
        self.assertRedirects(response, reverse("home"))

    def test_login_with_a_wrong_password_fails(self):
        response = self.client.post(reverse("login"), {"username": "ben", "password": "nope"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_redirects_back_to_the_page_you_wanted(self):
        response = self.client.post(reverse("login") + "?next=/bookings/new/", {"username": "ben", "password": "Correct-Horse-2027"})
        self.assertRedirects(response, "/bookings/new/", fetch_redirect_response=False)

    def test_logout_needs_a_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.client.post(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_the_login_form_needs_a_csrf_token(self):
        self.assertEqual(Client(enforce_csrf_checks=True).post(reverse("login"), {"username": "ben", "password": "x"}).status_code, 403)

    def test_the_navbar_changes_with_the_login_state(self):
        self.assertContains(self.client.get("/"), "Log in")
        self.client.force_login(self.user)
        page = self.client.get("/")
        self.assertContains(page, "Log out")
        self.assertContains(page, "My bookings")
