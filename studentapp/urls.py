from django.urls import path 

from . import views 


urlpatterns = [
    path('',views.home,name="home"),
    path("api/register/student",views.register_student,name="register_student")
]