from django.db import models


class RoleChoices(models.TextChoices):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"
    RECEPTIONIST = "receptionist"


class BloodGroupChoices(models.TextChoices):
    A_POSITIVE = "A+", "A+"
    A_NEGATIVE = "A-", "A-"
    B_POSITIVE = "B+", "B+"
    B_NEGATIVE = "B-", "B-"
    AB_POSITIVE = "AB+", "AB+"
    AB_NEGATIVE = "AB-", "AB-"
    O_POSITIVE = "O+", "O+"
    O_NEGATIVE = "O-", "O-"
