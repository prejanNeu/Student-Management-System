from rest_framework import serializers 
from .models import Marksheet, ExamType
from account.models import CustomUser, Subject, ClassLevel

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'role']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']

class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = ['id', 'level']

class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = '__all__'

class MarksheetSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    student_id = serializers.IntegerField(write_only=True)
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.IntegerField(write_only=True)
    classlevel = ClassLevelSerializer(read_only=True)
    classlevel_id = serializers.IntegerField(write_only=True)
    examtype = ExamTypeSerializer(read_only=True)
    examtype_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Marksheet
        fields = [
            'id', 'student', 'student_id', 'classlevel', 'classlevel_id',
            'subject', 'subject_id', 'examtype', 'examtype_id',
            'full_marks', 'marks','date'
        ]
        read_only_fields = ['id', 'date']

    def validate(self, data):
        # Validate that marks cannot exceed full_marks
        if data.get('marks') and data.get('full_marks'):
            if data['marks'] > data['full_marks']:
                raise serializers.ValidationError("Marks cannot exceed full marks")
        
        # Validate that marks cannot be negative
        if data.get('marks') and data['marks'] < 0:
            raise serializers.ValidationError("Marks cannot be negative")
        
        # Validate that full_marks cannot be negative
        if data.get('full_marks') and data['full_marks'] < 0:
            raise serializers.ValidationError("Full marks cannot be negative")
        
        return data

    def create(self, validated_data):
        # Extract the IDs and create the marksheet
        student_id = validated_data.pop('student_id')
        subject_id = validated_data.pop('subject_id')
        classlevel_id = validated_data.pop('classlevel_id')
        examtype_id = validated_data.pop('examtype_id')
        
        # Get the actual objects
        student = CustomUser.objects.get(id=student_id)
        subject = Subject.objects.get(id=subject_id)
        classlevel = ClassLevel.objects.get(id=classlevel_id)
        examtype = ExamType.objects.get(id=examtype_id)
        
        # Create the marksheet
        marksheet = Marksheet.objects.create(
            student=student,
            subject=subject,
            classlevel=classlevel,
            examtype=examtype,
            **validated_data
        )
        return marksheet

class MarksheetListSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    classlevel = ClassLevelSerializer(read_only=True)
    examtype = ExamTypeSerializer(read_only=True)
    percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Marksheet
        fields = [
            'id', 'student', 'classlevel', 'subject', 'examtype',
            'full_marks', 'marks', 'date', 'percentage'
        ]
    
    def get_percentage(self, obj):
        if obj.full_marks > 0:
            return round((obj.marks / obj.full_marks) * 100, 2)
        return 0



