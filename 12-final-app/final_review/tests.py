from django.test import TestCase

from final_review import debug, perf


class DebuggingReviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.facts = debug.evaluate()

    def test_finding_1_the_bug_is_reproduced(self):
        self.assertNotIn("Lab C", self.facts["buggy_10_to_12"])
        self.assertEqual(self.facts["fixed_10_to_12"], ["Lab C", "Open Studio"])

    def test_finding_2_the_buggy_sql_has_two_separate_exists_and_the_fix_has_one(self):
        self.assertEqual(self.facts["buggy_sql"].count("EXISTS("), 2)
        self.assertEqual(self.facts["fixed_sql"].count("EXISTS("), 1)

    def test_finding_3_the_fix_is_one_query(self):
        self.assertEqual(self.facts["fixed_query_count"], 1)

    def test_claim_4_back_to_back_bookings_do_not_clash(self):
        self.assertEqual(self.facts["buggy_back_to_back"], ["Open Studio", "Room A"])
        self.assertEqual(self.facts["fixed_back_to_back"], ["Lab C", "Open Studio", "Room A"])

    def test_claim_5_select_related_does_not_change_the_answer(self):
        self.assertEqual(self.facts["with_select_related"], self.facts["buggy_10_to_12"])


class PerformanceReviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.facts = perf.measure(rows=4000, rooms=20, repeats=1)

    def test_asking_once_per_room_costs_one_query_per_room_plus_one(self):
        self.assertEqual(self.facts["naive_queries"], 1 + 20)

    def test_one_exists_query_gives_the_same_answer_in_one_query(self):
        self.assertEqual(self.facts["single_queries"], 1)
        self.assertTrue(self.facts["same_answer"])

    def test_the_composite_index_turns_the_lookup_into_a_covering_index_search(self):
        self.assertNotIn("COVERING INDEX", self.facts["plan_without_index"][-1])
        self.assertIn("COVERING INDEX booking_room_start_end_idx", self.facts["plan_with_index"][-1])
