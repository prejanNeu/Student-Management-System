from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import Student
from .serializers import  UserInfoSerializer
from django.contrib.auth import get_user_model
from .serializers import UserInfoSerializer
from account.models import ClassLevel, StudentClassEnrollment, Subject, ClassSubject


User = get_user_model()


@swagger_auto_schema(method='get', responses={200: 'Student details'})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def studentDetail(request):
    user = request.user
    # Check if the student object exists for this user
    if user.role == "student":
        user_data = UserInfoSerializer(user).data

    else :
        return Response({"message":"user is not student "}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "data":user_data
    }, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def home(request):
    return Response({"message":"Bro add swagger to the end point of the url"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_list(request, classlevel):
    classobj = get_object_or_404(ClassLevel, level=classlevel)

    # Filter students enrolled in this class
    enrolled_students = User.objects.filter(
        role="student",
        class_enrollments__class_level=classobj
    ).distinct()

    serializer = UserInfoSerializer(enrolled_students, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
