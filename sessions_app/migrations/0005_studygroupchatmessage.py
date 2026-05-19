# Adds StudyGroupChatMessage so chat works inside study-group rooms.
#
# Per product spec, messages persist while the room is live and are
# bulk-deleted from the DB the moment the session is ended (handled in
# study_group_views._end_study_group_internal). The table itself stays
# in place across sessions.

import django.db.models.deletion
import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sessions_app", "0004_studygroupsession_studygroupinvite"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StudyGroupChatMessage",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("sender_name", models.CharField(max_length=255)),
                (
                    "sender_role",
                    models.CharField(default="student", max_length=20),
                ),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="study_group_messages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chat_messages",
                        to="sessions_app.studygroupsession",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
                "indexes": [
                    models.Index(
                        fields=["session", "created_at"],
                        name="sessions_ap_session_chatidx",
                    ),
                ],
            },
        ),
    ]
