import uuid
from django.db import models


class TripPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_payload = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    route_mode = models.CharField(max_length=24, default="demo")
    rule_set_version = models.CharField(max_length=32, default="FMCSA-395-2022")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DutyEvent(models.Model):
    trip = models.ForeignKey(
        TripPlan, related_name="duty_events", on_delete=models.CASCADE
    )
    event_id = models.CharField(max_length=32)
    sequence = models.PositiveIntegerField()
    status = models.CharField(max_length=32)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    route_distance_m = models.PositiveBigIntegerField(default=0)
    coordinates = models.JSONField(null=True, blank=True)
    reason_code = models.CharField(max_length=40)
    remark = models.CharField(max_length=300)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "sequence"], name="trip_event_sequence_unique"
            )
        ]
