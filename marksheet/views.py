from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Max, Min, ExpressionWrapper, FloatField
from rest_framework import status
from django.db.models import Q
from .serializers import (
    MarksheetSerializer, 
    MarksheetListSerializer,
    ExamTypeSerializer,
    ClassParticipationSerializer,
    ClassParticipationListSerializer,
    ClassParticipationCreateSerializer
)
from .models import ExamType, Marksheet, ClassParticipation
from .permissions import (
    IsAdminOrTeacher, 
    CanViewMarks, 
    CanModifyMarks,
    IsAdminOrTeacherOrStudent
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from account.models import CustomUser


@swagger_auto_schema(
    method='post',
    request_body=MarksheetSerializer,
    responses={
        201: MarksheetSerializer,
        400: 'Bad Request',
        403: 'Permission Denied'
    },
    operation_description="Add new marks (Admin/Teacher only)"
)
@api_view(['POST'])
# @permission_classes([CanModifyMarks])
def add_marks(request):
    """
    Add new marks for students.
    Only admin and teacher users can add marks.
    """
    try:
        # Check if data is a list (bulk create) or single object
        if isinstance(request.data, list):
            serializer = MarksheetSerializer(data=request.data, many=True)
        else:
            serializer = MarksheetSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Marks added successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Validation error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            "message": "Error occurred while adding marks",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='put',
    request_body=MarksheetSerializer,
    responses={
        200: MarksheetSerializer,
        400: 'Bad Request',
        403: 'Permission Denied',
        404: 'Marksheet not found'
    },
    operation_description="Update existing marks (Admin/Teacher only)"
)
@api_view(['PUT'])
# @permission_classes([CanModifyMarks])
def update_mark(request, mark_id):
    """
    Update existing marks.
    Only admin and teacher users can update marks.
    """
    try:
        marksheet = get_object_or_404(Marksheet, id=mark_id)
        serializer = MarksheetSerializer(marksheet, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Mark updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Validation error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Marksheet.DoesNotExist:
        return Response({
            "message": "Marksheet record not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "message": "Error occurred while updating marks",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='delete',
    responses={
        200: 'Mark deleted successfully',
        403: 'Permission Denied',
        404: 'Marksheet not found'
    },
    operation_description="Delete marks (Admin/Teacher only)"
)
@api_view(['DELETE'])
# @permission_classes([CanModifyMarks])
def delete_mark(request, mark_id):
    """
    Delete marks.
    Only admin and teacher users can delete marks.
    """
    try:
        marksheet = get_object_or_404(Marksheet, id=mark_id)
        marksheet.delete()
        return Response({
            "message": "Mark deleted successfully"
        }, status=status.HTTP_200_OK)
        
    except Marksheet.DoesNotExist:
        return Response({
            "message": "Marksheet record not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "message": "Error occurred while deleting marks",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    responses={
        200: MarksheetListSerializer(many=True),
        403: 'Permission Denied'
    },
    operation_description="Get marks by class level (Admin/Teacher can view all, Students can view their own)"
)
@api_view(['GET'])
# @permission_classes([IsAdminOrTeacherOrStudent])
def mark_list_by_class(request, classlevel):
    """
    Get marks by class level.
    Admin and teachers can view all marks.
    Students can only view their own marks.
    """
    try:
        # if request.user.role == 'student':
        #     # Students can only view their own marks
        #     marks = Marksheet.objects.filter(
        #         classlevel_id=classlevel,
        #         student=request.user
        #     )
        # else:
            # Admin and teachers can view all marks
        marks = Marksheet.objects.filter(classlevel_id=classlevel)
        
        serializer = MarksheetListSerializer(marks, many=True)
        return Response({
            "message": "Marks retrieved successfully",
            "data": serializer.data,
            "count": len(serializer.data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "message": "Error occurred while retrieving marks",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    responses={
        200: MarksheetListSerializer(many=True),
        403: 'Permission Denied'
    },
    operation_description="Get all marks with role-based access control"
)
@api_view(['GET'])
# @permission_classes([IsAdminOrTeacherOrStudent])
def mark_list(request):
    """
    Get all marks with role-based access control.
    Admin and teachers can view all marks.
    Students can only view their own marks.
    """
    try:
        # if request.user.role == 'student':
        #     # Students can only view their own marks
        #     marks = Marksheet.objects.filter(student=request.user)
        # else:
            # Admin and teachers can view all marks
        marks = Marksheet.objects.all()
        
        # Apply filters if provided
        student_id = request.query_params.get('student_id')
        subject_id = request.query_params.get('subject_id')
        examtype_id = request.query_params.get('examtype_id')
        
        if student_id and request.user.role in ['admin', 'teacher']:
            marks = marks.filter(student_id=student_id)
        
        if subject_id:
            marks = marks.filter(subject_id=subject_id)
            
        if examtype_id:
            marks = marks.filter(examtype_id=examtype_id)
        
        serializer = MarksheetListSerializer(marks, many=True)
        return Response({
            "message": "Marks retrieved successfully",
            "data": serializer.data,
            "count": len(serializer.data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "message": "Error occurred while retrieving marks",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    responses={
        200: MarksheetListSerializer,
        403: 'Permission Denied',
        404: 'Marksheet not found'
    },
    operation_description="Get specific marks by ID with role-based access control"
)
@api_view(['GET'])
# @permission_classes([IsAdminOrTeacherOrStudent])
def get_mark_detail(request, mark_id):
    """
    Get specific marks by ID.
    Admin and teachers can view any marks.
    Students can only view their own marks.
    """
    try:
        marksheet = get_object_or_404(Marksheet, id=mark_id)
        
        # Check if student can view this mark
        if request.user.role == 'student' and marksheet.student != request.user:
            return Response({
                "message": "You can only view your own marks"
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MarksheetListSerializer(marksheet)
        return Response({
            "message": "Mark retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    except Marksheet.DoesNotExist:
        return Response({
            "message": "Marksheet record not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "message": "Error occurred while retrieving mark",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    request_body=ExamTypeSerializer,
    responses={
        201: ExamTypeSerializer,
        400: 'Bad Request',
        403: 'Permission Denied'
    },
    operation_description="Add new exam type (Admin/Teacher only)"
)
@api_view(['POST'])
# @permission_classes([IsAdminOrTeacher])
def add_exam_type(request):
    """
    Add new exam type.
    Only admin and teacher users can add exam types.
    """
    try:
        serializer = ExamTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Exam type added successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Validation error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            "message": "Error occurred while adding exam type",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    responses={
        200: ExamTypeSerializer(many=True),
        403: 'Permission Denied'
    },
    operation_description="Get all exam types"
)
@api_view(['GET'])
# @permission_classes([IsAdminOrTeacherOrStudent])
def get_exam_type(request):
    """
    Get all exam types.
    All authenticated users can view exam types.
    """
    try:
        exam_types = ExamType.objects.all()
        serializer = ExamTypeSerializer(exam_types, many=True)
        return Response({
            "message": "Exam types retrieved successfully",
            "data": serializer.data,
            "count": len(serializer.data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "message": "Error occurred while retrieving exam types",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    responses={
        200: 'Student performance statistics',
        403: 'Permission Denied'
    },
    operation_description="Get student performance statistics (Admin/Teacher only)"
)
@api_view(['GET'])
def student_performance_stats(request, student_id):
    
    try:
        marks = Marksheet.objects.filter(student_id=student_id)

        if not marks.exists():
            return Response({
                "message": "No marks found for this student"
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            student = CustomUser.objects.get(id=student_id)
            
        except:
            return Response("Something happen in the system")
        
        
        total_subjects = marks.values('subject').distinct().count()
        total_exams = marks.count()

        average_percentage = marks.aggregate(
            avg_percentage=ExpressionWrapper(
                (Avg('marks') * 100.0) / Avg('full_marks'),
                output_field=FloatField()
            )
        )['avg_percentage'] or 0

        # Serialize all marksheet records
        marksheet_data = MarksheetSerializer(marks, many=True).data

        return Response({
            "message": "Performance statistics retrieved successfully",
            "data": {
                "student_id": student_id,
                'student_name': student.full_name,
                "total_subjects": total_subjects,
                "total_exams": total_exams,
                "average_percentage": round(average_percentage, 2),
                "marksheets": marksheet_data  # all raw fields of marksheet
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "message": "Error occurred while retrieving performance statistics",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
        
@swagger_auto_schema(
    method='post',
    request_body=ClassParticipationCreateSerializer,
    responses={
        201: ClassParticipationSerializer,
        400: 'Bad Request',
        403: 'Permission Denied'
    },
    operation_description="Add class participation marks (Admin/Teacher only)"
)
@api_view(['POST'])
@permission_classes([IsAdminOrTeacher])
def add_class_participation(request):
    """
    Add class participation marks for students.
    Only admin and teacher users can add participation marks.
    """
    try:
        # Check if data is a list (bulk create) or single object
        if isinstance(request.data, list):
            serializer = ClassParticipationCreateSerializer(data=request.data, many=True, context={'request': request})
        else:
            serializer = ClassParticipationCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Class participation marks added successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Validation error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            "message": "Error occurred while adding class participation marks",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    responses={
        200: ClassParticipationListSerializer(many=True),
        403: 'Permission Denied'
    },
    operation_description="Get class participation records with role-based access control"
)
@api_view(['GET'])
@permission_classes([IsAdminOrTeacherOrStudent])
def get_class_participation_list(request):
    """
    Get class participation records.
    Admin and teachers can view all records.
    Students can only view their own records.
    """
    try:
        if request.user.role == 'student':
            # Students can only view their own participation records
            participations = ClassParticipation.objects.filter(student=request.user)
        else:
            # Admin and teachers can view all participation records
            participations = ClassParticipation.objects.all()
        
        # Apply filters if provided
        student_id = request.query_params.get('student_id')
        subject_id = request.query_params.get('subject_id')
        classlevel_id = request.query_params.get('classlevel_id')
        
        if student_id and request.user.role in ['admin', 'teacher']:
            participations = participations.filter(student_id=student_id)
        
        if subject_id:
            participations = participations.filter(subject_id=subject_id)
            
        if classlevel_id:
            participations = participations.filter(classlevel_id=classlevel_id)
        
        serializer = ClassParticipationListSerializer(participations, many=True)
        return Response({
            "message": "Class participation records retrieved successfully",
            "data": serializer.data,
            "count": len(serializer.data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "message": "Error occurred while retrieving class participation records",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    responses={
        200: ClassParticipationSerializer,
        403: 'Permission Denied',
        404: 'Class participation record not found'
    },
    operation_description="Get specific class participation record by ID"
)
@api_view(['GET'])
@permission_classes([IsAdminOrTeacherOrStudent])
def get_class_participation_detail(request, participation_id):
    """
    Get specific class participation record by ID.
    Admin and teachers can view any record.
    Students can only view their own records.
    """
    try:
        participation = get_object_or_404(ClassParticipation, id=participation_id)
        
        # Check if student can view this record
        if request.user.role == 'student' and participation.student != request.user:
            return Response({
                "message": "You can only view your own participation records"
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ClassParticipationSerializer(participation)
        return Response({
            "message": "Class participation record retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    except ClassParticipation.DoesNotExist:
        return Response({
            "message": "Class participation record not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "message": "Error occurred while retrieving class participation record",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='put',
    request_body=ClassParticipationSerializer,
    responses={
        200: ClassParticipationSerializer,
        400: 'Bad Request',
        403: 'Permission Denied',
        404: 'Class participation record not found'
    },
    operation_description="Update class participation record (Admin/Teacher only)"
)
@api_view(['PUT'])
@permission_classes([IsAdminOrTeacher])
def update_class_participation(request, participation_id):
    """
    Update class participation record.
    Only admin and teacher users can update participation records.
    """
    try:
        participation = get_object_or_404(ClassParticipation, id=participation_id)
        serializer = ClassParticipationSerializer(participation, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Class participation record updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Validation error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except ClassParticipation.DoesNotExist:
        return Response({
            "message": "Class participation record not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "message": "Error occurred while updating class participation record",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='delete',
    responses={
        200: 'Class participation record deleted successfully',
        403: 'Permission Denied',
        404: 'Class participation record not found'
    },
    operation_description="Delete class participation record (Admin/Teacher only)"
)
@api_view(['DELETE'])
@permission_classes([IsAdminOrTeacher])
def delete_class_participation(request, participation_id):
    """
    Delete class participation record.
    Only admin and teacher users can delete participation records.
    """
    try:
        participation = get_object_or_404(ClassParticipation, id=participation_id)
        participation.delete()
        return Response({
            "message": "Class participation record deleted successfully"
        }, status=status.HTTP_200_OK)
        
    except ClassParticipation.DoesNotExist:
        return Response({
            "message": "Class participation record not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "message": "Error occurred while deleting class participation record",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    responses={
        200: 'Student participation statistics',
        403: 'Permission Denied'
    },
    operation_description="Get student participation statistics (Admin/Teacher only)"
)
@api_view(['GET'])
@permission_classes([IsAdminOrTeacher])
def student_participation_stats(request, student_id):
    """
    Get student participation statistics.
    Only admin and teacher users can view participation statistics.
    """
    try:
        participations = ClassParticipation.objects.filter(student_id=student_id)

        if not participations.exists():
            return Response({
                "message": "No participation records found for this student"
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            student = CustomUser.objects.get(id=student_id)
        except CustomUser.DoesNotExist:
            return Response({
                "message": "Student not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        total_subjects = participations.values('subject').distinct().count()
        total_participations = participations.count()
        average_mark = participations.aggregate(avg_mark=Avg('mark'))['avg_mark'] or 0
        excellent_count = participations.filter(mark=5).count()
        good_count = participations.filter(mark__gte=4).count()

        # Serialize all participation records
        participation_data = ClassParticipationListSerializer(participations, many=True).data

        return Response({
            "message": "Participation statistics retrieved successfully",
            "data": {
                "student_id": student_id,
                'student_name': student.full_name,
                "total_subjects": total_subjects,
                "total_participations": total_participations,
                "average_mark": round(average_mark, 2),
                "excellent_count": excellent_count,
                "good_count": good_count,
                "participation_records": participation_data
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "message": "Error occurred while retrieving participation statistics",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        