from rest_framework import serializers
from .models import Student
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from account.serializers import RegisterSerializer

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'date_of_birth', 'father_name', 'image', 'user']
        read_only_fields = ['user']
        
    
class RegisterStudentRequestSerializer(serializers.Serializer):
    user = RegisterSerializer()
    student = StudentSerializer()

    def to_internal_value(self, data):
        # manually build nested structure from flattened form-data
        user_data = {}
        student_data = {}

        for key in data:
            if key.startswith('user.'):
                user_data[key[5:]] = data.get(key)
            elif key.startswith('student.'):
                student_data[key[8:]] = data.get(key)

        # handle file field separately
        if 'student.image' in data:
            student_data['image'] = data.get('student.image')

        return {
            'user': user_data,
            'student': student_data
        }

    def create(self, validated_data):
        user_data = validated_data.get('user')
        student_data = validated_data.get('student')

        user = User.objects.create_user(**user_data)
        student = Student.objects.create(user=user, **student_data)
        return {
            "user": user,
            "student": student
        }
    
    



