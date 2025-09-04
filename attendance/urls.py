from django.urls import path 
from .views import (
    attendance_detail, 
    mark_attendance, 
    class_list, 
    subject_list,
    get_student_by_class,
    get_attendance_detail_by_id,
    mark_attendance_by_id,
    # Enhanced attendance views (student-centric)
    student_attendance,
    mark_attendance_with_status,
    # attendance_statistics,
    student_attendance_report,
    get_attendance_summary_by_class
)


urlpatterns = [
    # Existing URLs (unchanged for frontend compatibility)
    path("api/attendance_detail/",attendance_detail, name="attendance_detail"),
    path("api/mark_attendance/", mark_attendance, name="mark_attendance"),
    path("api/class_list/", class_list, name="class_list"),
    path("api/subject_list/<int:classlevel>/",subject_list, name="subject_list"),
    path("api/get_student_by_class/<int:classlevel>", get_student_by_class, name="get_student_by_class"),
    path("api/get_attendance_detail_by_id/<int:id>/",get_attendance_detail_by_id,name="get_attendance_detail_by_id"),
    path("api/mark_attendance_by_id/<int:id>/", mark_attendance_by_id, name="mark_attendance_by_id"),
    
    # Enhanced student-centric attendance URLs
    path("api/student_attendance/<int:classlevel>/", student_attendance, name="student_attendance"),
    path("api/mark_attendance_with_status/", mark_attendance_with_status, name="mark_attendance_with_status"),
    # path("api/attendance_statistics/", attendance_statistics, name="attendance_statistics"),
    # path("api/attendance_statistics/<int:classlevel_id>/", attendance_statistics, name="attendance_statistics_class"),
    path("api/student_attendance_report/<int:student_id>/", student_attendance_report, name="student_attendance_report"),
    path("api/get_attendance_summary/<int:classlevel>", get_attendance_summary_by_class, name="get_summary"),
]