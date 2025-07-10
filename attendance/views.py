from django.shortcuts import rende
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from account.models import StudentClass 


@api_view(["GET"])
def view_attendance(request):
    
    user = request.user 
    
    if user.role == "student" and user.is_active:
        
        
        
        
        
        
        
    
    