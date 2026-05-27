from rest_framework import serializers
from .models import StudyMaterial, MaterialFile


class MaterialFileSerializer(serializers.ModelSerializer):

    file_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = MaterialFile
        fields = ["id", "file_url", "file_name", "file_size"]

    def get_file_name(self, obj):
        try:
            return obj.filename()
        except (ValueError, AttributeError):
            return None

    def get_file_url(self, obj):
        if not obj.file:
            return None
        try:
            url = obj.file.url
        except ValueError:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_file_size(self, obj):
        if not obj.file:
            return None
        try:
            size = obj.file.size
        except (FileNotFoundError, OSError):
            return None
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{round(size / 1024, 1)} KB"
        return f"{round(size / (1024 * 1024), 1)} MB"


class StudyMaterialSerializer(serializers.ModelSerializer):

    files = serializers.SerializerMethodField()
    chapter_title = serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "chapter_title",
            "files",
        ]

    def get_files(self, obj):
        request = self.context.get("request")
        return MaterialFileSerializer(
            obj.files.all(),
            many=True,
            context={"request": request},
        ).data

    def get_chapter_title(self, obj):
        if obj.chapter:
            return obj.chapter.title
        return getattr(obj, "custom_chapter", None) or "No chapter"