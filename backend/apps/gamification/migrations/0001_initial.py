import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("territories", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TierCapability",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tier", models.IntegerField(help_text="Governance tier at which this capability is unlocked (10, 50, 100, 1000).")),
                ("name", models.CharField(max_length=100)),
                ("key", models.SlugField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Tier Capability",
                "verbose_name_plural": "Tier Capabilities",
                "ordering": ["tier", "key"],
            },
        ),
        migrations.CreateModel(
            name="TerritoryProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("member_count", models.PositiveIntegerField(default=0)),
                ("group_count", models.PositiveIntegerField(default=0)),
                ("current_tier", models.IntegerField(default=0)),
                ("members_for_next_tier", models.IntegerField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "precinct",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="progress",
                        to="territories.precinct",
                    ),
                ),
            ],
            options={
                "verbose_name": "Territory Progress",
                "verbose_name_plural": "Territory Progress",
            },
        ),
    ]
