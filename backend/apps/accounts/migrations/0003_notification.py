import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_precinct_user_accounts_us_precinc_4d2098_idx"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("sos", "SOS Update"),
                            ("election", "Election"),
                            ("endorsement", "Endorsement"),
                            ("initiative", "Initiative"),
                            ("arbitration", "Arbitration"),
                            ("system", "System"),
                        ],
                        db_index=True,
                        default="system",
                        max_length=20,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("body", models.TextField(blank=True)),
                ("is_read", models.BooleanField(db_index=True, default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["user", "is_read"], name="accounts_no_user_id_is_read_idx"),
        ),
    ]
