
# Create your tests here.
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from companies.models import Company
from employees.models import Employee
from attendance.models import Attendance

User = get_user_model()

class AttendanceTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="admin@test.com", password="12345678")
        self.company = Company.objects.create(name="TestCo")

        self.user.company = self.company
        self.user.save()

        self.employee = Employee.objects.create(
    first_name="John",
    last_name="Doe",
    email="john@test.com",
    hire_date="2026-03-17",  # ✅ ADD THIS
    company=self.company
)

        self.client.force_authenticate(user=self.user)

    def test_clock_in(self):
        response = self.client.post("/api/attendance/", {
            "employee": str(self.employee.id),
            "date": "2026-03-17",
            "status": "present"
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Attendance.objects.count(), 1)
