from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import Student
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
from assignment.models import Assignment 
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncDate

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
            'date': assignment.created_at,  # This is datetime.datetime
            'class_name': f"Class {assignment.classlevel.level}" if assignment.classlevel else None
        })
    
    # Recent marks entries
    recent_marks = Marksheet.objects.order_by('-date')[:5]
    for mark in recent_marks:
        # Convert date to datetime for consistent comparison
        mark_datetime = datetime.combine(mark.date, datetime.min.time())
        activities.append({
            'type': 'marks',
            'title': f"Marks added for {mark.subject.name if mark.subject else 'Unknown Subject'}",
            'description': f"{mark.student.full_name} scored {mark.marks}/{mark.full_marks}",
            'date': mark_datetime,  # Convert to datetime for comparison
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
        return get_teacher_dashboard(user)
    elif user.role == "student":
        return get_student_dashboard(user)
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

def get_teacher_dashboard(teacher):
    """Comprehensive teacher dashboard"""
    # Basic counts
    teacher_assignments = Assignment.objects.filter(teacher=teacher)
    total_assignments = teacher_assignments.count()
    
    # Get classes taught by this teacher
    classes_taught = ClassLevel.objects.filter(
        assignments__teacher=teacher
    ).distinct()
    total_classes = classes_taught.count()
    
    # Get total students across all classes
    total_students = StudentClassEnrollment.objects.filter(
        class_level__in=classes_taught, is_current=True
    ).count()
    
    # Active assignments (not past deadline)
    today = timezone.now().date()
    active_assignments = teacher_assignments.filter(deadline__gte=today).count()
    
    # Recent assignments
    recent_assignments = teacher_assignments.order_by('-created_at')[:5]
    recent_assignments_data = []
    for assignment in recent_assignments:
        # Count submissions (assuming you have a submission model)
        submission_count = 0  # Placeholder - implement based on your submission model
        total_students_in_class = StudentClassEnrollment.objects.filter(
            class_level=assignment.classlevel, is_current=True
        ).count()
        
        recent_assignments_data.append({
            "id": assignment.id,
            "title": assignment.title,
            "subject": assignment.subject.name if assignment.subject else None,
            "class_name": f"Class {assignment.classlevel.level}" if assignment.classlevel else None,
            "deadline": assignment.deadline,
            "created_at": assignment.created_at,
            "submission_count": submission_count,
            "total_students": total_students_in_class
        })
    
    # Class performance
    class_performance = []
    for cls in classes_taught:
        student_count = StudentClassEnrollment.objects.filter(
            class_level=cls, is_current=True
        ).count()
        
        # Calculate average attendance for this class
        total_attendance = Attendance.objects.filter(classlevel=cls).count()
        present_attendance = Attendance.objects.filter(classlevel=cls, status="present").count()
        avg_attendance = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0
        
        # Calculate average marks for this class
        marks_avg = Marksheet.objects.filter(
            classlevel=cls
        ).aggregate(avg_marks=Avg('marks'))['avg_marks'] or 0
        
        assignments_count = Assignment.objects.filter(
            teacher=teacher, classlevel=cls
        ).count()
        
        class_performance.append({
            "class_id": cls.id,
            "class_name": f"Class {cls.level}",
            "level": cls.level,
            "student_count": student_count,
            "average_attendance": round(avg_attendance, 2),
            "average_marks": round(marks_avg, 2) if marks_avg else None,
            "assignments_count": assignments_count
        })
    
    # Assignments due today and this week
    assignments_due_today = teacher_assignments.filter(deadline=today).count()
    week_end = today + timedelta(days=7)
    assignments_due_this_week = teacher_assignments.filter(
        deadline__range=[today, week_end]
    ).count()
    
    # Average class attendance across all classes
    if classes_taught.exists():
        total_attendance_all = Attendance.objects.filter(classlevel__in=classes_taught).count()
        present_attendance_all = Attendance.objects.filter(
            classlevel__in=classes_taught, status="present"
        ).count()
        average_class_attendance = (present_attendance_all / total_attendance_all * 100) if total_attendance_all > 0 else 0
    else:
        average_class_attendance = 0
    
    # Upcoming deadlines
    upcoming_deadlines = teacher_assignments.filter(
        deadline__gte=today
    ).order_by('deadline')[:5]
    upcoming_deadlines_data = []
    for assignment in upcoming_deadlines:
        submission_count = 0  # Placeholder
        total_students_in_class = StudentClassEnrollment.objects.filter(
            class_level=assignment.classlevel, is_current=True
        ).count()
        
        upcoming_deadlines_data.append({
            "id": assignment.id,
            "title": assignment.title,
            "subject": assignment.subject.name if assignment.subject else None,
            "class_name": f"Class {assignment.classlevel.level}" if assignment.classlevel else None,
            "deadline": assignment.deadline,
            "created_at": assignment.created_at,
            "submission_count": submission_count,
            "total_students": total_students_in_class
        })
    
    data = {
        "total_classes": total_classes,
        "total_assignments": total_assignments,
        "total_students": total_students,
        "active_assignments": active_assignments,
        "recent_assignments": recent_assignments_data,
        "class_performance": class_performance,
        "assignments_due_today": assignments_due_today,
        "assignments_due_this_week": assignments_due_this_week,
        "average_class_attendance": round(average_class_attendance, 2),
        "upcoming_deadlines": upcoming_deadlines_data
    }
    
    serializer = TeacherDashboardSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)

def get_student_dashboard(student):
    """Comprehensive student dashboard"""
    # Get current class
    enrollment = StudentClassEnrollment.objects.filter(student=student, is_current=True).first()
    current_class = enrollment.class_level if enrollment else None
    
    # Student info
    student_name = student.full_name
    student_id = student.id
    
    # Attendance calculations
    total_days = Attendance.objects.filter(student=student).count()
    present_days = Attendance.objects.filter(student=student, status="present").count()
    absent_days = total_days - present_days
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    # Attendance trend (last 30 days)
    attendance_trend = []
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        was_present = Attendance.objects.filter(
            student=student, date=date, status="present"
        ).exists()
        attendance_trend.append({
            'date': date.isoformat(),
            'present': was_present
        })
    attendance_trend.reverse()
    
    # Assignments due
    today = timezone.now().date()
    assignments_due = 0
    assignments_overdue = 0
    assignments_due_list = []
    
    if current_class:
        assignments = Assignment.objects.filter(classlevel=current_class)
        for assignment in assignments:
            days_remaining = (assignment.deadline - today).days
            is_overdue = days_remaining < 0
            
            if days_remaining >= 0:
                assignments_due += 1
            else:
                assignments_overdue += 1
            
            assignments_due_list.append({
                "id": assignment.id,
                "title": assignment.title,
                "subject": assignment.subject.name if assignment.subject else None,
                "deadline": assignment.deadline,
                "days_remaining": days_remaining,
                "is_overdue": is_overdue
            })
    
    # Recent marks
    recent_marks = Marksheet.objects.filter(student=student).order_by('-date')[:5]
    recent_marks_data = []
    for mark in recent_marks:
        percentage = (float(mark.marks) / float(mark.full_marks) * 100) if mark.full_marks > 0 else 0
        recent_marks_data.append({
            "subject_name": mark.subject.name if mark.subject else "Unknown",
            "marks_obtained": mark.marks,
            "full_marks": mark.full_marks,
            "percentage": round(percentage, 2),
            "exam_type": mark.examtype.name if mark.examtype else None,
            "date": mark.date
        })
    
    # Calculate average marks
    marks_avg = Marksheet.objects.filter(student=student).aggregate(
        avg_marks=Avg('marks')
    )['avg_marks'] or 0
    
    # Marks trend (last 5 exams)
    marks_trend = []
    last_5_marks = Marksheet.objects.filter(student=student).order_by('-date')[:5]
    for mark in last_5_marks:
        percentage = (float(mark.marks) / float(mark.full_marks) * 100) if mark.full_marks > 0 else 0
        marks_trend.append({
            'date': mark.date.isoformat(),
            'percentage': round(percentage, 2),
            'subject': mark.subject.name if mark.subject else "Unknown"
        })
    
    # Quick stats
    total_subjects = Subject.objects.filter(
        classsubject__class_level=current_class
    ).count() if current_class else 0
    
    completed_assignments = 0  # Placeholder - implement based on submission model
    upcoming_exams = 0  # Placeholder - implement based on exam model
    
    # Attendance stats
    attendance_stats = {
        "total_days": total_days,
        "present_days": present_days,
        "absent_days": absent_days,
        "percentage": round(attendance_percentage, 2),
        "attendance_trend": attendance_trend
    }
    
    data = {
        "student_name": student_name,
        "current_class": ClassLevelSerializer(current_class).data if current_class else None,
        "student_id": student_id,
        "attendance_percentage": round(attendance_percentage, 2),
        "assignments_due": assignments_due,
        "assignments_overdue": assignments_overdue,
        "average_marks": round(marks_avg, 2) if marks_avg else None,
        "attendance_stats": attendance_stats,
        "recent_marks": recent_marks_data,
        "assignments_due_list": assignments_due_list,
        "marks_trend": marks_trend,
        "attendance_trend": attendance_trend,
        "total_subjects": total_subjects,
        "completed_assignments": completed_assignments,
        "upcoming_exams": upcoming_exams
    }
    
    serializer = StudentDashboardSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)
