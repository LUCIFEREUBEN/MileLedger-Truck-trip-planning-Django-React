from rest_framework.test import APITestCase


class TripApiTests(APITestCase):
    payload = {
        "current_location": "Louisville, KY",
        "pickup_location": "Nashville, TN",
        "dropoff_location": "Memphis, TN",
        "cycle_used_hours": "28.25",
        "log_timezone": "America/Chicago",
    }

    def test_health(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ok")

    def test_plan_and_get(self):
        response = self.client.post("/api/trips/plan/", self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["trip_id"])
        detail = self.client.get(f"/api/trips/{response.data['trip_id']}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["route"]["mode"], "demo")
        self.assertEqual(detail.data["input"]["pickup_location"], "Nashville, TN")

    def test_recalculate(self):
        first = self.client.post("/api/trips/plan/", self.payload, format="json")
        response = self.client.post(
            f"/api/trips/{first.data['trip_id']}/recalculate/",
            {"cycle_used_hours": "69"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data["trip_id"], first.data["trip_id"])

    def test_field_errors_are_structured(self):
        response = self.client.post(
            "/api/trips/plan/", {**self.payload, "cycle_used_hours": 71}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "invalid_input")
        self.assertIn("cycle_used_hours", response.data["field_errors"])
