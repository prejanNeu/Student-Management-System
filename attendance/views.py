
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
from .models import Attendance, AuthorizedDevice
from account.models import StudentClassEnrollment, CustomUser
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated
from .serializers import AttendanceSerializer, StudentSerializer
from django.db import IntegrityError
from account.models import ClassLevel, ClassSubject, Subject
from attendance.serializers import ClassLevelSerializer, SubjectOnlySerializer, MarkAttendanceSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
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
    if request.user.role == "teacher" or request.user.role == "admin":
        students = []

        objs = StudentClassEnrollment.objects.filter(class_level_id=classlevel, is_current=True)

        for obj in objs:
            student = obj.student
            students.append(student)  

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response({"message": "You are not teacher or admin"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_attendance_detail_by_id(request, id):
    # if request.user.role not in ["teacher", "admin"]:
    #     return Response(
    #         {"message": "You are not authorized to view attendance details."},
    #         status=status.HTTP_403_FORBIDDEN
    #     )

    # Get the user
    obj = CustomUser.objects.filter(id=id).first()

    if not obj:
        return Response(
            {"message": "Student not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if obj.role != "student":
        return Response(
            {"message": "Invalid user role. Expected a student."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    studentclass = StudentClassEnrollment.objects.filter(student=obj, is_current=True).first()
    # Get the student's current class level
    classlevel = studentclass.class_level

    if not classlevel:
        return Response(
            {"message": "Current class level not found for this student."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get attendance data
    attendance_data = Attendance.objects.filter(student=obj, classlevel=classlevel)

    serializer = AttendanceSerializer(attendance_data, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

        
@api_view(['POST'])
def mark_attendance_by_id(request):
    try:
        serializer = MarkAttendanceSerializer(data=request.data)
        device_key = request.headers.get('X-DEVICE-ID')

        if not device_key:
            return Response({'error': 'Missing device key'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = AuthorizedDevice.objects.get(device_id=device_key, is_active=True)
        except AuthorizedDevice.DoesNotExist:
            return Response({'error': 'Unauthorized device'}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            student_id = serializer.validated_data['student_id']

            try:
                student = CustomUser.objects.get(id=student_id, role='student')
            except CustomUser.DoesNotExist:
                return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

            enrollment = StudentClassEnrollment.objects.filter(student=student, is_current=True).first()
            if not enrollment:
                return Response({"error": "Student is not enrolled in any current class."}, status=status.HTTP_400_BAD_REQUEST)

            class_level = enrollment.class_level
            today = timezone.now().date()

            if Attendance.objects.filter(student=student, classlevel=class_level, date=today).exists():
                return Response({"message": "Attendance already marked."}, status=status.HTTP_200_OK)

            Attendance.objects.create(student=student, classlevel=class_level, status="present", date=today)

            return Response({"message": "Attendance marked successfully."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Also shows full traceback in your logs
        return Response({"error": "Internal Server Error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
