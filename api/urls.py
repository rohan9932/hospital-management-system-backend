from django.urls import path
from api.views import (
    LoginAPIView, DoctorListAPIView, DoctorDetailAPIView, PatientListAPIView, PatientDetailAPIView
)

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name='login'),

    # doctor profiles
    path("doctors/", DoctorListAPIView.as_view(), name='doctors'),
    path("doctors/<int:pk>/", DoctorDetailAPIView.as_view(), name='doctor-details'),

    # patient profiles
    path("patients/", PatientListAPIView.as_view(), name='patients'),
    path("patients/<int:pk>", PatientDetailAPIView.as_view(), name='patient-details'),
]