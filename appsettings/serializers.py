# settings/serializers.py
from rest_framework import serializers
from .models import CompanySettings

class CompanySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySettings
        fields = '__all__'   # or list them explicitly if you prefer

    def validate(self, attrs):
        # Optional extra validation
        if attrs.get('payroll_day', 0) < 1 or attrs.get('payroll_day', 0) > 31:
            raise serializers.ValidationError({"payroll_day": "Must be between 1 and 31"})
        return attrs