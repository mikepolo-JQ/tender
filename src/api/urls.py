from django.urls import path

from . import views
from .apps import ApiConfig

# from django.views.decorators.csrf import csrf_exempt


app_name = ApiConfig.name

urlpatterns = [
    path("offer/", views.OfferListView.as_view(), name="offer"),
    path("data-update/", views.DataUpdateView.as_view(), name="update"),
    path("data-upload/", views.UploadToTheDBView.as_view(), name="upload"),
]
# csrf_exempt(
