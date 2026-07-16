from django.urls import path
from api.views import (
    LoginAPIView, DoctorListAPIView, DoctorDetailAPIView, PatientListAPIView, PatientDetailAPIView,
    AppointmentViewSet, MedicineViewSet, BillViewSet, PatientRegistrationAPIView, HospitalAdminRegistrationAPIView,
    ReceptionistRegistrationAPIView, DoctorRegistrationAPIView, PrescriptionListCreateAPIView
)
from rest_framework.routers import DefaultRouter

urlpatterns = [
    # auth and registrations
    path("auth/login/", LoginAPIView.as_view(), name='login'),
    path('auth/register/patient/', PatientRegistrationAPIView.as_view(), name='register-patient'),
    path('auth/register/admin/', HospitalAdminRegistrationAPIView.as_view(), name='register-admin'),
    path('auth/register/receptionist/', ReceptionistRegistrationAPIView.as_view(), name='register-receptionist'),
    path('auth/register/doctor/', DoctorRegistrationAPIView.as_view(), name='register-doctor'),

    # doctor profiles
    path("doctors/", DoctorListAPIView.as_view(), name='doctors'),
    path("doctors/<int:pk>/", DoctorDetailAPIView.as_view(), name='doctor-details'),

    # patient profiles
    path("patients/", PatientListAPIView.as_view(), name='patients'),
    path("patients/<int:pk>", PatientDetailAPIView.as_view(), name='patient-details'),

    # Prescription Endpoints (Doctors only for POST)
    path('prescriptions/', PrescriptionListCreateAPIView.as_view(), name='prescription-list-create'),
]


router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointments')
router.register(r'medicines', MedicineViewSet, basename='medicines')
router.register(r'bills', BillViewSet, basename='bills')
urlpatterns += router.urls