import os
from django.conf import settings
from django.core.exceptions import ValidationError


ALLOWED_EXTENSIONS = {
    # Documents
    ".pdf",
    ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".odt", ".ods", ".odp",
    ".txt", ".csv", ".md", ".rtf",
    # Images
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic",
    # Audio
    ".mp3", ".wav", ".m4a", ".ogg",
}

BLOCKED_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".com", ".msi", ".scr",
    ".sh", ".bash", ".zsh", ".ps1",
    ".app", ".dmg", ".pkg",
    ".jar", ".apk", ".ipa",
    ".html", ".htm", ".svg", ".js", ".mjs",
    ".docm", ".xlsm", ".pptm",
    ".dll", ".so", ".dylib",
}

MAX_FILE_SIZE_MB = getattr(settings, "MATERIAL_MAX_FILE_SIZE_MB", 50)
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def validate_material_file(file_obj):
    """Validate an uploaded study-material file. Raises ValidationError on failure."""
    name = getattr(file_obj, "name", "") or ""
    ext = os.path.splitext(name)[1].lower()

    if ext in BLOCKED_EXTENSIONS:
        raise ValidationError(
            f"File type '{ext}' is not allowed for security reasons."
        )
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File type '{ext or 'unknown'}' is not supported. "
            f"Allowed: PDF, Word, PowerPoint, Excel, images, audio, text."
        )

    size = getattr(file_obj, "size", 0)
    if size == 0:
        raise ValidationError("File appears to be empty.")
    if size > MAX_FILE_SIZE_BYTES:
        size_mb = round(size / (1024 * 1024), 1)
        raise ValidationError(
            f"File is {size_mb} MB. Maximum allowed is {MAX_FILE_SIZE_MB} MB."
        )