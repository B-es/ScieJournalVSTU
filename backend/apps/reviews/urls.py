from django.urls import path

from .views import MyReviewsView, ReassignView, RespondView

urlpatterns = [
    path("", MyReviewsView.as_view(), name="review-list"),
    path("<uuid:review_id>/respond", RespondView.as_view(), name="review-respond"),
    path("<uuid:review_id>/reassign", ReassignView.as_view(), name="review-reassign"),
]
