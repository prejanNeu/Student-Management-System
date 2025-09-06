from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import Student
from .serializers import  UserInfoSerializer, StudentEditSerializer
from django.contrib.auth import get_user_model
from .serializers import UserInfoSerializer, StudentCurrentClassSerializer, AdminDashboardSerializer, TeacherDashboardSerializer, StudentDashboardSerializer
from account.models import ClassLevel, StudentClassEnrollment, Subject, ClassSubject, CustomUser
from marksheet.models import Marksheet
from attendance.models import Attendance 
from assignment.models import Assignment 


User = get_user_model()

@swagger_auto_schema(method='get', responses={200: 'Student details'})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userDetail(request):
    user = request.user
    # Check if the student object exists for this user
    user_data = UserInfoSerializer(user).data
    return Response({
        "data":user_data
    }, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def home(request):
    return Response({"message":"Bro add swagger to the end point of the url"})

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def student_list(request, classlevel):
    classobj = get_object_or_404(ClassLevel, level=classlevel)

    # Filter students enrolled in this class
    enrolled_students = User.objects.filter(
        role="student",
        class_enrollments__class_level=classobj
    ).distinct()

    serializer = UserInfoSerializer(enrolled_students, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="put",
    request_body=StudentEditSerializer,
    responses={200: StudentEditSerializer}
)
@api_view(['PUT'])
def update_student(request):
    user = get_object_or_404(User, id=request.data.get("id"))
    serializer = StudentEditSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(StudentCurrentClassSerializer(user).data, status=200)

    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    user = request.user

    print(user.role)
    
    if user.role == "admin":
        total_students = CustomUser.objects.filter(role="student").count()
        total_teachers = CustomUser.objects.filter(role="teacher").count()
        total_classes = ClassLevel.objects.count()
        total_assignments = Assignment.objects.count()

        # Average attendance per class
        class_attendance = []
        classes = ClassLevel.objects.all()
        for cls in classes:
            total_days = Attendance.objects.filter(classlevel=cls).count()
            present_days = Attendance.objects.filter(classlevel=cls, status="present").count()
            avg_attendance = (present_days) if total_days > 0 else 0
            class_attendance.append({
                "class_id": cls.id,
                "level": cls.level,
                "average_attendance": round(avg_attendance, 2)
            })

        data = {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_classes": total_classes,
            "total_assignments": total_assignments,
            "class_attendance": class_attendance
        }
        serializer = AdminDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ----- TEACHER -----
    elif user.role == "teacher":
        teacher_assignments = Assignment.objects.filter(teacher=user).order_by("-created_at")[:5]
        recent = [{"title": a.title, "deadline": a.deadline, "class": a.classlevel.level if a.classlevel else None} for a in teacher_assignments]

        classes_count = Assignment.objects.filter(teacher=user).values("classlevel").distinct().count()
        students_count = StudentClassEnrollment.objects.filter(class_level__subjects__classsubject__class_level__assignments__teacher=user).count()

        data = {
            "total_classes": classes_count,
            "total_assignments": teacher_assignments.count(),
            "recent_assignments": recent,
            "students_count": students_count,
        }
        serializer = TeacherDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ----- STUDENT -----
    elif user.role == "student":
        enrollment = StudentClassEnrollment.objects.filter(student=user, is_current=True).first()
        current_class = enrollment.class_level if enrollment else None

        # Attendance %
        total_days = Attendance.objects.filter(student=user).count()
        present_days = Attendance.objects.filter(student=user, status="present").count()
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

        # Assignments due
        assignments_due = Assignment.objects.filter(classlevel=current_class).count()

        # Recent marks
        marks = Marksheet.objects.filter(student=user).order_by("-date")[:5]
        recent_marks = [{"subject": m.subject.name if m.subject else None, "marks": m.marks, "full": m.full_marks} for m in marks]

        data = {
            "current_class": {"id": current_class.id, "level": current_class.level} if current_class else None,
            "attendance_percentage": attendance_percentage,
            "assignments_due": assignments_due,
            "recent_marks": recent_marks,
        }
        serializer = StudentDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        return Response({"detail": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)
