# Create your tests here.
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from companies.models import Company

User = get_user_model()

class CompanyTests(APITestCase):

    def test_create_company(self):
        response = self.client.post("/api/companies/signup/", {
            "company_name": "TestCo",
            "email": "admin@test.com",
            "password": "12345678",
            "first_name": "Admin",
            "last_name": "User"
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Company.objects.count(), 1)
