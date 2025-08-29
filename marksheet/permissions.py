from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsTeacherUser(permissions.BasePermission):
    """
    Custom permission to only allow teacher users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

class IsStudentUser(permissions.BasePermission):
    """
    Custom permission to only allow student users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsAdminOrTeacher(permissions.BasePermission):
    """
    Custom permission to allow admin or teacher users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher']

class IsAdminOrTeacherOrStudent(permissions.BasePermission):
    """
    Custom permission to allow admin, teacher, or student users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher', 'student']

class CanViewMarks(permissions.BasePermission):
    """
    Custom permission to check if user can view marks.
    Admin and teachers can view all marks.
    Students can only view their own marks.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher', 'student']

    def has_object_permission(self, request, view, obj):
        # Admin and teachers can view all marks
        if request.user.role in ['admin', 'teacher']:
            return True
        # Students can only view their own marks
        return obj.student == request.user

class CanModifyMarks(permissions.BasePermission):
    """
    Custom permission to check if user can modify marks.
    Only admin and teachers can modify marks.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher'] 