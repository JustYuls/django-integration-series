from django.test import TestCase

from security_review import review


class SecurityReviewVerificationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.facts = review.evaluate()

    def test_finding_1_login_required_alone_lets_any_user_cancel_any_booking(self):
        self.assertTrue(self.facts["flawed_lets_alice_delete_bobs_booking"])

    def test_finding_2_the_real_view_answers_404_and_keeps_the_booking(self):
        self.assertEqual(self.facts["real_view_status_for_alice"], 404)
        self.assertTrue(self.facts["real_view_keeps_the_booking"])

    def test_finding_3_a_star_in_allowed_hosts_accepts_any_host(self):
        self.assertTrue(self.facts["star_accepts_evil_host"])
        self.assertTrue(self.facts["real_hosts_reject_evil_host"])

    def test_finding_3_check_deploy_does_not_warn_about_the_star(self):
        self.assertTrue(self.facts["check_deploy_is_silent_about_star"])

    def test_claim_5_hiding_the_button_is_not_authorization(self):
        self.assertTrue(self.facts["link_is_hidden_for_alice"])
        self.assertTrue(self.facts["flawed_lets_alice_delete_bobs_booking"])

    def test_claim_6_passwords_are_salted_hashes(self):
        self.assertEqual(self.facts["password_hash"], "pbkdf2_sha256")
