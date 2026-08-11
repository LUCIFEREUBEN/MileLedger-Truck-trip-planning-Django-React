from django.urls import path
from .views import HealthView, PlanTripView, RecalculateTripView, TripDetailView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("trips/plan/", PlanTripView.as_view(), name="trip-plan"),
    path("trips/<uuid:trip_id>/", TripDetailView.as_view(), name="trip-detail"),
    path(
        "trips/<uuid:trip_id>/recalculate/",
        RecalculateTripView.as_view(),
        name="trip-recalculate",
    ),
]
