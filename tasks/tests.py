from django.test import TestCase
from .scoring import calculate_task_score

class ScoringTests(TestCase):
    def test_overdue_boost(self):
        t = {"title":"A","due_date":"2000-01-01","importance":5,"estimated_hours":1,"done":False}
        s = calculate_task_score(t, all_tasks=[t])
        self.assertTrue(s > 100)
