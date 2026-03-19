from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from companies.models import Company
from employees.models import Employee

User = get_user_model()

class EmployeeTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="admin@test.com",
            password="12345678"
        )

        self.company = Company.objects.create(name="TestCo")
        self.user.company = self.company
        self.user.save()

        self.client.force_authenticate(user=self.user)

    def test_create_employee(self):
        response = self.client.post("/api/employees/", {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@test.com",
     "phone": "08012345678",
    "hire_date": "2026-03-17",
    "status": "active",
    "company": str(self.company.id)  #  important if serializer expects it
})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # 👇 PUT IT HERE
    def test_unauthorized_access(self):
        # remove authentication
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/employees/")
        self.assertEqual(response.status_code, 401)
