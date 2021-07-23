from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views
from .apps import ApiConfig

# from django.views.decorators.csrf import csrf_exempt


app_name = ApiConfig.name

urlpatterns = [
    path("", views.UserListView.as_view(), name="hello")
]
# csrf_exempt(
