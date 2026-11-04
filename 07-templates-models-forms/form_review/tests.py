from django.test import TestCase

from form_review import review


class FormReviewVerificationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.facts = review.evaluate()

    def test_finding_1_the_flawed_template_has_no_token_and_a_post_gets_403(self):
        self.assertFalse(self.facts["flawed_has_token"])
        self.assertEqual(self.facts["post_without_token_status"], 403)

    def test_the_real_page_does_have_a_token(self):
        self.assertTrue(self.facts["real_page_has_token"])

    def test_finding_2_safe_lets_a_script_through(self):
        self.assertTrue(self.facts["safe_leaves_script"])

    def test_finding_3_the_flawed_form_accepts_too_many_attendees(self):
        self.assertTrue(self.facts["flawed_accepts_too_many"])

    def test_finding_3_the_flawed_form_accepts_a_double_booking(self):
        self.assertTrue(self.facts["flawed_accepts_double_booking"])

    def test_the_real_form_rejects_both(self):
        self.assertTrue(self.facts["real_rejects_too_many"])
        self.assertTrue(self.facts["real_rejects_double_booking"])

    def test_claim_6_variables_are_escaped_by_default(self):
        self.assertTrue(self.facts["default_escapes_script"])
