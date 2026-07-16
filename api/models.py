from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django_softdelete.models import SoftDeleteModel
from api.choices import RoleChoices, BloodGroupChoices

# custom hybrid manager
class HospitalAppUserManager(UserManager):
    def get_queryset(self):
        # Exclude soft-deleted users by default
        return super().get_queryset().filter(deleted_at__isnull=True)

# User Models
class HospitalAppUser(SoftDeleteModel, AbstractUser):
    role = models.CharField(choices=RoleChoices.choices, max_length=15)

    #Tell Django to use hybrid manager instead of SoftDeleteManager
    objects = HospitalAppUserManager()

class Department(SoftDeleteModel):
    name = models.CharField(max_length=100)
    description = models.TextField()


class Doctor(SoftDeleteModel):
    user = models.OneToOneField(HospitalAppUser, related_name="doctor", on_delete=models.CASCADE)
    department = models.ForeignKey(Department, related_name='doctors', on_delete=models.SET_NULL, null=True)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    experience = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)


class Patient(SoftDeleteModel):
    user = models.OneToOneField(HospitalAppUser, related_name="patient", on_delete=models.CASCADE)
    age = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=3, choices=BloodGroupChoices.choices)
    address = models.TextField()
    phone = models.CharField(max_length=15)


# utility models
class Appointment(SoftDeleteModel):
    class StatusChoices(models.TextChoices):
        pending = "Pending", "Pending"
        approved = "Approved", "Approved"
        completed = "Completed", "Completed"
        cancelled = "Cancelled", "Cancelled"

    patient = models.ForeignKey(Patient, related_name='appointment', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='appointment', on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=15, choices=StatusChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)



class Medicine(SoftDeleteModel):
    name = models.CharField(max_length=150)
    description = models.TextField()
    unit = models.CharField(max_length=15)


class Prescription(SoftDeleteModel):
    appointment = models.OneToOneField(Appointment, related_name='prescription', on_delete=models.CASCADE)
    diagnosis = models.TextField()
    notes = models.TextField()
    medicines = models.ManyToManyField(Medicine, related_name='prescriptions', through='PrescriptionMedicine')
    created_at = models.DateTimeField(auto_now_add=True)


class PrescriptionMedicine(SoftDeleteModel):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)


class Bill(SoftDeleteModel):
    patient = models.ForeignKey(Patient, related_name='bills', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
