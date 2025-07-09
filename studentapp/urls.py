from django.urls import path 

from . import views 


urlpatterns = [
    path('',views.home,name="home"),
    path('api/student/',views.studentDetail,name="student_detail"),
]