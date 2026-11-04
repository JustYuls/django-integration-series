from django.test import SimpleTestCase

from holiday_review import review


class SuggestedTestsAgainstTheClientsTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.results = review.evaluate()

    def test_the_fixed_client_passes_every_suggested_scenario(self):
        self.assertTrue(all(self.results["fixed"].values()), self.results["fixed"])

    def test_the_naive_client_passes_only_the_happy_path(self):
        passed = [name for name, ok in self.results["naive"].items() if ok]
        self.assertEqual(passed, ["returns the holidays on a 200 answer"])

    def test_the_naive_client_has_no_timeout(self):
        self.assertFalse(self.results["naive"]["passes a timeout to requests"])

    def test_the_naive_client_crashes_on_http_500(self):
        self.assertFalse(self.results["naive"]["HTTP 500 becomes HolidayServiceError"])

    def test_the_naive_client_crashes_on_a_connection_error(self):
        self.assertFalse(self.results["naive"]["connection error becomes HolidayServiceError"])

    def test_the_naive_client_calls_the_api_every_time(self):
        self.assertFalse(self.results["naive"]["the second call uses the cache"])

    def test_there_are_eight_scenarios(self):
        self.assertEqual(len(review.SCENARIOS), 8)
