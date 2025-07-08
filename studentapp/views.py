from django.shortcuts import render
from django.http import HttpResponse
from .models import Student 
from rest_framework.response import Response 


def home(request):
    return HttpResponse("You are in Home Page")


# def studentDetails(request,pk):
#     try :
        
        
        
        
        
    
    