
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
from .models import Attendance 
from account.models import StudentClassEnrollment
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated
from .serializers import AttendanceSerializer
from django.db import IntegrityError


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def attendance_detail(request):

    user = request.user

    if user.role == "student" and user.is_active:

        student = user
        # Get the student's current class level
        current_enrollment = StudentClassEnrollment.objects.filter(student=student, is_current=True).first()

        if current_enrollment:
            attendance_details = Attendance.objects.filter(student=student, classlevel=current_enrollment.class_level)

            serializer = AttendanceSerializer(attendance_details, many=True)

            return Response({
                "details":serializer.data,
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "detail": "No current class enrollment found for this student."
            }, status=status.HTTP_404_NOT_FOUND)

    else:
        return Response({
            "detail": "Unauthorized or inactive user."
        }, status=status.HTTP_403_FORBIDDEN)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):

    user = request.user 
    if user.role == "student" and user.is_active :
        current_class = StudentClassEnrollment.objects.filter(student=user).first().class_level
        if current_class:

            try:
                obj = Attendance.objects.create(student = user, classlevel=current_class)
                obj.save()

            except IntegrityError:
                return Response({"message":"You are aleady present "}, status=status.HTTP_400_BAD_REQUEST)


        else:
            return Response({"message":"No class enrollment found"}, status=status.HTTP_404_NOT_FOUND)
    else :
        return Response({"message":"No Student found "},status=status.HTTP_400_BAD_REQUEST)

    return Response({"message":"attendance mark successfully "}, status=status.HTTP_201_CREATED)






        