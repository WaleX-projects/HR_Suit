# Create your tests here.
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):

    def setUp(self):
        self.user_data = {
            "email": "test@test.com",
            "password": "12345678",
            "first_name": "Test",
            "last_name": "User"
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_login(self):
        url = reverse("token_obtain_pair")

        response = self.client.post(url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        
def test_employee_cannot_create_employee(self):
    self.user.role = "employee"
    self.user.save()

    self.client.force_authenticate(user=self.user)

    response = self.client.post("/api/employees/", {
        "first_name": "Hack",
        "last_name": "User",
        "email": "hack@test.com",
        "phone": "08000000000",
        "hire_date": "2026-03-17",
        "status": "active"
    })

    self.assertEqual(response.status_code, 403)  # ❌ Forbidden