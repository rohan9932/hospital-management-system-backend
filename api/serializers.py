from rest_framework import serializers
from api.models import (
    HospitalAppUser
)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)


class PatientRegistrationSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(default=0, write_only=True, required=True)
    gender = serializers.CharField(max_length=15, write_only=True, required=True)
    blood_group = serializers.CharField(max_length=3, choices=BloodGroupChoices.choices)
    address = serializers.CharField(style={'base_template': 'textarea.html'}, write_only=True, required=True)
    phone = serializers.CharField(max_length=15, write_only=True, required=True)

    class Meta:
        model = HospitalAppUser