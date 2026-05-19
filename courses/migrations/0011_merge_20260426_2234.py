# 0011 - defused merge migration.
#
# Originally generated as a merge that listed
# ('courses', '0010_sessionrecording_live_session') as a parent. That
# parent migration has never existed in this repo's git history, so
# `manage.py migrate` fails with NodeNotFoundError.
#
# The original operations list was empty, so dropping that bogus
# dependency is safe. This file is now a no-op that simply chains
# after the real 0010 (course_subscription_duration_days) and
# contributes nothing of its own. It can be deleted entirely once
# the team is comfortable; we left it as a hollow file because the
# sandbox cannot delete files in the user-mounted folder.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0010_course_subscription_duration_days"),
    ]

    operations = []
