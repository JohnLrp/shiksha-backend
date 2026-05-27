"""
Adds Instant Meeting + Admit-Mode + short-code support to GroupSession.

Schema changes:
  * GroupSession.short_code        — unique shareable code (e.g. 'zfk-pbmc-rxd')
  * GroupSession.session_type      — 'scheduled' | 'instant'
  * GroupSession.admit_mode        — 'open' | 'lobby'
  * GroupSession.subject           — now nullable (instant meetings have no subject)
  * GroupSession.subject_name      — now blank-able (mirrors the above)
  * GroupSession.duration_minutes  — choices extended with 3-hour option for instant rooms

Backwards-compatible: every existing row gets session_type='scheduled',
admit_mode='open', short_code='' (filled in lazily on next save where needed),
which preserves the current join semantics.
"""

import secrets
import string

from django.db import migrations, models


def _generate_short_code():
    alphabet = string.ascii_lowercase + string.digits
    parts = ["".join(secrets.choice(alphabet) for _ in range(3)) for _ in range(3)]
    return "-".join(parts)


def populate_short_codes(apps, schema_editor):
    GroupSession = apps.get_model("sessions_app", "GroupSession")
    used = set(
        GroupSession.objects.exclude(short_code="")
        .values_list("short_code", flat=True)
    )
    for gs in GroupSession.objects.filter(short_code=""):
        while True:
            code = _generate_short_code()
            if code not in used:
                used.add(code)
                break
        gs.short_code = code
        gs.save(update_fields=["short_code"])


class Migration(migrations.Migration):

    dependencies = [
        ("sessions_app", "0007_rename_study_group_to_group_session"),
        # courses app is referenced via the FK below — keep the existing dep chain.
    ]

    operations = [
        migrations.AddField(
            model_name="groupsession",
            name="short_code",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Short shareable code (e.g. 'zfk-pbmc-rxd').",
                max_length=20,
            ),
        ),
        migrations.RunPython(populate_short_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="groupsession",
            name="short_code",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Short shareable code (e.g. 'zfk-pbmc-rxd').",
                max_length=20,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="groupsession",
            name="session_type",
            field=models.CharField(
                choices=[("scheduled", "Scheduled"), ("instant", "Instant")],
                default="scheduled",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="groupsession",
            name="admit_mode",
            field=models.CharField(
                choices=[("open", "Allow anyone"), ("lobby", "Admit Users")],
                default="open",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="groupsession",
            name="subject",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.PROTECT,
                related_name="group_sessions",
                to="courses.subject",
            ),
        ),
        migrations.AlterField(
            model_name="groupsession",
            name="subject_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="groupsession",
            name="duration_minutes",
            field=models.PositiveIntegerField(
                choices=[
                    (30, "30 minutes"),
                    (45, "45 minutes"),
                    (60, "1 hour"),
                    (180, "3 hours"),
                ],
                default=45,
            ),
        ),
    ]
