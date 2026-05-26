from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0011_merge_20260426_2234"),
    ]

    operations = [
        migrations.AddField(
            model_name="board",
            name="description",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="board",
            name="is_active",
            field=models.BooleanField(
                default=True,
                help_text="Inactive boards render as 'Coming Soon' / dormant on the public site.",
            ),
        ),
    ]
