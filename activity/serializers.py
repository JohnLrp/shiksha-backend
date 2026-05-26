"""
activity/serializers.py  — patched for mobile inbox.tsx compatibility

Changes vs original:
  ActivitySerializer → adds unread, subject (plain string), message alias,
                       lowercase type mapping
"""

from rest_framework import serializers
from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    """
    Returned by GET /activity/feed/

    Mobile inbox.tsx reads:
      n.id
      n.type          ← 'recording' | 'material' | 'quiz' | 'session'
      n.title ?? n.message
      n.subject       ← plain string (subtitle line)
      n.unread        ← bool
      n.created_at ?? n.when

    Activity.type DB values: ASSIGNMENT / QUIZ / SESSION / SUBMISSION
    """

    # ── Mobile-compat additions ───────────────────────────────────────────────
    unread  = serializers.SerializerMethodField()
    type    = serializers.SerializerMethodField()   # overrides auto field
    subject = serializers.SerializerMethodField()   # plain string
    message = serializers.CharField(source="title", read_only=True)

    class Meta:
        model  = Activity
        fields = [
            "id",
            "type",           # lowercased + mapped
            "title",
            "message",        # alias for title — inbox uses n.title ?? n.message
            "due_date",
            "is_read",
            "unread",         # inverted is_read — inbox uses n.unread
            "created_at",
            "subject_id",
            "subject_name",
            "subject",        # plain string — inbox uses n.subject
            "object_id",
        ]

    # Activity.TYPE_* → inbox.tsx TONE/FMAP keys
    _TYPE_MAP = {
        Activity.TYPE_SESSION:    "session",
        Activity.TYPE_QUIZ:       "quiz",
        Activity.TYPE_ASSIGNMENT: "material",
        Activity.TYPE_SUBMISSION: "material",
    }

    def get_unread(self, obj):
        return not obj.is_read

    def get_type(self, obj):
        return self._TYPE_MAP.get(obj.type, obj.type.lower())

    def get_subject(self, obj):
        return obj.subject_name or ""
