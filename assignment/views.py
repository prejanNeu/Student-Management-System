# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Assignment
from .serializers import AssignmentSerializer, AssignmentListDataSerializer
from account.models import ClassLevel, StudentClassEnrollment # assuming user has classlevel
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
    

    elif user.role == "admin":

        objs = Assignment.objects.all()
        serializer = AssignmentSerializer(objs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:

        return Response({"message":"Ke garxa keta ho ramari kaam gara na yrr"}, status=status.HTTP_400_BAD_REQUEST)
    

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('classlevel', openapi.IN_QUERY, description="Class Level ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('subject', openapi.IN_QUERY, description="Subject ID", type=openapi.TYPE_INTEGER),
    ]
)
@api_view(['GET'])
def teacher_assignment_list(request):

    if request.user.role == "teacher":
        classlevel = request.GET.get("classlevel")
        subject = request.GET.get("subject")

        if not classlevel or not subject:
            return Response({"error": "classlevel and subject are required"}, status=status.HTTP_400_BAD_REQUEST)

        data = Assignment.objects.filter(
            teacher=request.user,
            classlevel_id=classlevel,
            subject_id=subject
        )

        serializer = AssignmentSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.user.role == "admin":

        lasslevel = request.GET.get("classlevel")
        subject = request.GET.get("subject")

        if not classlevel or not subject:
            return Response({"error": "classlevel and subject are required"}, status=status.HTTP_400_BAD_REQUEST)

        data = Assignment.objects.filter(
            classlevel_id=classlevel,
            subject_id=subject
        )

        serializer = AssignmentSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response({"message": "You are not a teacher or admin , so you cannot view the assignments."}, status=status.HTTP_200_OK)


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

    if request.user == assignment.teacher:
        assignment.delete()

    if request.user == "admin":
        assignment.delete()
    return Response({"message": "Assignment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



@api_view(["GET"])
def get_assignment_by_id(request, assignment_id):
    
    assignment = Assignment.objects.filter(id= assignment_id).first()

    if assignment:
        serializer = AssignmentSerializer(assignment)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    else :
        return Response({"message":"assignment not found "}, status=status.HTTP_404_NOT_FOUND)

    
