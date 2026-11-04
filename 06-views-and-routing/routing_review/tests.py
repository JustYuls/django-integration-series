from django.test import SimpleTestCase

from routing_review import review


class RoutingReviewVerificationTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.facts = review.evaluate()

    def test_finding_1_a_missing_app_name_breaks_reverse(self):
        self.assertTrue(self.facts["namespace_missing"])

    def test_finding_2_a_catch_all_before_the_include_shadows_rooms(self):
        self.assertTrue(self.facts["rooms_is_shadowed"])

    def test_finding_3_an_unanchored_re_path_matches_too_much(self):
        self.assertTrue(self.facts["unanchored_matches_extra"])

    def test_claim_4_the_first_matching_route_wins_not_the_most_specific(self):
        self.assertTrue(self.facts["rooms_is_shadowed"])

    def test_claim_5_re_path_is_not_anchored_automatically(self):
        self.assertTrue(self.facts["unanchored_matches_extra"])

    def test_claim_6_include_with_app_name_gives_namespaced_names(self):
        self.assertEqual(self.facts["fixed_reverse"], "/rooms/")
        self.assertTrue(self.facts["fixed_resolves_list"])

    def test_the_real_urls_reject_the_extra_path(self):
        self.assertTrue(self.facts["fixed_rejects_extra"])
