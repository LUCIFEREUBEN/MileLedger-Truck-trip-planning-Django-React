from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from trips.models import TripPlan
from trips.services.planner import create_plan
from trips.services.routing import RoutingError
from .serializers import RecalculateSerializer, TripPlanRequestSerializer


class HealthView(APIView):
    throttle_classes = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "mileledger-api",
                "version": "1.0.0",
                "route_mode": "live" if settings.OPENROUTESERVICE_API_KEY else "demo",
            }
        )


def _routing_error(exc: RoutingError) -> Response:
    fields = {exc.field: [exc.message]} if exc.field else {}
    return Response(
        {
            "code": exc.code,
            "message": exc.message,
            "field_errors": fields,
            "retryable": exc.retryable,
        },
        status=status.HTTP_503_SERVICE_UNAVAILABLE
        if exc.retryable
        else status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


class PlanTripView(APIView):
    def post(self, request):
        serializer = TripPlanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            trip = create_plan(serializer.validated_data)
        except RoutingError as exc:
            return _routing_error(exc)
        return Response(trip.result, status=status.HTTP_201_CREATED)


class TripDetailView(APIView):
    def get(self, request, trip_id):
        return Response(get_object_or_404(TripPlan, id=trip_id).result)


class RecalculateTripView(APIView):
    def post(self, request, trip_id):
        previous = get_object_or_404(TripPlan, id=trip_id)
        merged = {**previous.request_payload, **request.data}
        serializer = RecalculateSerializer(data=merged)
        serializer.is_valid(raise_exception=True)
        try:
            trip = create_plan(serializer.validated_data)
        except RoutingError as exc:
            return _routing_error(exc)
        return Response(trip.result, status=status.HTTP_201_CREATED)
