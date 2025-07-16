from django.urls import path 

from . import views 


urlpatterns = [
    path('',views.home,name="home"),
    path('api/user/',views.userDetail,name="user_detail"),
    path("api/students/<int:classlevel>", views.student_list, name="student_list"),
]