# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Assignment
from .serializers import AssignmentSerializer
from account.models import ClassLevel, StudentClassEnrollment # assuming user has classlevel
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method='post',
    request_body=AssignmentSerializer,
    responses={201: 'Assignment Created successfully'}
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_assignment(request):
    user = request.user
    if not user.role == "teacher":

        return Response({"error": "Only teachers can create assignments."}, status=status.HTTP_403_FORBIDDEN)
    
    data = request.data.copy()
    data['teacher'] = user.id  # assign teacher

    serializer = AssignmentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_assignments(request):
    user = request.user

    # Check if the user is a student
    if user.role == "student":
    # Get current class level enrollment
        enrollment = StudentClassEnrollment.objects.filter(student=user, is_current=True).first()
        if not enrollment:
            return Response({"error": "User is not enrolled in any class."}, status=status.HTTP_400_BAD_REQUEST)

        # Get assignments for the enrolled class
        class_level = enrollment.class_level
        assignments = Assignment.objects.filter(classlevel=class_level)

        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data)
    
    elif user.role == "teacher":
        objs = Assignment.objects.filter(teacher=request.user)

        serializer = AssignmentSerializer(objs, many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)
    
    elif user.role == "admin":

        objs = Assignment.objects.all()
        serializer = AssignmentSerializer(objs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:

        return Response({"message":"Ke garxa keta ho ramari kaam gara na yrr"}, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='put',
    request_body=AssignmentSerializer,
    responses={201: 'Assignment Created successfully'}
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if assignment.teacher != request.user:
        return Response({"error": "Only the teacher who created the assignment can update it."}, status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    data['teacher'] = assignment.teacher.id  # prevent changing teacher

    serializer = AssignmentSerializer(assignment, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if assignment.teacher != request.user and not request.user.is_staff:
        return Response({"error": "Only the teacher or admin can delete this assignment."}, status=status.HTTP_403_FORBIDDEN)
    if request.user == assignment.teacher:
        assignment.delete()

    if request.user == "admin":
        assignment.delete()
    return Response({"message": "Assignment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

