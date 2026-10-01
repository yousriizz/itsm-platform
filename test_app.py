import unittest
from app import app, init_db


class TicketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_ticket_lifecycle(self):
        created = self.client.post(
            "/tickets", json={"title": "Imprimante en panne"}
        )
        self.assertEqual(created.status_code, 201)
        ticket_id = created.json["id"]

        listed = self.client.get("/tickets")
        self.assertEqual(listed.status_code, 200)
        self.assertTrue(any(t["id"] == ticket_id for t in listed.json))

        updated = self.client.patch(
            f"/tickets/{ticket_id}", json={"status": "résolu"}
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json["status"], "résolu")


if __name__ == "__main__":
    unittest.main()
