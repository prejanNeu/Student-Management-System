from rest_framework import serializers
from .models import Student
from django.conf import settings 
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from account.serializers import RegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','full_name','role', 'is_active','email']







