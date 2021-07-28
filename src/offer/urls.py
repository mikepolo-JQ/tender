from django.urls import path

from . import views
from .apps import ApiConfig

# from django.views.decorators.csrf import csrf_exempt


app_name = ApiConfig.name

urlpatterns = [
    path("offer/", views.OfferListView.as_view(), name="offers"),
    path("store/", views.StoreListView.as_view(), name="stores"),
    path("store/<int:pk>/", views.StoreDetailView.as_view(), name="store"),
    path(
        "store/<int:pk>/reviews/",
        views.StoreReviewsView.as_view(),
        name="store_reviews",
    ),
    path("review/<int:pk>/", views.ReviewDetailView.as_view(), name="review"),
    path("review/<int:pk>/like/", views.ReviewLikeView.as_view(), name="review_like"),
    path("data-update/", views.DataUpdateView.as_view(), name="update"),
    path("data-upload/", views.UploadToTheDBView.as_view(), name="upload"),
]
# csrf_exempt(
