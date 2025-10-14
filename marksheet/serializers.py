from rest_framework import serializers 
from .models import Marksheet, ExamType, ClassParticipation
from account.models import CustomUser, Subject, ClassLevel
from django.contrib.auth import get_user_model
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
    
    
class ClassParticipationSerializer(serializers.ModelSerializer):
    """
    Serializer for ClassParticipation model with full CRUD support.
    Handles creation, reading, updating, and deletion of class participation records.
    """
    # Nested serializers for output (read-only)
    student = UserSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    classlevel = ClassLevelSerializer(read_only=True)
    added_by = UserSerializer(read_only=True)

    # Writable fields for input
    student_id = serializers.IntegerField(write_only=True)
    subject_id = serializers.IntegerField(write_only=True)
    classlevel_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ClassParticipation
        fields = [
            "id",
            "student", "subject", "classlevel", "added_by",  # read-only nested
            "student_id", "subject_id", "classlevel_id",  # write-only IDs
            "mark",
            "added_at"
        ]
        read_only_fields = ['id', 'added_at', 'added_by']

    def validate_mark(self, value):
        """
        Validate that the mark is within the allowed range (0-5).
        """
        if value < 0 or value > 5:
            raise serializers.ValidationError("Mark must be between 0 and 5.")
        return value

    def validate(self, data):
        """
        Validate the entire data set for class participation.
        """
        # Check if student exists
        try:
            student = CustomUser.objects.get(id=data['student_id'])
            if student.role != 'student':
                raise serializers.ValidationError("Selected user is not a student.")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Student does not exist.")

        # Check if subject exists
        try:
            Subject.objects.get(id=data['subject_id'])
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Subject does not exist.")

        # Check if class level exists
        try:
            ClassLevel.objects.get(id=data['classlevel_id'])
        except ClassLevel.DoesNotExist:
            raise serializers.ValidationError("Class level does not exist.")

        # Check for duplicate participation record
        if not self.instance:  # Only check for duplicates during creation
            if ClassParticipation.objects.filter(
                student_id=data['student_id'],
                classlevel_id=data['classlevel_id'],
                subject_id=data['subject_id']
            ).exists():
                raise serializers.ValidationError(
                    "A participation record already exists for this student in this class and subject."
                )

        return data

    def create(self, validated_data):
        """
        Create a new class participation record.
        """
        # Extract IDs
        student_id = validated_data.pop('student_id')
        subject_id = validated_data.pop('subject_id')
        classlevel_id = validated_data.pop('classlevel_id')

        # Get the actual objects
        student = CustomUser.objects.get(id=student_id)
        subject = Subject.objects.get(id=subject_id)
        classlevel = ClassLevel.objects.get(id=classlevel_id)

        # Create the participation record
        participation = ClassParticipation.objects.create(
            student=student,
            subject=subject,
            classlevel=classlevel,
            added_by=self.context['request'].user,  # Set the user who added the record
            **validated_data
        )
        return participation

    def update(self, instance, validated_data):
        """
        Update an existing class participation record.
        """
        # Extract IDs if provided
        student_id = validated_data.pop('student_id', None)
        subject_id = validated_data.pop('subject_id', None)
        classlevel_id = validated_data.pop('classlevel_id', None)

        # Update related objects if provided
        if student_id:
            instance.student = CustomUser.objects.get(id=student_id)
        if subject_id:
            instance.subject = Subject.objects.get(id=subject_id)
        if classlevel_id:
            instance.classlevel = ClassLevel.objects.get(id=classlevel_id)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ClassParticipationListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for listing class participation records.
    Includes calculated fields and summary information.
    """
    student = UserSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    classlevel = ClassLevelSerializer(read_only=True)
    added_by = UserSerializer(read_only=True)
    
    # Calculated fields
    grade_description = serializers.SerializerMethodField()
    is_excellent = serializers.SerializerMethodField()

    class Meta:
        model = ClassParticipation
        fields = [
            "id",
            "student", "subject", "classlevel", "added_by",
            "mark", "grade_description", "is_excellent",
            "added_at"
        ]

    def get_grade_description(self, obj):
        """
        Get a descriptive text for the participation grade.
        """
        grade_map = {
            0: "No participation",
            1: "Very poor",
            2: "Poor", 
            3: "Average",
            4: "Good",
            5: "Excellent"
        }
        return grade_map.get(obj.mark, "Unknown")

    def get_is_excellent(self, obj):
        """
        Check if the participation grade is excellent (5).
        """
        return obj.mark == 5


class ClassParticipationCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for bulk creation of class participation records.
    """
    student_id = serializers.IntegerField()
    subject_id = serializers.IntegerField()
    classlevel_id = serializers.IntegerField()

    class Meta:
        model = ClassParticipation
        fields = ['student_id', 'subject_id', 'classlevel_id', 'mark']

    def validate_mark(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Mark must be between 0 and 5.")
        return value

    def validate(self, data):
        # Validate student exists and is a student
        try:
            student = CustomUser.objects.get(id=data['student_id'])
            if student.role != 'student':
                raise serializers.ValidationError("Selected user is not a student.")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Student does not exist.")

        # Validate subject exists
        try:
            Subject.objects.get(id=data['subject_id'])
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Subject does not exist.")

        # Validate class level exists
        try:
            ClassLevel.objects.get(id=data['classlevel_id'])
        except ClassLevel.DoesNotExist:
            raise serializers.ValidationError("Class level does not exist.")

        return data

    def create(self, validated_data):
        student_id = validated_data.pop('student_id')
        subject_id = validated_data.pop('subject_id')
        classlevel_id = validated_data.pop('classlevel_id')

        student = CustomUser.objects.get(id=student_id)
        subject = Subject.objects.get(id=subject_id)
        classlevel = ClassLevel.objects.get(id=classlevel_id)

        participation = ClassParticipation.objects.create(
            student=student,
            subject=subject,
            classlevel=classlevel,
            added_by=self.context['request'].user,
            **validated_data
        )
        return participation
