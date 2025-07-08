from django.shortcuts import render
from django.http import HttpResponse
from .models import Student 
from rest_framework.response import Response 
from account.serializers import RegisterSerializer
from rest_framework import status 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.models import User
from .models import Student
from .serializers import StudentSerializer,RegisterStudentRequestSerializer, UserInfoSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction 


@swagger_auto_schema(method='post', request_body=RegisterStudentRequestSerializer)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_student(request):
    user_data = request.data.get('user')
    student_data = request.data.get('student')

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
    return HttpResponse("You are in Home Page")

@api_view(['GET'])
def studentDetails(request,pk):
    student = Student.objects.filter(id=pk).first()
    
    
        
    if not student:
        return Response({'detail': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    user = student.user 
    
    serializer1 = StudentSerializer(student)
    serializer2 = UserInfoSerializer(student.user)
    
    
    return Response({
        "student": serializer1.data,
        "user": serializer2.data
    }, status=status.HTTP_200_OK)


    
    
    
    
        
        
        
        
        
    
    