from rest_framework import serializers
from .models import Student
from django.conf import settings 
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from account.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from account.models import ClassLevel, StudentClassEnrollment, Subject, ClassSubject, CustomUser
from marksheet.models import Marksheet, ExamType
from attendance.models import Attendance
from assignment.models import Assignment
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'role', 'is_active', 'email']

class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = ["id", "level"]

class StudentClassEnrollmentSerializer(serializers.ModelSerializer):
    class_level_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(), source='class_level'
    )

    class Meta:
        model = StudentClassEnrollment
        fields = ['id', 'class_level_id', 'is_current']

class StudentEditSerializer(serializers.ModelSerializer):
    class_enrollments = StudentClassEnrollmentSerializer(many=True)
    class Meta:
        model = User
        fields = ["id", "full_name", "is_active", "email", "class_enrollments"]

    def update(self, instance, validated_data):
        enrollments_data = validated_data.pop('class_enrollments', [])

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create enrollments
        for enrollment_data in enrollments_data:
            enrollment_id = enrollment_data.pop("id", None)
            class_level = enrollment_data.get("class_level")

            if enrollment_id:
                # Update existing enrollment
                enrollment = StudentClassEnrollment.objects.get(
                    id=enrollment_id, student=instance
                )
                for key, val in enrollment_data.items():
                    setattr(enrollment, key, val)
                enrollment.save()

            else:
                # --- Promotion Logic ---
                # Mark all old enrollments as not current
                if enrollment_data.get("is_current", True):
                    StudentClassEnrollment.objects.filter(
                        student=instance, is_current=True
                    ).update(is_current=False)

                # Create or update the new enrollment
                StudentClassEnrollment.objects.update_or_create(
                    student=instance,
                    class_level=class_level,
                    defaults={"is_current": enrollment_data.get("is_current", True)},
                )

        return instance

class StudentCurrentClassSerializer(serializers.ModelSerializer):
    current_class = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "is_active", "email", "current_class"]

    def get_current_class(self, obj):
        current = obj.class_enrollments.filter(is_current=True).first()
        return StudentClassEnrollmentSerializer(current).data if current else None

# ========== DASHBOARD SERIALIZERS ==========

# -------- ADMIN DASHBOARD --------
class ClassAttendanceSerializer(serializers.Serializer):
    class_id = serializers.IntegerField()
    class_name = serializers.CharField()
    level = serializers.IntegerField()
    student_count = serializers.IntegerField()
    average_attendance = serializers.FloatField()
    attendance_trend = serializers.ListField()  # Last 7 days data

class RecentActivitySerializer(serializers.Serializer):
    type = serializers.CharField()  # 'assignment', 'attendance', 'marks'
    title = serializers.CharField()
    description = serializers.CharField()
    date = serializers.DateTimeField()
    class_name = serializers.CharField(allow_null=True)

class AdminDashboardSerializer(serializers.Serializer):
    # Overview Cards
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_classes = serializers.IntegerField()
    total_assignments = serializers.IntegerField()
    
    # Charts Data
    class_attendance = ClassAttendanceSerializer(many=True)
    recent_activities = RecentActivitySerializer(many=True)
    
    # Statistics
    overall_attendance_rate = serializers.FloatField()
    active_assignments = serializers.IntegerField()
    pending_assignments = serializers.IntegerField()
    
    # Quick Stats
    students_this_month = serializers.IntegerField()
    teachers_this_month = serializers.IntegerField()

# -------- TEACHER DASHBOARD --------
class AssignmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subject = serializers.CharField(allow_null=True)
    class_name = serializers.CharField(allow_null=True)
    deadline = serializers.DateField()
    created_at = serializers.DateTimeField()
    submission_count = serializers.IntegerField()
    total_students = serializers.IntegerField()

class ClassPerformanceSerializer(serializers.Serializer):
    class_id = serializers.IntegerField()
    class_name = serializers.CharField()
    level = serializers.IntegerField()
    student_count = serializers.IntegerField()
    average_attendance = serializers.FloatField()
    average_marks = serializers.FloatField(allow_null=True)
    assignments_count = serializers.IntegerField()

class TeacherDashboardSerializer(serializers.Serializer):
    # Overview Cards
    total_classes = serializers.IntegerField()
    total_assignments = serializers.IntegerField()
    total_students = serializers.IntegerField()
    active_assignments = serializers.IntegerField()
    
    # Recent Assignments
    recent_assignments = AssignmentSerializer(many=True)
    
    # Class Performance
    class_performance = ClassPerformanceSerializer(many=True)
    
    # Statistics
    assignments_due_today = serializers.IntegerField()
    assignments_due_this_week = serializers.IntegerField()
    average_class_attendance = serializers.FloatField()
    
    # Quick Actions
    upcoming_deadlines = AssignmentSerializer(many=True)

# -------- STUDENT DASHBOARD --------
class SubjectMarksSerializer(serializers.Serializer):
    subject_name = serializers.CharField()
    marks_obtained = serializers.DecimalField(max_digits=5, decimal_places=2)
    full_marks = serializers.DecimalField(max_digits=5, decimal_places=2)
    percentage = serializers.FloatField()
    exam_type = serializers.CharField(allow_null=True)
    date = serializers.DateField()

class AssignmentDueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subject = serializers.CharField(allow_null=True)
    deadline = serializers.DateField()
    days_remaining = serializers.IntegerField()
    is_overdue = serializers.BooleanField()

class AttendanceStatsSerializer(serializers.Serializer):
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    percentage = serializers.FloatField()
    attendance_trend = serializers.ListField()  # Last 30 days

class StudentDashboardSerializer(serializers.Serializer):
    # Student Info
    student_name = serializers.CharField()
    current_class = ClassLevelSerializer(allow_null=True)
    student_id = serializers.IntegerField()
    
    # Overview Cards
    attendance_percentage = serializers.FloatField()
    assignments_due = serializers.IntegerField()
    assignments_overdue = serializers.IntegerField()
    average_marks = serializers.FloatField(allow_null=True)
    
    # Detailed Data
    attendance_stats = AttendanceStatsSerializer()
    recent_marks = SubjectMarksSerializer(many=True)
    assignments_due_list = AssignmentDueSerializer(many=True)
    
    # Performance Trends
    marks_trend = serializers.ListField()  # Last 5 exams
    attendance_trend = serializers.ListField()  # Last 30 days
    
    # Quick Stats
    total_subjects = serializers.IntegerField()
    completed_assignments = serializers.IntegerField()
    upcoming_exams = serializers.IntegerField()
