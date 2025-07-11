from account.views import register_user,upload_user_photo,update_user,delete_user
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    # Function-based registration
    path('api/register/', register_user, name='register_user'),
    path('api/register/update/', update_user, name='update_user'),
    path('api/register/delete/', delete_user, name='delete_user'),
    path("api/upload_photo/",upload_user_photo,name="upload_user_photo"),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]