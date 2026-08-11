import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="TripPlan",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("request_payload", models.JSONField(default=dict)),
                ("result", models.JSONField(default=dict)),
                ("route_mode", models.CharField(default="demo", max_length=24)),
                (
                    "rule_set_version",
                    models.CharField(default="FMCSA-395-2022", max_length=32),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="DutyEvent",
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
                ("event_id", models.CharField(max_length=32)),
                ("sequence", models.PositiveIntegerField()),
                ("status", models.CharField(max_length=32)),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField()),
                ("duration_minutes", models.PositiveIntegerField()),
                ("route_distance_m", models.PositiveBigIntegerField(default=0)),
                ("coordinates", models.JSONField(blank=True, null=True)),
                ("reason_code", models.CharField(max_length=40)),
                ("remark", models.CharField(max_length=300)),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="duty_events",
                        to="trips.tripplan",
                    ),
                ),
            ],
            options={"ordering": ["sequence"]},
        ),
        migrations.AddConstraint(
            model_name="dutyevent",
            constraint=models.UniqueConstraint(
                fields=("trip", "sequence"), name="trip_event_sequence_unique"
            ),
        ),
    ]
