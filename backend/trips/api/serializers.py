from datetime import timezone
from decimal import Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from rest_framework import serializers


class TripPlanRequestSerializer(serializers.Serializer):
    current_location = serializers.CharField(max_length=240, trim_whitespace=True)
    pickup_location = serializers.CharField(max_length=240, trim_whitespace=True)
    dropoff_location = serializers.CharField(max_length=240, trim_whitespace=True)
    cycle_used_hours = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal("0"), max_value=Decimal("70")
    )
    start_datetime = serializers.DateTimeField(
        required=False, default_timezone=timezone.utc
    )
    log_timezone = serializers.CharField(
        max_length=64, required=False, default="America/Chicago"
    )
    driver_name = serializers.CharField(
        max_length=120, required=False, allow_blank=True
    )
    carrier_name = serializers.CharField(
        max_length=160, required=False, allow_blank=True
    )
    main_office_address = serializers.CharField(
        max_length=240, required=False, allow_blank=True
    )
    vehicle_number = serializers.CharField(
        max_length=80, required=False, allow_blank=True
    )
    shipping_document_number = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    shipper_commodity = serializers.CharField(
        max_length=200, required=False, allow_blank=True
    )

    def validate_log_timezone(self, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise serializers.ValidationError("Enter a valid IANA time zone.") from exc
        return value


class RecalculateSerializer(TripPlanRequestSerializer):
    current_location = serializers.CharField(max_length=240, required=False)
    pickup_location = serializers.CharField(max_length=240, required=False)
    dropoff_location = serializers.CharField(max_length=240, required=False)
    cycle_used_hours = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal("0"),
        max_value=Decimal("70"),
        required=False,
    )
