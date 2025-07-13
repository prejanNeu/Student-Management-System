from django.urls import path 
from .views import attendance_detail, mark_attendance


urlpatterns = [
    path("api/attendance_detail/",attendance_detail, name="attendance_detail"),
    path("api/mark_attendance/", mark_attendance, name="mark_attendance"),
]