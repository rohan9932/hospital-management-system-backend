from rest_framework import generics, request, status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.serializers import LoginSerializer, DoctorSerializer, PatientSerializer
from api.models import HospitalAppUser, Doctor, Patient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend


# AUTH View
def get_token(user):
    token = RefreshToken.for_user(user)
    return {
        'refresh': str(token),
        'access': str(token.access_token)
    }


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, *args, **kwargs):
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


# Features View
class DoctorListAPIView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_available']

class DoctorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class PatientListAPIView(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
