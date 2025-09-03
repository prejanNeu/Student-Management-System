from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from .serializers import (
    MarksheetSerializer, 
    MarksheetListSerializer,
    ExamTypeSerializer
)
from .models import ExamType, Marksheet
from .permissions import (
    IsAdminOrTeacher, 
    CanViewMarks, 
    CanModifyMarks,
    IsAdminOrTeacherOrStudent
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
    """
    Get performance statistics for a specific student.
    Only admin and teacher users can view performance statistics.
    """
    try:
        from django.db.models import Avg, Count, Max, Min, ExpressionWrapper, FloatField, F

        # Get all marks for the student
        marks = Marksheet.objects.filter(student_id=student_id)

        if not marks.exists():
            return Response({
                "message": "No marks found for this student"
            }, status=status.HTTP_404_NOT_FOUND)

        # Overall statistics
        total_subjects = marks.values('subject').distinct().count()
        total_exams = marks.count()

        average_percentage = marks.aggregate(
            avg_percentage=ExpressionWrapper(
                (Avg('marks') * 100.0) / Avg('full_marks'),
                output_field=FloatField()
            )
        )['avg_percentage'] or 0

        # Subject-wise statistics (with percentage)
        subject_stats = marks.values('subject__name').annotate(
            avg_marks=Avg('marks'),
            max_marks=Max('marks'),
            min_marks=Min('marks'),
            # exam_count=Count('id'),
            exam_type = marks.examtype.id,
            full_marks = marks.full_marks,
            avg_percentage=ExpressionWrapper(
                (Avg('marks') * 100.0) / Avg('full_marks'),
                output_field=FloatField()
            )
        )

        return Response({
            "message": "Performance statistics retrieved successfully",
            "data": {
                "student_id": student_id,
                "total_subjects": total_subjects,
                "total_exams": total_exams,
                "average_percentage": round(average_percentage, 2),
                "subject_wise_stats": list(subject_stats)  # ensure JSON serializable
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "message": "Error occurred while retrieving performance statistics",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

