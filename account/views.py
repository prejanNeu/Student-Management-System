from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from.models import UserPhoto
from .serializers import RegisterSerializer, UserPhotoSerializer, RegisterUpdateSerializer, UserIdSerializer
from account.models import StudentClassEnrollment

User = get_user_model()


@swagger_auto_schema(
    method='post',
    request_body=RegisterSerializer,
    responses={201: 'User registered successfully'}
)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='put',
    request_body=RegisterUpdateSerializer,
    responses={200: 'User updated successfully'}
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user_id = request.data.get('id')
    if not user_id:
        return Response({"error": "User ID required for update"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    serializer = RegisterUpdateSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User updated successfully"}, status=200)

    return Response(serializer.errors, status=400)


@swagger_auto_schema(
    method='delete',
    request_body=UserIdSerializer,  # Optional: Create a separate serializer for ID input
    responses={204: 'User deleted successfully', 404: 'User not found'}
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    user_id = request.data.get('id')
    if not user_id:
        return Response({"error": "User ID is required to delete"}, status=400)
    
    if user_id == 46:
        return Response({"message":"ab bol ab bol tuh"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    user.delete()
    return Response({"message": "User deleted successfully"}, status=204)



@swagger_auto_schema(method='post', request_body=UserPhotoSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_user_photo(request):
    
    try:
        photo = request.user.photo  # related_name='photo'
    except UserPhoto.DoesNotExist:
        photo = None

    serializer = UserPhotoSerializer(instance=photo, data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=200)
    return Response(serializer.errors, status=400)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_picture(request):
    try:
        profile = UserPhoto.objects.get(user=request.user)
        if profile.user_image:
            picture_url = request.build_absolute_uri(profile.user_image.url)
            return Response({'profile_picture_url': picture_url})
        else:
            return Response({'error': 'No profile picture found'}, status=404)
    except UserPhoto.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=404)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_student_class(request):
    if request.user.role != "student":
        return Response({"message": "Only students can access their class info"}, status=status.HTTP_403_FORBIDDEN)

    student = request.user
    enrollment = StudentClassEnrollment.objects.filter(student=student, is_current=True).first()

    if not enrollment:
        return Response({"message": "No current class enrollment found"}, status=status.HTTP_404_NOT_FOUND)

    class_level = enrollment.class_level
    return Response({
        "class": {
            "id": class_level.id,
            "level": class_level.level
        }
    }, status=status.HTTP_200_OK)


