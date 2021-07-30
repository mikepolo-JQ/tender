from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("applications.offer.urls"), name="offer"),
    path("api/profile/", include("applications.user_profile.urls"), name="profile"),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    # path("auth/", include("djoser.urls.jwt")),
]
