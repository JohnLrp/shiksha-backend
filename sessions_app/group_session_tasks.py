"""
Celery tasks for Group Sessions.

Hard-duration cutoff: when a group session's room_started_at + duration
elapses, this task is scheduled (from views.join_group_session) via
``apply_async(eta=...)`` and force-ends the session if it's still live.

The existing idle-cleanup mechanism (via management command +
consumer-side 5-minute timer) is reused via a longer 7-minute grace
period for group sessions — see cleanup_expired_sessions.
"""

from datetime import timedelta
import logging

from django.utils import timezone

from config.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=2, default_retry_delay=10)
def hard_expire_group_session(self, session_id):
    """
    Force-end a GroupSession when its duration has elapsed.

    Safe to call at any time: if the group is already completed /
    cancelled, this is a no-op.
    """
    try:
        from .models import GroupSession
        from .group_session_views import _end_group_session_internal, _broadcast

        session = GroupSession.objects.filter(pk=session_id).first()
        if not session:
            return
        if session.status != "live":
            return

        # Double-check timing in case the task fired early for any reason.
        if session.room_started_at:
            end_at = session.room_started_at + timedelta(minutes=session.duration_minutes)
            if timezone.now() < end_at:
                # Reschedule to the correct moment
                self.retry(countdown=max(1, int((end_at - timezone.now()).total_seconds())))
                return

        _end_group_session_internal(session, reason="hard_duration_cutoff")
        _broadcast(session)
    except Exception:
        logger.exception("hard_expire_group_session failed for %s", session_id)
