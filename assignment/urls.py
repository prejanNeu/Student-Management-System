# urls.py
from django.urls import path
from .views import (
    create_assignment, list_assignments, update_assignment, delete_assignment, 
    teacher_assignment_list, get_assignment_by_id, get_teacher_list,
    assignment_submission, assignment_submission_list, assignment_submission_edit, assignment_submission_delete
)



urlpatterns = [
    # Assignment URLs
    path('api/assignments/create/', create_assignment, name='create-assignment'),
    path('api/assignments/', list_assignments, name='list-assignments'),
    path('api/assignments/<int:pk>/update/', update_assignment, name='update-assignment'),
    path('api/assignments/<int:pk>/delete/', delete_assignment, name='delete-assignment'),
    path("api/teacher_assignment_list/",teacher_assignment_list,name="teacher_assignment_list"),
    path("api/get_assignment_by_id/<int:assignment_id>/", get_assignment_by_id, name="get_assignment_by_id"),
    path("api/get_teacher_list/", get_teacher_list, name="get_teacher_list"),
    
    # Assignment Submission URLs
    path('api/assignment-submissions/create/', assignment_submission, name='assignment-submission-create'),
    path('api/assignment-submissions/', assignment_submission_list, name='assignment-submission-list'),
    path('api/assignment-submissions/<int:pk>/edit/', assignment_submission_edit, name='assignment-submission-edit'),
    path('api/assignment-submissions/<int:pk>/delete/', assignment_submission_delete, name='assignment-submission-delete'),
]
