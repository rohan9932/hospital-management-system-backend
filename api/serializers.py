from django_softdelete.models import SoftDeleteModel
from rest_framework import serializers

from api.choices import RoleChoices, BloodGroupChoices
from api.models import (
    HospitalAppUser, Patient, Department, Doctor
)
from django.db import transaction


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)


class PatientRegistrationSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(write_only=True, required=True)
    gender = serializers.CharField(max_length=15, write_only=True, required=True)
    blood_group = serializers.ChoiceField(choices=BloodGroupChoices.choices)
    address = serializers.CharField(style={'base_template': 'textarea.html'}, write_only=True, required=True)
    phone = serializers.CharField(max_length=15, write_only=True, required=True)

    class Meta:
        model = HospitalAppUser
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'age',  'gender', 'blood_group', 'address', 'phone', 'date_joined'
        ]
        extra_kwargs = {
            'username': {
                'write_only': True,
                'required': True
            },
            'password': {
                'write_only': True,
                'required': True
            },
            'email': {
                'write_only': True,
                'required': True
            }
        }

    # no duplicate emails (custom validation)
    def validate_email(self, value):
        if HospitalAppUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    # to create related model data
    def create(self, validated_data):
        with transaction.atomic():
            age = validated_data.pop('age')
            gender = validated_data.pop('gender')
            blood_group = validated_data.pop('blood_group')
            address = validated_data.pop('address')
            phone = validated_data.pop('phone')

            # create user object
            user = HospitalAppUser.objects.create(
                role = RoleChoices.PATIENT,
                **validated_data
            )

            # create patient object
            Patient.objects.create(
                user = user,
                age = age,
                gender = gender,
                blood_group = blood_group,
                address = address,
                phone = phone
            )

        return user


# this only has Admin permission
class HospitalAdminRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalAppUser
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 'date_joined'
        ]
        extra_kwargs = {
            'username': {
                'write_only': True,
                'required': True
            },
            'password': {
                'write_only': True,
                'required': True
            },
            'email': {
                'write_only': True,
                'required': True
            }
        }

    def validate_email(self, value):
        if HospitalAppUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        with transaction.atomic():  # for rollback in case of error
            role = RoleChoices.ADMIN
            # create user
            user = HospitalAppUser.objects.create_user(
                role=role,
                **validated_data
            )

        return user


# this only has admin and hospitaladmin permission
class ReceptionistRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalAppUser
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 'date_joined'
        ]
        extra_kwargs = {
            'username': {
                'write_only': True,
                'required': True
            },
            'password': {
                'write_only': True,
                'required': True
            },
            'email': {
                'write_only': True,
                'required': True
            }
        }

    def validate_email(self, value):
        if HospitalAppUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        with transaction.atomic():  # for rollback in case of error
            role = RoleChoices.RECEPTIONIST
            # create user
            user = HospitalAppUser.objects.create_user(
                role=role,
                **validated_data
            )

        return user


class DoctorRegisterSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), write_only=True)
    specialization = serializers.CharField(max_length=30,write_only=True)
    phone = serializers.CharField(max_length=20, write_only=True)
    experience = serializers.IntegerField(min_value=0, write_only=True)

    class Meta:
        model = HospitalAppUser
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            # doctor fields
            'department', 'specialization', 'phone', 'experience',
        ]

        extra_kwargs = {
            'username': {
                'write_only': True,
                'required': True
            },
            'email': {
                'write_only': True,
                'required': True
            },
            'password': {
                'write_only': True,
                'required': True
            }
        }

    def validate_email(self, value):
        if HospitalAppUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def create(self, validated_data):
        with transaction.atomic():
            department = validated_data.pop('department')
            specialization = validated_data.pop('specialization')
            phone = validated_data.pop('phone')
            experience = validated_data.pop('experience')

            user = HospitalAppUser.objects.create_user(
                role=RoleChoices.DOCTOR,
                **validated_data
            )

            Doctor.objects.create(
                user=user,
                department=department,
                specialization=specialization,
                phone=phone,
                experience=experience,
                is_available=True
            )

            return user


class HospitalAppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalAppUser
        fields = ['id', 'username', 'first_name', 'last_name', 'role', 'date_joined']


class DoctorSerializer(serializers.ModelSerializer):
    user = HospitalAppUserSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'department', 'specialization', 'phone', 'experience', 'is_available']


class PatientSerializer(serializers.ModelSerializer):
    user = HospitalAppUserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user', 'age', 'gender', 'blood_group', 'address', 'phone']
