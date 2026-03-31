from rest_framework import serializers
from .models import User
from companies.models import Company 
from companies.serializers import CompanySerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name","role"]



class RegisterSerializer(serializers.ModelSerializer):
    # pass company data while registering 
    company_data = CompanySerializer(write_only=True)
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "phone","company_data"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        company_data = validated_data.pop("company_data")
        company_email = validated_data.get("email")
        company_phone = validated_data.get("phone")
        #1. create the company 
        company,created = Company.objects.get_or_create(
            name=company_data['name'],
            email=company_email,
            phone = company_phone,
            address= company_data['address'],
            country=company_data['country'],
            timezone=company_data['timezone']
        )
        #2. create an admin
        user = User.objects.create_user(**validated_data)
        #3. connect the company and admin
        user.company=company
        user.save()
        return user