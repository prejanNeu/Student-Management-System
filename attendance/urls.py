from django.urls import path 
from .views import (
    attendance_detail, 
    mark_attendance, 
    class_list, 
    subject_list,
    get_student_by_class
)


urlpatterns = [
    path("api/attendance_detail/",attendance_detail, name="attendance_detail"),
    path("api/mark_attendance/", mark_attendance, name="mark_attendance"),
    path("api/class_list/", class_list, name="class_list"),
    path("api/subject_list/<int:classlevel>/",subject_list, name="subject_list"),
    path("api/get_student_by_class/", get_student_by_class, name="get_student_by_class"),
]