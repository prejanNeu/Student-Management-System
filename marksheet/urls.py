from django.urls import path
from . import views 

urlpatterns = [
    # Exam Type APIs
    path("api/exam-types/", views.get_exam_type, name="get_exam_type"),
    path("api/exam-types/add/", views.add_exam_type, name="add_exam_type"),
    
    # Marks CRUD APIs
    path("api/marks/add/", views.add_marks, name="add_marks"),
    path("api/marks/update/<int:mark_id>/", views.update_mark, name="update_mark"),
    path("api/marks/delete/<int:mark_id>/", views.delete_mark, name="delete_mark"),
    path("api/marks/<int:mark_id>/", views.get_mark_detail, name="get_mark_detail"),
    path("api/marks/", views.mark_list, name="mark_list"),
    path("api/marks/class/<int:classlevel>/", views.mark_list_by_class, name="marks_by_class"),
    
    # Performance Statistics API
    path("api/performance/<int:student_id>/", views.student_performance_stats, name="student_performance_stats"),
    
    # Class Participation CRUD APIs
    path("api/class-participation/add/", views.add_class_participation, name="add_class_participation"),
    path("api/class-participation/", views.get_class_participation_list, name="get_class_participation_list"),
    path("api/class-participation/<int:participation_id>/", views.get_class_participation_detail, name="get_class_participation_detail"),
    path("api/class-participation/update/<int:participation_id>/", views.update_class_participation, name="update_class_participation"),
    path("api/class-participation/delete/<int:participation_id>/", views.delete_class_participation, name="delete_class_participation"),
    
    # Class Participation Statistics API
    path("api/participation-stats/<int:student_id>/", views.student_participation_stats, name="student_participation_stats"),
]