from rest_framework import serializers 
from .models import Attendance 
import nepali_datetime
from rest_framework import serializers
from .models import Attendance
import nepali_datetime
from account.models import ClassLevel, ClassSubject, Subject
from account.models import CustomUser

class AttendanceSerializer(serializers.ModelSerializer):
    nepali_date = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['nepali_date', 'status']

    def get_nepali_date(self, obj):
        ad_date = obj.date
        bs_date = nepali_datetime.date.from_datetime_date(ad_date)
        return f"{bs_date.year}-{bs_date.month:02d}-{bs_date.day:02d}"
    

class ClassLevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassLevel
        fields = ["id", "level"]


class SubjectOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

class StudentSerializer(serializers.ModelSerializer):
    current_class = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "full_name", "email", "current_class"]

    def get_current_class(self, obj):
        enrollment = obj.class_enrollments.filter(is_current=True).first()
        if enrollment:
            return ClassLevelSerializer(enrollment.class_level).data
        return None

class MarkAttendanceSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
        

