from django.urls import path 
from . import views 

urlpatterns = [
    path("api/score_prediction/", views.score_prediction, name="score_prediction"),
]