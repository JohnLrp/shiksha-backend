from django.urls import path
from .views import ChapterMaterials, UploadStudyMaterial

urlpatterns = [

    path(
        "chapters/<uuid:chapter_id>/materials/",
        ChapterMaterials.as_view()
    ),

    path(
        "materials/upload/",
        UploadStudyMaterial.as_view()
    ),
]
