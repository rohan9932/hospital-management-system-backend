import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

# --- Adjust this import to match your actual app name ---
from api.models import (
    HospitalAppUser,
    Department,
    Doctor,
    Patient,
    Appointment,
    Medicine,
    Prescription,
    PrescriptionMedicine,
    Bill,
)

from api.choices import RoleChoices, BloodGroupChoices

class Command(BaseCommand):
    help = "Seed the database with sample hospital data (departments, doctors, patients, appointments, etc.)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing seed-created records before seeding again.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.flush_data()

        with transaction.atomic():
            departments = self.seed_departments()
            admin_user = self.seed_admin()
            receptionist_user = self.seed_receptionist()
            doctors = self.seed_doctors(departments)
            patients = self.seed_patients()
            medicines = self.seed_medicines()
            appointments = self.seed_appointments(patients, doctors)
            self.seed_prescriptions(appointments, medicines)
            self.seed_bills(patients)

        self.stdout.write(self.style.SUCCESS("Done seeding data."))

    # ------------------------------------------------------------------
    # Optional cleanup
    # ------------------------------------------------------------------
    def flush_data(self):
        """
        Permanently removes previously-seeded rows.

        NOTE: django-soft-delete's `.delete()` only ever soft-deletes
        (sets is_deleted=True / deleted_at=now), even when called on a
        queryset. To actually remove rows we must:
          1. Query with `global_objects` so we catch rows that are
             already soft-deleted from a previous run too (the default
             `objects` manager only sees "alive" rows).
          2. Call `.hard_delete()` on each instance. There is no
             documented bulk/queryset-level hard_delete, so this loops
             per row.
        """
        self.stdout.write("Flushing existing seed data (hard delete)...")

        def hard_delete_all(queryset, label):
            count = 0
            for obj in queryset:
                obj.hard_delete()
                count += 1
            self.stdout.write(f"  Hard-deleted {count} {label}")

        hard_delete_all(Bill.global_objects.all(), "bills")
        hard_delete_all(PrescriptionMedicine.global_objects.all(), "prescription medicines")
        hard_delete_all(Prescription.global_objects.all(), "prescriptions")
        hard_delete_all(Appointment.global_objects.all(), "appointments")
        hard_delete_all(Medicine.global_objects.all(), "medicines")
        hard_delete_all(Patient.global_objects.all(), "patients")
        hard_delete_all(Doctor.global_objects.all(), "doctors")
        hard_delete_all(Department.global_objects.all(), "departments")

        seed_usernames = [
            "admin",
            "receptionist1",
            "dr_ahmed", "dr_farah", "dr_kabir", "dr_nusrat", "dr_shuvo",
            "patient_alam", "patient_bristi", "patient_himel", "patient_joya", "patient_rakib",
        ]
        # HospitalAppUser is a SoftDeleteModel too, via the same global_objects manager
        hard_delete_all(
            HospitalAppUser.global_objects.filter(username__in=seed_usernames),
            "hospital users",
        )

    # ------------------------------------------------------------------
    # Departments
    # ------------------------------------------------------------------
    def seed_departments(self):
        dept_data = [
            ("Cardiology", "Heart and cardiovascular system"),
            ("Neurology", "Brain and nervous system"),
            ("Orthopedics", "Bones, joints, and muscles"),
            ("Pediatrics", "Child healthcare"),
            ("General Medicine", "General diagnosis and treatment"),
        ]
        departments = []
        for name, desc in dept_data:
            dept, _ = Department.objects.get_or_create(name=name, defaults={"description": desc})
            departments.append(dept)
        self.stdout.write(f"  Departments: {len(departments)}")
        return departments

    # ------------------------------------------------------------------
    # Admin user
    # ------------------------------------------------------------------
    def seed_admin(self):
        admin_user, created = HospitalAppUser.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@hospital.test",
                "role": RoleChoices.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
        self.stdout.write(f"  Admin user: {admin_user.username}")
        return admin_user

    # ------------------------------------------------------------------
    # Receptionist
    # ------------------------------------------------------------------
    def seed_receptionist(self):
        receptionist_user, created = HospitalAppUser.objects.get_or_create(
            username="receptionist1",
            defaults={
                "email": "receptionist1@hospital.test",
                "role": RoleChoices.RECEPTIONIST,
                "first_name": "Rina",
                "last_name": "Karim",
            },
        )
        if created:
            receptionist_user.set_password("password123")
            receptionist_user.save()
        self.stdout.write(f"  Receptionist user: {receptionist_user.username}")
        return receptionist_user

    # ------------------------------------------------------------------
    # Doctors
    # ------------------------------------------------------------------
    def seed_doctors(self, departments):
        doctor_specs = [
            ("dr_ahmed", "Ahmed", "Rahman", "Cardiology", "Cardiologist", "01711000001", 12),
            ("dr_farah", "Farah", "Islam", "Neurology", "Neurologist", "01711000002", 8),
            ("dr_kabir", "Kabir", "Hossain", "Orthopedics", "Orthopedic Surgeon", "01711000003", 15),
            ("dr_nusrat", "Nusrat", "Jahan", "Pediatrics", "Pediatrician", "01711000004", 6),
            ("dr_shuvo", "Shuvo", "Chowdhury", "General Medicine", "General Physician", "01711000005", 10),
        ]
        dept_by_name = {d.name: d for d in departments}
        doctors = []
        for username, first, last, dept_name, specialization, phone, exp in doctor_specs:
            user, created = HospitalAppUser.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@hospital.test",
                    "role": RoleChoices.DOCTOR,
                    "first_name": first,
                    "last_name": last,
                },
            )
            if created:
                user.set_password("password123")
                user.save()

            doctor, _ = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    "department": dept_by_name[dept_name],
                    "specialization": specialization,
                    "phone": phone,
                    "experience": exp,
                    "is_available": True,
                },
            )
            doctors.append(doctor)
        self.stdout.write(f"  Doctors: {len(doctors)}")
        return doctors

    # ------------------------------------------------------------------
    # Patients
    # ------------------------------------------------------------------
    def seed_patients(self):
        patient_specs = [
            ("patient_alam", "Alam", "Khan", 34, "Male", BloodGroupChoices.A_POSITIVE, "01911000001", "Dhanmondi, Dhaka"),
            ("patient_bristi", "Bristi", "Akter", 27, "Female", BloodGroupChoices.O_NEGATIVE, "01911000002", "Uttara, Dhaka"),
            ("patient_himel", "Himel", "Das", 45, "Male", BloodGroupChoices.B_POSITIVE, "01911000003", "Mirpur, Dhaka"),
            ("patient_joya", "Joya", "Sultana", 19, "Female", BloodGroupChoices.AB_POSITIVE, "01911000004", "Banani, Dhaka"),
            ("patient_rakib", "Rakib", "Mia", 60, "Male", BloodGroupChoices.O_POSITIVE, "01911000005", "Mohammadpur, Dhaka"),
        ]
        patients = []
        for username, first, last, age, gender, blood_group, phone, address in patient_specs:
            user, created = HospitalAppUser.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@hospital.test",
                    "role": RoleChoices.PATIENT,
                    "first_name": first,
                    "last_name": last,
                },
            )
            if created:
                user.set_password("password123")
                user.save()

            patient, _ = Patient.objects.get_or_create(
                user=user,
                defaults={
                    "age": age,
                    "gender": gender,
                    "blood_group": blood_group,
                    "address": address,
                    "phone": phone,
                },
            )
            patients.append(patient)
        self.stdout.write(f"  Patients: {len(patients)}")
        return patients

    # ------------------------------------------------------------------
    # Medicines
    # ------------------------------------------------------------------
    def seed_medicines(self):
        medicine_data = [
            ("Paracetamol", "Pain reliever and fever reducer", "tablet"),
            ("Amoxicillin", "Antibiotic", "capsule"),
            ("Ibuprofen", "NSAID pain reliever", "tablet"),
            ("Cetirizine", "Antihistamine for allergies", "tablet"),
            ("Metformin", "Blood sugar control", "tablet"),
            ("Omeprazole", "Reduces stomach acid", "capsule"),
        ]
        medicines = []
        for name, desc, unit in medicine_data:
            med, _ = Medicine.objects.get_or_create(name=name, defaults={"description": desc, "unit": unit})
            medicines.append(med)
        self.stdout.write(f"  Medicines: {len(medicines)}")
        return medicines

    # ------------------------------------------------------------------
    # Appointments (mix of statuses, past and future)
    # ------------------------------------------------------------------
    def seed_appointments(self, patients, doctors):
        statuses = [
            Appointment.StatusChoices.pending,
            Appointment.StatusChoices.approved,
            Appointment.StatusChoices.completed,
            Appointment.StatusChoices.cancelled,
        ]

        appointments = []
        now = timezone.now()
        for i in range(12):
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            status = statuses[i % len(statuses)]
            if status in (Appointment.StatusChoices.completed, Appointment.StatusChoices.cancelled):
                appt_date = now - timedelta(days=random.randint(1, 60))
            else:
                appt_date = now + timedelta(days=random.randint(1, 30))

            appointment, _ = Appointment.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                appointment_date=appt_date,
                defaults={"status": status},
            )
            appointments.append(appointment)
        self.stdout.write(f"  Appointments: {len(appointments)}")
        return appointments

    # ------------------------------------------------------------------
    # Prescriptions + PrescriptionMedicine for completed appointments
    # ------------------------------------------------------------------
    def seed_prescriptions(self, appointments, medicines):
        completed_appointments = [a for a in appointments if a.status == Appointment.StatusChoices.completed]
        diagnoses = [
            "Common cold with mild fever",
            "Seasonal allergy",
            "Muscle strain",
            "Mild hypertension",
            "Acid reflux",
        ]
        prescriptions_created = 0
        for appointment in completed_appointments:
            prescription, created = Prescription.objects.get_or_create(
                appointment=appointment,
                defaults={
                    "diagnosis": random.choice(diagnoses),
                    "notes": "Follow up after 7 days if symptoms persist.",
                },
            )
            if created:
                for medicine in random.sample(medicines, k=min(2, len(medicines))):
                    PrescriptionMedicine.objects.get_or_create(
                        prescription=prescription,
                        medicine=medicine,
                        defaults={
                            "dosage": random.choice(["1 tablet twice daily", "1 capsule after meals", "500mg once daily"]),
                            "duration": random.choice(["5 days", "7 days", "10 days"]),
                        },
                    )
                prescriptions_created += 1
        self.stdout.write(f"  Prescriptions: {prescriptions_created}")

    # ------------------------------------------------------------------
    # Bills
    # ------------------------------------------------------------------
    def seed_bills(self, patients):
        bills_created = 0
        for patient in patients:
            for _ in range(random.randint(1, 2)):
                Bill.objects.create(
                    patient=patient,
                    amount=random.choice(["500.00", "750.00", "1200.00", "2000.00"]),
                    paid=random.choice([True, False]),
                )
                bills_created += 1
        self.stdout.write(f"  Bills: {bills_created}")