# urls.py
from django.urls import path
from .views import create_assignment, list_assignments, update_assignment, delete_assignment, teacher_assignment_list, get_assignment_by_id



urlpatterns = [
    path('api/assignments/create/', create_assignment, name='create-assignment'),
    path('api/assignments/', list_assignments, name='list-assignments'),
    path('api/assignments/<int:pk>/update/', update_assignment, name='update-assignment'),
    path('api/assignments/<int:pk>/delete/', delete_assignment, name='delete-assignment'),
    path("api/teacher_assignment_list/",teacher_assignment_list,name="teacher_assignment_list"),
    path("api/get_assignment_by_id/<int:assignment_id>/", get_assignment_by_id, name="get_assignment_by_id"),
]
