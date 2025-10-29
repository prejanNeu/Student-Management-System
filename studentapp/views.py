from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import Student
from django.shortcuts import redirect 
from .serializers import (
    UserInfoSerializer, StudentEditSerializer, StudentCurrentClassSerializer, 
    AdminDashboardSerializer, TeacherDashboardSerializer, StudentDashboardSerializer,
    ClassAttendanceSerializer, RecentActivitySerializer, AssignmentSerializer,
    ClassPerformanceSerializer, SubjectMarksSerializer, AssignmentDueSerializer,
    AttendanceStatsSerializer, ClassLevelSerializer
)
from django.contrib.auth import get_user_model
from account.models import ClassLevel, StudentClassEnrollment, Subject, ClassSubject, CustomUser
from marksheet.models import Marksheet, ExamType
from attendance.models import Attendance 
from assignment.models import Assignment, AssignmentSubmission
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncDate
from studentapp.utils.score_prediction_utils import (
    get_attendance_detail,
    get_total_assignment_marks,
    get_internal_assesment_marks,
    get_gender,
    get_eca,
    get_internet_access,
    get_parent_education_level,
    get_internal_marks,
    get_past_mark,
    get_study_hour_per_week,
) 
from studentapp.utils.student_dashboard_utils import get_dashboard

from django.contrib.auth.decorators import login_required
User = get_user_model()

