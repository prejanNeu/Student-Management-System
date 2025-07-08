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
    
    



