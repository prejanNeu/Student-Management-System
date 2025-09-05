from rest_framework import serializers
from .models import Student
from django.conf import settings 
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from account.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from marksheet.serializers import ClassLevelSerializer

from account.models import ClassLevel, StudentClassEnrollment

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
