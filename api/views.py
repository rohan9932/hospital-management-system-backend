from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.serializers import LoginSerializer, DoctorSerializer, PatientSerializer, AppointmentSerializer, \
    MedicineSerializer, BillSerializer, HospitalAdminRegistrationSerializer, PatientRegistrationSerializer, \
    ReceptionistRegistrationSerializer, DoctorRegistrationSerializer, PrescriptionSerializer
from api.models import HospitalAppUser, Doctor, Patient, Appointment, Medicine, Bill, Prescription
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from api.permissions import IsDoctor, IsReceptionist, IsHospitalAdmin
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


# AUTH View
def get_token(user):
    token = RefreshToken.for_user(user)
    return {
        'refresh': str(token),
        'access': str(token.access_token)
    }


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) # raises exception if data not valid
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        # check if user exists
        try:
            user = HospitalAppUser.objects.get(email=email)
        except HospitalAppUser.DoesNotExist:
            return Response(
                {'error': "Invalid user or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # check for wrong password
        if not user.check_password(password):
            return Response(
                {'error': "Invalid user or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = get_token(user)

        return Response({
            'message': "Login successful",
            'token': token,
            'username': user.username,
            'email': email
        })

class PatientRegistrationAPIView(generics.CreateAPIView):
    queryset = HospitalAppUser.objects.all()
    serializer_class = PatientRegistrationSerializer


class HospitalAdminRegistrationAPIView(generics.CreateAPIView):
    queryset = HospitalAppUser.objects.all()
    serializer_class = HospitalAdminRegistrationSerializer
    permission_classes = [IsAdminUser]


class ReceptionistRegistrationAPIView(generics.CreateAPIView):
    queryset = HospitalAppUser.objects.all()
    serializer_class = ReceptionistRegistrationSerializer
    permission_classes = [IsHospitalAdmin]


class DoctorRegistrationAPIView(generics.CreateAPIView):
    queryset = HospitalAppUser.objects.all()
    serializer_class = DoctorRegistrationSerializer
    permission_classes = [IsHospitalAdmin]


# Features View

# ----- Doctor Views -------
class DoctorListAPIView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_available']

class DoctorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsHospitalAdmin()]
        return [IsAuthenticated()]


# ------ Patient Views -----------
class PatientListAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [(IsHospitalAdmin | IsReceptionist)()]
        return [IsAuthenticated()]


# -------- Appointment Views ----------
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['doctor', 'patient', 'appointment_date']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [(IsHospitalAdmin | IsReceptionist | IsDoctor)()]
        return [IsAuthenticated()]


# -------- Medicine Views -----------
class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer

    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsHospitalAdmin()]
        return [IsAuthenticated()]


# -------- Prescription Views -------------
class PrescriptionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def get_permissions(self):
        # Requirement: Only Doctors can write/POST a prescription
        if self.request.method == 'POST':
            return [IsDoctor()]
        return [IsAuthenticated()]


# -------- Bill Views ---------------
class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [(IsHospitalAdmin | IsReceptionist)()]
        return [IsAuthenticated()]