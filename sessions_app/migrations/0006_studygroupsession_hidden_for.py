# Adds a per-user "hidden_for" M2M on StudyGroupSession so users can clear
# entries from their History tab without touching the underlying row.
#
# The host and other participants still see the session — this is a soft
# delete scoped to the requesting user, deliberately decoupled from the
# session's own lifecycle state (scheduled/live/completed/cancelled/expired).

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("sessions_app", "0005_studygroupchatmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="studygroupsession",
            name="hidden_for",
            field=models.ManyToManyField(
                blank=True,
                related_name="hidden_study_groups",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
