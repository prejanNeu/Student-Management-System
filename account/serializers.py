from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from .models import UserPhoto
from .models import ClassLevel, StudentClassEnrollment

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],  # add queryset=
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(
        choices=[('student', 'Student'), ('teacher', 'Teacher'), ('admin', 'Admin')],
        default='student'
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'password2', 'full_name', 'role', 'gender']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)  # corrected UserL to User
        user.set_password(password)
        user.save()
        return user
    
    
class UserPhotoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserPhoto
        fields = ['id','user','user_image']
        read_only_fields = ['id','user']

class GetUserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoto
        fields = ["user_image"]

class RegisterUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()  # explicitly include for Swagger schema
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'gender']  # exclude password fields for safety

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    

class UserIdSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    
    



class StudentRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(
        choices=[('student', 'Student')],
        default='student'
    )

    # optionally allow frontend to send class level id
    class_level_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'password2',
            'full_name', 'role', 'gender', 'class_level_id'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # Remove unnecessary fields
        validated_data.pop('password2')
        class_level_id = validated_data.pop('class_level_id', None)
        password = validated_data.pop('password')

        # Create user
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Determine class level
        if class_level_id:
            class_level = ClassLevel.objects.get(id=class_level_id)
        else:
            # Default to first class level or any logic you prefer
            class_level = ClassLevel.objects.first()

        # Create student enrollment record
        StudentClassEnrollment.objects.create(
            student=user,
            class_level=class_level,
            is_current=True
        )

        return user