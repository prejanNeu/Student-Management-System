
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
from .models import Attendance 
from account.models import StudentClassEnrollment
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated
from .serializers import AttendanceSerializer, StudentSerializer
from django.db import IntegrityError
from account.models import ClassLevel, ClassSubject, Subject
from attendance.serializers import ClassLevelSerializer, SubjectOnlySerializer


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
    



def student_attendance(request, classlevel):

    if request.role == "teacher" or request.role == "admin":

        classlevel = ClassLevel.objects.get(id=classlevel)
        list = Attendance.objects.filter(classlevel=classlevel)


    
    
    


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


@api_view(["GET"])
def class_list(request):

    objs = ClassLevel.objects.all()

    serializer = ClassLevelSerializer(objs, many=True)

    return Response(serializer.data, status= status.HTTP_200_OK)


@api_view(["GET"])
def subject_list(request, classlevel):
    if not classlevel:
        return Response({"message": "class level required"}, status=status.HTTP_400_BAD_REQUEST)

    # Get all related subject IDs
    subject_ids = ClassSubject.objects.filter(class_level_id=classlevel).values_list("subject_id", flat=True).distinct()

    # Fetch unique subjects
    subjects = Subject.objects.filter(id__in=subject_ids)

    serializer = SubjectOnlySerializer(subjects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(["GET"])
def get_student_by_class(request, classlevel):
    if request.role == "teacher" or request.role == "admin":
        students = []

        objs = StudentClassEnrollment.objects.filter(classlevel_id=classlevel, is_current=True)

        for obj in objs:
            student = obj.student
            students.append(student)  

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response({"message": "You are not teacher or admin"}, status=status.HTTP_400_BAD_REQUEST)




        