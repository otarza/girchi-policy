# Generated manually for GP-025

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("territories", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GroupOfTen",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=200)),
                ("is_full", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "precinct",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="groups",
                        to="territories.precinct",
                    ),
                ),
            ],
            options={
                "verbose_name": "Group of Ten",
                "verbose_name_plural": "Groups of Ten",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Membership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("left_at", models.DateTimeField(blank=True, null=True)),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="communities.groupoften",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="membership",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Membership",
                "verbose_name_plural": "Memberships",
                "ordering": ["-joined_at"],
            },
        ),
        migrations.AddIndex(
            model_name="groupoften",
            index=models.Index(
                fields=["precinct", "is_full"], name="communities_precin_4c8b3f_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="membership",
            index=models.Index(
                fields=["group", "is_active"], name="communities_group_i_13f8a2_idx"
            ),
        ),
    ]
