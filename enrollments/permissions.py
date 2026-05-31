from rest_framework.permissions import BasePermission
from .models import Enrollment


class IsEnrolledInCourse(BasePermission):
    """Grants access only to users with an ACTIVE enrollment in the course
    identified by `course_id` in the URL kwargs.

    NOTE ON THE NO-`course_id` CASE:
      The previous version returned True when the route had no `course_id`,
      which effectively granted access to *every* authenticated (or even
      anonymous) caller on such routes. That is an easy way to leak data.

      This version DENIES by default when there is no course in scope. If you
      have a list route that should be open to any logged-in user, don't guard
      it with this permission class — use IsAuthenticated there instead.
    """

    message = "You are not enrolled in this course."

    # Flip to True only if you have a deliberate reason to allow routes that
    # carry no course_id through this specific permission.
    allow_when_no_course = False

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        course_id = view.kwargs.get("course_id")
        if not course_id:
            return self.allow_when_no_course

        return Enrollment.objects.filter(
            user=request.user,
            course__id=course_id,
            status=Enrollment.STATUS_ACTIVE,
        ).exists()
