
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
from django.db.models import Count, Q
from datetime import datetime, timedelta

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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_attendance(request, classlevel):
    """Get attendance for all students in a specific class (Teacher/Admin only)"""
    if request.user.role == "teacher" or request.user.role == "admin":
        try:
            classlevel_obj = ClassLevel.objects.get(id=classlevel)
            # Get all students enrolled in this class
            enrollments = StudentClassEnrollment.objects.filter(
                class_level=classlevel_obj, 
                is_current=True
            )
            
            attendance_data = []
            for enrollment in enrollments:
                student = enrollment.student
                # Get attendance for this student in this class
                student_attendance = Attendance.objects.filter(
                    student=student, 
                    classlevel=classlevel_obj
                ).order_by('-date')
                
                # Calculate attendance statistics
                total_days = student_attendance.count()
                present_days = student_attendance.filter(status="present").count()
                absent_days = student_attendance.filter(status="absent").count()
                late_days = student_attendance.filter(status="late").count()
                
                attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
                
                attendance_data.append({
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "total_days": total_days,
                    "present_days": present_days,
                    "absent_days": absent_days,
                    "late_days": late_days,
                    "attendance_percentage": round(attendance_percentage, 2),
                    "recent_attendance": AttendanceSerializer(student_attendance[:5], many=True).data
                })
            
            return Response({
                "message": "Attendance data retrieved successfully",
                "class_level": classlevel_obj.level,
                "data": attendance_data
            }, status=status.HTTP_200_OK)
            
        except ClassLevel.DoesNotExist:
            return Response({
                "message": "Class level not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "Error retrieving attendance data",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        "message": "You are not authorized to view class attendance"
    }, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    """Students mark their own attendance"""
    user = request.user 
    if user.role == "student" and user.is_active:
        current_enrollment = StudentClassEnrollment.objects.filter(student=user, is_current=True).first()
        if current_enrollment:
            try:
                # Check if attendance already exists for today
                today = timezone.now().date()
                existing_attendance = Attendance.objects.filter(
                    student=user, 
                    classlevel=current_enrollment.class_level,
                    date=today
                ).first()
                
                if existing_attendance:
                    return Response({
                        "message": "You have already marked your attendance for today"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create new attendance record
                obj = Attendance.objects.create(
                    student=user, 
                    classlevel=current_enrollment.class_level,
                    status="present",
                    date=today
                )
                
                return Response({
                    "message": "Attendance marked successfully for today",
                    "date": today,
                    "status": "present"
                }, status=status.HTTP_201_CREATED)
                
            except IntegrityError:
                return Response({
                    "message": "You are already present for today"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": "No class enrollment found"
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({
            "message": "Only active students can mark attendance"
        }, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance_with_status(request):
    """Students mark their own attendance with specific status (present/late)"""
    user = request.user 
    if user.role == "student" and user.is_active:
        current_enrollment = StudentClassEnrollment.objects.filter(student=user, is_current=True).first()
        if current_enrollment:
            try:
                status_type = request.data.get('status', 'present')
                
                # Validate status
                if status_type not in ['present', 'late']:
                    return Response({
                        "message": "Status must be 'present' or 'late'"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                today = timezone.now().date()
                existing_attendance = Attendance.objects.filter(
                    student=user, 
                    classlevel=current_enrollment.class_level,
                    date=today
                ).first()
                
                if existing_attendance:
                    # Update existing attendance status
                    existing_attendance.status = status_type
                    existing_attendance.save()
                    
                    return Response({
                        "message": f"Attendance status updated to {status_type}",
                        "date": today,
                        "status": status_type
                    }, status=status.HTTP_200_OK)
                else:
                    # Create new attendance record
                    obj = Attendance.objects.create(
                        student=user, 
                        classlevel=current_enrollment.class_level,
                        status=status_type,
                        date=today
                    )
                    
                    return Response({
                        "message": f"Attendance marked as {status_type}",
                        "date": today,
                        "status": status_type
                    }, status=status.HTTP_201_CREATED)
                
            except IntegrityError:
                return Response({
                    "message": "Error marking attendance"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": "No class enrollment found"
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({
            "message": "Only active students can mark attendance"
        }, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_statistics(request, classlevel_id=None):
    """Get attendance statistics for a class or overall (Teacher/Admin only)"""
    if request.user.role not in ["teacher", "admin"]:
        return Response({
            "message": "Only teachers and admins can view attendance statistics"
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get date range (default: last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        if classlevel_id:
            # Statistics for specific class
            try:
                classlevel = ClassLevel.objects.get(id=classlevel_id)
                attendance_data = Attendance.objects.filter(
                    classlevel=classlevel,
                    date__range=[start_date, end_date]
                )
                
                class_stats = {
                    "class_level": classlevel.level,
                    "total_students": StudentClassEnrollment.objects.filter(
                        class_level=classlevel, 
                        is_current=True
                    ).count(),
                    "date_range": {
                        "start": start_date,
                        "end": end_date
                    }
                }
            except ClassLevel.DoesNotExist:
                return Response({
                    "message": "Class level not found"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Overall statistics
            attendance_data = Attendance.objects.filter(
                date__range=[start_date, end_date]
            )
            class_stats = {
                "overall": True,
                "date_range": {
                    "start": start_date,
                    "end": end_date
                }
            }
        
        # Calculate statistics
        total_records = attendance_data.count()
        present_count = attendance_data.filter(status="present").count()
        absent_count = attendance_data.filter(status="absent").count()
        late_count = attendance_data.filter(status="late").count()
        
        # Daily breakdown
        daily_stats = attendance_data.values('date').annotate(
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late'))
        ).order_by('date')
        
        statistics = {
            **class_stats,
            "total_records": total_records,
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count,
            "attendance_rate": round((present_count / total_records * 100), 2) if total_records > 0 else 0,
            "daily_breakdown": list(daily_stats)
        }
        
        return Response({
            "message": "Attendance statistics retrieved successfully",
            "data": statistics
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "message": "Error retrieving attendance statistics",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_attendance_report(request, student_id):
    """Get detailed attendance report for a specific student (Teacher/Admin/Student own)"""
    try:
        # Check if user can view this student's attendance
        if request.user.role == "student":
            if request.user.id != student_id:
                return Response({
                    "message": "You can only view your own attendance"
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Get student
        try:
            student = CustomUser.objects.get(id=student_id, role='student')
        except CustomUser.DoesNotExist:
            return Response({
                "message": "Student not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get current enrollment
        enrollment = StudentClassEnrollment.objects.filter(
            student=student, 
            is_current=True
        ).first()
        
        if not enrollment:
            return Response({
                "message": "Student is not enrolled in any current class"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get attendance data
        attendance_data = Attendance.objects.filter(
            student=student,
            classlevel=enrollment.class_level
        ).order_by('-date')
        
        # Calculate statistics
        total_days = attendance_data.count()
        present_days = attendance_data.filter(status="present").count()
        absent_days = attendance_data.filter(status="absent").count()
        late_days = attendance_data.filter(status="late").count()
        
        # Monthly breakdown
        monthly_stats = attendance_data.extra(
            select={'month': "EXTRACT(month FROM date)"}
        ).values('month').annotate(
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late'))
        ).order_by('month')
        
        report = {
            "student": {
                "id": student.id,
                "name": student.full_name,
                "email": student.email
            },
            "class": {
                "id": enrollment.class_level.id,
                "level": enrollment.class_level.level
            },
            "statistics": {
                "total_days": total_days,
                "present_days": present_days,
                "absent_days": absent_days,
                "late_days": late_days,
                "attendance_percentage": round((present_days / total_days * 100), 2) if total_days > 0 else 0
            },
            "monthly_breakdown": list(monthly_stats),
            "recent_attendance": AttendanceSerializer(attendance_data[:10], many=True).data
        }
        
        return Response({
            "message": "Student attendance report retrieved successfully",
            "data": report
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "message": "Error retrieving student attendance report",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        print(objs)

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
def mark_attendance_by_id(request, id):
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


