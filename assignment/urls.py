# urls.py
from django.urls import path
from .views import create_assignment, list_assignments, update_assignment, delete_assignment

urlpatterns = [
    path('assignments/create/', create_assignment, name='create-assignment'),
    path('assignments/', list_assignments, name='list-assignments'),
    path('assignments/<int:pk>/update/', update_assignment, name='update-assignment'),
    path('assignments/<int:pk>/delete/', delete_assignment, name='delete-assignment'),
]