@swagger_auto_schema(method='get', responses={200: 'Student details'})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userDetail(request):
    user = request.user
    user_data = UserInfoSerializer(user).data
    return Response({
        "data": user_data
    }, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def home(request):
    
    return Response({"message": "Bro add swagger to the end point of the url"})

@api_view(['POST'])
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

def get_attendance_trend(class_level, days=7):
    """Get attendance trend for the last N days"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    trend_data = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        total_students = StudentClassEnrollment.objects.filter(
            class_level=class_level, is_current=True
        ).count()
        
        if total_students > 0:
            present_count = Attendance.objects.filter(
                classlevel=class_level, 
                date=current_date, 
                status='present'
            ).count()
            attendance_rate = (present_count / total_students) * 100
        else:
            attendance_rate = 0
            
        trend_data.append({
            'date': current_date.isoformat(),
            'attendance_rate': round(attendance_rate, 2)
        })
    
    return trend_data

def get_recent_activities():
    """Get recent activities across the system"""
    activities = []
    
    # Recent assignments
    recent_assignments = Assignment.objects.order_by('-created_at')[:5]
    for assignment in recent_assignments:
        activities.append({
            'type': 'assignment',
            'title': assignment.title,
            'description': f"New assignment created for Class {assignment.classlevel.level if assignment.classlevel else 'N/A'}",
            'date': assignment.created_at,  # This is timezone-aware
            'class_name': f"Class {assignment.classlevel.level}" if assignment.classlevel else None
        })
    
    # Recent marks entries
    recent_marks = Marksheet.objects.order_by('-date')[:5]
    for mark in recent_marks:
        # Convert date to timezone-aware datetime for consistent comparison
        mark_datetime = timezone.make_aware(
            datetime.combine(mark.date, datetime.min.time())
        )
        activities.append({
            'type': 'marks',
            'title': f"Marks added for {mark.subject.name if mark.subject else 'Unknown Subject'}",
            'description': f"{mark.student.full_name} scored {mark.marks}/{mark.full_marks}",
            'date': mark_datetime,  # Now timezone-aware
            'class_name': f"Class {mark.classlevel.level}" if mark.classlevel else None
        })
    
    # Sort by date and return top 10
    activities.sort(key=lambda x: x['date'], reverse=True)
    return activities[:10]

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    user = request.user
    
    if user.role == "admin":
        return get_admin_dashboard()
    elif user.role == "teacher":
        return get_admin_dashboard()
    else:
        return Response({"detail": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

def get_admin_dashboard():
    """Comprehensive admin dashboard"""
    # Basic counts
    total_students = CustomUser.objects.filter(role="student").count()
    total_teachers = CustomUser.objects.filter(role="teacher").count()
    total_classes = ClassLevel.objects.count()
    total_assignments = Assignment.objects.count()
    
    # Calculate overall attendance rate
    total_attendance_records = Attendance.objects.count()
    present_records = Attendance.objects.filter(status="present").count()
    overall_attendance_rate = (present_records / total_attendance_records * 100) if total_attendance_records > 0 else 0
    
    # Active and pending assignments
    today = timezone.now().date()
    active_assignments = Assignment.objects.filter(deadline__gte=today).count()
    pending_assignments = Assignment.objects.filter(deadline__lt=today).count()
    
    # Students and teachers added this month
    this_month = timezone.now().replace(day=1)
    try:
        students_this_month = CustomUser.objects.filter(
            role="student", 
            date_joined__gte=this_month
        ).count()
        teachers_this_month = CustomUser.objects.filter(
            role="teacher", 
            date_joined__gte=this_month
        ).count()
    except:
        # Fallback if date_joined field doesn't exist yet
        students_this_month = 0
        teachers_this_month = 0
    
    # Class attendance data
    class_attendance = []
    classes = ClassLevel.objects.all()
    for cls in classes:
        # Get students in this class
        student_count = StudentClassEnrollment.objects.filter(
            class_level=cls, is_current=True
        ).count()
        
        # Calculate average attendance
        total_days = Attendance.objects.filter(classlevel=cls).count()
        present_days = Attendance.objects.filter(classlevel=cls, status="present").count()
        avg_attendance = (present_days / total_days * 100) if total_days > 0 else 0
        
        # Get attendance trend
        attendance_trend = get_attendance_trend(cls, 7)
        
        class_attendance.append({
            "class_id": cls.id,
            "class_name": f"Class {cls.level}",
            "level": cls.level,
            "student_count": student_count,
            "average_attendance": round(avg_attendance, 2),
            "attendance_trend": attendance_trend
        })
    
    # Recent activities
    recent_activities = get_recent_activities()
    
    data = {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_classes": total_classes,
        "total_assignments": total_assignments,
        "class_attendance": class_attendance,
        "recent_activities": recent_activities,
        "overall_attendance_rate": round(overall_attendance_rate, 2),
        "active_assignments": active_assignments,
        "pending_assignments": pending_assignments,
        "students_this_month": students_this_month,
        "teachers_this_month": teachers_this_month
    }
    
    serializer = AdminDashboardSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET'])
def studentMarkPrediction(request):
    
    if request.user.role == "student":
        id = request.user.id 
        
        
        
        data = {
            "Gender": get_gender(id),
            "Study_Hours_per_Week": get_study_hour_per_week(id),
            "Attendance_Rate": get_attendance_detail(id),
            "Past_Exam_Scores": get_past_mark(id),
            "Parental_Education_Level": get_parent_education_level(id),
            "Internet_Access_at_Home": get_internet_access(id),
            "Extracurricular_Activities": get_eca(id),
            "Internal_Marks": get_internal_marks(id),
            "Assignment_Submission_Rate": get_total_assignment_marks(id),
            "Internal_Assessment_Marks": get_internal_assesment_marks(id)
        }
        

    return Response(data)



@api_view(['GET'])
def studentMarkPredictionById(request, id):
    
    data = {
        "Gender": get_gender(id),
        "Study_Hours_per_Week": get_study_hour_per_week(id),
        "Attendance_Rate": get_attendance_detail(id),
        "Past_Exam_Scores": get_past_mark(id),
        "Parental_Education_Level": get_parent_education_level(id),
        "Internet_Access_at_Home": get_internet_access(id),
        "Extracurricular_Activities": get_eca(id),
        "Internal_Marks": get_internal_marks(id),
        "Assignment_Submission_Rate": get_total_assignment_marks(id),
        "Internal_Assessment_Marks": get_internal_assesment_marks(id)
    }
    
    return Response(data)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_dashboard(request):
    if request.user.role != "student":
        return Response({"error":"only student can access this api", }, status=status.HTTP_401_UNAUTHORIZED)
    
    else :
        id = request.user.id 
        print(id)
        if  not id :
            return Response ({"error":"No user id found "}, status=status.HTTP_400_BAD_REQUEST)

        context = get_dashboard(id)
        if not context :
            return Response({"message":"Error while fetching student dashboard"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        return Response(context, status=status.HTTP_200_OK)
    
    
    
    
    
    
    