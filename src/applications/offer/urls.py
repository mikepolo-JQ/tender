from django.urls import path

from . import views
from .apps import OfferConfig

# from django.views.decorators.csrf import csrf_exempt


app_name = OfferConfig.label

urlpatterns = [
    path("offer/", views.OfferListView.as_view(), name="offers"),
    path("offer/<int:pk>/", views.OfferDetailView.as_view(), name="offer"),
    path(
        "offer/<int:pk>/reviews/",
        views.OwnerReviewsListView.as_view(),
        name="offer_reviews",
    ),
    path(
        "offer/<int:pk>/add-delete/",
        views.UserAddDeleteOffer.as_view(),
        name="offer_add_delete",
    ),
    path("store/", views.StoreListView.as_view(), name="stores"),
    path("store/<int:pk>/", views.StoreDetailView.as_view(), name="store"),
    path(
        "store/<int:pk>/reviews/",
        views.OwnerReviewsListView.as_view(),
        name="store_reviews",
    ),
    path("review/<int:pk>/", views.ReviewDetailView.as_view(), name="review"),
    path("review/<int:pk>/like/", views.ReviewLikeView.as_view(), name="review_like"),
    path("data-update/", views.DataUpdateView.as_view(), name="update"),
    path("data-upload/", views.UploadToTheDBView.as_view(), name="upload"),
]
# csrf_exempt(
