from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from .serializers import MarksheetSerializer, ExamTypeSerializer
from rest_framework import status
from .models import ExamType, Marksheet


@api_view(['POST'])
def add_marks(request):

    serializer = MarksheetSerializer(data=request.data, many=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"message":"mula unique ketaharule kati pragati garisake tme mula marks add garera basa"}, status=status.HTTP_200)
    
    else :
        return Response({"message":"error while saving the data"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_mark(request, mark_id):

    try:
        marksheet = Marksheet.objects.get(id=mark_id)
    except Marksheet.DoesNotExist:
        return Response({"message": "Marksheet record not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = MarksheetSerializer(marksheet, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Mark updated successfully."}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def delete_mark(request):
    ...

def mark_list():
    ...


def add_exam_type(request):

    ...

@api_view(['GET'])
def get_exam_type(request):
    
    data = ExamType.objects.all()
    serializer = ExamTypeSerializer(data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




