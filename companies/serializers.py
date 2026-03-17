from rest_framework import serializers
from .models import Company
from accounts.models import User


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


# SaaS Signup Serializer
class CompanySignupSerializer(serializers.Serializer):
    company_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def create(self, validated_data):
        # Create Company
        company = Company.objects.create(
            name=validated_data["company_name"],
            email=validated_data["email"],
        )

        # Create Admin User
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            company=company,
            is_staff=True,
        )

        return {"company": company, "user": user}