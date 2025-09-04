from rest_framework import serializers
from .models import Assignment
from django.contrib.auth import get_user_model


User = get_user_model()
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = [
            'id',
            'title',
            'assignment',
            'classlevel',
            'subject',
            'deadline',
            'created_at',
            'teacher',
        ]
        read_only_fields = ['created_at']


class AssignmentListDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment 
        fields = ["classlevel", 'subject']
        
        
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','full_name','role', 'is_active','email']


