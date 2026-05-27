"""
Safety-net management command to auto-end private sessions that have been
empty (all participants left) for longer than the grace period.

This catches edge cases where Daphne restarted and the in-memory asyncio
timer was lost.

Usage:
    python manage.py cleanup_expired_sessions

Run via cron every few minutes on the server, e.g.:
    */3 * * * * cd /path/to/project && python manage.py cleanup_expired_sessions
"""

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from sessions_app.models import PrivateSession, GroupSession
from sessions_app.views import _end_session_internal


# Must match AUTO_EXPIRE_DELAY in consumers.py
GRACE_PERIOD = timedelta(minutes=5)
# Must match GROUP_SESSION_AUTO_EXPIRE_DELAY in consumers.py
GROUP_SESSION_GRACE_PERIOD = timedelta(minutes=7)
# How long a scheduled-but-never-opened group session lingers on the
# Invitations tab before being marked "Not attended" and moved to
# History. Measured from scheduled_date + scheduled_time.
GROUP_SESSION_UNATTENDED_GRACE = timedelta(hours=6)


class Command(BaseCommand):
    help = (
        "Auto-end private sessions where all participants left 5+ minutes "
        "ago, and group sessions where all participants left 7+ minutes ago. "
        "Also hard-expires group sessions whose selected duration has elapsed, "
        "and flags scheduled group sessions that nobody attended within 6h "
        "of their start time."
    )

    def handle(self, *args, **options):
        # ── Private sessions (unchanged behaviour) ───────────────────
        cutoff = timezone.now() - GRACE_PERIOD
        orphaned = PrivateSession.objects.filter(
            status="ongoing",
            all_left_at__isnull=False,
            all_left_at__lte=cutoff,
            active_connections__lte=0,
        )
        count = 0
        for session in orphaned:
            ended = _end_session_internal(session, reason="cleanup_command")
            if ended:
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  Auto-ended session {session.id}")
                )
        if count:
            self.stdout.write(
                self.style.SUCCESS(f"Cleaned up {count} expired session(s).")
            )
        else:
            self.stdout.write("No orphaned sessions found.")

        # ── Group sessions: idle cleanup ───────────────────────────────
        from sessions_app.group_session_views import _end_group_session_internal

        gs_cutoff = timezone.now() - GROUP_SESSION_GRACE_PERIOD
        gs_orphaned = GroupSession.objects.filter(
            status="live",
            all_left_at__isnull=False,
            all_left_at__lte=gs_cutoff,
            active_connections__lte=0,
        )
        gs_count = 0
        for session in gs_orphaned:
            if _end_group_session_internal(session, reason="cleanup_command_idle"):
                gs_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  Auto-ended group session {session.id}")
                )

        # ── Group sessions: hard-duration safety net ───────────────────
        now = timezone.now()
        live = GroupSession.objects.filter(
            status="live", room_started_at__isnull=False,
        )
        gs_hard = 0
        for session in live:
            end_at = session.room_started_at + timedelta(minutes=session.duration_minutes)
            if now >= end_at:
                if _end_group_session_internal(session, reason="cleanup_command_duration"):
                    gs_hard += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Duration-expired group session {session.id}"
                        )
                    )

        # ── Group sessions: unattended grace window ────────────────────
        # A group session that was scheduled but never opened (nobody
        # joined) lingers in the Invitations / Upcoming tabs for up to
        # GROUP_SESSION_UNATTENDED_GRACE after its scheduled start. After
        # that we flag it "expired" and leave `cancel_reason` empty so
        # the frontend can show "Not attended" (the distinguishing
        # marker is status == 'expired' AND room_started_at is NULL).
        scheduled_groups = GroupSession.objects.filter(
            status="scheduled", room_started_at__isnull=True,
        )
        gs_unattended = 0
        for session in scheduled_groups:
            try:
                scheduled_dt = timezone.make_aware(
                    datetime.combine(session.scheduled_date, session.scheduled_time)
                )
            except Exception:
                # Data glitch: if we can't compute, skip and log.
                self.stdout.write(
                    self.style.WARNING(
                        f"  Skipped {session.id}: bad scheduled_date/time."
                    )
                )
                continue

            if now >= scheduled_dt + GROUP_SESSION_UNATTENDED_GRACE:
                session.status = "expired"
                session.ended_at = now
                session.save(update_fields=["status", "ended_at", "updated_at"])
                gs_unattended += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Marked group session {session.id} as Not attended"
                    )
                )

        total_gs = gs_count + gs_hard + gs_unattended
        if total_gs:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Cleaned up {total_gs} group session(s) "
                    f"({gs_count} idle, {gs_hard} duration, "
                    f"{gs_unattended} not attended)."
                )
            )
        else:
            self.stdout.write("No orphaned group sessions found.")
