from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_doctor


class IsNurse(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_nurse


class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_receptionist


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_patient


class IsAdminOrDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_doctor
        )


class IsAdminOrReceptionist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_receptionist
        )


class IsMedicalStaff(BasePermission):
    """Doctor or Nurse"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_doctor or request.user.is_nurse
        )