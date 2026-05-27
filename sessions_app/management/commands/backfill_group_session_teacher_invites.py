"""
Idempotent one-off (safe to re-run) backfill: ensure every GroupSession
that has ``invited_teacher_id`` set also has a matching ``GroupSessionInvite``
row with ``invite_role='teacher'``. Older groups created before that line
landed in ``create_group_session`` won't have it, which is why the teacher
dashboard's Accept/Decline buttons fail to appear for them — `myInvite` is
never found.

Usage:
    python manage.py backfill_group_session_teacher_invites
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from sessions_app.models import GroupSession, GroupSessionInvite


class Command(BaseCommand):
    help = (
        "Create missing teacher GroupSessionInvite rows for legacy study "
        "groups whose invited_teacher_id was set but never had a matching "
        "invite row. Idempotent and safe to re-run."
    )

    def handle(self, *args, **options):
        candidates = GroupSession.objects.filter(
            invited_teacher_id__isnull=False,
        ).only("id", "invited_teacher_id")

        created = 0
        skipped = 0
        for session in candidates:
            with transaction.atomic():
                exists = GroupSessionInvite.objects.filter(
                    session_id=session.id,
                    user_id=session.invited_teacher_id,
                ).exists()
                if exists:
                    skipped += 1
                    continue
                GroupSessionInvite.objects.create(
                    session_id=session.id,
                    user_id=session.invited_teacher_id,
                    invite_role="teacher",
                    status="pending",
                )
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Created teacher invite for session {session.id}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created}, already-present: {skipped}, "
                f"sessions checked: {created + skipped}."
            )
        )
