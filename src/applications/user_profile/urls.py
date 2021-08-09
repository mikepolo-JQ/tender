from django.urls import path

from . import views
from .apps import UserProfileConfig

# from django.views.decorators.csrf import csrf_exempt


app_name = UserProfileConfig.label

urlpatterns = [
    path("<int:pk>/", views.UserProfileView.as_view(), name="profile"),
    path("contacts/add/", views.UserAddDeleteToContact.as_view(), name="add_contact"),
]
# csrf_exempt(
