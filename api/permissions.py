from rest_framework.permissions import BasePermission

# custom permission users
class IsHospitalAdmin(BasePermission):
    def has_permission(self, request, view):
        # ensure logged in
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role == 'admin'


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role == 'doctor'


class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role == 'receptionist'
