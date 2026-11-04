from django.test import SimpleTestCase

from ai_review import review


class AiReviewVerificationTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.facts = review.evaluate()

    def test_issue_1_the_app_really_is_not_registered(self):
        self.assertTrue(self.facts["app_not_registered"])

    def test_issue_2_the_template_folder_typo_really_breaks_rendering(self):
        self.assertTrue(self.facts["template_folder_typo"])

    def test_issue_3_the_missing_static_folder_is_found_by_check(self):
        self.assertEqual(self.facts["check_ids"], ["staticfiles.W004"])

    def test_issue_4_static_without_load_is_a_template_syntax_error(self):
        self.assertTrue(self.facts["static_without_load"])

    def test_issue_5_debug_and_hosts_only_show_up_with_check_deploy(self):
        self.assertTrue(self.facts["debug_and_hosts"])
        self.assertTrue(self.facts["deploy_only"])

    def test_claim_6_check_does_not_flag_all_five_problems(self):
        self.assertEqual(len(self.facts["check_ids"]), 1)

    def test_claim_7_turning_debug_off_does_not_fix_the_template_error(self):
        self.assertFalse(self.facts["debug_false_fixes_template"])
