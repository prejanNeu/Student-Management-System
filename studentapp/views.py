from django.shortcuts import render
from django.http import HttpResponse
from .models import Student 
from rest_framework.response import Response 
from account.serializers import RegisterSerializer
from rest_framework import status 
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from .models import Student
from .serializers import StudentSerializer,RegisterStudentRequestSerializer, UserInfoSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction 

@swagger_auto_schema(method='post', request_body=RegisterStudentRequestSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def register_student(request):
    # Flattened multipart/form-data → build nested dictionaries
    user_data = {}
    student_data = {}

    for key in request.data:
        if key.startswith('user.'):
            user_data[key[5:]] = request.data.get(key)
        elif key.startswith('student.'):
            student_data[key[8:]] = request.data.get(key)

    # Handle file upload explicitly
    if 'student.image' in request.FILES:
        student_data['image'] = request.FILES['student.image']

    if not user_data or not student_data:
        return Response({"detail": "Both 'user' and 'student' fields are required."}, status=400)

    with transaction.atomic():
        user_serializer = RegisterSerializer(data=user_data)
        if not user_serializer.is_valid():
            return Response({"user_errors": user_serializer.errors}, status=400)
        
        user = user_serializer.save()

        student_serializer = StudentSerializer(data=student_data)
        if not student_serializer.is_valid():
            transaction.set_rollback(True)
            return Response({"student_errors": student_serializer.errors}, status=400)
        
        student = student_serializer.save(user=user)

    return Response({
        "message": "User and Student registered successfully",
        "student": StudentSerializer(student).data
    }, status=201)

def home(request):
    return HttpResponse("Bro Maile API haru rakhdya xu end point ma gayera swagger type garera hernu hai ")




@permission_classes([IsAuthenticated])
@api_view(['GET'])
def studentDetail(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'}, status=401)

    
    user = request.user
    student = Student.objects.filter(user=user).first()
        
    if not student:
        return Response({'detail': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer1 = StudentSerializer(student)
    serializer2 = UserInfoSerializer(student.user)
    
    return Response({
        "student": serializer1.data,
        "user": serializer2.data
    }, status=status.HTTP_200_OK)

    
    
        
        
        
        
        
    
    