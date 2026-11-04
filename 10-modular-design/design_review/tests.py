from django.test import SimpleTestCase

from design_review import check_imports as ci
from design_review import review


class DesignReviewVerificationTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.facts = review.evaluate()

    def test_the_real_graph_follows_the_design_rule(self):
        self.assertEqual(self.facts["graph"], {"rooms": set(), "bookings": {"rooms", "holiday_api"}, "holiday_api": set()})
        self.assertEqual(self.facts["violations"], [])

    def test_finding_1_dependencies_point_one_way(self):
        self.assertFalse(self.facts["rooms_imports_bookings"])

    def test_finding_2_views_use_the_service_and_never_send_mail_themselves(self):
        self.assertTrue(self.facts["views_use_services"])
        self.assertFalse(self.facts["views_call_mail_directly"])

    def test_finding_3_the_holiday_app_depends_on_no_other_app(self):
        self.assertTrue(self.facts["holiday_api_is_independent"])

    def test_claim_4_there_is_no_circular_import(self):
        self.assertIsNone(self.facts["cycle"])

    def test_claim_6_the_checker_finds_a_cycle_in_a_bad_design(self):
        self.assertEqual(self.facts["flawed_cycle"], ["bookings", "rooms", "bookings"])
        self.assertIn(("rooms", "bookings"), self.facts["flawed_violations"])

    def test_the_checker_ignores_tests_and_migrations(self):
        paths = {p.name for app in ci.APPS for p in ci.real_files(app)}
        self.assertNotIn("tests.py", paths)
        self.assertNotIn("0001_initial.py", paths)
