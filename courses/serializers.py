from rest_framework import serializers
from .models import Subject, Course


class SubjectSerializer(serializers.ModelSerializer):
    teachers = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = (
            "id",
            "name",
            "order",
            "teachers",
        )

    def get_teachers(self, obj):
        subject_teachers = (
            obj.subject_teachers
            .select_related("teacher__teacher_profile")
            .order_by("order")
        )

        data = []

        for st in subject_teachers:
            teacher = st.teacher
            profile = getattr(teacher, "teacher_profile", None)

            data.append({
                "id": teacher.id,
                "name": teacher.username,
                "display_role": st.display_role,
                "qualification": profile.qualification if profile else "",
                "bio": profile.bio if profile else "",
                "rating": profile.rating if profile else None,
                "photo": profile.photo.url if profile and profile.photo else None,
            })

        return data


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
