from rest_framework import serializers
from .models import Assignment

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


