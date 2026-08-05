import copy
import sys
import unittest
from pathlib import Path

from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import activities, signup_for_activity


class SignupCapacityTests(unittest.TestCase):
    def setUp(self):
        self.original_activities = copy.deepcopy(activities)
        self.activity_name = "Math Club"
        self.activity = activities[self.activity_name]

    def tearDown(self):
        activities.clear()
        activities.update(self.original_activities)

    def test_signup_fills_final_available_spot(self):
        self.activity["participants"] = [
            f"student{i}@mergington.edu"
            for i in range(self.activity["max_participants"] - 1)
        ]

        response = signup_for_activity(
            self.activity_name, "final-student@mergington.edu"
        )

        self.assertEqual(
            response,
            {
                "message": (
                    "Signed up final-student@mergington.edu for Math Club"
                )
            },
        )
        self.assertEqual(
            len(self.activity["participants"]),
            self.activity["max_participants"],
        )

    def test_signup_rejects_student_when_activity_is_full(self):
        self.activity["participants"] = [
            f"student{i}@mergington.edu"
            for i in range(self.activity["max_participants"])
        ]
        participants_before_signup = self.activity["participants"][:]

        with self.assertRaises(HTTPException) as context:
            signup_for_activity(
                self.activity_name, "overflow@mergington.edu"
            )

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Activity is full")
        self.assertEqual(
            self.activity["participants"], participants_before_signup
        )

    def test_duplicate_signup_is_still_rejected(self):
        existing_email = self.activity["participants"][0]

        with self.assertRaises(HTTPException) as context:
            signup_for_activity(self.activity_name, existing_email)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail, "Student is already signed up"
        )


if __name__ == "__main__":
    unittest.main()