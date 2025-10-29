from django.urls import path 
from . import views 

urlpatterns = [
    path('',views.home,name="home"),
    path('api/user/',views.userDetail,name="user_detail"),
    path("api/students/<int:classlevel>", views.student_list, name="student_list"),
    path("api/update_student/", views.update_student, name="update_student"),
    path("api/dashboard/", views.dashboard_view, name="dashboard_view"),
    path("api/mark_prediction/", views.studentMarkPrediction, name="mark_prediction"),
    path("api/mark_prediction_by_id/<int:id>", views.studentMarkPredictionById, name="mark_prediction_by_id"),
    path("api/student_dashboard/", views.get_student_dashboard, name="student_dashboard"),
]