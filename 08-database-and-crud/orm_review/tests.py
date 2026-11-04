from django.test import TestCase

from orm_review import review


class OrmReviewVerificationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.facts = review.evaluate()

    def test_finding_1_the_flawed_helper_runs_n_plus_one_queries(self):
        self.assertEqual(self.facts["flawed_lines_queries"], 1 + self.facts["rows"])

    def test_finding_2_select_related_gives_one_query_and_the_same_result(self):
        self.assertEqual(self.facts["fixed_lines_queries"], 1)
        self.assertTrue(self.facts["lines_equal"])

    def test_finding_3_len_loads_every_row(self):
        self.assertTrue(self.facts["len_loads_rows"])
        self.assertTrue(self.facts["flawed_busy"])

    def test_the_fixed_busy_check_asks_the_database_for_one_row(self):
        self.assertIn("LIMIT 1", self.facts["fixed_busy_sql"])

    def test_claim_4_filter_is_lazy(self):
        self.assertEqual(self.facts["queries_when_building"], 0)
        self.assertEqual(self.facts["queries_when_evaluating"], 1)

    def test_claim_6_count_and_len_do_different_work(self):
        self.assertTrue(self.facts["count_uses_count_sql"])
