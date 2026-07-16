from django.urls import path
from api.views import (
    LoginAPIView, DoctorListAPIView, DoctorDetailAPIView, PatientListAPIView, PatientDetailAPIView,
    AppointmentViewSet, MedicineViewSet, BillViewSet
)
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name='login'),

    # doctor profiles
    path("doctors/", DoctorListAPIView.as_view(), name='doctors'),
    path("doctors/<int:pk>/", DoctorDetailAPIView.as_view(), name='doctor-details'),

    # patient profiles
    path("patients/", PatientListAPIView.as_view(), name='patients'),
    path("patients/<int:pk>", PatientDetailAPIView.as_view(), name='patient-details'),
]


router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointments')
router.register(r'medicines', MedicineViewSet, basename='medicines')
router.register(r'bills', BillViewSet, basename='bills')
urlpatterns += router.urls