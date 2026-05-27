from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sessions_app", "0006_studygroupsession_hidden_for"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="StudyGroupSession",
            new_name="GroupSession",
        ),
        migrations.RenameModel(
            old_name="StudyGroupInvite",
            new_name="GroupSessionInvite",
        ),
        migrations.RenameModel(
            old_name="StudyGroupChatMessage",
            new_name="GroupSessionChatMessage",
        ),
        migrations.AlterField(
            model_name="groupsession",
            name="max_invitees",
            field=models.PositiveIntegerField(default=50),
        ),
    ]
