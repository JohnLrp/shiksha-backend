from django.urls import path
from .views import (
    CourseAssignmentsView,
    AssignmentDetailView,
    SubmitAssignmentView,
)

urlpatterns = [
    path(
        "courses/<uuid:course_id>/",
        CourseAssignmentsView.as_view(),
    ),
    path(
        "<uuid:assignment_id>/",
        AssignmentDetailView.as_view(),
    ),
    path(
        "<uuid:assignment_id>/submit/",
        SubmitAssignmentView.as_view(),
    ),
]
